import asyncio
import subprocess
import numpy as np
import cv2
import websockets
import base64
import json
import os
from asgiref.sync import sync_to_async
import django
from datetime import datetime
import signal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grandview.settings")
django.setup()

import importlib
from django.conf import settings
from video.models import Video, Detection, Event
from custom_logic.models import UserEventAssignment
from custom_logic.utils import load_logic
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime, now

User = get_user_model()

MAX_CONNECTIONS = 10
FRAME_WIDTH = 2304
FRAME_HEIGHT = 1296
semaphore = asyncio.Semaphore(MAX_CONNECTIONS)


@sync_to_async
def get_video_and_model(video_id):
    video = Video.objects.select_related('yolo_model').get(id=video_id)
    model_path = video.yolo_model.model_file.path if video.yolo_model else "default_model.pt"
    return video, model_path

@sync_to_async
def get_video_creator(video_obj):
    return video_obj.created_by

@sync_to_async
def create_detection(user, video_obj, label, conf):
    Detection.objects.create(user=user, camera=video_obj, label=label, confidence=conf)

@sync_to_async
def evaluate_user_events(context):
    user = context["user"]
    labels = context["labels"]
    video_obj = context["video"]

    print(f"[DEBUG] Evaluating events for {user.username} with labels: {labels}")

    assignments = UserEventAssignment.objects.filter(user=user)
    for assignment in assignments:
        logic = load_logic(assignment.event_def.import_path)
        result = logic.evaluate_event(context)
        print(f"[DEBUG] Result from {assignment.event_def.name}:", result)

        if result:
            Event.objects.create(
                user=user,
                camera=video_obj,
                event_type=result.get("event_type", "CUSTOM_EVENT"),
                details=result.get("details", "")
            )

async def save_detections(result, video_obj, frame):
    try:
        user = await get_video_creator(video_obj)
        labels = []

        for box in result.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = box
            label = result.names[int(cls)]
            labels.append(label)
            await create_detection(user, video_obj, label, conf)

        context = {
            "labels": labels,
            "timestamp": localtime(now()),
            "camera_id": video_obj.id,
            "user": user,
            "video": video_obj,
            "frame": frame
        }

        await evaluate_user_events(context)

    except Exception as e:
        print("[ERROR] Failed to save detections:", e)

def start_ffmpeg(rtsp_url):
    cmd = [
        'ffmpeg', '-rtsp_transport', 'tcp', '-i', rtsp_url,
        '-loglevel', 'quiet', '-an',
        '-f', 'image2pipe', '-pix_fmt', 'bgr24', '-vcodec', 'rawvideo', '-'
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

async def video_stream(websocket, path):
    async with semaphore:
        video_id = path.strip("/").split("/")[-1]
        print(f"[INFO] WebSocket connection started for video ID: {video_id}")

        try:
            video_obj, model_path = await get_video_and_model(video_id)
            rtsp_url = video_obj.rtsp
        except Video.DoesNotExist:
            await websocket.send(json.dumps({'error': 'Invalid video ID'}))
            await websocket.close()
            return

        from ultralytics import YOLO
        model = YOLO(model_path)

        ffmpeg_proc = start_ffmpeg(rtsp_url)
        detection_tasks = []
        restart_attempts = 0

        try:
            while True:
                raw_frame = ffmpeg_proc.stdout.read(FRAME_WIDTH * FRAME_HEIGHT * 3)
                if not raw_frame:
                    print("[WARNING] No frame data received, restarting ffmpeg...")
                    ffmpeg_proc.terminate()
                    try:
                        os.killpg(os.getpgid(ffmpeg_proc.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    ffmpeg_proc.wait()

                    restart_attempts += 1
                    if restart_attempts > 3:
                        print("[ERROR] FFmpeg failed too many times, ending stream.")
                        break
                    ffmpeg_proc = start_ffmpeg(rtsp_url)
                    continue

                try:
                    frame = np.frombuffer(raw_frame, np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))
                except Exception as e:
                    print("[ERROR] Frame decode failed:", e)
                    continue

                try:
                    results = model(frame, conf=0.4)
                    annotated_frame = results[0].plot()
                except Exception as e:
                    print("[ERROR] YOLO inference failed:", e)
                    continue

                # Save detection task
                task = asyncio.create_task(save_detections(results[0], video_obj, frame))
                detection_tasks.append(task)

                if len(detection_tasks) > 10:
                    done, pending = await asyncio.wait(detection_tasks, return_when=asyncio.FIRST_COMPLETED)
                    detection_tasks = list(pending)

                try:
                    _, original_buf = cv2.imencode('.jpg', frame)
                    _, annotated_buf = cv2.imencode('.jpg', annotated_frame)

                    original_b64 = base64.b64encode(original_buf).decode('utf-8')
                    annotated_b64 = base64.b64encode(annotated_buf).decode('utf-8')

                    await websocket.send(json.dumps({
                        'original': original_b64,
                        'annotated': annotated_b64,
                    }))
                except websockets.exceptions.ConnectionClosed:
                    print("[INFO] WebSocket client disconnected")
                    break
                except Exception as e:
                    print("[ERROR] Failed to send frame to client:", e)
                    break

                await asyncio.sleep(0.1)

        except Exception as e:
            print("[CRITICAL] Unhandled error in video stream:", e)

        finally:
            print(f"[INFO] Closing stream for video ID: {video_id}")
            try:
                ffmpeg_proc.terminate()
                os.killpg(os.getpgid(ffmpeg_proc.pid), signal.SIGTERM)
                ffmpeg_proc.wait()
            except Exception as e:
                print("[WARNING] FFmpeg shutdown failed:", e)

async def main():
    print("🚀 WebSocket server starting on ws://0.0.0.0:8001")
    async with websockets.serve(video_stream, "0.0.0.0", 8001):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

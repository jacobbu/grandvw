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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grandview.settings")
django.setup()

from video.models import Video, Detection
from ultralytics import YOLO
from django.contrib.auth import get_user_model

User = get_user_model()

# Load YOLO model once
model = YOLO("/Users/jacobbuckner/Desktop/grandview/grandview/yolo11n.pt")  # Replace with your custom or pretrained model

# Store connected clients
connected_clients = {}

@sync_to_async
def get_video_creator(video_obj):
    return video_obj.created_by

async def save_detections(result, video_obj):
    user = await get_video_creator(video_obj)
    
    for box in result.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        await sync_to_async(Detection.objects.create)(
            user=video_obj.created_by,
            camera=video_obj,
            label=result.names[int(cls)],
            confidence=conf,
        )

async def video_stream(websocket, path):
    print("New WebSocket connection on:", path)

    video_id = path.strip("/").split("/")[-1]

    # Look up the RTSP URL from the database
    try:
        video_obj = await sync_to_async(Video.objects.get)(id=video_id)
        rtsp_url = video_obj.rtsp
        print(f"Requested stream for video ID: {video_id}")
        print(f"Resolved RTSP URL: {rtsp_url}")

    except Video.DoesNotExist:
        await websocket.send(json.dumps({'error': 'Invalid video ID'}))
        await websocket.close()
        return

    ffmpeg_cmd = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',
        '-i', rtsp_url,
        '-loglevel', 'quiet',
        '-an',  # disable audio
        '-f', 'image2pipe',
        '-pix_fmt', 'bgr24',
        '-vcodec', 'rawvideo',
        '-'
    ]

    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)

    connected_clients[websocket] = video_id

    try:
        frame_width = 2304
        frame_height = 1296

        while True:
            raw_frame = ffmpeg_proc.stdout.read(frame_width * frame_height * 3)
            if not raw_frame:
                print("No frame data received.")
                break

            frame = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))

            # Run YOLO detection
            results = model(frame)
            annotated_frame = results[0].plot()

            # Save detections to DB (non-blocking)
            asyncio.create_task(save_detections(results[0], video_obj))

            # Encode original and annotated frame
            _, original_buf = cv2.imencode('.jpg', frame)
            _, annotated_buf = cv2.imencode('.jpg', annotated_frame)

            original_b64 = base64.b64encode(original_buf).decode('utf-8')
            annotated_b64 = base64.b64encode(annotated_buf).decode('utf-8')

            await websocket.send(json.dumps({
                'original': original_b64,
                'annotated': annotated_b64,
            }))

            await asyncio.sleep(0.1)

    except Exception as e:
        print("Streaming error:", e)

    finally:
        ffmpeg_proc.terminate()
        connected_clients.pop(websocket, None)

async def main():
    print("WebSocket server starting on ws://0.0.0.0:8001")
    async with websockets.serve(video_stream, "0.0.0.0", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

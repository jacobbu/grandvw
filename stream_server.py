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

from video.models import Video

# Store connected clients
connected_clients = {}

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

    # Use your actual working RTSP stream here
    # rtsp_url = f"rtsp://admin:Buf57alo!@136.36.76.5:8554/h264Preview_01_main"

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

            _, buffer = cv2.imencode('.jpg', frame)
            encoded = base64.b64encode(buffer).decode('utf-8')
            await websocket.send(json.dumps({'image': encoded}))
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

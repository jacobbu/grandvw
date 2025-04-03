import asyncio
import cv2
import websockets
import base64
import json

# Store clients
connected_clients = {}

async def video_stream(websocket, path):
    # Parse video ID from URL
    video_id = path.strip("/").split("/")[-1]
    
    # replace this with database lookup if needed
    rtsp_url = f"rtsp://admin:Buf57alo!@192.168.86.200:554/h264Preview_01_main"  # Replace or fetch from DB

    cap = cv2.VideoCapture(rtsp_url)

    connected_clients[websocket] = video_id

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            encoded = base64.b64encode(buffer).decode('utf-8')
            await websocket.send(json.dumps({'image': encoded}))
            await asyncio.sleep(0.03)  # ~30 FPS
    except Exception as e:
        print("Error:", e)
    finally:
        cap.release()
        connected_clients.pop(websocket, None)

async def main():
    async with websockets.serve(video_stream, "localhost", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

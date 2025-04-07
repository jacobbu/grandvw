import threading
from datetime import datetime
from video.models import Event
from PIL import Image
import os

# Track active detection windows by (user_id, camera_id)
active_windows = {}

REQUIRED_ITEMS = {"Avy Beacon", "Avy Shovel", "Avy Probe", "Backpack"}

def finalize_event(user, camera_id, window_data):
    found = window_data["found"]
    video_obj = window_data["video"]
    frames = window_data.get("frames", [])

    print(f"[TIMER] Finalizing kit check for user={user.username} on camera={camera_id}")
    print(f"[TIMER] Found items: {found}")

    gif_file = None
    if frames:
        gif_path = f"media/event_gifs/event_{user.id}_{camera_id}_{int(datetime.now().timestamp())}.gif"
        save_gif(frames, gif_path)
        gif_file = f"event_gifs/{os.path.basename(gif_path)}"
    else:
        print("[TIMER] No frames captured — skipping GIF")

    missing = REQUIRED_ITEMS - found
    
    people = window_data.get("people", set())
    people_str = ", ".join(sorted(people)) if people else "Unknown"
    
    event_type = "✅ KIT_SUCCESS" if not missing else "❌ KIT_ERROR"
    details = "Avy kit packed" if not missing else f"Missing items: {', '.join(sorted(missing - {'Backpack'}))}"

    Event.objects.create(
        user=user,
        camera=video_obj,
        event_type=event_type,
        people=people_str,
        details=details,
        gif=gif_file
    )

    # Clear event window so a new one can start
    key = (user.id, camera_id)
    if key in active_windows:
        del active_windows[key]
        print(f"[TIMER] Cleared active window for {user.username} / Camera {camera_id}")



def evaluate_event(context):
    labels = set(context.get("labels", []))
    user = context.get("user")
    video = context.get("video")  # full Video object, not just ID

    if not user or not video:
        return None

    key = (user.id, video.id)

    # Start timer on Backpack detection
    if "Backpack" in labels and key not in active_windows:
        # Start a 30s window
        window_data = {
            "found": {"Backpack"},
            "start_time": datetime.now(),
            "video": video,
            "frames": []
        }
        timer = threading.Timer(30.0, finalize_event, args=[user, video.id, window_data])
        window_data["timer"] = timer
        active_windows[key] = window_data
        timer.start()

    # If timer is already active, add new labels
    if key in active_windows:
        active_windows[key]["found"].update(labels)

    if "Jacob" in labels:
        active_windows[key].setdefault("people", set()).add("Jacob")

    frame = context.get("frame")  # Pass this from stream_server.py

    if frame is not None and key in active_windows:
        active_windows[key]["frames"].append(frame.copy())

    return None  # do not return an event immediately


def save_gif(frames, output_path):
    pil_frames = [Image.fromarray(f) for f in frames]
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=100,  # ms per frame
        loop=0
    )

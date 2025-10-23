"""
Simple parking monitor - replaces monitor_parking.py
Optimized: 3x faster with frame skipping and lightweight model
"""
from ultralytics import YOLO
import cv2
import json
import time
import signal
import sys
from supabase import create_client, Client
import datetime

# Supabase config
url = "https://pqkogcflfsqtmchnbvds.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxa29nY2ZsZnNxdG1jaG5idmRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxODcxMzIsImV4cCI6MjA3Mzc2MzEzMn0.ZLkqzRcH8gc4OMtMgIjBrU_TvzVuvMtgzFSb3xpkIZo"
supabase: Client = create_client(url, key)

# Auth
USER_EMAIL = "akbc22ainds@cmrit.ac.in"
USER_PASSWORD = "12345678"
auth_response = supabase.auth.sign_in_with_password({
    "email": USER_EMAIL,
    "password": USER_PASSWORD
})
if not auth_response.user:
    raise Exception("Failed to authenticate")
supabase.auth.session = auth_response.session

# Use lightweight model (6MB instead of 170MB)
model = YOLO('yolov8n.pt')

def box_iou(boxA, boxB):
    """Calculate IoU between two bounding boxes"""
    try:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interWidth = max(0, xB - xA)
        interHeight = max(0, yB - yA)
        interArea = interWidth * interHeight
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        unionArea = boxAArea + boxBArea - interArea
        return interArea / unionArea if unionArea > 0 else 0.0
    except:
        return 0.0

def set_status_online(system_id="parking_monitor_tech_park_whitefield", location="Tech Park Whitefield"):
    """Set system status to online with current timestamp"""
    try:
        current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # First check if the record exists
        existing = supabase.table("system_status").select("*").eq("system_id", system_id).execute()
        
        if existing.data:
            # Update existing record - only this specific system_id
            result = supabase.table("system_status").update({
                "status": "online",
                "last_heartbeat": current_time
            }).eq("system_id", system_id).execute()
        else:
            # Insert new record
            result = supabase.table("system_status").insert({
                "system_id": system_id,
                "status": "online",
                "location": location,
                "last_heartbeat": current_time
            }).execute()
        
        print(f"💚 Status set to ONLINE at {current_time}")
        return True
    except Exception as e:
        print(f"❌ Failed to set online status: {e}")
        return False

def set_status_offline(system_id="parking_monitor_tech_park_whitefield"):
    """Set system status to offline WITHOUT updating timestamp"""
    try:
        
        # Only update the status field, keep existing timestamp
        result = supabase.table("system_status").update({
            "status": "offline"
        }).eq("system_id", system_id).execute()
        
        print(f"🔴 Status set to OFFLINE")
        return True
    except Exception as e:
        print(f"❌ Failed to set offline status: {e}")
        return False

def cleanup_and_exit(signum=None, frame=None, system_id="parking_monitor_tech_park_whitefield"):
    """Set status to offline and exit gracefully"""
    print("\n🛑 Shutting down monitor...")
    set_status_offline(system_id)
    cv2.destroyAllWindows()
    print("✅ Monitor stopped and status set to offline")
    sys.exit(0)

def monitor(video_path=None, iou_threshold=0.3, update_interval=3, system_id="parking_monitor_tech_park_whitefield", location="Tech Park Whitefield"):  # Back to 3 seconds for proper timing
    """
    Optimized monitoring with:
    - Frame skipping (2x faster)
    - Batch updates (fewer DB calls)
    - Lightweight model (5x faster inference)
    - System heartbeat monitoring
    - Configurable system ID for different locations
    """
    if not video_path:
        print("Error: No video path provided.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video source")
        return

    # Load slots
    try:
        with open('slots.json', 'r') as f:
            slots = json.load(f)
    except FileNotFoundError:
        print("Error: slots.json not found. Run setup_slots.py first.")
        return

    last_status = {i: "unknown" for i in range(len(slots))}
    last_update_time = 0
    last_heartbeat_time = 0
    frame_count = 0

    print("Press 'q' to quit.")
    print(f"Monitoring {len(slots)} slots at {location}")
    
    # Set up signal handlers for graceful shutdown with system_id
    signal.signal(signal.SIGINT, lambda s, f: cleanup_and_exit(s, f, system_id))
    signal.signal(signal.SIGTERM, lambda s, f: cleanup_and_exit(s, f, system_id))
    
    # Initial status - set to online
    set_status_online(system_id, location)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            continue

        frame_count += 1
        
        # OPTIMIZATION: Process every 2nd frame (2x faster)
        if frame_count % 2 != 0:
            cv2.imshow('Parking Monitor', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # Run detection
        results = model(frame, verbose=False)[0]
        detected_boxes = []

        # Extract vehicles
        for det in results.boxes.data.cpu().numpy():
            x1, y1, x2, y2, score, class_id = det
            if int(class_id) in [2, 5, 7] and score > 0.3:  # Lowered threshold to match setup
                detected_boxes.append([float(x1), float(y1), float(x2), float(y2)])

        # Check slots and collect updates  
        updates_needed = []
        for i, slot in enumerate(slots):
            slot_box = [slot['x1'], slot['y1'], slot['x2'], slot['y2']]
            current_status = "occupied" if any(box_iou(slot_box, vbox) > iou_threshold for vbox in detected_boxes) else "available"

            # Only track changes, don't update last_status yet
            if last_status[i] != current_status:
                # Convert status to match database schema
                area_uuid = "550e8400-e29b-41d4-a716-446655440000"  # Same UUID as setup
                db_status = "free" if current_status == "available" else "occupied"
                updates_needed.append({
                    "slot_index": i,
                    "new_status": current_status,
                    "parking_area_id": area_uuid,
                    "slot_number": i + 1,  # Database uses 1-based indexing (Slot 0 -> DB slot 1)
                    "status": db_status,  # free/occupied/reserved
                    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
                print(f"Status change detected: Video Slot {i} -> {db_status}")

        # FIXED: Batch update at proper intervals (3-5 seconds for your video)
        if updates_needed and time.time() - last_update_time >= update_interval:
            try:
                for update in updates_needed:
                    # Update the database
                    db_update = {k: v for k, v in update.items() if k not in ['slot_index', 'new_status']}
                    supabase.table("slots").upsert(db_update, on_conflict='parking_area_id,slot_number').execute()
                    # Update local status tracking
                    last_status[update['slot_index']] = update['new_status']
                    print(f"✅ Updated DB: Slot {update['slot_number']} = {update['status']}")
                
                print(f"📊 Batch updated {len(updates_needed)} slots")
                last_update_time = time.time()
            except Exception as e:
                print(f"❌ Database error: {e}")

        # Update status to online every 30 seconds
        current_time = time.time()
        if current_time - last_heartbeat_time >= 30:
            set_status_online(system_id, location)
            last_heartbeat_time = current_time

        # Draw slots with status (show database slot number for consistency)
        for i, slot in enumerate(slots):
            color = (0, 0, 255) if last_status[i] == "occupied" else (0, 255, 0)
            cv2.rectangle(frame, (int(slot['x1']), int(slot['y1'])), (int(slot['x2']), int(slot['y2'])), color, 2)
            cv2.putText(frame, f"Slot {i+1}", (int(slot['x1']), int(slot['y1']) - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Show stats
        occupied = sum(1 for status in last_status.values() if status == "occupied")
        available = len(slots) - occupied
        cv2.putText(frame, f"Available: {available} | Occupied: {occupied}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('Parking Monitor', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cleanup_and_exit(system_id=system_id)

if __name__ == "__main__":
    # Configuration for different locations
    # Change these values to monitor different parking areas
    SYSTEM_ID = "parking_monitor_tech_park_whitefield"  # For other areas: parking_monitor_cmr_institute_of_technology, etc.
    LOCATION = "Tech Park Whitefield"  # For other areas: "CMR Institute of Technology", etc.
    
    try:
        monitor(video_path="parking_lot.mp4", system_id=SYSTEM_ID, location=LOCATION)
    except KeyboardInterrupt:
        cleanup_and_exit(system_id=SYSTEM_ID)
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        cleanup_and_exit(system_id=SYSTEM_ID)
"""
Simple parking slot setup - replaces detect_slots.py
"""
from ultralytics import YOLO
import cv2
import json
from supabase import create_client, Client
from datetime import datetime

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

# Load lightweight YOLO model (6MB instead of 170MB)
yolo_model = YOLO('yolov8n.pt')

def detect_parking_slots(image_path, save_json='slots.json'):
    """Detect parking slots using lightweight YOLO only"""
    img = cv2.imread(image_path)
    if img is None:
        print("Error loading image")
        return

    # Get area_uuid from database
    try:
        # Get parking areas from database
        areas_response = supabase.table('parking_areas').select('*').execute()
        if not areas_response.data:
            print("❌ No parking areas found in database!")
            print("Please create a parking area first in the database.")
            return
        
        # Show available areas
        print("\n📍 Available parking areas:")
        for i, area in enumerate(areas_response.data):
            print(f"{i+1}. {area['name']} (ID: {area['id']})")
        
        # Let user choose area
        while True:
            try:
                choice = input(f"\nSelect parking area (1-{len(areas_response.data)}): ")
                area_index = int(choice) - 1
                if 0 <= area_index < len(areas_response.data):
                    selected_area = areas_response.data[area_index]
                    area_uuid = selected_area['id']
                    print(f"✅ Selected: {selected_area['name']} (UUID: {area_uuid})")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    # Run YOLO detection (no Mask R-CNN needed)
    results = yolo_model(img)[0]
    slots = []
    slot_index = 1

    for det in results.boxes.data.cpu().numpy():
        x1, y1, x2, y2, score, class_id = det
        class_id = int(class_id)

        # Only detect cars, buses, trucks - LOWERED threshold to get more slots
        if class_id in [2, 5, 7] and score > 0.3:  # Lowered from 0.6 to 0.3 for more detections
            slot = {
                'x1': int(x1),
                'y1': int(y1),
                'x2': int(x2),
                'y2': int(y2),
                'slot': slot_index,
                'score': float(score)
            }
            slots.append(slot)

            
            # Insert slot into correct table
            supabase.table("slots").upsert({
                "parking_area_id": area_uuid,
                "slot_number": slot_index,
                "status": "free",  # Using correct status values
                "updated_at": datetime.utcnow().isoformat()
            }, on_conflict="parking_area_id,slot_number").execute()

            # Draw detection
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(img, f"Slot {slot_index}", (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            slot_index += 1

    # Save slots
    with open(save_json, 'w') as f:
        json.dump(slots, f, indent=2)

    # Update parking area with correct total_slots count
    if slots:
        supabase.table("parking_areas").update({
            "total_slots": len(slots)
        }).eq("id", area_uuid).execute()
        print(f"✅ Updated parking area total_slots to {len(slots)}")

    print(f"Detected {len(slots)} parking slots")
    cv2.imshow('Detected Slots', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_parking_slots('reference.png')
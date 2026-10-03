from traffic_state import update_traffic
import cv2
import os
import time
import serial
from collections import deque
from datetime import datetime
from ultralytics import YOLO

# ==========================================
# CONFIGURATION
# ==========================================

CAMERA_INDEX = 0
MODEL_NAME = "yolo11n.pt"

ARDUINO_PORT = "COM15"
BAUD_RATE = 9600

LINE_Y = 350
CONFIDENCE = 0.35

SAVE_DIR = "captured_vehicles"

# Fixed signal mode for demonstration
SIGNAL_STATE = "RED"

# Traffic density settings
DENSITY_WINDOW = 10
LOW_LIMIT = 2
MEDIUM_LIMIT = 5

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

os.makedirs(SAVE_DIR, exist_ok=True)

# ==========================================
# ARDUINO CONNECTION
# ==========================================

arduino = None

try:
    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD_RATE,
        timeout=1
    )

    time.sleep(2)

    print("Arduino connected successfully!")

    # Set traffic signal to RED
    arduino.write(b"SIGNAL_RED\n")
    print("Traffic Signal: RED")

except serial.SerialException as e:
    print("Arduino unavailable:", e)
    print("Continuing in AI-only mode.")

def send_arduino(command):
    global arduino

    if arduino is None or not arduino.is_open:
        return

    try:
        arduino.write((command + "\n").encode("utf-8"))
        print("Arduino command:", command)

    except serial.SerialException as e:
        print("Arduino communication error:", e)

# ==========================================
# LOAD YOLO MODEL
# ==========================================

print("Loading YOLO model...")
model = YOLO(MODEL_NAME)

# ==========================================
# LAPTOP CAMERA
# ==========================================

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("ERROR: Laptop camera could not open.")

    if arduino is not None:
        arduino.close()

    raise SystemExit

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("AI Traffic Monitoring System Started!")
print("Signal Mode: FIXED RED")
print("Show traffic video on your phone.")
print("Press Q to exit.")

# ==========================================
# TRACKING VARIABLES
# ==========================================

previous_positions = {}
captured_ids = set()

vehicle_count = 0
violation_count = 0

crossing_times = deque()

current_density = "LOW"

send_arduino("LOW")

# ==========================================
# MAIN MONITORING LOOP
# ==========================================

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Could not receive camera frame.")
            break

        height, width = frame.shape[:2]
        line_y = min(LINE_Y, height - 1)

        now = time.time()

        # Remove old crossing events
        while (
            crossing_times
            and now - crossing_times[0] > DENSITY_WINDOW
        ):
            crossing_times.popleft()

        # ======================================
        # YOLO TRACKING
        # ======================================

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
            conf=CONFIDENCE
        )

        # ======================================
        # VIRTUAL STOP LINE
        # ======================================

        cv2.line(
            frame,
            (0, line_y),
            (width, line_y),
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "VIRTUAL STOP LINE",
            (20, max(line_y - 15, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        # Track whether this frame has a new violation
        new_violation = False

        # ======================================
        # PROCESS VEHICLES
        # ======================================

        for result in results:

            boxes = result.boxes

            if boxes is None or boxes.id is None:
                continue

            track_ids = boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):

                class_id = int(box.cls[0])

                if class_id not in VEHICLE_CLASSES:
                    continue

                vehicle_name = VEHICLE_CLASSES[class_id]

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].cpu().tolist()
                )

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (0, 0, 255),
                    -1
                )

                label = f"{vehicle_name} ID:{track_id}"

                cv2.putText(
                    frame,
                    label,
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                # ==================================
                # LINE CROSSING DETECTION
                # ==================================

                previous_y = previous_positions.get(track_id)

                crossed_line = (
                    previous_y is not None
                    and (
                        previous_y < line_y <= center_y
                        or
                        previous_y > line_y >= center_y
                    )
                )

                if (
                    crossed_line
                    and track_id not in captured_ids
                ):

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S_%f"
                    )

                    filename = os.path.join(
                        SAVE_DIR,
                        f"{vehicle_name}_ID{track_id}_{timestamp}.jpg"
                    )

                    # Count the crossing
                    captured_ids.add(track_id)
                    vehicle_count += 1
                    violation_count += 1

                    crossing_times.append(time.time())
                    new_violation = True

                    # Mark violation on current frame
                    cv2.putText(
                        frame,
                        "RED LIGHT VIOLATION - DEMO",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        3
                    )

                    # Save annotated evidence image
                    cv2.imwrite(filename, frame)

                    print("\n================================")
                    print("RED LIGHT VIOLATION - DEMO")
                    print("Signal:", SIGNAL_STATE)
                    print("Vehicle:", vehicle_name)
                    print("Tracking ID:", track_id)
                    print("Image:", filename)
                    print("Total Crossings:", vehicle_count)
                    print("Total Demo Violations:", violation_count)
                    print("================================")

                previous_positions[track_id] = center_y

        # ======================================
        # BUZZER EVENT
        # ======================================

        if new_violation and SIGNAL_STATE == "RED":
            send_arduino("EVENT")

        # ======================================
        # TRAFFIC DENSITY
        # ======================================

        recent_count = len(crossing_times)

        if recent_count <= LOW_LIMIT:
            new_density = "LOW"

        elif recent_count <= MEDIUM_LIMIT:
            new_density = "MEDIUM"

        else:
            new_density = "HIGH"

        if new_density != current_density:

            current_density = new_density
            send_arduino(current_density)

            print("Traffic Density:", current_density)

            update_traffic({
                "vehicle_count": vehicle_count,
                "violation_count": violation_count,
                "density": current_density,
                "lane": "LANE 1",
                "signal": SIGNAL_STATE,
                "system_status": "ONLINE"
            })

            

        # ======================================
        # DISPLAY INFORMATION
        # ======================================

        cv2.putText(
            frame,
            f"Signal: {SIGNAL_STATE}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Total Crossings: {vehicle_count}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Demo Violations: {violation_count}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"Vehicles in last 10 sec: {recent_count}",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Traffic Density: {current_density}",
            (20, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.imshow(
            "AI Traffic Monitoring System",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")

finally:

    cap.release()
    cv2.destroyAllWindows()

    if arduino is not None and arduino.is_open:
        arduino.close()

    print("\nTraffic Monitoring System Stopped!")
    print("Total Vehicle Crossings:", vehicle_count)
    print("Total Demo Violations:", violation_count)
    print("Images saved in:", SAVE_DIR)

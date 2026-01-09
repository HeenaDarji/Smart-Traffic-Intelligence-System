import cv2
import csv
from datetime import datetime
from ultralytics import YOLO
import os

# ================= LOAD MODEL =================
MODEL_PATH = r"C:\GDG hackthon\runs\detect\train3\weights\best.pt"
model = YOLO(MODEL_PATH)

# ================= CONSTANTS =================
EMISSION_FACTOR = {
    "motor": 0.02,
    "mobil": 0.12,
    "bus": 0.80,
    "truk": 1.00
}

IDLE_TIME = {
    "Low": 1,
    "Medium": 3,
    "High": 6
}

CSV_FILE = "traffic_data.csv"

# ================= CSV INIT =================
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", "time", "location",
                "car", "bike", "bus", "truck",
                "total", "density",
                "pollution", "fuel_waste"
            ])

init_csv()

# =========================================================
# ================= IMAGE PROCESSING ======================
# =========================================================
def process_image_and_get_density(image_path, location="Junction-1"):

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    results = model(image_path, conf=0.25)

    counts = {"mobil":0, "motor":0, "bus":0, "truk":0}

    for r in results:
        if r.boxes is not None:
            for cls in r.boxes.cls:
                label = model.names[int(cls)]
                if label in counts:
                    counts[label] += 1

    total = sum(counts.values())

    # -------- Density --------
    if total < 10:
        density = "Low"
    elif total < 25:
        density = "Medium"
    else:
        density = "High"

    idle = IDLE_TIME[density]

    # -------- Pollution --------
    pollution = round(
        counts["mobil"]*0.12 +
        counts["motor"]*0.02 +
        counts["bus"]*0.8 +
        counts["truk"]*1.0,
        2
    ) * idle

    # -------- Fuel Waste --------
    fuel_waste = round(total * idle * 0.01, 2)

    # -------- Save to CSV --------
    now = datetime.now()

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            now.date(), now.strftime("%H:%M"),
            location,
            counts["mobil"], counts["motor"],
            counts["bus"], counts["truk"],
            total, density,
            pollution, fuel_waste
        ])

    return (
        counts["mobil"], counts["motor"],
        counts["bus"], counts["truk"],
        total, density,
        pollution, fuel_waste
    )

# =========================================================
# ================= VIDEO PROCESSING ======================
# =========================================================
def process_video_for_presentation(video_path, frame_skip=15, location="Junction-1"):

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("❌ Could not open video file")

    frame_no = 0
    timeline = []
    pollution_timeline = []

    final_counts = {"mobil":0, "motor":0, "bus":0, "truk":0}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_no += 1
        if frame_no % frame_skip != 0:
            continue

        results = model(frame, conf=0.25)

        frame_total = 0
        frame_pollution = 0

        for r in results:
            if r.boxes is not None:
                for cls in r.boxes.cls:
                    label = model.names[int(cls)]
                    if label in final_counts:
                        final_counts[label] += 1
                        frame_total += 1
                        frame_pollution += EMISSION_FACTOR[label]

        timeline.append(frame_total)
        pollution_timeline.append(frame_pollution)

    cap.release()

    # -------- Averages --------
    avg = round(sum(timeline)/len(timeline), 2) if timeline else 0

    if avg < 10:
        density = "Low"
    elif avg < 25:
        density = "Medium"
    else:
        density = "High"

    idle = IDLE_TIME[density]

    avg_pollution = (
        round(sum(pollution_timeline)/len(pollution_timeline), 2) * idle
        if pollution_timeline else 0
    )

    fuel_waste = round(avg * idle * 0.01, 2)

    # -------- Save to CSV --------
    now = datetime.now()

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            now.date(), now.strftime("%H:%M"),
            location,
            final_counts["mobil"], final_counts["motor"],
            final_counts["bus"], final_counts["truk"],
            avg, density,
            avg_pollution, fuel_waste
        ])

    return {
        "final_counts": final_counts,
        "timeline": timeline,
        "pollution_timeline": pollution_timeline,
        "average": avg,
        "density": density,
        "pollution": avg_pollution,
        "fuel": fuel_waste
    }

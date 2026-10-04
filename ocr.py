import sqlite3
import cv2
import easyocr

VIDEOS = ["video.mp3.mp4", "video.mp4.mp4"]
DB = "results.db"
MIN_CONF = 0.20

conn = sqlite3.connect(DB)
conn.execute("DROP TABLE IF EXISTS ocr_results")
conn.execute("""
CREATE TABLE ocr_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video TEXT,
    timestamp REAL,
    text TEXT,
    confidence REAL
)
""")

reader = easyocr.Reader(["en"], gpu=False)

for name in VIDEOS:
    cap = cv2.VideoCapture(name)
    if not cap.isOpened():
        print("Could not open", name)
        continue

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    step = max(1, int(fps / 2))  # 2 frames per second
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            ts = round(i / fps, 2)
            found = 0
            for _, text, conf in reader.readtext(frame):
                text = text.replace(" ", "")
                if conf >= MIN_CONF and any(c.isdigit() for c in text):
                    conn.execute(
                        "INSERT INTO ocr_results (video, timestamp, text, confidence) VALUES (?, ?, ?, ?)",
                        (name, ts, text, float(conf)),
                    )
                    found += 1
            conn.commit()
            print(name, "second", ts, "-> readings:", found)
        i += 1
    cap.release()

conn.close()
print("Done. Results saved in results.db")
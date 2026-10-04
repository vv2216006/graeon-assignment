import cv2, os

for name in ["video.mp3.mp4", "video.mp4.mp4"]:
    cap = cv2.VideoCapture(name)
    ok = cap.isOpened()
    print(name, "-> opens:", ok)
    if ok:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print("   fps:", fps, "| frames:", frames, "| seconds:", round(frames / fps, 1))
        good, frame = cap.read()
        if good:
            cv2.imwrite(name + ".png", frame)
            print("   saved frame:", name + ".png")
    cap.release()
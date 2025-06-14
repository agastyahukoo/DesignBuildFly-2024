import cv2
import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Media files", "*.jpg *.jpeg *.png *.mp4 *.avi")])
    if file_path:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            infer_image(file_path)
        elif file_path.lower().endswith(('.mp4', '.avi')):
            infer_video(file_path)

def infer_image(path):
    model = YOLO("weights.yaml")
    results = model(path)
    for r in results:
        annotated = r.plot()
        cv2.imshow("Detection", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def infer_video(path):
    model = YOLO("weights.yaml")
    cap = cv2.VideoCapture(path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        for r in results:
            annotated = r.plot()
            cv2.imshow("Detection", annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Select Image or Video")
root.geometry("300x100")
btn = tk.Button(root, text="Select File", command=select_file)
btn.pack(expand=True)
root.mainloop()
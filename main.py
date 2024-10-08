import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
from roboflow import Roboflow
import threading
import time
import os
from fpdf import FPDF
from datetime import datetime
import shutil
from pygrabber.dshow_graph import FilterGraph
import numpy as np

# The open source model being used currently.. meaning it needs to be connected to internet
def initialize_roboflow():
    rf = Roboflow(api_key="Ig1F9Y1p5qSulNYEAxwb")
    project = rf.workspace().project("giam_sat_gian_lan")
    return project.version(2).model

model = initialize_roboflow()

camera_active = False
detection_active = False
cap = None
current_image = None
detections = []

# Helper Functions
def list_cameras():
    graph = FilterGraph()
    return graph.get_input_devices()

def create_temp_folder():
    if not os.path.exists("tempcaptures"):
        os.makedirs("tempcaptures")

def capture_cheating_image(detection, current_image):
    x_center, y_center = detection['x'], detection['y']
    width, height = int(detection['width']), int(detection['height'])
    x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
    x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

    cheating_image = current_image[y0:y1, x0:x1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"tempcaptures/cheating_{timestamp}.jpg"

    resized_cheating_image = cv2.resize(cheating_image, (1000, 1000))
    cv2.imwrite(image_filename, resized_cheating_image)

    history_text.insert(tk.END, f"Cheating detected at {timestamp}. Saved to {image_filename}\n")

def clear_temp_images():
    shutil.rmtree("tempcaptures")
    os.makedirs("tempcaptures")
    history_text.delete(1.0, tk.END)
    messagebox.showinfo("Images Cleared", "All temporary images have been cleared.")

# Camera Control Functions
def toggle_camera():
    global camera_active, cap
    camera_active = not camera_active
    if camera_active:
        use_camera()
        btn_camera.config(text="Stop Camera")
    else:
        stop_camera()
        btn_camera.config(text="Start Camera")

def use_camera():
    global cap
    camera_name = selected_camera.get()
    camera_index = camera_devices.index(camera_name)
    cap = cv2.VideoCapture(camera_index)
    if cap.isOpened():
        threading.Thread(target=update_camera, daemon=True).start()
    else:
        messagebox.showerror("Error", "Selected camera is not available.")

def stop_camera():
    global cap
    if cap and cap.isOpened():
        cap.release()
        cap = None

def update_camera():
    while cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            global current_image
            current_image = frame
            display_frame(frame)
        time.sleep(1 / 30)

# Frame Display Functions
def display_frame(frame):
    global detections
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    for detection in detections:
        if detection['class'] == label_filter.get():
            draw_bounding_box(image_rgb, detection)
    update_canvas(image_rgb)

def draw_bounding_box(image, detection):
    x_center, y_center = detection['x'], detection['y']
    width, height = detection['width'], detection['height']
    x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
    x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

    class_name = detection['class']
    confidence = detection['confidence']
    color = (0, 255, 0) if class_name == "not_cheating" else (255, 0, 0)

    cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
    label_text = class_name if display_mode.get() == "draw_labels" else f"{confidence:.2f}%"
    put_text(image, label_text, x0, y0, color)

def put_text(image, text, x, y, color):
    text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    text_x, text_y = x, y - text_size[1] - 4
    cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
    cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def update_canvas(image_rgb):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    image_pil = Image.fromarray(image_rgb)

    image_aspect = image_pil.width / image_pil.height
    canvas_aspect = canvas_width / canvas_height

    if image_aspect > canvas_aspect:
        new_width = canvas_width
        new_height = int(canvas_width / image_aspect)
    else:
        new_height = canvas_height
        new_width = int(canvas_height * image_aspect)

    image_pil = image_pil.resize((new_width, new_height), Image.LANCZOS)
    image_tk = ImageTk.PhotoImage(image_pil)

    canvas.create_image((canvas_width - new_width) // 2, (canvas_height - new_height) // 2, anchor=tk.NW, image=image_tk)
    canvas.image = image_tk

# Detection Functions
def toggle_detection():
    global detection_active
    detection_active = not detection_active
    if detection_active:
        threading.Thread(target=process_camera_feed, daemon=True).start()
        btn_toggle_detection.config(text="Stop Detection")
    else:
        btn_toggle_detection.config(text="Start Detection")

def process_camera_feed():
    while detection_active and cap and cap.isOpened():
        if current_image is not None:
            global detections
            detections = process_image(current_image)
        time.sleep(1)

def process_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    confidence_threshold = confidence_slider.get()
    result = model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()

    num_objects = len(result['predictions'])
    label.config(text=f"Detected Objects: {num_objects}")
    display_predictions(result['predictions'])

    return result['predictions']

def display_predictions(predictions):
    predictions_text.delete(1.0, tk.END)
    for detection in predictions:
        predictions_text.insert(tk.END, f"Class: {detection['class']}, Confidence: {detection['confidence']:.2f}%, "
                                        f"X: {detection['x']}, Y: {detection['y']}, Width: {detection['width']}, "
                                        f"Height: {detection['height']}\n")
        if detection['class'] == "cheating":
            capture_cheating_image(detection, current_image)

# PDF Generation
def save_pdf():
    pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_filename:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=20)
    pdf.cell(200, 10, txt="ProctorAI", ln=True, align="C")
    pdf.cell(200, 10, txt="Generated Report", ln=True, align="C")
    
    current_datetime = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {current_datetime}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Time: {current_time}", ln=True, align="C")
    
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for filename in os.listdir("tempcaptures"):
        if filename.endswith(".jpg"):
            image_path = os.path.join("tempcaptures", filename)
            pdf.cell(200, 10, txt=filename, ln=True)
            pdf.image(image_path, x=10, y=None, w=80)

    pdf.output(pdf_filename)
    messagebox.showinfo("PDF Saved", f"PDF saved as {pdf_filename}")
    clear_temp_images()

# Tkinter GUI Setup
root = tk.Tk()
root.title("ProctorAI")

dark_bg = "#2b2b2b"
dark_fg = "#e0e0e0"
accent_color = "#007acc"
root.configure(bg=dark_bg)

# Initialize Temp Folder
create_temp_folder()

# Define Widgets
frame = tk.Frame(root, bg=dark_bg)
frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame, bg=dark_bg, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

controls_frame = tk.Frame(root, bg=dark_bg)
controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

camera_label = tk.Label(controls_frame, text="Select Camera:", fg=dark_fg, bg=dark_bg)
camera_label.pack(side=tk.LEFT)

camera_devices = list_cameras()
selected_camera = tk.StringVar(value=camera_devices[0])
camera_dropdown = ttk.Combobox(controls_frame, textvariable=selected_camera, values=camera_devices)
camera_dropdown.pack(side=tk.LEFT)

btn_camera = tk.Button(controls_frame, text="Start Camera", command=toggle_camera, bg=accent_color, fg="white")
btn_camera.pack(side=tk.LEFT)

label_filter = tk.StringVar(value="cheating")
filter_label = tk.Label(controls_frame, text="Filter By:", fg=dark_fg, bg=dark_bg)
filter_label.pack(side=tk.LEFT)
filter_dropdown = ttk.Combobox(controls_frame, textvariable=label_filter, values=["cheating", "not_cheating"])
filter_dropdown.pack(side=tk.LEFT)

display_mode = tk.StringVar(value="draw_labels")
display_dropdown = ttk.Combobox(controls_frame, textvariable=display_mode, values=["draw_labels", "draw_confidence"])
display_dropdown.pack(side=tk.LEFT)

btn_toggle_detection = tk.Button(controls_frame, text="Start Detection", command=toggle_detection, bg=accent_color, fg="white")
btn_toggle_detection.pack(side=tk.LEFT)

confidence_label = tk.Label(controls_frame, text="Confidence Threshold:", fg=dark_fg, bg=dark_bg)
confidence_label.pack(side=tk.LEFT)
confidence_slider = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, bg=dark_bg, fg=dark_fg)
confidence_slider.pack(side=tk.LEFT)

btn_clear_images = tk.Button(controls_frame, text="Clear Images history", command=clear_temp_images, bg=accent_color, fg="white")
btn_clear_images.pack(side=tk.LEFT)

btn_save_pdf = tk.Button(controls_frame, text="Generate PDF Report", command=save_pdf, bg=accent_color, fg="white")
btn_save_pdf.pack(side=tk.LEFT)

# Text Widgets for Predictions and History
predictions_text = ScrolledText(root, height=5, bg=dark_bg, fg=dark_fg)
predictions_text.pack(fill=tk.X, padx=10, pady=5)

history_text = ScrolledText(root, height=5, bg=dark_bg, fg=dark_fg)
history_text.pack(fill=tk.X, padx=10, pady=5)

label = tk.Label(root, text="Detected Objects: 0", bg=dark_bg, fg=dark_fg)
label.pack(fill=tk.X)

# Start the Tkinter Event Loop
root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
from roboflow import Roboflow
import threading
import time
import os
from fpdf import FPDF

# Initialize Roboflow
def initialize_roboflow():
    rf = Roboflow(api_key="Ig1F9Y1p5qSulNYEAxwb")
    project = rf.workspace().project("giam_sat_gian_lan")
    return project.version(2).model

model = initialize_roboflow()

# Initialize main window
root = tk.Tk()
root.title("ProctorAI")

# Create folder for temporary captures
if not os.path.exists("tempcaptures"):
    os.makedirs("tempcaptures")

# Frame to organize layout
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Configure grid weights for responsiveness
for i in range(5):
    frame.grid_columnconfigure(i, weight=1)
frame.grid_rowconfigure(0, weight=1)

# Canvas to display image
canvas = tk.Canvas(frame, width=800, height=600)
canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")

# Label to display number of detected objects
label = tk.Label(frame, text="Detected Objects: 0")
label.grid(row=1, column=0, columnspan=4, sticky="ew")

# Slider for confidence threshold
confidence_slider = tk.Scale(frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Confidence Threshold")
confidence_slider.set(40)  # Default value
confidence_slider.grid(row=2, column=0, columnspan=4, sticky="ew")

# Dropdown for display mode
display_mode = tk.StringVar()
display_mode.set("draw_labels")  # Default value
display_mode_menu = ttk.Combobox(frame, textvariable=display_mode, values=("draw_labels", "draw_confidence"))
display_mode_menu.grid(row=3, column=0, columnspan=2, sticky="ew")

# Dropdown for label filter ("cheating", "not_cheating")
label_filter = tk.StringVar()
label_filter.set("cheating")  # Default value
label_filter_menu = ttk.Combobox(frame, textvariable=label_filter, values=("cheating", "not_cheating"))
label_filter_menu.grid(row=3, column=2, columnspan=2, sticky="ew")

# Text widget to display predictions
predictions_text = ScrolledText(frame, width=50, height=10)
predictions_text.grid(row=4, column=0, columnspan=2, sticky="nsew")

# History widget to show captured cheating images
history_text = ScrolledText(frame, width=50, height=10)
history_text.grid(row=4, column=2, columnspan=2, sticky="nsew")

# Global variables
current_image = None
last_slider_value = None
cap = None
last_update_time = 0
detections = []

def use_camera():
    """Start the camera feed."""
    global cap
    cap = cv2.VideoCapture(0)
    threading.Thread(target=update_camera, daemon=True).start()
    threading.Thread(target=process_camera_feed, daemon=True).start()

def update_camera():
    """Continuously read frames from the camera and display them."""
    while cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            global current_image
            current_image = frame
            display_frame(frame)
        time.sleep(1 / 30)  # 30 FPS

def display_frame(frame):
    """Draw bounding boxes and labels on the frame and display it on the canvas."""
    global detections
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    for detection in detections:
        if detection['class'] == label_filter.get():  # Apply label filter
            draw_bounding_box(image_rgb, detection)

    update_canvas(image_rgb)

def draw_bounding_box(image, detection):
    """Draw bounding boxes and labels/confidence on the image."""
    x_center, y_center = detection['x'], detection['y']
    width, height = detection['width'], detection['height']
    x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
    x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

    class_name = detection['class']
    confidence = detection['confidence']
    color = (0, 255, 0) if class_name == "not_cheating" else (255, 0, 0)

    # Draw bounding box and label/confidence
    cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
    label_text = class_name if display_mode.get() == "draw_labels" else f"{confidence:.2f}%"
    put_text(image, label_text, x0, y0, color)

def put_text(image, text, x, y, color):
    """Put a label or confidence score on the image."""
    text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    text_x, text_y = x, y - text_size[1] - 4
    cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
    cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def update_canvas(image_rgb):
    """Update the canvas with the current image."""
    image_pil = Image.fromarray(image_rgb)
    image_tk = ImageTk.PhotoImage(image_pil)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image = image_tk

def process_camera_feed():
    """Continuously process the camera feed and detect objects."""
    while cap and cap.isOpened():
        if current_image is not None:
            global detections
            detections = process_image(current_image)
        time.sleep(1)

def process_image(image):
    """Run the Roboflow model on the image and return detections."""
    if image is None:
        return []

    image_resized = cv2.resize(image, (640, 480))
    image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
    confidence_threshold = confidence_slider.get()
    result = model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()

    num_objects = len(result['predictions'])
    label.config(text=f"Detected Objects: {num_objects}")
    display_predictions(result['predictions'])

    return result['predictions']

def display_predictions(predictions):
    """Display object predictions in the text widget and capture cheating images."""
    predictions_text.delete(1.0, tk.END)
    for detection in predictions:
        predictions_text.insert(tk.END, f"Class: {detection['class']}, Confidence: {detection['confidence']:.2f}%, "
                                        f"X: {detection['x']}, Y: {detection['y']}, Width: {detection['width']}, "
                                        f"Height: {detection['height']}\n")
        if detection['class'] == "cheating":
            capture_cheating_image(detection)

def capture_cheating_image(detection):
    """Capture and store images of detected cheating."""
    global current_image

    if current_image is None:
        print("Warning: No current image available to capture.")
        return

    x_center, y_center = detection['x'], detection['y']
    width, height = detection['width'], detection['height']
    x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
    x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

    # Ensure the crop coordinates are within image bounds
    h, w, _ = current_image.shape
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)

    # Crop the cheating area
    cheating_image = current_image[y0:y1, x0:x1]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"tempcaptures/cheating_{timestamp}.jpg"
    cv2.imwrite(filename, cheating_image)

    # Add to history widget
    history_text.insert(tk.END, f"Captured: {filename}\n")

def generate_pdf():
    """Generate a PDF with the captured cheating images."""
    pdf = FPDF()
    image_files = [f for f in os.listdir("tempcaptures") if f.endswith(".jpg")]
    if not image_files:
        messagebox.showinfo("No Captures", "No cheating images found.")
        return
    
    for image_file in image_files:
        pdf.add_page()
        pdf.image(f"tempcaptures/{image_file}", x=10, y=10, w=190)  # Fit image to page
    
    pdf_file = "cheating_report.pdf"
    pdf.output(pdf_file)
    messagebox.showinfo("PDF Generated", f"PDF saved as {pdf_file}.")
    
    # Delete temporary images after generating PDF
    clear_temp_captures()

def clear_temp_captures():
    """Clear all temporary captured images."""
    for f in os.listdir("tempcaptures"):
        os.remove(f"tempcaptures/{f}")

def stop_preview():
    """Stop the camera preview and clear the canvas."""
    global cap, current_image
    if cap:
        cap.release()
        cap = None
    current_image = None
    canvas.delete("all")
    label.config(text="Detected Objects: 0")
    predictions_text.delete(1.0, tk.END)
    history_text.delete(1.0, tk.END)

def on_exit():
    """Handle app exit, including clearing temp files."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        stop_preview()
        clear_temp_captures()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)

# Buttons to use camera, stop preview, and generate PDF
btn_camera = tk.Button(frame, text="Use Camera", command=use_camera)
btn_camera.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

btn_stop = tk.Button(frame, text="Stop Preview", command=stop_preview)
btn_stop.grid(row=5, column=2, padx=10, pady=10, sticky="ew")

btn_pdf = tk.Button(frame, text="Generate PDF", command=generate_pdf)
btn_pdf.grid(row=5, column=3, padx=10, pady=10, sticky="ew")

# Run the application
root.mainloop()

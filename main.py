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

# Initialize Roboflow
def initialize_roboflow():
    rf = Roboflow(api_key="Ig1F9Y1p5qSulNYEAxwb")
    project = rf.workspace().project("giam_sat_gian_lan")
    return project.version(2).model

model = initialize_roboflow()

# Initialize main window
root = tk.Tk()
root.title("ProctorAI")

# Dark mode settings
dark_bg = "#2b2b2b"
dark_fg = "#e0e0e0"
accent_color = "#007acc"
root.configure(bg=dark_bg)

# Create folder for temporary captures
if not os.path.exists("tempcaptures"):
    os.makedirs("tempcaptures")

# Frame to organize layout
frame = tk.Frame(root, bg=dark_bg)
frame.pack(fill=tk.BOTH, expand=True)

# Configure grid weights for responsiveness
for i in range(5):
    frame.grid_columnconfigure(i, weight=1)
frame.grid_rowconfigure(0, weight=1)

# Canvas to display image
canvas = tk.Canvas(frame, width=800, height=600, bg=dark_bg, highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")

# Label to display number of detected objects
label = tk.Label(frame, text="Detected Objects: 0", bg=dark_bg, fg=dark_fg)
label.grid(row=1, column=0, columnspan=4, sticky="ew")

# Slider for confidence threshold
confidence_slider = tk.Scale(frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Confidence Threshold", bg=dark_bg, fg=dark_fg, highlightthickness=0)
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
predictions_text = ScrolledText(frame, width=50, height=10, bg=dark_bg, fg=dark_fg)
predictions_text.grid(row=4, column=0, columnspan=2, sticky="nsew")

# History widget to show captured cheating images
history_text = ScrolledText(frame, width=50, height=10, bg=dark_bg, fg=dark_fg)
history_text.grid(row=4, column=2, columnspan=2, sticky="nsew")

# Global variables
current_image = None
cap = None
detections = []
detection_active = False  # Track if detection is active

def use_camera():
    """Start the camera feed."""
    global cap
    cap = cv2.VideoCapture(0)
    threading.Thread(target=update_camera, daemon=True).start()

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

def toggle_detection():
    """Toggle the detection process on or off."""
    global detection_active
    detection_active = not detection_active
    if detection_active:
        threading.Thread(target=process_camera_feed, daemon=True).start()
        btn_toggle_detection.config(text="Stop Detection")
    else:
        btn_toggle_detection.config(text="Start Detection")

def process_camera_feed():
    """Continuously process the camera feed and detect objects."""
    while detection_active and cap and cap.isOpened():
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

    cheating_image = current_image[y0:y1, x0:x1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"tempcaptures/cheating_{timestamp}.jpg"
    cv2.imwrite(image_filename, cheating_image)

    # Add to history text widget
    history_text.insert(tk.END, f"Cheating detected at {timestamp}. Saved to {image_filename}\n")

def save_pdf():
    """Generate a PDF file with the cheating images."""
    # Open file dialog to select save location
    pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_filename:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add current date and time to the PDF
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(200, 10, txt=f"Cheating Report - {current_datetime}", ln=True, align="C")
    
    for filename in os.listdir("tempcaptures"):
        if filename.endswith(".jpg"):
            image_path = os.path.join("tempcaptures", filename)
            pdf.cell(200, 10, txt=filename, ln=True)
            pdf.image(image_path, x=10, y=None, w=100)

    pdf.output(pdf_filename)

    messagebox.showinfo("PDF Saved", f"PDF saved as {pdf_filename}")

    clear_temp_images()

def clear_temp_images():
    """Clear all temporary capture images."""
    for filename in os.listdir("tempcaptures"):
        file_path = os.path.join("tempcaptures", filename)
        os.remove(file_path)
    history_text.delete(1.0, tk.END)
    messagebox.showinfo("Images Cleared", "All temporary images have been cleared.")

# Create buttons
btn_camera = tk.Button(frame, text="Use Camera", command=use_camera, bg=accent_color, fg=dark_fg)
btn_camera.grid(row=5, column=0, sticky="ew")

btn_toggle_detection = tk.Button(frame, text="Start Detection", command=toggle_detection, bg=accent_color, fg=dark_fg)
btn_toggle_detection.grid(row=5, column=1, sticky="ew")

btn_pdf = tk.Button(frame, text="Generate PDF", command=save_pdf, bg=accent_color, fg=dark_fg)
btn_pdf.grid(row=5, column=2, sticky="ew")

btn_clear_images = tk.Button(frame, text="Clear Temp Images", command=clear_temp_images, bg=accent_color, fg=dark_fg)
btn_clear_images.grid(row=5, column=3, sticky="ew")

# Start the main loop
root.mainloop()

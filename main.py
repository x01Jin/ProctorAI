import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
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
import requests

class CameraManager:
    def __init__(self, root):
        self.camera_active = False
        self.cap = None
        self.current_image = None
        self.camera_devices = self.list_cameras()
        self.selected_camera = tk.StringVar(root, value=self.camera_devices[0])

    def list_cameras(self):
        graph = FilterGraph()
        return graph.get_input_devices()

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            self.use_camera()
            btn_camera.config(text="Stop Camera")
        else:
            self.stop_camera()
            btn_camera.config(text="Start Camera")

    def use_camera(self):
        camera_name = self.selected_camera.get()
        camera_index = self.camera_devices.index(camera_name)
        self.cap = cv2.VideoCapture(camera_index)
        if self.cap.isOpened():
            threading.Thread(target=self.update_camera, daemon=True).start()
        else:
            messagebox.showerror("Error", "Selected camera is not available.")

    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def update_camera(self):
        while self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_image = frame
                GUIManager.display_frame(frame)
            time.sleep(1 / 30)

class DetectionManager:
    def __init__(self, model):
        self.detection_active = False
        self.model = model
        self.detections = []

    def toggle_detection(self):
        self.detection_active = not self.detection_active
        if self.detection_active:
            threading.Thread(target=self.process_camera_feed, daemon=True).start()
            btn_toggle_detection.config(text="Stop Detection", bg=accent_color)
        else:
            btn_toggle_detection.config(text="Start Detection", bg=accent_color)

    def process_camera_feed(self):
        while self.detection_active and camera_manager.cap and camera_manager.cap.isOpened():
            if camera_manager.current_image is not None:
                self.detections = self.process_image(camera_manager.current_image)
            time.sleep(1)

    def process_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        confidence_threshold = confidence_slider.get()
        try:
            result = self.model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
            num_objects = len(result['predictions'])
            label.config(text=f"Detected Objects: {num_objects}")
            GUIManager.display_predictions(result['predictions'])
            return result['predictions']
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "An error occurred while attempting a connection. Please retry.")
            btn_toggle_detection.config(text="Retry", bg="red")
            self.detection_active = False
            return []

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 20)
        self.cell(0, 5, "Proctor AI", ln=True, align='C')
        self.set_font("Arial", 'B', 20)
        self.cell(0, 8, "Generated Report", ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def body(self, proctor_name, block, exam_date, subject, room):
        self.set_font("Arial", 'B', 12)
        self.cell(120, 7, f"Name: {proctor_name}", ln=False)
        self.cell(0, 7, f"Time: {datetime.now().strftime('%H:%M:%S')}", ln=True)
        self.cell(120, 7, f"Exam Date: {exam_date}", ln=False)
        self.cell(0, 7, f"Subject: {subject}", ln=True)
        self.cell(120, 7, f"Block: {block}", ln=False)
        self.cell(0, 7, f"Room: {room}", ln=True)

    @staticmethod
    def prompt_report_details():
        def on_submit():
            nonlocal proctor_name, block, exam_date, subject, room
            proctor_name = entry_proctor_name.get()
            block = entry_block.get()
            exam_date = entry_exam_date.get()
            subject = entry_subject.get()
            room = entry_room.get()
            root.destroy()

        root = tk.Tk()
        root.withdraw()

        dialog = tk.Toplevel(root)
        dialog.title("Report Details")

        tk.Label(dialog, text="Proctor's Name:").grid(row=0, column=0)
        entry_proctor_name = tk.Entry(dialog)
        entry_proctor_name.grid(row=0, column=1)

        tk.Label(dialog, text="Block:").grid(row=1, column=0)
        entry_block = tk.Entry(dialog)
        entry_block.grid(row=1, column=1)

        tk.Label(dialog, text="Exam Date:").grid(row=2, column=0)
        entry_exam_date = tk.Entry(dialog)
        entry_exam_date.grid(row=2, column=1)

        tk.Label(dialog, text="Subject:").grid(row=3, column=0)
        entry_subject = tk.Entry(dialog)
        entry_subject.grid(row=3, column=1)

        tk.Label(dialog, text="Room:").grid(row=4, column=0)
        entry_room = tk.Entry(dialog)
        entry_room.grid(row=4, column=1)

        submit_button = tk.Button(dialog, text="Submit", command=on_submit)
        submit_button.grid(row=5, columnspan=2)

        proctor_name = block = exam_date = subject = room = None
        root.wait_window(dialog)

        return proctor_name, block, exam_date, subject, room

    @staticmethod
    def save_pdf():
        proctor_name, block, exam_date, subject, room = PDFReport.prompt_report_details()
        if not all([proctor_name, block, exam_date, subject, room]):
            messagebox.showerror("Error", "All details must be provided.")
            return
    
        pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not pdf_filename:
            return
    
        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.body(proctor_name, block, exam_date, subject, room)
    
        image_count = 0
        x_positions = [10, 110]
        y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]
    
        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                if image_count > 0 and image_count % 4 == 0:
                    pdf.add_page()
                    y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]
    
                image_path = os.path.join("tempcaptures", filename)
                x = x_positions[image_count % 2]
                y = y_positions[(image_count // 2) % 2]
                pdf.image(image_path, x=x, y=y, w=90, h=90)
                image_count += 1
    
        pdf.output(pdf_filename)
        messagebox.showinfo("PDF Saved", f"PDF saved as {pdf_filename}")
        GUIManager.clear_temp_images()

class GUIManager:
    @staticmethod
    def create_temp_folder():
        if not os.path.exists("tempcaptures"):
            os.makedirs("tempcaptures")

    @staticmethod
    def capture_cheating_image(detection, current_image):
        x_center, y_center = detection['x'], detection['y']
        width, height = int(detection['width'] * 1.5), int(detection['height'] * 1.5)
        x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
        x1, y1 = int(x_center + width / 2), int(y_center + height / 2)

        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(current_image.shape[1], x1)
        y1 = min(current_image.shape[0], y1)

        cheating_image = current_image[y0:y1, x0:x1]

        if cheating_image.size == 0:
            print(f"Invalid crop: x0={x0}, y0={y0}, x1={x1}, y1={y1}, image_shape={current_image.shape}")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"tempcaptures/cheating_{timestamp}.jpg"

        cv2.imwrite(image_filename, cheating_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

        history_text.insert(tk.END, f"Cheating detected at {timestamp}. Saved to {image_filename}\n")

    @staticmethod
    def clear_temp_images():
        shutil.rmtree("tempcaptures")
        os.makedirs("tempcaptures")
        history_text.delete(1.0, tk.END)
        messagebox.showinfo("Images Cleared", "All temporary images have been cleared.")

    @staticmethod
    def display_frame(frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for detection in detection_manager.detections:
            if detection['class'] == label_filter.get():
                GUIManager.draw_bounding_box(image_rgb, detection)
        GUIManager.update_canvas(image_rgb)

    @staticmethod
    def draw_bounding_box(image, detection):
        fixed_width = 151
        fixed_height = 151

        x_center, y_center = detection['x'], detection['y']

        x0, y0 = int(x_center - fixed_width / 2), int(y_center - fixed_height / 2)
        x1, y1 = int(x_center + fixed_width / 2), int(y_center + fixed_height / 2)

        class_name = detection['class']
        confidence = detection['confidence']
        color = (0, 255, 0) if class_name == "not_cheating" else (255, 0, 0)

        cv2.rectangle(image, (x0, y0), (x1, y1), color, 1)
        label_text = class_name if display_mode.get() == "draw_labels" else f"{confidence:.2f}%"
        GUIManager.put_text(image, label_text, x0, y0, color)

    @staticmethod
    def put_text(image, text, x, y, color):
        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        text_x, text_y = x, y - text_size[1] - 4
        cv2.rectangle(image, (text_x, text_y), (text_x + text_size[0], text_y + text_size[1] + baseline), color, -1)
        cv2.putText(image, text, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    @staticmethod
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

    @staticmethod
    def display_predictions(predictions):
        predictions_text.delete(1.0, tk.END)
        for detection in predictions:
            predictions_text.insert(tk.END, f"Class: {detection['class']}, Confidence: {detection['confidence']:.2f}%, "
                                            f"X: {detection['x']}, Y: {detection['y']}, Width: {detection['width']}, "
                                            f"Height: {detection['height']}\n")
            if detection['class'] == "cheating":
                GUIManager.capture_cheating_image(detection, camera_manager.current_image)

# Initialize Roboflow model
def initialize_roboflow():
    rf = Roboflow(api_key="Ig1F9Y1p5qSulNYEAxwb")
    project = rf.workspace().project("giam_sat_gian_lan")
    return project.version(2).model

model = initialize_roboflow()

# Tkinter GUI Setup
root = tk.Tk()
root.title("ProctorAI")

dark_bg = "#2b2b2b"
dark_fg = "#e0e0e0"
accent_color = "#007acc"
root.configure(bg=dark_bg)

# Initialize Managers
camera_manager = CameraManager(root)
detection_manager = DetectionManager(model)

# Temp Folder for Image Captures
GUIManager.create_temp_folder()

# Define Widgets
frame = tk.Frame(root, bg=dark_bg)
frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame, bg=dark_bg, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

controls_frame = tk.Frame(root, bg=dark_bg)
controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

camera_label = tk.Label(controls_frame, text="Select Camera:", fg=dark_fg, bg=dark_bg)
camera_label.pack(side=tk.LEFT)

camera_dropdown = ttk.Combobox(controls_frame, textvariable=camera_manager.selected_camera, values=camera_manager.camera_devices)
camera_dropdown.pack(side=tk.LEFT)

btn_camera = tk.Button(controls_frame, text="Start Camera", command=camera_manager.toggle_camera, bg=accent_color, fg="white")
btn_camera.pack(side=tk.LEFT)

label_filter = tk.StringVar(value="cheating")
filter_label = tk.Label(controls_frame, text="Filter By:", fg=dark_fg, bg=dark_bg)
filter_label.pack(side=tk.LEFT)
filter_dropdown = ttk.Combobox(controls_frame, textvariable=label_filter, values=["cheating", "not_cheating"])
filter_dropdown.pack(side=tk.LEFT)

display_mode = tk.StringVar(value="draw_labels")
display_dropdown = ttk.Combobox(controls_frame, textvariable=display_mode, values=["draw_labels", "draw_confidence"])
display_dropdown.pack(side=tk.LEFT)

btn_toggle_detection = tk.Button(controls_frame, text="Start Detection", command=detection_manager.toggle_detection, bg=accent_color, fg="white")
btn_toggle_detection.pack(side=tk.LEFT)

confidence_label = tk.Label(controls_frame, text="Confidence Threshold:", fg=dark_fg, bg=dark_bg)
confidence_label.pack(side=tk.LEFT)
confidence_slider = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, bg=dark_bg, fg=dark_fg)
confidence_slider.pack(side=tk.LEFT)

btn_clear_images = tk.Button(controls_frame, text="Clear Images history", command=GUIManager.clear_temp_images, bg=accent_color, fg="white")
btn_clear_images.pack(side=tk.LEFT)

btn_save_pdf = tk.Button(controls_frame, text="Generate PDF Report", command=PDFReport.save_pdf, bg=accent_color, fg="white")
btn_save_pdf.pack(side=tk.LEFT)

# Text Widgets for Predictions and History
predictions_text = ScrolledText(root, height=5, bg=dark_bg, fg=dark_fg)
predictions_text.pack(fill=tk.X, padx=10, pady=5)

history_text = ScrolledText(root, height=5, bg=dark_bg, fg=dark_fg)
history_text.pack(fill=tk.X, padx=10, pady=5)

label = tk.Label(root, text="Detected Objects: 0", bg=dark_bg, fg=dark_fg)
label.pack(fill=tk.X)

root.mainloop()
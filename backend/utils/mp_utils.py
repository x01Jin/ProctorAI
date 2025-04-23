from multiprocessing import get_context, Queue, Event, Value
from queue import Empty, Full
import cv2
import logging

camera_logger = logging.getLogger("camera")
detection_logger = logging.getLogger("detection")

def start_camera_process(frame_queue: Queue, stop_event: Event, camera_index: int):
    ctx = get_context('spawn')
    process = ctx.Process(target=_camera_process_entry, args=(frame_queue, stop_event, camera_index))
    process.daemon = True
    return process

def start_detection_process(frame_queue: Queue, result_queue: Queue, stop_event: Event, model_config: dict, confidence_value: Value, connection_state: Value):
    ctx = get_context('spawn')
    process = ctx.Process(target=_detection_process_entry, args=(frame_queue, result_queue, stop_event, model_config, confidence_value, connection_state))
    process.daemon = True
    return process

def _camera_process_entry(frame_queue: Queue, stop_event: Event, camera_index: int):
    _camera_loop(frame_queue, stop_event, camera_index)

def _detection_process_entry(frame_queue: Queue, result_queue: Queue, stop_event: Event, model_config: dict, confidence_value: Value, connection_state: Value):
    _detection_loop(frame_queue, result_queue, stop_event, model_config, confidence_value, connection_state)

def _camera_loop(frame_queue: Queue, stop_event: Event, camera_index: int):
    cap = cv2.VideoCapture(camera_index)
    while not stop_event.is_set() and cap.isOpened():
        ret, frame = cap.read()
        if ret and not frame_queue.full():
            try:
                frame_queue.put_nowait(frame.copy())
            except Full:
                camera_logger.debug("Frame queue full, skipping frame")
                continue
    cap.release()

def _detection_loop(frame_queue: Queue, result_queue: Queue, stop_event: Event, model_config: dict, confidence_value: Value, connection_state: Value):
    model = model_config.get('model')
    while not stop_event.is_set():
        if not frame_queue.empty():
            try:
                frame = frame_queue.get_nowait()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                confidence = confidence_value.value
                connection_state.value = 0
                try:
                    results = model.predict(frame_rgb, confidence=confidence, overlap=30).json()
                    predictions = results.get('predictions', [])
                    try:
                        result_queue.put_nowait(predictions)
                    except Full:
                        detection_logger.debug("Result queue full, skipping predictions")
                except Exception:
                    connection_state.value = 2
                    import time
                    time.sleep(1)
                    continue
            except Empty:
                detection_logger.debug("Frame queue empty, waiting for next frame")
                continue
            except Exception as e:
                detection_logger.error(f"Error processing frame: {str(e)}")
                connection_state.value = 1
                continue

def clean_up_process(process, stop_event: Event):
    if not process:
        return
        
    if process.is_alive():
        stop_event.set()
        process.join(timeout=2)
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
    process.close()

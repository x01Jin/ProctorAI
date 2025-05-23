from multiprocessing import get_context
from multiprocessing.synchronize import Event as EventType
from multiprocessing.queues import Queue as QueueType
from multiprocessing.sharedctypes import Value as ValueType
from queue import Empty, Full
from typing import Dict, Any
import cv2
import logging
import time

camera_logger = logging.getLogger("camera")
detection_logger = logging.getLogger("detection")

CAM_WIDTH = 1280
CAM_HEIGHT = 720
CAM_FRAMES = 30.0

def start_camera_process(frame_queue: QueueType, stop_event: EventType, device_index: int):
    ctx = get_context('spawn')
    process = ctx.Process(target=_camera_process_entry, args=(frame_queue, stop_event, device_index))
    process.daemon = True
    return process

def start_detection_process(frame_queue: QueueType, result_queue: QueueType, stop_event: EventType, model_config: Dict[str, Any], confidence_value: ValueType, connection_state: ValueType):
    ctx = get_context('spawn')
    process = ctx.Process(target=_detection_process_entry, args=(frame_queue, result_queue, stop_event, model_config, confidence_value, connection_state))
    process.daemon = True
    return process

def _camera_process_entry(frame_queue: QueueType, stop_event: EventType, device_index: int):
    _camera_loop(frame_queue, stop_event, device_index)

def _detection_process_entry(frame_queue: QueueType, result_queue: QueueType, stop_event: EventType, model_config: Dict[str, Any], confidence_value: ValueType, connection_state: ValueType):
    _detection_loop(frame_queue, result_queue, stop_event, model_config, confidence_value, connection_state)

def _camera_loop(frame_queue: QueueType, stop_event: EventType, device_index: int):
    frame_interval = 1.0 / CAM_FRAMES
    cap = cv2.VideoCapture(device_index + cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    last_frame_time = 0
    
    while not stop_event.is_set() and cap.isOpened():
        current_time = time.time()
        time_since_last_frame = current_time - last_frame_time
        
        if time_since_last_frame < frame_interval:
            time.sleep(frame_interval - time_since_last_frame)
            continue
            
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
            
        try:
            frame_queue.put(frame, timeout=0.1)
            last_frame_time = time.time()
        except Full:
            camera_logger.debug("Frame queue full, maintaining frame rate")
            last_frame_time = time.time()
            
    cap.release()

def _detection_loop(frame_queue: QueueType, result_queue: QueueType, stop_event: EventType, model_config: Dict[str, Any], confidence_value: ValueType, connection_state: ValueType):
    import time
    model = model_config.get('model')
    frame_skip = 2
    frame_count = 0
    retry_delay = 0.1
    max_retry_delay = 2.0
    
    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=0.1)
            frame_count += 1
            
            if frame_count % frame_skip != 0:
                continue
                
            target_width, target_height = 320, 240
            frame_small = cv2.resize(frame, (target_width, target_height))
            frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
            confidence = confidence_value.value
            connection_state.value = 0
            
            try:
                results = model.predict(frame_rgb, confidence=confidence, overlap=30).json()
                predictions = results.get('predictions', [])
                if predictions:
                    scale_x = frame.shape[1] / target_width
                    scale_y = frame.shape[0] / target_height
                    
                    for pred in predictions:
                        pred['x'] = pred['x'] * scale_x
                        pred['y'] = pred['y'] * scale_y
                        if 'width' in pred:
                            pred['width'] = pred['width'] * scale_x
                        if 'height' in pred:
                            pred['height'] = pred['height'] * scale_y
                            
                    result_queue.put(predictions, timeout=0.1)
                retry_delay = 0.1
                
            except Exception as e:
                detection_logger.error(f"Model prediction error: {str(e)}")
                connection_state.value = 2
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                continue
                
        except Empty:
            time.sleep(0.01)
        except Exception as e:
            detection_logger.error(f"Detection loop error: {str(e)}")
            connection_state.value = 1
            time.sleep(0.1)

def clean_up_process(process: Any, stop_event: EventType):
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

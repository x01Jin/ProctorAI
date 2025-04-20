import time
import logging

DEADZONE_SIZE = 60
DEADZONE_DURATION = 180

_deadzones = []

def deduplicate(predictions, capture_class):
    logger = logging.getLogger('detection')
    now = time.time()
    global _deadzones
    before = len(_deadzones)
    _deadzones = [
        dz for dz in _deadzones if now - dz['timestamp'] < DEADZONE_DURATION
    ]
    after = len(_deadzones)
    if before > after:
        logger.info(f"Deadzone removed, total now: {after}")
    filtered = []
    for det in predictions:
        if det['class'] == capture_class:
            if _in_deadzone(det):
                continue
            filtered.append(det)
        else:
            filtered.append(det)
    filtered = _dedup_same_class(filtered, capture_class)
    return filtered

def _in_deadzone(det):
    for dz in _deadzones:
        if det['class'] == dz['class']:
            if (
                abs(det['x'] - dz['x']) <= DEADZONE_SIZE // 2 and
                abs(det['y'] - dz['y']) <= DEADZONE_SIZE // 2
            ):
                return True
    return False

def add_deadzone(det, timestamp):
    logger = logging.getLogger('detection')
    _deadzones.append({
        'x': det['x'],
        'y': det['y'],
        'class': det['class'],
        'timestamp': timestamp
    })
    logger.info(f"Deadzone created at x={det['x']}, y={det['y']}, class={det['class']}")

def _dedup_same_class(predictions, capture_class):
    result = []
    seen = []
    for det in sorted(predictions, key=lambda d: -d.get('confidence', 0)):
        if det['class'] == capture_class:
            duplicate = False
            for s in seen:
                if (
                    abs(det['x'] - s['x']) <= DEADZONE_SIZE // 2 and
                    abs(det['y'] - s['y']) <= DEADZONE_SIZE // 2
                ):
                    duplicate = True
                    break
            if not duplicate:
                seen.append(det)
                result.append(det)
        else:
            result.append(det)
    return result

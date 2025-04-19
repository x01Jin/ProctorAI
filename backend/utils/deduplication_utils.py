import time
import logging

DEADZONE_SIZE = 60
DEADZONE_DURATION = 180

class DetectionDeduplicator:
    _deadzones = []

    @staticmethod
    def deduplicate(predictions, capture_class):
        logger = logging.getLogger('detection')
        now = time.time()
        before = len(DetectionDeduplicator._deadzones)
        DetectionDeduplicator._deadzones = [
            dz for dz in DetectionDeduplicator._deadzones if now - dz['timestamp'] < DEADZONE_DURATION
        ]
        after = len(DetectionDeduplicator._deadzones)
        if before > after:
            logger.info(f"Deadzone removed, total now: {after}")
        filtered = []
        for det in predictions:
            if det['class'] == capture_class:
                if DetectionDeduplicator._in_deadzone(det):
                    continue
                filtered.append(det)
            else:
                filtered.append(det)
        filtered = DetectionDeduplicator._dedup_same_class(filtered, capture_class)
        return filtered

    @staticmethod
    def _in_deadzone(det):
        for dz in DetectionDeduplicator._deadzones:
            if det['class'] == dz['class']:
                if (
                    abs(det['x'] - dz['x']) <= DEADZONE_SIZE // 2 and
                    abs(det['y'] - dz['y']) <= DEADZONE_SIZE // 2
                ):
                    return True
        return False

    @staticmethod
    def _add_deadzone(det, timestamp):
        logger = logging.getLogger('detection')
        DetectionDeduplicator._deadzones.append({
            'x': det['x'],
            'y': det['y'],
            'class': det['class'],
            'timestamp': timestamp
        })
        logger.info(f"Deadzone created at x={det['x']}, y={det['y']}, class={det['class']}")

    @staticmethod
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

import cv2
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FilterProcessor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.current_filter = None

    def apply_warm_filter(self, frame: np.ndarray, intensity: float = 0.4) -> np.ndarray:
        """Apply warm color filter to frame"""
        warm_layer = np.full_like(frame, [20, 40, 115])
        return cv2.addWeighted(frame, 1.0, warm_layer, intensity, 0)

    def apply_cool_filter(self, frame: np.ndarray, intensity: float = 0.4) -> np.ndarray:
        """Apply cool color filter to frame"""
        cool_layer = np.full_like(frame, [128, 60, 20])
        return cv2.addWeighted(frame, 1.0, cool_layer, intensity, 0)

    def apply_cinematic_filter(self, frame: np.ndarray, 
                             contrast: float = 1.2, 
                             saturation: float = 0.85) -> np.ndarray:
        """Apply cinematic color grading to frame"""
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=10)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * saturation
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def process_frame(self, frame: np.ndarray, filter_name: Optional[str] = None) -> np.ndarray:
        """Process a frame with the specified filter"""
        if filter_name is None:
            return frame

        try:
            settings = self.config.get('FILTERS', {}).get(filter_name, {})

            if filter_name == 'warm':
                intensity = settings.get('intensity', 0.4)
                return self.apply_warm_filter(frame, intensity)
            elif filter_name == 'cool':
                intensity = settings.get('intensity', 0.4)
                return self.apply_cool_filter(frame, intensity)
            elif filter_name == 'cinematic':
                contrast = settings.get('contrast', 1.2)
                saturation = settings.get('saturation', 0.85)
                return self.apply_cinematic_filter(frame, contrast, saturation)

        except Exception as e:
            logger.error(f"Error applying filter {filter_name}: {str(e)}")
            return frame

        return frame

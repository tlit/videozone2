import cv2
import numpy as np

class MotionEngine:
    def __init__(self, zoom_factor: float = 1.05):
        self.zoom_factor = zoom_factor

    def apply_zoom(self, frame: np.ndarray) -> np.ndarray:
        """
        Applies a center zoom to the frame to simulate forward motion.
        """
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        
        # Create rotation matrix for zoom (scale only, 0 rotation)
        M = cv2.getRotationMatrix2D(center, 0, self.zoom_factor)
        
        # Warp affine
        zoomed = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        return zoomed

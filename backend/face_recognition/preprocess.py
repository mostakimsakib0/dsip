import cv2
import numpy as np
from backend.config import (
    PREPROCESS_ENABLED,
    PREPROCESS_RESIZE,
    PREPROCESS_GAMMA,
    PREPROCESS_CONTRAST,
    PREPROCESS_BRIGHTNESS,
    PREPROCESS_GAUSSIAN_KERNEL,
)


class Preprocessor:
    def resize(self, frame, size=None):
        size = size or PREPROCESS_RESIZE
        return cv2.resize(frame, size)

    def to_grayscale(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def normalize_brightness(self, frame, target=128):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean = np.mean(gray)
        delta = target - mean
        return np.clip(frame.astype(np.float32) + delta, 0, 255).astype(np.uint8)

    def enhance_contrast(self, frame, alpha=None):
        alpha = alpha or PREPROCESS_CONTRAST
        return cv2.convertScaleAbs(frame, alpha=alpha, beta=PREPROCESS_BRIGHTNESS)

    def histogram_equalization(self, frame):
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    def gamma_correction(self, frame, gamma=None):
        gamma = gamma or PREPROCESS_GAMMA
        table = (np.linspace(0, 1, 256) ** gamma) * 255
        table = table.astype(np.uint8)
        return cv2.LUT(frame, table)

    def noise_reduction(self, frame, kernel=None):
        kernel = kernel or PREPROCESS_GAUSSIAN_KERNEL
        return cv2.GaussianBlur(frame, (kernel, kernel), 0)

    def process(self, frame):
        if frame is None:
            return frame
        processed = self.resize(frame)
        processed = self.noise_reduction(processed)
        processed = self.enhance_contrast(processed)
        processed = self.gamma_correction(processed)
        processed = self.histogram_equalization(processed)
        return processed

    def should_apply(self):
        return PREPROCESS_ENABLED

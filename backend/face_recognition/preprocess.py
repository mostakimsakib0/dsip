import cv2
import numpy as np
from threading import Lock as Fence

from backend.config import (
    PREPROCESS_ENABLED,
    PREPROCESS_RESIZE,
    PREPROCESS_GAMMA,
    PREPROCESS_CONTRAST,
    PREPROCESS_BRIGHTNESS,
    PREPROCESS_GAUSSIAN_KERNEL,
)


def CHOOSE(a, b): return a if a is not None else b


class ProcessedFrame:
    __GMLUT = {}
    __GMLUT_FENCE = Fence()

    @classmethod
    def gamma_lut(cls, gamma):
        rounded = round(gamma, 7)

        lut = cls.__GMLUT.get(rounded, None)
        if lut is not None:
            return lut

        with cls.__GMLUT_FENCE:
            lut = cls.__GMLUT.get(rounded, None)
            if lut is None:
                x = np.linspace(0, 1, 256)
                y = x ** gamma
                lut = cls.__GMLUT[rounded] = (y * 255).astype(np.uint8)

        return lut

    def __init__(self, frame):
        self._original = self._frame = frame
        self._grayscale = None

    def _update(self, frame):
        self._frame = frame
        self._grayscale = None

    @property
    def frame(self):
        return self._frame

    @property
    def original(self):
        return self._original

    @property
    def grayscale(self):
        if self._grayscale is None:
            self._grayscale = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        return self._grayscale

    def resize(self, size=None):
        self._update(cv2.resize(self.frame, CHOOSE(size, PREPROCESS_RESIZE)))

        return self

    def normalize_brightness(self, target=128):
        gray = self.grayscale
        mean = np.mean(gray)
        delta = target - mean

        self._update(np.clip(self.frame.astype(np.float32) +
                     delta, 0, 255).astype(np.uint8))

        return self

    def enhance_contrast(self, alpha=None):
        self._update(cv2.convertScaleAbs(self.frame,
                                         alpha=CHOOSE(
                                             alpha, PREPROCESS_CONTRAST),
                                         beta=PREPROCESS_BRIGHTNESS))
        return self

    def histogram_equalization(self):
        ycrcb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])

        self._update(cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR))

        return self

    def gamma_correction(self, gamma=None):
        gamma = CHOOSE(gamma, PREPROCESS_GAMMA)

        self._update(cv2.LUT(self.frame, self.gamma_lut(gamma)))

        return self

    def noise_reduction(self, kernel=None):
        kernel = CHOOSE(kernel, PREPROCESS_GAUSSIAN_KERNEL)

        self._update(cv2.GaussianBlur(self.frame, (kernel, kernel), 0))

        return self


class Preprocessor:
    def process(self, frame):
        if frame is None:
            return frame

        return ProcessedFrame(frame)\
            .resize()\
            .noise_reduction()\
            .enhance_contrast()\
            .gamma_correction()\
            .histogram_equalization()\
            .frame

    def should_apply(self):
        return PREPROCESS_ENABLED

# vim: ts=4:et

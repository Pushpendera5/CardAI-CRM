from __future__ import annotations

from pathlib import Path


class ImagePreprocessor:
    def preprocess(self, image_path: Path) -> Path:
        try:
            import cv2
        except Exception:
            return image_path
        image = cv2.imread(str(image_path))
        if image is None:
            # Fall back to original file so OCR can still attempt extraction.
            return image_path
        image = self._resize(image)
        image = self._auto_crop_and_transform(image)
        image = self._denoise(image)
        image = self._enhance_brightness(image)
        image = self._sharpen(image)
        image = self._deskew(image)
        output_path = image_path.with_name(f"{image_path.stem}_processed{image_path.suffix}")
        cv2.imwrite(str(output_path), image)
        return output_path

    def _resize(self, image: np.ndarray, max_width: int = 1600) -> np.ndarray:
        import cv2
        height, width = image.shape[:2]
        if width <= max_width:
            return image
        ratio = max_width / width
        return cv2.resize(image, (max_width, int(height * ratio)), interpolation=cv2.INTER_AREA)

    def _auto_crop_and_transform(self, image: np.ndarray) -> np.ndarray:
        import cv2
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4 and cv2.contourArea(approx) > image.shape[0] * image.shape[1] * 0.2:
                return self._four_point_transform(image, approx.reshape(4, 2))
        return image

    def _four_point_transform(self, image: np.ndarray, points: np.ndarray) -> np.ndarray:
        import cv2
        import numpy as np
        rect = self._order_points(points)
        top_left, top_right, bottom_right, bottom_left = rect
        width_a = np.linalg.norm(bottom_right - bottom_left)
        width_b = np.linalg.norm(top_right - top_left)
        height_a = np.linalg.norm(top_right - bottom_right)
        height_b = np.linalg.norm(top_left - bottom_left)
        max_width = int(max(width_a, width_b))
        max_height = int(max(height_a, height_b))
        if max_width <= 0 or max_height <= 0:
            return image
        destination = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype="float32",
        )
        matrix = cv2.getPerspectiveTransform(rect, destination)
        return cv2.warpPerspective(image, matrix, (max_width, max_height))

    def _order_points(self, points: np.ndarray) -> np.ndarray:
        import numpy as np
        rect = np.zeros((4, 2), dtype="float32")
        sums = points.sum(axis=1)
        diffs = np.diff(points, axis=1)
        rect[0] = points[np.argmin(sums)]
        rect[2] = points[np.argmax(sums)]
        rect[1] = points[np.argmin(diffs)]
        rect[3] = points[np.argmax(diffs)]
        return rect

    def _denoise(self, image: np.ndarray) -> np.ndarray:
        import cv2
        return cv2.fastNlMeansDenoisingColored(image, None, 8, 8, 7, 21)

    def _enhance_brightness(self, image: np.ndarray) -> np.ndarray:
        import cv2
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(l_channel)
        return cv2.cvtColor(cv2.merge((enhanced, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

    def _sharpen(self, image: np.ndarray) -> np.ndarray:
        import cv2
        import numpy as np
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        import cv2
        import numpy as np
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 120, minLineLength=100, maxLineGap=10)
        if lines is None:
            return image
        angles = []
        for line in lines[:20]:
            x1, y1, x2, y2 = line[0]
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        angle = float(np.median([a for a in angles if -30 < a < 30] or [0]))
        if abs(angle) < 0.5:
            return image
        height, width = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        return cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

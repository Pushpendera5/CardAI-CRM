import logging
import time
from pathlib import Path

from app.schemas.card import OCRBlock

logger = logging.getLogger(__name__)

# Tesseract binary path on Windows (winget installs here)
_TESS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class EasyOCREngine:
    """
    OCR engine with multiple backend support (in priority order):
    1. pytesseract — lightweight pure-Python wrapper around Tesseract binary
    2. easyocr     — heavy ML-based reader (if installed)
    3. Silent fallback — returns empty text so scan pipeline still runs
    """

    # Class-level singleton for the heavy easyocr Reader (lazy-loaded once)
    _easyocr_reader = None

    # ── pytesseract ──────────────────────────────────────────────────────────

    def _run_pytesseract(self, image_path: Path) -> str | None:
        try:
            import pytesseract
            from PIL import Image

            pytesseract.pytesseract.tesseract_cmd = _TESS_PATH
            img = Image.open(str(image_path))
            text = pytesseract.image_to_string(img, lang="eng")
            return text
        except ImportError:
            return None
        except Exception as exc:
            logger.warning("pytesseract failed: %s", exc)
            return None

    # ── easyocr fallback ─────────────────────────────────────────────────────

    def _run_easyocr(self, image_path: Path) -> list | None:
        try:
            import easyocr
            from app.config.settings import get_settings

            if EasyOCREngine._easyocr_reader is None:
                EasyOCREngine._easyocr_reader = easyocr.Reader(get_settings().ocr_language_list, gpu=False)
            return EasyOCREngine._easyocr_reader.readtext(str(image_path), detail=1, paragraph=False)
        except ImportError:
            return None
        except Exception as exc:
            logger.warning("easyocr failed: %s", exc)
            return None

    # ── Public API ───────────────────────────────────────────────────────────

    def extract(self, image_path: Path) -> tuple[str, list[OCRBlock], float, int]:
        start = time.perf_counter()

        # 1. Try pytesseract
        tess_text = self._run_pytesseract(image_path)
        if tess_text is not None:
            lines = [line.strip() for line in tess_text.splitlines() if line.strip()]
            blocks = [OCRBlock(text=line, confidence=85.0) for line in lines]
            raw_text = "\n".join(lines)
            confidence = 85.0 if blocks else 0.0
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.debug("pytesseract extracted %d lines in %dms", len(lines), duration_ms)
            return raw_text, blocks, confidence, duration_ms

        # 2. Try easyocr
        easy_results = self._run_easyocr(image_path)
        if easy_results is not None:
            blocks = [
                OCRBlock(text=str(text), confidence=round(float(conf) * 100, 2), bbox=bbox)
                for bbox, text, conf in easy_results
                if str(text).strip()
            ]
            raw_text = "\n".join(block.text for block in blocks)
            confidence = round(sum(b.confidence for b in blocks) / len(blocks), 2) if blocks else 0.0
            duration_ms = int((time.perf_counter() - start) * 1000)
            return raw_text, blocks, confidence, duration_ms

        # 3. Silent fallback — no OCR backend available
        logger.warning("No OCR backend available — scan will return empty text. Install Tesseract or easyocr.")
        duration_ms = int((time.perf_counter() - start) * 1000)
        return "", [], 0.0, duration_ms

    def batch_extract(self, image_paths: list[Path]) -> list[tuple[str, list[OCRBlock], float, int]]:
        return [self.extract(path) for path in image_paths]

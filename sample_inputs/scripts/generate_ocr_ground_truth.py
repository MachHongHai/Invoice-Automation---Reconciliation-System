from __future__ import annotations

from generation_core import generate_ocr_ground_truth


if __name__ == "__main__":
    print(f"Generated OCR ground truth rows: {len(generate_ocr_ground_truth())}")


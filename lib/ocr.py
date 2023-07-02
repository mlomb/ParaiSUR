import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import easyocr
import pytesseract

OCR_CACHE_PATH = Path("../data-ocr")

__global_easyocr_reader: easyocr.Reader | None = None


@dataclass
class OCRParams:
    engine: Literal["tesseract", "easyocr"]
    grayscale: bool
    threshold: int | None

    def id(self):
        id = self.engine
        if self.grayscale:
            id += "_grayscale"
        if self.threshold is not None:
            id += "_threshold" + str(self.threshold)
        return id


def ocr_sample(sample, params: OCRParams, only_cache=False) -> str:
    id = params.id()
    cache_path = OCR_CACHE_PATH / sample["filename"]
    cache_file = cache_path / f"{id}.txt"

    # try to load from cache
    if cache_file.exists():
        return cache_file.read_text()

    if only_cache:
        return ""

    # run OCR
    # combine texts from all images
    text = ""
    for image_path in sample["images"]:
        text += run_ocr(image_path, params) + "\n"

    # save to cache
    os.makedirs(cache_path, exist_ok=True)
    cache_file.write_text(text)

    return text


def run_ocr(image_path: str, params: OCRParams) -> str:
    image = cv2.imread(image_path)

    # preprocess image
    if params.grayscale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if params.threshold is not None:
        _, image = cv2.threshold(image, params.threshold, 255, cv2.THRESH_BINARY)

    # run OCR
    if params.engine == "tesseract":
        return pytesseract.image_to_string(image)
    elif params.engine == "easyocr":
        global __global_easyocr_reader
        if __global_easyocr_reader is None:
            print("Initializing EasyOCR reader...")
            __global_easyocr_reader = easyocr.Reader(["en"], gpu=True)

        return "\n".join(__global_easyocr_reader.readtext(image, detail=0, batch_size=50))  # type: ignore
    else:
        raise ValueError(f"Unknown OCR engine: {params.engine}")

from dataclasses import dataclass
from functools import cache
from typing import Literal

import cv2
import easyocr
import pytesseract
from deskew import determine_skew
from paddleocr import PaddleOCR
from skimage.color import rgb2gray
from skimage.transform import rotate

from lib.cache import get_cache, set_cache


def get_ocrs(sample) -> dict:
    """
    Obtiene los OCRs ya computados
    """
    return get_cache(sample["filename"] + "-ocr.json") or {}


@dataclass
class OCRParams:
    engine: Literal["paddleocr", "easyocr", "tesseract"]
    grayscale: bool = False
    threshold: int | None = None
    deskew: bool = False

    def id(self):
        id = self.engine
        if self.grayscale:
            id += "_grayscale"
        if self.deskew:
            id += "_deskew"
        if self.threshold is not None:
            id += "_threshold" + str(self.threshold)
        return id


def run_ocr_sample(sample, params: OCRParams):
    """
    Realiza OCR en un sample con los parámetros especificados y lo guarda en la caché.
    """
    id = params.id()
    cache_key = sample["filename"] + "-ocr.json"

    db = get_cache(cache_key)
    if db is not None:
        # check if it is already generated
        if id in db:
            return

    # must generate
    pages = []
    for image_path in sample["images"]:
        pages.append(run_ocr_image(image_path, params))

    # save to cache
    if db is None:
        db = {}
    db[id] = pages
    set_cache(cache_key, db)


def run_ocr_image(image_path: str, params: OCRParams) -> dict:
    image = cv2.imread(image_path)

    # preprocess image
    if params.grayscale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if params.deskew:
        angle = determine_skew(image)  # type: ignore
        image_deskew = rotate(image, angle, resize=True)  # type: ignore
        image = (image_deskew * 255).astype("uint8")  # volver a 0-255
    if params.threshold is not None:
        _, image = cv2.threshold(image, params.threshold, 255, cv2.THRESH_BINARY)

    boxes = []

    # run OCR
    if params.engine == "paddleocr":
        result = get_paddleocr_instance().ocr(image, cls=False)[0]
        boxes = [
            {
                "bounds": [list(map(int, lst)) for lst in item[0]],
                "text": item[1][0],
                "confidence": item[1][1],
            }
            for item in result
        ]
    elif params.engine == "easyocr":
        results = get_easyocr_reader().readtext(
            image, detail=1, batch_size=40, paragraph=False
        )
        boxes = [
            {"bounds": [list(map(int, lst)) for lst in item[0]], "text": item[1], "confidence": item[2]}  # type: ignore
            for item in results
        ]
    elif params.engine == "tesseract":
        d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        boxes = []
        n_boxes = len(d["level"])
        for i in range(n_boxes):
            if d["conf"][i] < 0:
                continue
            (x, y, w, h) = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])

            boxes.append(
                {
                    "bounds": [
                        [x, y],
                        [x + w, y],
                        [x + w, y + h],
                        [x, y + h],
                    ],
                    "text": d["text"][i],
                    "confidence": d["conf"][i] / 100,
                }
            )
    else:
        raise ValueError(f"Unknown OCR engine: {params.engine}")

    text = "\n".join([box["text"] for box in boxes])

    return {"boxes": boxes, "text": text}


@cache
def get_easyocr_reader():
    print("Initializing EasyOCR reader...")
    return easyocr.Reader(["en"], gpu=True)


@cache
def get_paddleocr_instance():
    print("Initializing PaddleOCR instance...")
    return PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False, show_log=False)

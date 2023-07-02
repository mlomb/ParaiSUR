from dataclasses import dataclass
from PIL import Image

import pytesseract
import easyocr

from lib.text import try_extract_from_text

reader = easyocr.Reader(["en"], gpu=True)


@dataclass
class ImagePreprocessParams:
    # TODO: set good values here
    threshold_value: int = 100


def preprocess_image(image, params: ImagePreprocessParams):
    # Grayscale
    image = image.convert("L")
    # Threshold
    image = image.point(lambda p: 255 if p > params.threshold_value else 0)
    # To mono
    image = image.convert("1")

    return image


def ocr_images(image_paths: list[str], params: ImagePreprocessParams):
    # combine texts from all images
    text = ""
    for image_path in image_paths:
        text += "\n".join(reader.readtext(image_path, detail=0, batch_size=50))  # type: ignore
        # text += pytesseract.image_to_string(
        #    preprocess_image(Image.open(image_path), params)
        # )
    return text

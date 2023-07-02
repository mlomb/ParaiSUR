import pytesseract

from lib.text import try_extract_from_text


def try_extract_from_ocr(sample):
    # combine texts from all images
    text = ""
    for image in sample["images"]:
        text += pytesseract.image_to_string(image)

    # now try to parse invoice and total
    return try_extract_from_text(text)

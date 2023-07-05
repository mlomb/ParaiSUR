from lib.details_ocr import extract_lines_ocr, filter_detail_lines, split_detail_line
from lib.details_text import extract_details_from_text
from lib.ocr import get_ocrs


def find_detail_lines(sample):
    detail_lines = []

    if sample["text"] != "":
        return extract_details_from_text(sample["text"])
    else:
        ocrs = get_ocrs(sample)
        if "paddleocr_deskew" in ocrs:
            all_lines = []
            for ocr_page in ocrs["paddleocr_deskew"]:
                all_lines = all_lines + extract_lines_ocr(ocr_page["boxes"])

            num_none = 0
            num_not_none = 0

            for line in filter_detail_lines(all_lines):
                if line is not None:
                    num_not_none += 1
                    detail_lines.append(split_detail_line(line))
                else:
                    num_none += 1

            if num_none / (num_none + num_not_none) > 0.3:
                # too noisy
                return []

    return detail_lines

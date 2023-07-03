import re


def extract_total(text: str):
    total = None
    total_regex = "Total: (-?)\\$(\\d{1,3}(?:,?\\d{3})*(?:\\.|,))(\\d{2})\\s+"
    total_match = re.search(total_regex, text)
    if total_match is not None:
        sign = total_match.group(1)
        integer = total_match.group(2).replace(",", "").replace(".", "")
        decimal = total_match.group(3).replace(",", "").replace(".", "")

        total = float(sign + integer + "." + decimal)

        if abs(total) < 100:
            return None

    return total

import re
from datetime import date

number = r"(?:\d|O|l|\|)"
regex = f"({number}{number}{number}{number})-({number}{number})-({number}{number})"


def parse_number(number: str):
    return int(number.replace("O", "0").replace("l", "1").replace("|", "1"))


def extract_dates(lines: list[dict | None]):
    dates = []

    for line in lines:
        if line is None:
            continue
        test = line["desc"]

        matches = re.findall(regex, test)
        for match in matches:
            try:
                dates.append(
                    date(
                        parse_number(match[0]),
                        parse_number(match[1]),
                        parse_number(match[2]),
                    )
                )
            except ValueError:
                pass

    return sorted(dates)

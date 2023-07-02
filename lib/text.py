import re


def build_invoice_regex():
    prefixes = [
        prefix + "(?:;|:)"  # match : or ;
        for prefix in [
            "Invoice num.",
            "Inv.",
            "Num",
            "Num.",
            "Invoice",
            "Invoice Locator",
        ]
    ]
    prefixes.append("(?:.*)#(?:.*?)")
    invoice = "[A-Z0-9]{6,}"

    return f"""(?i)\\s?({"|".join(prefixes)})\\s?({invoice})"""


def extract_invoice(text: str):
    invoice = None
    invoice_regex = build_invoice_regex()
    invoice_match = re.search(invoice_regex, text)
    if invoice_match is not None:
        invoice = invoice_match.group(2)
    else:
        # extraction failed, we can assume we have something like ": 12345678"
        # I'm assuming that there is a line that starts with ":"
        lines = text.split("\n")
        for line in lines:
            if len(line) > 0 and line[0] == ":":
                line = line[1:].strip()

                # now we have to check that we only have alpha chars
                # since we can have things like ": Jan 18, 2021\n"
                # and we want ": 514599571\n"
                if line.isalnum():
                    invoice = line
                    break  # pick first

    return invoice


def extract_total(text: str):
    total = None
    total_regex = "Total: -?\$((\d+),?)+\.?(\d*)"
    total_match = re.search(total_regex, text)
    if total_match is not None:
        total_str = (
            total_match.group(0)
            .replace(",", "")
            .replace("Total: $", "")
            .replace("Total: -$", "-")
        )
        total = float(total_str)

    return total


def try_extract_from_text(text: str):
    return {
        "invoice": extract_invoice(text),
        "total": extract_total(text),
    }

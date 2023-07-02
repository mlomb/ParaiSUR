from math import isnan
import re


def try_extract_from_text(text: str):
    invoice = None
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

    invoice_regex = "(Inv#:|Invoice num.:|Inv.:|Invoice #:|Num:|Locator #:|Invoice:|Invoice Locator:)\s([A-Z0-9]+)"
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

    return {
        "invoice": invoice,
        "total": total,
    }

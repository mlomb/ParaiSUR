import re

import editdistance

from lib.cache import get_cache, set_cache
from lib.data import load_all_invoices


def find_invoice_cached(sample: dict) -> str | None:
    """
    Intenta encontrar el invoice de un sample, se cachea si se encuentra.
    """
    cache_key = sample["filename"] + "-invoice.txt"

    invoice = get_cache(cache_key)
    if invoice is not None:
        return invoice

    invoice = find_invoice(sample)
    if invoice is not None:
        set_cache(cache_key, invoice)

    return invoice


def find_invoice(sample: dict) -> str | None:
    # intentar extraer del nombre
    invoice = sample["filename"][:-4]  # .pdf
    invoice = validate_invoice(invoice)

    # intentar extraer del texto real del PDF
    if invoice is None and len(sample["text"]) > 0:
        invoice = extract_invoice_from_text(sample["text"])
        invoice = validate_invoice(invoice)

    # intentar extraer del texto obtenido por OCR
    # TODO!

    return invoice


def validate_invoice(candidate: str | None) -> str | None:
    """
    Verifica si un invoice es valido utilizando la lista de invoices provista en el dataset.
    Si no es válido, intenta encontrar el invoice más cercano.
    Si aún así no lo encuentra, devuelve None.
    """
    all_invoices = load_all_invoices()

    if candidate is None:
        return None

    if candidate in all_invoices:
        # match perfecto
        return candidate

    best_dist = 999
    best_match = None

    for invoice in all_invoices:
        dist = editdistance.eval(invoice, candidate)
        if dist < best_dist:
            best_dist = dist
            best_match = invoice

    if best_dist <= 2:
        return best_match

    # no hubo suerte
    return None


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


INVOICE_REGEX = build_invoice_regex()


def extract_invoice_from_text(text: str):
    invoice = None
    invoice_regex = INVOICE_REGEX
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

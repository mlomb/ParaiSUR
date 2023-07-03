import re

import editdistance

from lib.cache import get_cache, set_cache
from lib.data import load_all_invoices
from lib.ocr import get_ocrs


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
    candidate = sample["filename"][:-4]  # .pdf
    invoice = validate_invoice(candidate)
    if invoice is not None:
        return invoice

    # intentar extraer del texto real del PDF
    if len(sample["text"]) > 0:
        candidates = extract_invoice_candidates_from_text(sample["text"])
        for candidate in candidates:
            invoice = validate_invoice(candidate)
            if invoice is not None:
                return invoice

    # intentar extraer del texto obtenido por OCR
    ocrs = get_ocrs(sample)
    for _, pages in ocrs.items():
        # invoice is always in page 0
        candidates = extract_invoice_candidates_from_text(pages[0]["text"])
        for candidate in candidates:
            invoice = validate_invoice(candidate)
            if invoice is not None:
                return invoice

    return None


def validate_invoice(candidate: str | None) -> str | None:
    """
    Verifica si un invoice es valido utilizando la lista de invoices provista en el dataset.
    Si no es válido, intenta encontrar el invoice más cercano.
    Si aún así no lo encuentra, devuelve None.
    """
    if candidate is None:
        return None

    all_invoices = load_all_invoices()
    candidate = candidate.strip().upper()

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


def extract_invoice_candidates_from_text(text: str) -> list[str]:
    candidates = []

    lines = text.split("\n")
    for line in lines:
        matches = re.findall("([A-Z0-9@]{6,})", line.strip(), re.IGNORECASE)
        for match in matches:
            candidates.append(match)

    return [c.upper() for c in candidates]

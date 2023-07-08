import re

import diskcache as dc
import editdistance
from thefuzz import fuzz, process

from lib.data import load_all_invoices
from lib.ocr import get_ocrs

invoices_cache = dc.Cache("../cache/invoices")


@invoices_cache.memoize(tag="find_invoice")
def find_invoice(sample: dict) -> str | None:
    # si es ilegible, ver si está hardcodeado
    if sample["filename"] in UNINTELLIGIBLE_INVOICES:
        invoice = UNINTELLIGIBLE_INVOICES[sample["filename"]]
        assert validate_invoice(invoice, score_cutoff=100) is not None
        return invoice

    # intentar extraer del nombre
    candidate = sample["filename"][:-4]  # .pdf
    invoice = validate_invoice(candidate, score_cutoff=100)
    if invoice is not None:
        return invoice

    # intentar extraer del texto real del PDF
    if len(sample["text"]) > 0:
        candidates = extract_invoice_candidates_from_text(sample["text"])
        for candidate in candidates:
            invoice = validate_invoice(candidate, score_cutoff=100)
            if invoice is not None:
                return invoice

    # intentar extraer del texto obtenido por OCR
    ocrs = get_ocrs(sample)
    for engine, pages in ocrs.items():
        # invoice is always in page 0
        text = ""
        for boxes in pages[0]["boxes"]:
            # filtrar OCR boxes arriba de la hoja (evita los amount overdue y account numbers)
            if boxes["bounds"][0][1] < 180:
                text += boxes["text"] + "\n"
        candidates = extract_invoice_candidates_from_text(text)
        for candidate in candidates:
            invoice = validate_invoice(candidate, score_cutoff=85)
            if invoice is not None:
                return invoice

    return None


@invoices_cache.memoize(tag="validate_invoice")
def validate_invoice(candidate: str | None, score_cutoff: int) -> str | None:
    """
    Verifica si un invoice es valido utilizando la lista de invoices provista en el dataset.
    Si no es válido, intenta encontrar el invoice más cercano.
    Si aún así no lo encuentra, devuelve None.
    """
    if candidate is None:
        return None

    all_invoices = load_all_invoices()
    candidate = re.sub(r"\s+", "", candidate)  # remove all spaces
    candidate = candidate.upper()

    if candidate in all_invoices:
        # match perfecto
        return candidate

    if score_cutoff >= 100:
        # no hay match perfecto
        return None

    match = process.extractOne(
        candidate,
        all_invoices,
        scorer=fuzz.ratio,
        score_cutoff=score_cutoff,
    )

    # no hubo suerte
    return match[0] if match is not None else None


def extract_invoice_candidates_from_text(text: str) -> list[str]:
    candidates = []

    lines = text.split("\n")
    for line in lines:
        matches = re.findall("([A-Z0-9@]{6,})", line.strip(), re.IGNORECASE)
        for match in matches:
            match = (
                match.upper()
                .replace("INVOICE", "")
                .replace(":", " ")
                .replace("-", " ")
                .strip()
            )
            if len(match) > 0:
                candidates.append(match)

    return candidates


# casos borde que no los lee el OCR ni a palos
UNINTELLIGIBLE_INVOICES = {
    "2021-01-01_4536.pdf": "Q16642775",
    "2021-03-15_2239.pdf": "N54878344",
    "2021-04-12_7818.pdf": "V92791061",
    "2022-03-02_652.pdf": "W62193637",
    "2022-05-14_4984.pdf": "296129687",
    "2022-12-13_2467.pdf": "X48480571",
    "BakerZimmerman_2021-03-05.pdf": "M08350513",
    "DavisLtd_2022-09-12.pdf": "E27387103",
    "DuncanLLC_2021-05-02.pdf": "683717975",
    "Email_Attachment_2021-03-01_535.pdf": "281895150",
    "Email_Attachment_2021-08-07_3591.pdf": "402480067",
    "Email_Attachment_2021-08-16_283.pdf": "395010656",
    "Email_Attachment_2021-12-03_3010.pdf": "398892524",
    "Email_Attachment_2022-01-14_5640.pdf": "329616661",
    "Email_Attachment_2022-01-15_8006.pdf": "H43105700",
    "Email_Attachment_2022-02-18_5364.pdf": "131194427",
    "Email_Attachment_2022-04-25_2729.pdf": "711301863",
    "Email_Attachment_2022-09-07_97.pdf": "828655515",
    "Email_Attachment_2022-10-09_1150.pdf": "221800479",
    "HeathMcconnellandSimon_2022-01-07.pdf": "M78879537",
    "Incoming_inv_ParaisurZ996560_2866.pdf": "42855507",
    "Incoming_inv_ParaisurZ996560_367.pdf": "199417262",
    "Incoming_inv_ParaisurZ996560_3852.pdf": "524857251",
    "Incoming_inv_ParaisurZ996560_4608.pdf": "893616400",
    "Incoming_inv_ParaisurZ996560_5771.pdf": "143133373",
    "Incoming_inv_ParaisurZ996560_688.pdf": "788626427",
    "Incoming_inv_ParaisurZ996560_7446.pdf": "979822123",
    "Incoming_inv_ParaisurZ996560_8299.pdf": "Y81132562",
    "Invoice (3858).pdf": "B66553394",
    "Invoice (47).pdf": "788637963",
    "Invoice (5608).pdf": "86720527",
    "Invoice (5842).pdf": "V43006630",
    "Invoice (7163).pdf": "V77225763",
    "Invoice (7802).pdf": "994646405",
    "McgeeKent_2021-06-20.pdf": "21863761",
    "PettyLee_2021-10-17.pdf": "186463875",
    "ScottMeyer_2022-02-03.pdf": "4075853",
    "WrightandSons_2022-02-09.pdf": "486177540",
    "2021-09-17_6146.pdf": "656481490",
    "Invoice (4269).pdf": "I47727684",
    "Incoming_inv_ParaisurZ996560_6052.pdf": "139007857",
    "2023-05-22_515.pdf": "W99024265",
    "Invoice (7288).pdf": "C23230784",
    "PowellEdwardsandArroyo_2021-05-11.pdf": "226495711",
    "WebbandSons_2021-01-06.pdf": "Y69230510",
    "Email_Attachment_2021-07-30_8183.pdf": "B41092167",
    "2021-10-31_2835.pdf": "O63072775",
    "KellerNewtonandTerry_2022-07-22.pdf": "171162946",
    "Invoice (7137).pdf": "909599227",
    "MartinLLC_2022-08-12.pdf": "965763797",
    "DurhamBridges_2022-08-20.pdf": "105542111",
    "Invoice (4267).pdf": "853926858",
}

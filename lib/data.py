import json
import random
from functools import cache
from typing import Literal


@cache
def load_extracted_samples(filter: Literal["only_text", "only_ocr"] | None = None):
    with open("../data-extracted/samples.json") as f:
        samples = json.load(f)

    if filter == "only_text":
        samples = [s for s in samples if len(s["text"]) > 0]
    if filter == "only_ocr":
        samples = [s for s in samples if len(s["text"]) == 0]

    # shuffle
    random.Random(42).shuffle(samples)

    return samples


def load_extracted_sample(filename):
    samples = load_extracted_samples()
    for sample in samples:
        if sample["filename"] == filename:
            return sample
    return None


@cache
def load_all_invoices():
    with open("../data/all-invoices.csv") as f:
        invoices = f.read().splitlines()

    return [i.upper() for i in invoices]


@cache
def load_first_names():
    with open("../data/first_names.txt") as f:
        names = f.read().splitlines()

    return [n.lower() for n in names]


@cache
def load_last_names():
    with open("../data/last_names.txt") as f:
        surnames = f.read().splitlines()

    return [s.lower() for s in surnames]

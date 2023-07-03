import json
from functools import cache


@cache
def load_extracted_samples():
    with open("../data-extracted/samples.json") as f:
        samples = json.load(f)

    return samples


@cache
def load_all_invoices():
    with open("../data/all-invoices.csv") as f:
        invoices = f.read().splitlines()

    return invoices

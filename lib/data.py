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

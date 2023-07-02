import json


def load_extracted_samples():
    with open("../data-extracted/samples.json") as f:
        samples = json.load(f)

    return samples


def load_all_invoices():
    with open("../all-invoices.csv") as f:
        invoices = f.read().splitlines()
    return invoices

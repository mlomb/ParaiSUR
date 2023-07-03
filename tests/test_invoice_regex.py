import sys

sys.path.append("..")

from lib.invoice import build_invoice_regex, extract_invoice_from_text

bold = lambda text: f"\033[1m{text}\033[0m"
red = lambda text: f"\033[91m{text}\033[0m"
green = lambda text: f"\033[92m{text}\033[0m"
yellow = lambda text: f"\033[93m{text}\033[0m"

print(bold(build_invoice_regex()))
print()

with open("should_match.txt") as f:
    should_match = f.read().splitlines()

with open("should_reject.txt") as f:
    should_reject = f.read().splitlines()

print(bold("Should match:"))
for line in should_match:
    if line == "":
        continue
    invoice = extract_invoice_from_text(line)
    print(yellow(line), end=" ")
    if invoice == "A1A1A1A1A":
        print(green(invoice))
    else:
        print(red(invoice))

print()
print(bold("Should reject:"))
for line in should_reject:
    if line == "":
        continue
    invoice = extract_invoice_from_text(line)
    print(yellow(line), end=" ")
    if invoice is None:
        print(green(invoice))
    else:
        print(red(invoice))

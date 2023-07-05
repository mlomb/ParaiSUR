def extract_details_from_text(text: str) -> list[dict]:
    DETAILS_LABELS = [
        "details on due fees",
        "items",
        "hours",
        "price/hour",
        "total",
        "billable (h)",
        "#h",
        "$/h",
        "client chargable expenses",
        "hrs.wrk",
        "hourly rate",
        "descriptor",
        "time (h)",
        "$/hour",
        "billed h",
        "service description",
        "details on record",
        "rate",
        "hrs.wk",
        "details",
        "prjct hours",
        "std fee",
        "billable details",
        "billed details",
        "outstanding charges",
        "description",
        "detail fees",
        "p/h",
        "charges",
        "#hours",
        "invoice details",
        "services rendered",
        "work performed - details",
        "list of outstanding charges",
        "list of items",
        "fees charged",
        "work performed - details",
        "list of services provided",
        "services provided",
    ]

    items = text.splitlines()

    lines = []
    line = []
    inside_details = False

    for item in items:
        lower = item.lower()

        if lower in DETAILS_LABELS:
            inside_details = True
            continue

        if not inside_details:
            continue

        if "page" in lower or "total" in lower or len(item) == 0:
            continue

        # terminar el item anterior si aparece uno que empieza con $ o tiene letras
        if item[0] != "$" and any(c.isalpha() for c in item):
            if line != []:
                lines.append(line)
            line = []

            # reiniciar si el item no empieza con $
            # if item[0] != "$":
            #    # ignorar linea entera si empieza con un detector
            #    if line != [] and line[0] not in DETAILS_LABELS:
            #        lines.append(line)
        #
        #    line = []

        line.append(item)

    def parse_number(x: str):
        return float(x.strip().replace("$", "").replace(",", ""))

    detail_lines = []

    for line in lines:
        # ACTIVAR ESTO PARA DETECTAR DETAILS_LABELS NUEVOS
        # esta desactivado por defecto porque hay filas vacias que tienen "0"
        # assert len(line) in [4, 7], line
        if len(line) < 4:
            continue

        # line looks like:
        # ['Alexandra Torres - Technical Supervisor', '2 ', '$193.24', '$386.48']

        item_hours = parse_number(line[1])
        item_price = parse_number(line[2])
        item_total = parse_number(line[3])

        # check last column
        expected_total = item_hours * item_price
        assert item_total - expected_total < 0.01, [
            line,
            item_hours,
            item_price,
            item_total,
            expected_total,
        ]

        detail_lines.append({"desc": line[0], "total": item_total})

    return detail_lines

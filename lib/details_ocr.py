import re


def extract_lines_ocr(boxes):
    """
    Extrae las líneas de detalle a partir de los ítems de OCR.

    Basado en https://stackoverflow.com/a/48629229

    """
    # Formato de bounds: [[startX,startY], [endX,startY], [endX,endY], [startX, endY]]

    # calcular altura mediana
    heights = list()
    for box in boxes:
        heights.append(box["bounds"][2][1] - box["bounds"][0][1])  # endY - startY
    heights = sorted(heights)
    median_height = heights[len(heights) // 2] / 2

    # extraer líneas
    def grouper(iterable, interval=2):
        prev = None
        group = []
        for item in iterable:
            if (
                not prev or abs(item["bounds"][0][1] - prev["bounds"][0][1]) <= interval
            ):  # startY - startY
                group.append(item)
            else:
                yield group
                group = [item]
            prev = item
        if group:
            yield group

    bboxes_list = sorted(boxes, key=lambda box: box["bounds"][0][1])  # startY
    combined_bboxes = list(grouper(bboxes_list, median_height))

    return combined_bboxes


def filter_detail_lines(lines):
    """
    Filtra las líneas de detalle para eliminar aquellas que no son de detalle.
    """
    # calculo todos largos de líneas
    widths = list()
    for boxes in lines:
        x_min = min(boxes, key=lambda k: k["bounds"][0][0])["bounds"][0][0]  # startX
        x_max = max(boxes, key=lambda k: k["bounds"][2][0])["bounds"][2][0]  # endX
        widths.append(x_max - x_min)

    widths_sorted = sorted(widths)
    median_width = widths_sorted[len(widths_sorted) // 2]

    # filtro líneas por un poco menos que la mediana
    # la gracia es que siempre hay mas lineas de detalle que lo demás, así que quedan las líneas de detalle en la mediana
    filtered_lines = list()
    for i, line in enumerate(lines):
        if widths[i] >= median_width * 0.9:
            filtered_lines.append(line)

    return filtered_lines


def split_detail_line(line):
    """
    Separa la información de las boxes de una línea de detalle.
    """
    # ordenamos la línea de izquierda a derecha
    line = sorted(line, key=lambda box: box["bounds"][0][0])  # startX

    # leemos de atrás hacia adelante
    # esperamos que el último box de la línea sea el total

    # cambiamos la S por $ que suele confundirse
    # TODO: si el numero empieza con 5, o -5, cambiar por un $, que tambien se confunde
    total_str = line[-1]["text"].strip()

    money_regex = r"(-?)(?:\$|S)(\d{1,3}(?:(?:\.|,)?\d{3})*(?:\.|,))(\d{1,2})"
    money_match = re.search(money_regex, total_str, re.IGNORECASE)

    if money_match is None:
        # print(total_str)
        return None

    sign = money_match.group(1)
    integer = money_match.group(2).replace(",", "").replace(".", "")
    decimal = money_match.group(3).replace(",", "").replace(".", "")

    total = float(sign + integer + "." + decimal)

    # TODO: si no se encuentra o esta cortado, reconstruir de las otras dos columnas

    return {
        "desc": " ".join([box["text"] for box in line[:-1]]),
        "total": total,
        "total_str": total_str,  # para debug
    }

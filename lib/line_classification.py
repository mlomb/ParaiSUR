from lib.data import load_first_names, load_last_names


def is_professional(desc: str):
    professional = False

    # lower
    desc = desc.lower()

    # replace all non-alphanumeric characters with spaces
    desc = "".join([c if c.isalnum() else " " for c in desc])

    words = desc.split()

    # matchear "Nombre Apellido"
    first_names = load_first_names()
    last_names = load_last_names()
    for i in range(len(words) - 1):
        if words[i] in first_names and words[i + 1] in last_names:
            professional = True

    PROFESSIONAL_KEYWORDS = [
        "administrative",
        "analyst",
        "associate",
        "cnslt",
        "compensation",
        "consultant",
        "consultant",
        "consutlant",
        "contractor",
        "coordinator",
        "designer",
        "director",
        "drafter",
        "electrical engi",
        "engi",
        "engineer",
        "engineering",
        "estimator",
        "expert",
        "managem",
        "management",
        "manager",
        "pm",
        "scientist",
        "senior",
        "specialist",
        "supervisor",
        "tec",
        "technical",
        "technician",
    ]

    for word in words:
        if word.lower() in PROFESSIONAL_KEYWORDS:
            professional = True

    NEGATIVE_KEYWORDS = ["travel", "trvl", "weekend", "credit", "equipment"]

    for word in words:
        if word.lower() in NEGATIVE_KEYWORDS:
            professional = False

    return professional

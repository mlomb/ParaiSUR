from lib.data import load_first_names, load_last_names


def is_professional(desc):
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
            return True

    PROFESSIONAL_KEYWORDS = [
        "drafter",
        "engineer",
        "associate",
        "manager",
        "managem",
        "consultant",
        "specialist",
        "administrative",
        "senior",
        "pm",
        "electrical engi",
        "engineering",
        "technician",
        "tec",
        "analyst",
        "consultant",
        "scientist",
        "supervisor",
    ]

    for word in words:
        if word.lower() in PROFESSIONAL_KEYWORDS:
            return True

    return False

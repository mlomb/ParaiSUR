from functools import cache

from thefuzz import fuzz, process

from lib.data import load_first_names, load_last_names


def is_professional(desc: str):
    professional = False

    # lower
    desc = desc.lower()

    # replace all non-alphanumeric characters with spaces
    desc = "".join([c if c.isalnum() else " " for c in desc])

    words = desc.split()

    # matchear "Nombre Apellido"
    # first_names = load_first_names()
    # last_names = load_last_names()
    for i in range(len(words) - 1):
        # if words[i] in first_names and words[i + 1] in last_names:
        #     professional = True

        if is_first_name(words[i]) and is_last_name(words[i + 1]):
            professional = True

    PROFESSIONAL_KEYWORDS = [
        "administrative",
        "analyst",
        "associate",
        "cnslt",
        "compensation",
        "consultant",
        "contractor",
        "coordinator",
        "designer",
        "director",
        "drafter",
        "electrical",
        "engi",
        "engineer",
        "engineering",
        "estimator",
        "expert",
        "extra hours",
        "management",
        "manager",
        "meeting",
        "scheduler",
        "scientist",
        "senior",
        "specialist",
        "supervisor",
        "support",
        "technical",
        "technician",
        "travel",
        "trvl",
        "weekend",
        "workshop",
    ]

    for word in words:
        if process.extractOne(
            word,
            PROFESSIONAL_KEYWORDS,
            scorer=fuzz.ratio,
            score_cutoff=60,
        ):
            professional = True

    NEGATIVE_KEYWORDS = [
        "charges",
        "contingent",
        "credit",
        "equipment",
        "expenses",
        "part",
        "travel expense",
    ]

    for word in words:
        if process.extractOne(
            word,
            NEGATIVE_KEYWORDS,
            scorer=fuzz.ratio,
            score_cutoff=60,
        ):
            professional = False

    return professional


@cache
def is_first_name(firstname: str):
    first_names = load_first_names()
    return process.extractOne(
        firstname,
        first_names,
        scorer=fuzz.partial_ratio,
        score_cutoff=85,
    )


@cache
def is_last_name(lastname: str):
    last_names = load_last_names()
    return process.extractOne(
        lastname,
        last_names,
        scorer=fuzz.partial_ratio,
        score_cutoff=85,
    )

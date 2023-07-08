from functools import cache
import diskcache as dc


from thefuzz import fuzz, process

from lib.data import load_first_names, load_last_names


def is_professional(desc: str, debug=False):
    professional = False

    # lower
    desc = desc.lower()

    # replace all non-alphanumeric characters with spaces
    chars = [c if c.isalnum() else " " for c in desc]
    desc = " ".join(
        # remove empty words
        [word for word in "".join(chars).split() if len(word) > 0]
    )

    if len(desc) < 3:
        return False

    words = desc.split()
    phrases2 = [words[i] + " " + words[i + 1] for i in range(len(words) - 1)]
    phrases3 = [
        words[i] + " " + words[i + 1] + " " + words[i + 2]
        for i in range(len(words) - 2)
    ]
    phrases = phrases2 + phrases3

    # matchear "Nombre Apellido"
    for i in range(len(words) - 1):
        name = is_first_name(words[i], score_cutoff=85) and words[i] != "project"
        last = is_last_name(words[i + 1], score_cutoff=75)
        if name and last:
            if debug:
                print("nombre apellido", words[i], words[i + 1])
            professional = True

    PROFESSIONAL_KEYWORDS = [
        "administrative",
        "analyst",
        "associate",
        "cnslt",
        "civil",
        "compensation",
        "construction",
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
        "management",
        "manager",
        "monitoring",
        "scheduler",
        "scientist",
        "senior",
        "specialist",
        "supervisor",
        "support",
        "technical",
        "technician",
        "trvl",
        "weekend",
        "gis",
        "I",
        "II",
        "III",
        "IV",
        "time",
        "entered",
        "lead",
        "managing",
        "subcontract",
        "design",
        "sr",
        "tec",  # technician
        "spe",  # specialist
        "nda",  # non-destructive analysis
        "sme",  # subject matter expert
        "wfh",  # work from home
    ]

    PROFESSIONAL_PHRASES = [
        "extra hours",
        "project work",
        "project manager",
        "special on site",
        "time entered",
        "sub cc",
        "travel weekend",
        "trvl weekend",
    ]

    NEGATIVE_KEYWORDS = [
        "charges",
        "credit",
        "equipment",
        "expenses",
        "fee",
        "fees",
        "meeting",
        "overdue",
        "part",
        "workshop",
        "client",
        "from",
        "travel",
        "individual",
        "group",
        "2021",
        "2022",
        "2023",
    ]

    NEGATIVE_PHRASES = [
        "group meal",
        "individual group meal",
        "meal on",
        "travel expense",
        "travel from",
        "admin fees",
        "credit note",
    ]

    professional = (
        professional
        or does_match(
            queries=words,
            choices=PROFESSIONAL_KEYWORDS,
            score_cutoff=75,
            debug_label="professional keyword",
            debug=debug,
        )
        or does_match(
            queries=phrases,
            choices=PROFESSIONAL_PHRASES,
            score_cutoff=87,
            debug_label="professional phrase",
            debug=debug,
        )
    )

    professional = (
        professional
        and not does_match(
            queries=words,
            choices=NEGATIVE_KEYWORDS,
            score_cutoff=90,
            debug_label="negative keyword",
            debug=debug,
        )
        and not does_match(
            queries=phrases,
            choices=NEGATIVE_PHRASES,
            score_cutoff=80,
            debug_label="negative phrase",
            debug=debug,
        )
    )

    return professional


names_cache = dc.Cache("../cache/names")


def does_match(
    queries: list[str],
    choices: list[str],
    score_cutoff: int,
    debug_label: str,
    debug: bool,
):
    for query in queries:
        # heur, si la palabra es larga y esta en el query, mandale
        for choice in choices:
            if len(choice) >= 4 and choice in query:
                if debug:
                    print(debug_label, "(in)", "|", query, "|", choice)
                return True

        match = process.extractOne(
            query,
            choices,
            scorer=fuzz.ratio,
            score_cutoff=score_cutoff,
        )
        if match:
            if debug:
                print(debug_label, "|", query, match)
            return True

    return False


@names_cache.memoize(tag="first_name")
def is_first_name(first_name: str, score_cutoff):
    first_names = load_first_names()
    match = process.extractOne(
        first_name,
        first_names,
        scorer=fuzz.ratio,
        score_cutoff=score_cutoff,
    )
    return match is not None


@names_cache.memoize(tag="last_name")
def is_last_name(last_name: str, score_cutoff):
    last_names = load_last_names()
    match = process.extractOne(
        last_name,
        last_names,
        scorer=fuzz.ratio,
        score_cutoff=score_cutoff,
    )
    return match is not None

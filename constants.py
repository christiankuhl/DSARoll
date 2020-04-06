TRIALS_BY_CATEGORY = {
    "Körpertalente": {
        "Fliegen": ["MU", "IN", "GE"],
        "Gaukeleien": ["MU", "CH", "FF"],
        "Klettern": ["MU", "GE", "KK"],
        "Körperbeherrschung": ["GE", "GE", "KO"],
        "Kraftakt": ["KO", "KK", "KK"],
        "Reiten": ["CH", "GE", "KK"],
        "Schwimmen": ["GE", "KO", "KK"],
        "Selbstbeherrschung": ["MU", "MU", "KO"],
        "Singen": ["KL", "CH", "KO"],
        "Sinnesschärfe": ["KL", "IN", "IN"],
        "Tanzen": ["KL", "CH", "GE"],
        "Taschendiebstahl": ["MU", "FF", "GE"],
        "Verbergen": ["MU", "IN", "GE"],
        "Zechen": ["KL", "KO", "KK"]
    },
    "Gesellschaftstalente": {
        "Bekehren & Überzeugen": ["MU", "KL", "CH"],
        "Betören": ["MU", "CH", "CH"],
        "Einschüchtern": ["MU", "IN", "CH"],
        "Etikette": ["KL", "IN", "CH"],
        "Gassenwissen": ["KL", "IN", "CH"],
        "Menschenkenntnis": ["KL", "IN", "CH"],
        "Überreden": ["MU", "IN", "CH"],
        "Verkleiden": ["IN", "CH", "GE"],
        "Willenskraft": ["MU", "IN", "CH"],
    },
    "Naturtalente": {
        "Fährtensuchen": ["MU", "IN", "GE"],
        "Fesseln": ["KL", "FF", "KK"],
        "Fischen & Angeln": ["FF", "GE", "KO"],
        "Orientierung": ["KL", "IN", "IN"],
        "Pflanzenkunde": ["KL", "FF", "KO"],
        "Tierkunde": ["MU", "MU", "CH"],
        "Wildnisleben": ["MU", "GE", "KO"]
    },
    "Wissenstalente": {
        "Brett- & Glücksspiel": ["KL", "KL", "IN"],
        "Geographie": ["KL", "KL", "IN"],
        "Geschichtswissen": ["KL", "KL", "IN"],
        "Götter & Kulte": ["KL", "KL", "IN"],
        "Kriegskunst": ["MU", "KL", "IN"],
        "Magiekunde": ["KL", "KL", "IN"],
        "Mechanik": ["KL", "KL", "FF"],
        "Rechnen": ["KL", "KL", "IN"],
        "Rechtskunde": ["KL", "KL", "IN"],
        "Sagen & Legenden": ["KL", "KL", "IN"],
        "Sphärenkunde": ["KL", "KL", "IN"],
        "Sternkunde": ["KL", "KL", "IN"]
    },
    "Handwerkstalente": {
        "Alchimie": ["MU", "KL", "FF"],
        "Boote & Schiffe": ["FF", "GE", "KK"],
        "Fahrzeuge": ["CH", "FF", "KO"],
        "Handel": ["KL", "IN", "CH"],
        "Heilkunde Gift": ["MU", "KL", "IN"],
        "Heilkunde Krankheiten": ["MU", "IN", "KO"],
        "Heilkunde Seele": ["IN", "CH", "KO"],
        "Heilkunde Wunden": ["KL", "FF", "FF"],
        "Holzbearbeitung": ["FF", "GE", "KK"],
        "Lebensmittelbearbeitung": ["IN", "FF", "FF"],
        "Lederbearbeitung": ["FF", "GE", "KO"],
        "Malen & Zeichnen": ["IN", "FF", "FF"],
        "Metallbearbeitung": ["FF", "KO", "KK"],
        "Musizieren": ["CH", "FF", "KO"],
        "Schlösserknacken": ["IN", "FF", "FF"],
        "Steinbearbeitung": ["FF", "FF", "KK"],
        "Stoffbearbeitung": ["KL", "FF", "FF"]
    }
}

SPELLS = {
    "Freundschaftslied": {
        "trial": ["IN", "CH", "CH"],
    },
    "Armatrutz": {
        "trial": ["KL, ""IN", "FF"]
    },
    "Balsam Salabunde": {
        "trial": ["KL", "IN", "FF"]
    },
    "Odem Arcanum": {
        "trial": ["KL", "IN", "IN"]
    },
    "Silentium": {
        "trial": ["KL", "FF", "KK"]
    },
    "Fulminictus": {
        "trial": ["KL", "IN", "KO"],
        "modifier": "ZK"
    },
    "Visibili": {
        "trial": ["KL", "IN", "KO"]
    },
    "Wasseratem": {
        "trial": ["KL", "IN", "KO"]
        },
    "Gardianum": {
        "trial": ["MU", "KL", "CH"]
    },
    "Blitz dich find": {
        "trial": ["MU", "IN", "CH"],
        "modifier": "SK"
    },
    "Ignifaxius": {
        "trial": ["MU", "KL", "CH"]
    },
    "Psychostabilis": {
        "trial": ["KL", "IN", "FF"]
    },
    "Paralysis": {
        "trial": ["KL", "IN", "KO"],
        "modifier": "ZK"
    }
}

TRIALS = dict([trial for category in TRIALS_BY_CATEGORY.values()
               for trial in category.items()])

IMPAIRMENTS = ["Belastung", "Betäubung", "Entrückung", "Furcht", "Paralyse",
               "Schmerz", "Verwirrung"]

SPECIES = {
    "Menschen": {"LE_GW": 5},
    "Halbelfen": {"LE_GW": 5},
    "Elfen": {"LE_GW": 2},
    "Zwerge": {"LE_GW": 8}
}

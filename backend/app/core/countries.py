# Configuration-driven country intelligence sources and metadata
# Add new countries here to extend support without code changes.
COUNTRIES = {
    "kenya": {
        "id": "kenya",
        "name": "Kenya",
        "iso": "KE",
        "official_name": "Republic of Kenya",
        "sources": {
            "gazette": ["https://gazettes.africa/kenya/"],
            "treasury": ["https://www.treasury.go.ke/"],
            "parliament": ["https://www.parliament.go.ke/"],
            "ppra": ["https://www.ppra.go.ke/"],
        },
        "language": "en",
        "level": "national",
    },
    "united states": {
        "id": "united_states",
        "name": "United States",
        "iso": "US",
        "official_name": "United States of America",
        "sources": {
            "federal_register": ["https://www.federalregister.gov/"],
            "congress": ["https://www.congress.gov/"],
            "usa_spending": ["https://www.usaspending.gov/"],
        },
        "language": "en",
        "level": "national",
    },
    "canada": {
        "id": "canada",
        "name": "Canada",
        "iso": "CA",
        "official_name": "Canada",
        "sources": {
            "open_gov": ["https://open.canada.ca/"],
            "buyandsell": ["https://buyandsell.gc.ca/"],
            "parliament": ["https://www.parl.ca/"],
        },
        "language": "en",
        "level": "national",
    },
    "united kingdom": {
        "id": "united_kingdom",
        "name": "United Kingdom",
        "iso": "GB",
        "official_name": "United Kingdom of Great Britain and Northern Ireland",
        "sources": {
            "gov_uk": ["https://www.gov.uk/"],
            "parliament": ["https://www.parliament.uk/"],
            "contracts_finder": ["https://www.contractsfinder.service.gov.uk/"],
        },
        "language": "en",
        "level": "national",
    },
}


def list_countries():
    """Return list of configured countries (id and name)."""
    return [{"id": v["id"], "name": v["name"]} for v in COUNTRIES.values()]


def get_country_config(name_or_id: str | None):
    if not name_or_id:
        return None
    key = name_or_id.strip().lower()
    if key in COUNTRIES:
        return COUNTRIES[key]
    # try match by id or name
    for v in COUNTRIES.values():
        if v.get("id") == key or v.get("name", "").lower() == key:
            return v
    return None


def normalize_country_id(candidate_id: str | None) -> str | None:
    """Normalize various country id/name forms to the canonical configured id.

    Rules:
    - Trim and lowercase input.
    - Strip leading "country_" prefix when present.
    - Resolve human-readable names like "united states" to canonical id "united_states"
    - Preserve canonical ids such as "kenya", "united_states", "canada", "united_kingdom".
    - Return None for unsupported or unknown inputs.
    """
    if not candidate_id:
        return None
    s = candidate_id.strip().lower()
    if s.startswith("country_"):
        s = s[len("country_"):]

    # Direct lookup via get_country_config (supports names and ids)
    cfg = get_country_config(s)
    if cfg:
        return cfg.get("id")

    # Try common alternates: underscores <-> spaces
    alt = s.replace("_", " ")
    cfg = get_country_config(alt)
    if cfg:
        return cfg.get("id")
    alt2 = s.replace(" ", "_")
    cfg = get_country_config(alt2)
    if cfg:
        return cfg.get("id")

    return None

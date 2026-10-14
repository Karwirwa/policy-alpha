import json

from app.services.kenya_opportunity import extract_ministry_from_ref


def test_extract_ministry_from_raw_text_prefers_pe_name():
    raw_text = json.dumps(
        {
            "pe_name": "Raw Kenya Procuring Entity",
            "pe_id": 1234,
            "pe": {"name": "Nested Entity"},
        }
    )
    summary_json = json.dumps({"pe_name": "Summary Procuring Entity"})

    assert (
        extract_ministry_from_ref("UNKNOWN/001", summary_json, raw_text)
        == "Raw Kenya Procuring Entity"
    )


def test_extract_ministry_from_raw_text_reads_nested_pe_name():
    raw_text = json.dumps({"pe": {"name": "Kisumu County Government"}})

    assert (
        extract_ministry_from_ref("UNKNOWN/001", "{}", raw_text)
        == "Kisumu County Government"
    )


def test_extract_ministry_from_ref_prefix_fallback():
    assert extract_ministry_from_ref("KPA/PROC/001", "{}") == "Kenya Ports Authority"


def test_extract_ministry_returns_pe_id_when_all_else_missing():
    raw_text = json.dumps({"pe_id": 5413})

    assert (
        extract_ministry_from_ref("UNKNOWN/PROC/001", "{}", raw_text) == "5413"
    )


def test_known_prefix_ksmwenc_maps_to_kisumu_water():
    assert (
        extract_ministry_from_ref("KSMWENC/1470/OPEN/015", "{}")
        == "Kisumu Water & Environment"
    )


def test_known_prefix_kenha_maps_to_highways_authority():
    assert (
        extract_ministry_from_ref("KeNHa/PROC/001", "{}")
        == "Kenya National Highways Authority"
    )

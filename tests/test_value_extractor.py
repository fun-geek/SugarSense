
from report_processing.value_extractor import (
    identify_measurement_type,
    extract_candidates,
)


def test_fasting_label():
    assert (
        identify_measurement_type("Blood Glucose Fasting (FBS)")
        == "fasting_glucose"
    )


def test_postprandial_label():
    assert (
        identify_measurement_type("Post Prandial Blood Sugar (PPBS)")
        == "postprandial_glucose"
    )


def test_hba1c_label():
    assert identify_measurement_type("HbA1c") == "hba1c"


def test_extract_fasting_result():
    text = "Fasting Blood Sugar: 118.00 mg/dL"

    results = extract_candidates(text)

    assert len(results) == 1
    assert results[0]["measurement_type"] == "fasting_glucose"
    assert results[0]["value"] == 118.0
    assert results[0]["unit"] == "mg/dL"
    assert results[0]["verified"] is False


import re


TEST_PATTERNS = {
    "fasting_glucose": [
        r"\bfasting\s+blood\s+glucose\b",
        r"\bblood\s+glucose\s+fasting\b",
        r"\bfasting\s+blood\s+sugar\b",
        r"\bFBS\b",
    ],
    "postprandial_glucose": [
        r"\bpost[\s-]*prandial\b",
        r"\bpost[\s-]*meal\b",
        r"\bPPBS\b",
        r"\b2\s*hours?\s*(?:after|post)\s+(?:a\s+)?meal\b",
    ],
    "random_glucose": [
        r"\brandom\s+blood\s+glucose\b",
        r"\brandom\s+blood\s+sugar\b",
        r"\bRBS\b",
    ],
    "hba1c": [
        r"\bHbA1c\b",
        r"\bA1C\b",
        r"\bglycated\s+haemoglobin\b",
        r"\bglycated\s+hemoglobin\b",
    ],
}

VALUE_PATTERN = re.compile(
    r"(?P<value>\d{1,5}(?:\.\d+)?)\s*"
    r"(?P<unit>mg\s*/\s*dL|mmol\s*/\s*L|%)",
    re.IGNORECASE,
)

REFERENCE_PATTERN = re.compile(
    r"(?P<low>\d{1,5}(?:\.\d+)?)\s*[-–]\s*"
    r"(?P<high>\d{1,5}(?:\.\d+)?)",
)


def identify_measurement_type(text: str):
    """Identify a likely test type from its label."""

    for measurement_type, patterns in TEST_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return measurement_type

    return None


def extract_candidates(text: str) -> list[dict]:
    """
    Extract candidate measurement fields from report text.

    These are suggestions only, not verified medical measurements.
    """

    candidates = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        measurement_type = identify_measurement_type(line)

        if measurement_type is None:
            continue

        # Find a result with a recognizable unit on this line.
        value_match = VALUE_PATTERN.search(line)

        if value_match is None:
            continue

        unit = re.sub(
            r"\s+",
            "",
            value_match.group("unit"),
        )

        unit = unit.replace("mg/dL", "mg/dL")
        unit = unit.replace("mmol/L", "mmol/L")

        value = float(value_match.group("value"))

        candidates.append({
            "measurement_type": measurement_type,
            "value": value,
            "unit": unit,
            "source_line": line.strip(),
            "line_number": line_number,
            "reference_range": None,
            "verified": False,
        })

    return candidates

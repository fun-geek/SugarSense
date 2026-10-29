
from datetime import date
import math

from database.connection import get_connection


# ==================================================
# VALID MEASUREMENT TYPES AND UNITS
# ==================================================

VALID_UNITS = {
    "fasting_glucose": {"mg/dL", "mmol/L"},
    "postprandial_glucose": {"mg/dL", "mmol/L"},
    "random_glucose": {"mg/dL", "mmol/L"},
    "hba1c": {"%"},
}


# ==================================================
# VALIDATION HELPER
# ==================================================

def validate_measurement(
    measurement_type: str,
    value: float,
    unit: str,
    measured_at: str,
) -> None:
    """Validate a measurement before saving it."""

    if measurement_type not in VALID_UNITS:
        raise ValueError("Invalid measurement type.")

    if unit not in VALID_UNITS[measurement_type]:
        raise ValueError("Invalid unit for this measurement type.")

    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(
            "Enter a valid, finite, non-negative measurement value."
        )

    try:
        parsed_date = date.fromisoformat(measured_at)
    except (ValueError, TypeError):
        raise ValueError("Date must use YYYY-MM-DD format.")

    if parsed_date.isoformat() != measured_at:
        raise ValueError("Date must use YYYY-MM-DD format.")


# ==================================================
# ADD ONE MEASUREMENT
# ==================================================

def add_measurement(
    measurement_type: str,
    value: float,
    unit: str,
    measured_at: str,
    report_id: int | None = None,
    verified_by_user: bool = True,
) -> int:
    """Validate and save one measurement."""

    validate_measurement(
        measurement_type,
        value,
        unit,
        measured_at,
    )

    if report_id is not None and (
        not isinstance(report_id, int)
        or isinstance(report_id, bool)
        or report_id <= 0
    ):
        raise ValueError("Invalid report ID.")

    if not isinstance(verified_by_user, bool):
        raise ValueError("Verification status must be True or False.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO measurements (
                report_id,
                measurement_type,
                value,
                unit,
                measured_at,
                verified_by_user
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                measurement_type,
                float(value),
                unit,
                measured_at,
                int(verified_by_user),
            ),
        )

        return cursor.lastrowid


# ==================================================
# GET MEASUREMENTS
# ==================================================

def get_measurements():
    """Return measurements in chronological order."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                report_id,
                measurement_type,
                value,
                unit,
                measured_at,
                verified_by_user,
                created_at
            FROM measurements
            ORDER BY measured_at ASC, id ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]


# ==================================================
# DELETE A MEASUREMENT
# ==================================================

def delete_measurement(measurement_id: int) -> bool:
    """Delete a measurement by its ID."""

    if (
        not isinstance(measurement_id, int)
        or isinstance(measurement_id, bool)
        or measurement_id <= 0
    ):
        raise ValueError(
            "Measurement ID must be a positive integer."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM measurements WHERE id = ?",
            (measurement_id,),
        )

        return cursor.rowcount > 0


# ==================================================
# ADD REPORT METADATA
# ==================================================

def add_report(
    original_filename: str,
    stored_filename: str,
    file_type: str = "pdf",
    processing_status: str = "processed",
) -> int:
    """Save report metadata and return its database ID."""

    if not original_filename or not original_filename.strip():
        raise ValueError("Original filename is required.")

    if not stored_filename or not stored_filename.strip():
        raise ValueError("Stored filename is required.")

    if file_type not in {"pdf", "png", "jpg", "jpeg"}:
        raise ValueError("Unsupported report file type.")

    if processing_status not in {
        "pending",
        "processed",
        "failed",
    }:
        raise ValueError("Invalid report processing status.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reports (
                original_filename,
                stored_filename,
                file_type,
                processing_status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                original_filename,
                stored_filename,
                file_type,
                processing_status,
            ),
        )

        return cursor.lastrowid


# ==================================================
# GET REPORTS
# ==================================================

def get_reports():
    """Return report metadata without reading report files."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                original_filename,
                stored_filename,
                file_type,
                uploaded_at,
                processing_status
            FROM reports
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


# ==================================================
# SAVE MULTIPLE VERIFIED MEASUREMENTS
# ==================================================

def save_measurements_batch(
    report_id: int,
    measurements: list[dict],
) -> list[int]:
    """
    Save verified measurements linked to one report.

    All inserts run within one database transaction.
    If an insert fails, the batch is rolled back.
    """

    if (
        not isinstance(report_id, int)
        or isinstance(report_id, bool)
        or report_id <= 0
    ):
        raise ValueError("Invalid report ID.")

    if not measurements:
        raise ValueError("There are no measurements to save.")

    prepared = []

    # Validate every measurement before starting the transaction.
    for item in measurements:
        if not isinstance(item, dict):
            raise ValueError("Each measurement must be a dictionary.")

        measurement_type = item.get("measurement_type")
        value = item.get("value")
        unit = item.get("unit")
        measured_at = item.get("measured_at")
        verified = item.get("verified_by_user", True)

        validate_measurement(
            measurement_type,
            value,
            unit,
            measured_at,
        )

        if verified is not True:
            raise ValueError(
                "Every measurement must be verified before saving."
            )

        prepared.append(
            (
                report_id,
                measurement_type,
                float(value),
                unit,
                measured_at,
                1,
            )
        )

    # This transaction commits all rows together or rolls them all back.
    with get_connection() as connection:
        report = connection.execute(
            "SELECT id FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()

        if report is None:
            raise ValueError("The source report does not exist.")

        saved_ids = []

        for values in prepared:
            cursor = connection.execute(
                """
                INSERT INTO measurements (
                    report_id,
                    measurement_type,
                    value,
                    unit,
                    measured_at,
                    verified_by_user
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                values,
            )

            saved_ids.append(cursor.lastrowid)

        return saved_ids

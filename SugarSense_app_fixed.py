import math
from datetime import date, datetime

import pandas as pd
import streamlit as st

from services.report_service import (
    process_report,
    store_report_file,
)
from database.repository import (
    add_measurement,
    delete_measurement,
    get_measurements,
    get_reports,
    save_measurements_batch,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SugarSense AI",
    page_icon="🩺",
    layout="wide",
)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

MEASUREMENT_LABELS = {
    "fasting_glucose": "Fasting Glucose",
    "postprandial_glucose": "Postprandial Glucose",
    "random_glucose": "Random Glucose",
    "hba1c": "HbA1c",
}

MEASUREMENT_TYPES = list(MEASUREMENT_LABELS.keys())

DEFAULT_UNITS = {
    "fasting_glucose": "mg/dL",
    "postprandial_glucose": "mg/dL",
    "random_glucose": "mg/dL",
    "hba1c": "%",
}

UNIT_OPTIONS = {
    "fasting_glucose": ["mg/dL", "mmol/L"],
    "postprandial_glucose": ["mg/dL", "mmol/L"],
    "random_glucose": ["mg/dL", "mmol/L"],
    "hba1c": ["%"],
}


def safe_candidate_value(value, fallback=100.0):
    """Return a finite number suitable for a Streamlit number input."""
    try:
        number = float(value)
        if math.isfinite(number) and number >= 0.01:
            return min(number, 2000.0)
    except (TypeError, ValueError):
        pass
    return fallback


def safe_candidate_date(value):
    """Convert supported date values to a Python date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip()[:10])
        except (ValueError, TypeError):
            pass

    return date.today()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🩺 SugarSense AI")
st.caption(
    "Track glucose measurements and review values extracted "
    "from your medical reports."
)
st.info(
    "SugarSense AI is a tracking tool, not a diagnostic system. "
    "Review report-extracted values carefully and consult your "
    "healthcare professional about medical decisions."
)


# --------------------------------------------------
# MANUAL MEASUREMENT ENTRY
# --------------------------------------------------

st.header("Add a Measurement")

with st.form("manual_measurement_form"):
    measurement_type = st.selectbox(
        "Measurement Type",
        options=MEASUREMENT_TYPES,
        format_func=lambda item: MEASUREMENT_LABELS[item],
        key="manual_measurement_type",
    )

    measurement_value = st.number_input(
        "Value",
        min_value=0.01,
        max_value=2000.0,
        value=100.0,
        step=1.0,
        key="manual_measurement_value",
    )

    measurement_unit = st.selectbox(
        "Unit",
        options=UNIT_OPTIONS[measurement_type],
        index=UNIT_OPTIONS[measurement_type].index(
            DEFAULT_UNITS[measurement_type]
        ),
        key="manual_measurement_unit",
    )

    measurement_date = st.date_input(
        "Measurement Date",
        value=date.today(),
        key="manual_measurement_date",
    )

    submitted = st.form_submit_button("Save Measurement")

if submitted:
    # The repository validates measured_at as YYYY-MM-DD,
    # so store a date-only ISO string here.
    measured_at = measurement_date.isoformat()

    try:
        add_measurement(
            measurement_type=measurement_type,
            value=measurement_value,
            unit=measurement_unit,
            measured_at=measured_at,
            verified_by_user=True,
        )
        st.success("Measurement saved successfully.")
        st.rerun()
    except Exception as error:
        st.error(f"Could not save the measurement: {error}")


st.divider()


# --------------------------------------------------
# REPORT UPLOAD AND EXTRACTION
# --------------------------------------------------

st.header("Upload a Medical Report")
st.write(
    "Upload a PDF with selectable text. Scanned PDFs and image-based "
    "reports require OCR, which is not configured yet."
)

uploaded_file = st.file_uploader(
    "Choose a PDF report",
    type=["pdf"],
    key="report_uploader",
)

if uploaded_file is not None:
    if st.button("Process Report", key="process_report_button"):
        try:
            file_bytes = uploaded_file.getvalue()

            # Extract text and identify candidate measurements first.
            extraction_result = process_report(
                uploaded_file.name,
                file_bytes,
            )

            # Save the report after text extraction succeeds.
            report_id = store_report_file(
                uploaded_file.name,
                file_bytes,
            )

            extraction_result["report_id"] = report_id
            st.session_state["report_extraction"] = extraction_result
            st.success("Report processed successfully.")

        except (ValueError, OSError) as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"An unexpected error occurred: {error}")


# --------------------------------------------------
# REVIEW EXTRACTED VALUES
# --------------------------------------------------

result = st.session_state.get("report_extraction")

if result:
    st.subheader("Review Extracted Measurements")
    st.caption(
        "Extracted values are candidates, not confirmed medical results. "
        "Compare each value with the original report before saving it."
    )
    st.write(f"**File:** {result.get('filename', 'Uploaded report')}")

    with st.expander("View extracted PDF text"):
        st.text_area(
            "Extracted text",
            value=result.get("text", ""),
            height=250,
            disabled=True,
            key="extracted_pdf_text",
        )

    candidates = result.get("candidates", [])

    if not candidates:
        st.warning(
            "No measurement candidates were identified. "
            "You can still add values manually."
        )
    else:
        with st.form("review_extracted_measurements"):
            reviewed_measurements = []

            for index, candidate in enumerate(candidates):
                st.markdown(f"**Candidate {index + 1}**")

                candidate_type = candidate.get(
                    "measurement_type",
                    "fasting_glucose",
                )
                if candidate_type not in MEASUREMENT_TYPES:
                    candidate_type = "fasting_glucose"

                candidate_unit = candidate.get(
                    "unit",
                    DEFAULT_UNITS[candidate_type],
                )
                if candidate_unit not in UNIT_OPTIONS[candidate_type]:
                    candidate_unit = DEFAULT_UNITS[candidate_type]

                col1, col2 = st.columns(2)

                with col1:
                    selected_type = st.selectbox(
                        "Measurement Type",
                        options=MEASUREMENT_TYPES,
                        index=MEASUREMENT_TYPES.index(candidate_type),
                        format_func=lambda item: MEASUREMENT_LABELS[item],
                        key=f"candidate_type_{index}",
                    )

                    selected_value = st.number_input(
                        "Value",
                        min_value=0.01,
                        max_value=2000.0,
                        value=safe_candidate_value(candidate.get("value")),
                        step=0.1,
                        key=f"candidate_value_{index}",
                    )

                with col2:
                    current_units = UNIT_OPTIONS[selected_type]
                    unit_index = (
                        current_units.index(candidate_unit)
                        if candidate_unit in current_units
                        else 0
                    )

                    selected_unit = st.selectbox(
                        "Unit",
                        options=current_units,
                        index=unit_index,
                        key=f"candidate_unit_{index}",
                    )

                    selected_date = st.date_input(
                        "Measurement Date",
                        value=safe_candidate_date(
                            candidate.get("measured_at")
                        ),
                        key=f"candidate_date_{index}",
                    )

                verified = st.checkbox(
                    "I checked this value against the original report.",
                    value=False,
                    key=f"candidate_verified_{index}",
                )

                reviewed_measurements.append(
                    {
                        "measurement_type": selected_type,
                        "value": selected_value,
                        "unit": selected_unit,
                        "measured_at": selected_date.isoformat(),
                        "verified_by_user": verified,
                    }
                )
                st.divider()

            save_reviewed = st.form_submit_button(
                "Save Verified Measurements"
            )

        if save_reviewed:
            verified_measurements = [
                item
                for item in reviewed_measurements
                if item["verified_by_user"]
            ]

            if not verified_measurements:
                st.warning(
                    "No measurements were marked as verified. "
                    "Review and confirm values before saving."
                )
            else:
                try:
                    save_measurements_batch(
                        report_id=result["report_id"],
                        measurements=verified_measurements,
                    )
                    st.success(
                        f"Saved {len(verified_measurements)} "
                        "verified measurement(s)."
                    )
                    st.session_state.pop("report_extraction", None)
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not save the measurements: {error}")


st.divider()


# --------------------------------------------------
# SAVED REPORTS
# --------------------------------------------------

st.header("Saved Reports")

try:
    reports = get_reports()

    if reports:
        reports_df = pd.DataFrame(reports)
        st.dataframe(
            reports_df,
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No reports saved yet.")
except Exception as error:
    st.error(f"Could not load saved reports: {error}")


st.divider()


# --------------------------------------------------
# MEASUREMENT HISTORY, CHARTS, AND DELETE
# --------------------------------------------------

def show_measurement_history():
    """Display saved measurements, charts, and record deletion."""

    try:
        measurements = get_measurements()
    except Exception as error:
        st.error(f"Could not load measurement history: {error}")
        return

    if measurements is None or len(measurements) == 0:
        st.info("No measurements saved yet.")
        return

    df = pd.DataFrame(measurements)
    if df.empty:
        st.info("No measurements saved yet.")
        return

    if "measurement_type" not in df.columns:
        st.error(
            "The measurement data does not contain a measurement_type column."
        )
        return

    df["measurement_label"] = (
        df["measurement_type"]
        .map(MEASUREMENT_LABELS)
        .fillna(df["measurement_type"])
    )

    st.subheader("Measurement History")

    display_columns = [
        column
        for column in [
            "id",
            "measurement_label",
            "value",
            "unit",
            "measured_at",
            "verified_by_user",
        ]
        if column in df.columns
    ]

    st.dataframe(
        df[display_columns],
        width="stretch",
        hide_index=True,
    )

    # Glucose readings in mg/dL are charted together.
    st.subheader("Glucose Trend")

    if {"unit", "value", "measured_at"}.issubset(df.columns):
        glucose_df = df[
            df["measurement_type"].isin(
                [
                    "fasting_glucose",
                    "postprandial_glucose",
                    "random_glucose",
                ]
            )
            & (df["unit"] == "mg/dL")
        ].copy()

        if not glucose_df.empty:
            glucose_df["measured_at"] = pd.to_datetime(
                glucose_df["measured_at"],
                errors="coerce",
            )
            glucose_df["value"] = pd.to_numeric(
                glucose_df["value"],
                errors="coerce",
            )
            glucose_df = glucose_df.dropna(
                subset=["measured_at", "value"]
            )

            if not glucose_df.empty:
                chart_df = glucose_df.pivot_table(
                    index="measured_at",
                    columns="measurement_label",
                    values="value",
                    aggfunc="mean",
                ).sort_index()
                st.line_chart(chart_df)
            else:
                st.caption("There are no valid glucose dates to chart.")
        else:
            st.caption(
                "No glucose readings in mg/dL are available to chart yet."
            )

    # HbA1c is charted separately because it uses a different unit.
    hba1c_df = df[df["measurement_type"] == "hba1c"].copy()

    if not hba1c_df.empty and {"value", "measured_at"}.issubset(
        hba1c_df.columns
    ):
        st.subheader("HbA1c History")
        hba1c_df["measured_at"] = pd.to_datetime(
            hba1c_df["measured_at"],
            errors="coerce",
        )
        hba1c_df["value"] = pd.to_numeric(
            hba1c_df["value"],
            errors="coerce",
        )
        hba1c_df = hba1c_df.dropna(
            subset=["measured_at", "value"]
        )

        if not hba1c_df.empty:
            hba1c_chart = hba1c_df.set_index(
                "measured_at"
            )[["value"]].sort_index()
            st.line_chart(hba1c_chart)

    # Use unique widget keys to prevent Streamlit duplicate-key errors.
    if "id" in df.columns and not df.empty:
        st.subheader("Delete a Measurement")

        record_ids = df["id"].tolist()
        selected_id = st.selectbox(
            "Choose a record",
            options=record_ids,
            format_func=lambda record_id: f"Record {record_id}",
            key="history_delete_measurement_id",
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this record.",
            key="history_confirm_delete_measurement",
        )

        if st.button(
            "Delete Selected Record",
            key="history_delete_measurement_button",
            disabled=not confirm_delete,
        ):
            try:
                delete_measurement(selected_id)
                st.success("Measurement deleted.")
                st.rerun()
            except Exception as error:
                st.error(f"Could not delete the measurement: {error}")


show_measurement_history()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "SugarSense AI • Keep medical reports private. "
    "This app does not replace professional medical advice."
)

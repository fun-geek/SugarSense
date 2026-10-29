
from database.connection import get_connection


def initialize_database():
    """Create SugarSense AI database tables and indexes."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processing_status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (
                        processing_status IN (
                            'pending',
                            'processed',
                            'failed'
                        )
                    )
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                report_id INTEGER,

                measurement_type TEXT NOT NULL
                    CHECK (
                        measurement_type IN (
                            'fasting_glucose',
                            'postprandial_glucose',
                            'random_glucose',
                            'hba1c'
                        )
                    ),

                value REAL NOT NULL CHECK (value >= 0),
                unit TEXT NOT NULL,
                measured_at TEXT NOT NULL,

                verified_by_user INTEGER NOT NULL DEFAULT 0
                    CHECK (verified_by_user IN (0, 1)),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (report_id)
                    REFERENCES reports(id)
                    ON DELETE SET NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_date
            ON measurements(measured_at)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_type
            ON measurements(measurement_type)
        """)

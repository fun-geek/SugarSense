
import sqlite3

from config.settings import DATABASE_PATH


def migrate_measurements():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")

        # Read the existing table definition.
        result = connection.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'measurements'
        """).fetchone()

        if result is None:
            connection.rollback()
            print("Measurements table does not exist. Nothing to migrate.")
            return

        schema = result[0]

        # Skip migration if the new types are already supported.
        if (
            "fasting_glucose" in schema
            and "postprandial_glucose" in schema
            and "random_glucose" in schema
        ):
            connection.rollback()
            print("Database already supports all measurement types.")
            return

        connection.execute("""
            CREATE TABLE measurements_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,

                measurement_type TEXT NOT NULL
                    CHECK (
                        measurement_type IN (
                            'glucose',
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

        # Preserve all existing measurement records.
        connection.execute("""
            INSERT INTO measurements_new (
                id,
                report_id,
                measurement_type,
                value,
                unit,
                measured_at,
                verified_by_user,
                created_at
            )
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
        """)

        connection.execute("DROP TABLE measurements")
        connection.execute(
            "ALTER TABLE measurements_new RENAME TO measurements"
        )

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_date
            ON measurements(measured_at)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_type
            ON measurements(measurement_type)
        """)

        connection.commit()
        print("Database migration completed successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_measurements()

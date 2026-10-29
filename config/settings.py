from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRIVATE_REPORTS_DIR = PROJECT_ROOT / "private_reports"
PRIVATE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "private_reports"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

DATABASE_PATH = DATA_DIR / "sugarsense.db"

MAX_UPLOAD_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

for directory in (DATA_DIR, REPORTS_DIR, ARTIFACTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FILE = BASE_DIR / "dataset" / "raw" / "library_records.csv"
PROCESSED_FILE = BASE_DIR / "dataset" / "processed" / "library_records.json"

UPLOAD_DIR = BASE_DIR / "results" / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "Smart Cloud Archival Digital Library"
APP_VERSION = "1.0.0"

AWS_REGION = "ap-south-1"

S3_BUCKET = ""
NEPTUNE_ENDPOINT = ""
BEDROCK_MODEL_ID = ""
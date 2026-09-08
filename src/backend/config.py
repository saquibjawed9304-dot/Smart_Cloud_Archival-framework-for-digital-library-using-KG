from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FILE = BASE_DIR / "dataset" / "raw" / "library_records.csv"
PROCESSED_FILE = BASE_DIR / "dataset" / "processed" / "library_records.json"

UPLOAD_DIR = BASE_DIR / "results" / "uploads"
FRONTEND_DIR = BASE_DIR / "src" / "frontend"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "Smart Cloud Archival Digital Library"
APP_VERSION = "1.0.0"

ENVIRONMENT = os.getenv("APP_ENV", "development")
DATA_BACKEND = os.getenv("DATA_BACKEND", "csv").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "smart_archival")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(25 * 1024 * 1024)))
ALLOWED_ORIGINS = [
	origin.strip()
	for origin in os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500").split(",")
	if origin.strip()
]

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

S3_BUCKET = os.getenv("S3_BUCKET", "")
NEPTUNE_ENDPOINT = os.getenv("NEPTUNE_ENDPOINT", "")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")


def mysql_connection_config():
	return {
		"host": MYSQL_HOST,
		"port": MYSQL_PORT,
		"database": MYSQL_DATABASE,
		"user": MYSQL_USER,
		"password": MYSQL_PASSWORD,
	}
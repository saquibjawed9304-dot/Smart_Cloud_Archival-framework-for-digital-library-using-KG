import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backend.config import DATASET_FILE, mysql_connection_config
from src.backend.database import initialize_schema


def seed_books() -> int:
	import mysql.connector

	connection = mysql.connector.connect(**mysql_connection_config())
	try:
		cursor = connection.cursor()
		with open(DATASET_FILE, "r", encoding="utf-8", newline="") as file:
			rows = csv.DictReader(file)
			values = [
				(
					row["id"].strip(), row["title"].strip(), row["author"].strip(),
					row["subject"].strip(), row["institution"].strip(),
					row["language"].strip(), int(row["year"]) if row["year"] else None,
				)
				for row in rows
			]
		cursor.executemany(
			"""
			INSERT INTO books (id, title, author, subject, institution, language, year)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
			ON DUPLICATE KEY UPDATE title = VALUES(title), author = VALUES(author),
				subject = VALUES(subject), institution = VALUES(institution),
				language = VALUES(language), year = VALUES(year)
			""",
			values,
		)
		connection.commit()
		return len(values)
	finally:
		connection.close()


if __name__ == "__main__":
	initialize_schema()
	count = seed_books()
	print(f"Seeded {count} books from {DATASET_FILE}")

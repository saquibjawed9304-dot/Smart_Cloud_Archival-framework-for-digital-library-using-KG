from __future__ import annotations

from .config import mysql_connection_config


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS books (
        id VARCHAR(64) PRIMARY KEY,
        title VARCHAR(500) NOT NULL,
        author VARCHAR(255) NOT NULL,
        subject VARCHAR(255) NOT NULL,
        institution VARCHAR(255) NOT NULL,
        language VARCHAR(100) NOT NULL,
        year SMALLINT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_books_title (title),
        INDEX idx_books_author (author),
        INDEX idx_books_subject (subject)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id CHAR(36) PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        storage_key VARCHAR(500) NULL,
        status VARCHAR(32) NOT NULL,
        characters_extracted INT NOT NULL DEFAULT 0,
        text_preview TEXT NULL,
        error_message TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS entities (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        document_id CHAR(36) NOT NULL,
        entity_key VARCHAR(255) NOT NULL,
        entity_type VARCHAR(100) NOT NULL,
        label VARCHAR(500) NOT NULL,
        confidence DECIMAL(5,4) NULL,
        UNIQUE KEY uq_document_entity (document_id, entity_key),
        CONSTRAINT fk_entities_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS relationships (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        document_id CHAR(36) NOT NULL,
        source_key VARCHAR(255) NOT NULL,
        relationship_type VARCHAR(100) NOT NULL,
        target_key VARCHAR(255) NOT NULL,
        UNIQUE KEY uq_document_relationship (document_id, source_key, relationship_type, target_key),
        CONSTRAINT fk_relationships_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
)


def initialize_schema() -> None:
    try:
        import mysql.connector
    except ImportError as error:
        raise RuntimeError("mysql-connector-python is required for MySQL schema setup") from error

    connection = mysql.connector.connect(**mysql_connection_config())
    try:
        cursor = connection.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        connection.commit()
    finally:
        connection.close()
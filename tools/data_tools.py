import sqlite3
import pandas as pd
import json
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS unified_data (
            id INTEGER PRIMARY KEY,
            source_id TEXT,
            data_type TEXT,
            raw_data TEXT,
            cleaned_data TEXT,
            quality_score REAL,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def ingest_csv(file_path):
    """Ingest CSV data into unified store"""
    df = pd.read_csv(file_path)
    conn = sqlite3.connect(DB_PATH)
    for _, row in df.iterrows():
        conn.execute(
            "INSERT INTO unified_data (source_id, data_type, raw_data, quality_score) VALUES (?, ?, ?, ?)",
            (file_path, 'csv', json.dumps(row.to_dict()), 0.85)
        )
    conn.commit()
    conn.close()
    return f"Ingested {len(df)} records from {file_path}"

def query_unified_store(query):
    """Query unified data store"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict('records')

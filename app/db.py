import sqlite3
import os
import pandas as pd
import asyncio

os.makedirs("data", exist_ok=True)

DB_PATH = "data/clients.db"
EXCEL_PATH = "data/clients.xlsx"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_lead(name, phone, message):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO leads (name, phone, message) VALUES (?, ?, ?)",
            (name, phone, message)
        )

def get_all_leads():
    """Возвращает список всех заявок."""
    if not os.path.exists(DB_PATH):
        return []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]

async def export_to_excel_loop():
    """Фоновая задача — экспортирует таблицу каждые 30 минут"""
    while True:
        await asyncio.sleep(60 * 30)  # 30 минут
        export_to_excel()

def export_to_excel():
    if not os.path.exists(DB_PATH):
        return
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM leads", conn)
    df.to_excel(EXCEL_PATH, index=False)
    print("📤 Leads exported to Excel:", EXCEL_PATH)

def clear_old_data(days=30):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM leads WHERE created_at < datetime('now', '-{days} day')")
        conn.commit()
        return cur.rowcount

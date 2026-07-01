import sqlite3
from contextlib import contextmanager
DATABASE = 'baza.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

@contextmanager
def get_connection(): # Безопасное подключение
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # для лучшей конкурентности
    try:
        yield conn
    finally:
        conn.close()


def read_tasks(): # Читает задачи из базы данных
  try:
    with get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM users")
      return cursor.fetchall()
  except sqlite3.OperationalError:
    create_database()


def create_database(): # Создает базу данных и таблицы
  with get_connection() as conn:
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
  ''')
  

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
  );
  ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    session_token TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
  );
  ''')
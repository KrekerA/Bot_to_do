import sqlite3
DATABASE = 'baza.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


def read_tasks(): # Читает задачи из базы данных
  try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
  except sqlite3.OperationalError:
    create_database()


def create_database(): # Создает базу данных и таблицы
  conn = sqlite3.connect(DATABASE) 
  conn.execute("PRAGMA foreign_keys = ON") # Включает поддержку внешних ключей в SQLite
  cursor = conn.cursor()

  conn = sqlite3.connect('baza.db')
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

def get_connection(): # Подключает базу данных 
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn  
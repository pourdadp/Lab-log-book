# database.py
from datetime import datetime
import sqlite3
import jdatetime
from config import DB_NAME


def get_connection():
  """ایجاد اتصال به دیتابیس SQLite"""
  try:
    conn = sqlite3.connect(DB_NAME)
    return conn
  except sqlite3.Error as e:
    print(f"Database connection error: {e}")
    return None


def init_db():
  """راه‌اندازی اولیه پایگاه داده و ایجاد جدول‌ها"""
  conn = get_connection()
  if not conn:
    return
  cursor = conn.cursor()

  try:
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                location TEXT,
                expert TEXT,
                default_temp REAL,
                default_param TEXT,
                calibration_date TEXT,
                status TEXT
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                reporter TEXT,
                datetime_shamsi TEXT,
                temp_recorded REAL,
                param_recorded TEXT,
                is_warning INTEGER,
                description TEXT,
                is_broken INTEGER
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                action TEXT,
                datetime_shamsi TEXT
            )
        """)

    # بررسی وجود ادمین پیش‌فرض (با پسورد هش شده)
    import bcrypt

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
      hashed_admin_pass = bcrypt.hashpw(
          "admin123".encode("utf-8"), bcrypt.gensalt()
      )
      cursor.execute(
          "INSERT INTO users VALUES (?, ?, ?)",
          ("admin", hashed_admin_pass, "مدیر سیستم (ادمین)"),
      )

    conn.commit()
  except sqlite3.Error as e:
    print(f"Error initializing database: {e}")
  finally:
    conn.close()


def log_audit(username, action):
  """ثبت رویدادهای سیستم در بخش حسابرسی"""
  conn = get_connection()
  if not conn:
    return
  cursor = conn.cursor()
  now_shamsi = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
  try:
    cursor.execute(
        "INSERT INTO audit_logs (username, action, datetime_shamsi) VALUES (?,"
        " ?, ?)",
        (username, action, now_shamsi),
    )
    conn.commit()
  except sqlite3.Error as e:
    print(f"Audit log error: {e}")
  finally:
    conn.close()

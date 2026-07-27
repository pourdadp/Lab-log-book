import sqlite3
from config import DB_NAME, hash_password


def get_connection():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  # جدول کاربران با سطوح دسترسی ۴گانه و وضعیت فعال/غیرفعال
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT, -- مدیر سیستم، کارشناس، گزارشگر، مشاهده‌کننده
            status TEXT DEFAULT 'فعال'
        )
    """)

  # جدول دستگاه‌ها (با قابلیت وضعیت‌دهی برای GLP/GMP)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            location TEXT,
            status TEXT DEFAULT 'فعال'
        )
    """)

  # جدول پارامترهای پویای دستگاه‌ها (مقادیر پیش‌فرض اختیاری)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            param_name TEXT,
            default_value TEXT, -- اختیاری (می‌تواند خالی باشد)
            status TEXT DEFAULT 'فعال',
            FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
        )
    """)

  # جدول لاگ‌ها / گزارش‌ها
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            username TEXT,
            jalali_date TEXT,
            has_warning INTEGER DEFAULT 0,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    """)

  # جدول مقادیر پویای ثبت‌شده در هر گزارش
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id INTEGER,
            param_name TEXT,
            recorded_value TEXT,
            FOREIGN KEY (log_id) REFERENCES logs (id) ON DELETE CASCADE
        )
    """)

  # جدول ممیزی (Audit Trail) جهت انطباق با GLP/GMP
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp TEXT
        )
    """)

  # ایجاد کاربر مدیر پیش‌فرض در صورت عدم وجود
  cursor.execute("SELECT COUNT(*) FROM users")
  if cursor.fetchone()[0] == 0:
    admin_pass = hash_password("admin123")
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", admin_pass, "مدیر سیستم"),
    )

  conn.commit()
  conn.close()


if __name__ == "__main__":
  init_db()

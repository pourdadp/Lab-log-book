# auth.py
import bcrypt
from database import get_connection


def verify_user(username, password):
  """بررسی صحت نام کاربری و پسورد هش شده"""
  conn = get_connection()
  if not conn:
    return None
  cursor = conn.cursor()
  try:
    cursor.execute(
        "SELECT password, role FROM users WHERE username = ?", (username,)
    )
    res = cursor.fetchone()
    if res:
      stored_password = res[0]
      role = res[1]
      # اگر پسورد به صورت بایت یا استرینگ باشد
      if isinstance(stored_password, str):
        stored_password = stored_password.encode("utf-8")

      if bcrypt.checkpw(password.encode("utf-8"), stored_password):
        return role
  except Exception as e:
    print(f"Auth error: {e}")
  finally:
    conn.close()
  return None


def create_user(username, password, role):
  """ایجاد کاربر جدید با پسورد هش‌شده"""
  conn = get_connection()
  if not conn:
    return False
  cursor = conn.cursor()
  try:
    hashed_pass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed_pass, role),
    )
    conn.commit()
    return True
  except Exception:
    return False
  finally:
    conn.close()

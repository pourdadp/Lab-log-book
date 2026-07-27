import hashlib

# تنظیمات امنیتی و پایه
DB_NAME = "lab_logbook.db"


def hash_password(password):
  """هش کردن پسورد با استاندارد امنیتی مناسب"""
  return hashlib.sha256(password.encode()).hexdigest()

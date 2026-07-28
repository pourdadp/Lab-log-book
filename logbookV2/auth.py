from database import get_connection
from config import hash_password


def authenticate_user(username, password):
  conn = get_connection()
  cursor = conn.cursor()
  hashed_pwd = hash_password(password)

  cursor.execute(
      "SELECT * FROM users WHERE username = ? AND password = ? AND status ="
      " 'فعال'",
      (username, hashed_pwd),
  )
  user = cursor.fetchone()
  conn.close()
  return user

import streamlit as st
import pandas as pd
import jdatetime
from database import init_db, get_connection
from auth import authenticate_user

# راه‌اندازی اولیه دیتابیس
init_db()

st.set_page_config(
    page_title="QuickLab - سامانه آزمایشگاهی", layout="wide"
)

# مدیریت نشست (Session State) برای لاگین
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["username"] = ""
  st.session_state["role"] = ""

# صفحه ورود
if not st.session_state["logged_in"]:
  st.title("🔐 ورود به سامانه مدیریت آزمایشگاه (QuickLab)")

  with st.form("login_form"):
    username = st.text_input("نام کاربری")
    password = st.text_input("رمز عبور", type="password")
    submit = st.form_submit_button("ورود")

    if submit:
      user = authenticate_user(username, password)
      if user:
        st.session_state["logged_in"] = True
        st.session_state["username"] = user["username"]
        st.session_state["role"] = user["role"]
        st.success("ورود موفقیت‌آمیز بود!")
        st.rerun()
      else:
        st.error(
            "نام کاربری یا رمز عبور اشتباه است و یا حساب کاربری غیرفعال است."
        )

else:
  # منوی سایدبار و سطوح دسترسی
  role = st.session_state["role"]
  username = st.session_state["username"]

  st.sidebar.title(f"👤 کاربر: {username}")
  st.sidebar.markdown(f"**نقش کاربری:** `{role}`")

  menu_options = []

  if role == "مدیر سیستم":
    menu_options = [
        "ثبت گزارش جدید",
        "مدیریت دستگاه‌ها و پارامترها",
        "مدیریت کاربران",
        "گزارشات و ممیزی",
    ]
  elif role == "کارشناس":
    menu_options = [
        "ثبت گزارش جدید",
        "مدیریت دستگاه‌ها و پارامترها",
        "گزارشات و ممیزی",
    ]
  elif role == "گزارشگر":
    menu_options = ["ثبت گزارش جدید", "گزارشات و ممیزی"]
  elif role == "مشاهده‌کننده":
    menu_options = ["مشاهده دستگاه‌ها و پارامترها", "گزارشات و ممیزی"]

  selected_menu = st.sidebar.selectbox("منوی اصلی", menu_options)

  if st.sidebar.button("خروج از سیستم"):
    st.session_state["logged_in"] = False
    st.rerun()

  # -------------------------------------------------------------
  # ۱. بخش ثبت گزارش جدید
  # -------------------------------------------------------------
  if selected_menu == "ثبت گزارش جدید":
    st.title("📝 ثبت گزارش و پارامترهای دستگاه")

    if role == "مشاهده‌کننده":
      st.error(
          "شما دسترسی لازم برای ثبت گزارش را ندارید (نقش شما مشاهده‌کننده"
          " است)."
      )
    else:
      conn = get_connection()
      devices_df = pd.read_sql(
          "SELECT * FROM devices WHERE status = 'فعال'", conn
      )

      if devices_df.empty:
        st.warning("هیچ دستگاه فعالی در سیستم ثبت نشده است.")
      else:
        dev_names = devices_df["name"].tolist()
        selected_dev_name = st.selectbox("انتخاب دستگاه", dev_names)

        dev_info = devices_df[
            devices_df["name"] == selected_dev_name
        ].iloc[0]
        dev_id = dev_info["id"]

        st.info(
            f"محل استقرار دستگاه: **{dev_info['location']}**"
        )

        # دریافت پارامترهای پویای این دستگاه
        params_df = pd.read_sql(
            "SELECT * FROM device_parameters WHERE device_id = ? AND status ="
            " 'فعال'",
            conn,
            params=(dev_id,),
        )

        if params_df.empty:
          st.warning(
              "هیچ پارامتری برای این دستگاه تعریف نشده است. لطفاً از طریق بخش"
              " مدیریت دستگاه‌ها پارامتر اضافه کنید."
          )
        else:
          st.markdown("### مقادیر پارامترهای دستگاه")
          recorded_values = {}
          has_warning = False

          for idx, row in params_df.iterrows():
            p_name = row["param_name"]
            p_default = row["default_value"]

            label = (
                f"مقدار برای {p_name} (استاندارد/پیش‌فرض:"
                f" {p_default if p_default else 'ندارد'})"
            )
            val = st.text_input(label, key=f"param_input_{idx}")
            recorded_values[p_name] = val

            # بررسی مغایرت در صورت وجود مقدار پیش‌فرض
            if p_default and val and (val != p_default):
              has_warning = True
              st.warning(
                  f"⚠️ مغایرت در پارامتر **{p_name}**! مقدار ثبت‌شده: `{val}` |"
                  f" مقدار استاندارد: `{p_default}`"
              )

              # پخش بوق صوتی و هشدار مرورگر
              audio_html = """
                            <audio autoplay>
                                <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
                            </audio>
                            """
              st.markdown(audio_html, unsafe_allow_html=True)

          if st.button("💾 ثبت نهایی گزارش"):
            current_jalali = str(jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M"))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (device_id, username, jalali_date,"
                " has_warning) VALUES (?, ?, ?, ?)",
                (dev_id, username, current_jalali, 1 if has_warning else 0),
            )
            log_id = cursor.lastrowid

            for p_name, val in recorded_values.items():
              cursor.execute(
                  "INSERT INTO log_parameters (log_id, param_name,"
                  " recorded_value) VALUES (?, ?, ?)",
                  (log_id, p_name, val),
              )

            conn.commit()
            st.success("گزارش با موفقیت ثبت شد!")

      conn.close()

  # -------------------------------------------------------------
  # ۲. مدیریت دستگاه‌ها و پارامترها (مخصوص مدیر و کارشناس)
  # -------------------------------------------------------------
  elif selected_menu == "مدیریت دستگاه‌ها و پارامترها":
    st.title("⚙️ مدیریت دستگاه‌ها، موقعیت‌ها و پارامترهای پویا")

    if role not in ["مدیر سیستم", "کارشناس"]:
      st.error("شما دسترسی لازم به این بخش را ندارید.")
    else:
      tab1, tab2 = st.tabs(
          ["افزودن دستگاه و پارامتر جدید", "لیست و ویرایش دستگاه‌ها"]
      )

      with tab1:
        with st.form("new_device_form"):
          d_name = st.text_input("نام دستگاه جدید")
          d_location = st.text_input("محل قرارگیری (Location)")

          st.markdown("---")
          st.markdown("#### تعریف پارامترهای سفارشی (مقادیر پیش‌فرض اختیاری)")

          p1_name = st.text_input("نام پارامتر ۱ (مثلاً CO2 یا Shaking)")
          p1_def = st.text_input("مقدار پیش‌فرض پارامتر ۱ (اختیاری)")

          p2_name = st.text_input("نام پارامتر ۲ (اختیاری)")
          p2_def = st.text_input("مقدار پیش‌فرض پارامتر ۲ (اختیاری)")

          submit_dev = st.form_submit_button("ایجاد دستگاه و پارامترها")

          if submit_dev and d_name:
            conn = get_connection()
            cursor = conn.cursor()
            try:
              cursor.execute(
                  "INSERT INTO devices (name, location) VALUES (?, ?)",
                  (d_name, d_location),
              )
              dev_id = cursor.lastrowid

              if p1_name:
                cursor.execute(
                    "INSERT INTO device_parameters (device_id, param_name,"
                    " default_value) VALUES (?, ?, ?)",
                    (dev_id, p1_name, p1_def),
                )
              if p2_name:
                cursor.execute(
                    "INSERT INTO device_parameters (device_id, param_name,"
                    " default_value) VALUES (?, ?, ?)",
                    (dev_id, p2_name, p2_def),
                )

              # ثبت در ممیزی
              cursor.execute(
                  "INSERT INTO audit_logs (username, action, timestamp) VALUES"
                  " (?, ?, ?)",
                  (
                      username,
                      f"افزودن دستگاه {d_name}",
                      str(jdatetime.datetime.now()),
                  ),
              )

              conn.commit()
              st.success(
                  "دستگاه و پارامترهای آن با موفقیت ثبت شد!"
              )
            except Exception as e:
              st.error(f"خطا در ثبت دستگاه (احتمالاً نام تکراری است): {e}")
            finally:
              conn.close()

      with tab2:
        conn = get_connection()
        devices_df = pd.read_sql("SELECT * FROM devices", conn)
        conn.close()
        st.dataframe(devices_df)

  # -------------------------------------------------------------
  # ۳. مدیریت کاربران (مخصوص مدیر سیستم)
  # -------------------------------------------------------------
  elif selected_menu == "مدیریت کاربران":
    st.title("👥 مدیریت کاربران و سطوح دسترسی")

    if role != "مدیر سیستم":
      st.error("فقط مدیر سیستم به این بخش دسترسی دارد.")
    else:
      conn = get_connection()
      users_df = pd.read_sql("SELECT id, username, role, status FROM users", conn)
      conn.close()
      st.dataframe(users_df)

  # -------------------------------------------------------------
  # ۴. گزارشات و ممیزی (قابل مشاهده برای همه با سطوح مختلف)
  # -------------------------------------------------------------
  elif selected_menu in ["گزارشات و ممیزی", "مشاهده دستگاه‌ها و پارامترها"]:
    st.title("📊 گزارشات ثبت‌شده و ممیزی سیستم (Audit Trail)")

    conn = get_connection()
    logs_df = pd.read_sql(
        """
        SELECT logs.id, devices.name AS device_name, logs.username, logs.jalali_date, logs.has_warning 
        FROM logs 
        JOIN devices ON logs.device_id = devices.id
    """,
        conn,
    )
    conn.close()

    if logs_df.empty:
      st.info("هیچ گزارشی تاکنون ثبت نشده است.")
    else:
      st.dataframe(logs_df)

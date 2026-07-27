from datetime import datetime
import sqlite3
import jdatetime
import pandas as pd
import streamlit as st

# --- تنظیمات صفحه و ظاهر (UI) ---
st.set_page_config(
    page_title="سیستم لاگ‌بوک آزمایشگاهی", page_icon="🧪", layout="wide"
)

# --- تنظیمات دیتابیس SQLite ---
DB_NAME = "lab_logbook.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

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

  cursor.execute("SELECT * FROM users WHERE username = 'admin'")
  if not cursor.fetchone():
    cursor.execute(
        "INSERT INTO users VALUES ('admin', 'admin123', 'مدیر سیستم (ادمین)')"
    )

  conn.commit()
  conn.close()


init_db()


def log_audit(username, action):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  now_shamsi = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
  cursor.execute(
      "INSERT INTO audit_logs (username, action, datetime_shamsi) VALUES (?, ?,"
      " ?)",
      (username, action, now_shamsi),
  )
  conn.commit()
  conn.close()


# --- مدیریت نشست (Session) ---
if "user" not in st.session_state:
  st.session_state["user"] = None
  st.session_state["role"] = None

# --- صفحه ورود ---
if not st.session_state["user"]:
  st.title("🔐 ورود به سیستم لاگ‌بوک آزمایشگاهی")
  col1, col2 = st.columns(2)
  with col1:
    username = st.text_input("نام کاربری")
    password = st.text_input("رمز عبور", type="password")

    if st.button("ورود به سیستم", use_container_width=True):
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT role FROM users WHERE username = ? AND password = ?",
          (username, password),
      )
      res = cursor.fetchone()
      conn.close()

      if res:
        st.session_state["user"] = username
        st.session_state["role"] = res[0]
        log_audit(username, "ورود به سیستم")
        st.rerun()
      else:
        st.error("نام کاربری یا رمز عبور اشتباه است.")
  st.stop()

# --- نوار کناری (Sidebar) ---
st.sidebar.markdown(f"### 👤 کاربر: {st.session_state['user']}")
st.sidebar.markdown(f"📌 **نقش:** `{st.session_state['role']}`")
st.sidebar.markdown("---")

if st.sidebar.button("🚪 خروج از حساب", use_container_width=True):
  log_audit(st.session_state["user"], "خروج از سیستم")
  st.session_state["user"] = None
  st.session_state["role"] = None
  st.rerun()

st.sidebar.markdown("### 🗂️ منوی اصلی سامانه")
menu = st.sidebar.radio(
    "انتخاب کنید:",
    [
        "📝 ثبت گزارش جدید (لاگ‌بوک)",
        "🖥️ مشاهده دستگاه‌ها و وضعیت",
        "⚙️ مدیریت دستگاه‌ها (ادمین)",
        "📍 مدیریت محل‌های استقرار (ادمین)",
        "👨‍🔬 مدیریت کارشناسان (ادمین)",
        "👥 مدیریت کاربران (ادمین)",
        "📊 گزارشات و قابلیت پرینت",
    ],
)

role = st.session_state["role"]

# --- بخش ۱: ثبت گزارش جدید ---
if menu == "📝 ثبت گزارش جدید (لاگ‌بوک)":
  st.header("📝 ثبت گزارش / وضعیت جدید دستگاه")

  conn = sqlite3.connect(DB_NAME)
  devices_df = pd.read_sql("SELECT * FROM devices", conn)
  conn.close()

  if devices_df.empty:
    st.warning("ابتدا باید حداقل یک دستگاه توسط ادمین تعریف شود.")
  else:
    device_names = devices_df["name"].tolist()
    selected_device = st.selectbox("انتخاب دستگاه", device_names)
    dev_info = devices_df[devices_df["name"] == selected_device].iloc[0]

    st.info(
        f"📍 محل استقرار: {dev_info['location']} | 👨‍🔬 کارشناس مسئول:"
        f" {dev_info['expert']} | 🌡️ دمای پیش‌فرض: {dev_info['default_temp']}°C"
    )

    with st.form("log_form"):
      reporter = st.text_input(
          "نام فرد گزارش‌دهنده", value=st.session_state["user"]
      )
      recorded_temp = st.number_input(
          "دمای اندازه‌گیری شده فعلی (°C)",
          value=float(dev_info["default_temp"]),
      )
      recorded_param = st.text_input(
          "وضعیت پارامتر خاص", value=str(dev_info["default_param"])
      )
      description = st.text_area("توضیحات / شرح وضعیت")
      is_broken = st.checkbox("⚠️ اعلام خرابی دستگاه")

      submit_log = st.form_submit_button("ثبت گزارش نهایی")

      if submit_log:
        is_warning = 0
        warning_messages = []
        if recorded_temp != dev_info["default_temp"]:
          is_warning = 1
          warning_messages.append(
              f"مغایرت دما! (مقدار ثبت‌شده: {recorded_temp}, مقدار پیش‌فرض:"
              f" {dev_info['default_temp']})"
          )

        now_shamsi = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO logs (device_name, reporter, datetime_shamsi, temp_recorded, param_recorded, is_warning, description, is_broken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                selected_device,
                reporter,
                now_shamsi,
                recorded_temp,
                recorded_param,
                is_warning,
                description,
                1 if is_broken else 0,
            ),
        )

        if is_broken:
          cursor.execute(
              "UPDATE devices SET status = 'خراب' WHERE name = ?",
              (selected_device,),
          )

        conn.commit()
        conn.close()

        log_audit(
            st.session_state["user"], f"ثبت گزارش برای دستگاه {selected_device}"
        )

        if warning_messages:
          st.warning("⚠️ اخطار: " + " | ".join(warning_messages))
        st.success("گزارش با موفقیت در تاریخ شمسی ثبت شد.")

# --- بخش ۲: مشاهده دستگاه‌ها و وضعیت ---
elif menu == "🖥️ مشاهده دستگاه‌ها و وضعیت":
  st.header("🖥️ لیست دستگاه‌ها، اعتبار کالیبراسیون و وضعیت")
  conn = sqlite3.connect(DB_NAME)
  devices_df = pd.read_sql("SELECT * FROM devices", conn)
  conn.close()
  if devices_df.empty:
    st.info("هیچ دستگاهی ثبت نشده است.")
  else:
    st.dataframe(devices_df, use_container_width=True)

# --- بخش ۳: مدیریت دستگاه‌ها (ادمین) ---
elif menu == "⚙️ مدیریت دستگاه‌ها (ادمین)":
  if role != "مدیر سیستم (ادمین)":
    st.error("شما به این بخش دسترسی ندارید.")
  else:
    st.header("⚙️ مدیریت دستگاه‌ها (افزودن، ویرایش و حذف)")
    conn = sqlite3.connect(DB_NAME)
    experts_df = pd.read_sql("SELECT name FROM experts", conn)
    locations_df = pd.read_sql("SELECT name FROM locations", conn)
    devices_df = pd.read_sql("SELECT * FROM devices", conn)
    conn.close()

    expert_list = experts_df["name"].tolist() if not experts_df.empty else []
    location_list = locations_df["name"].tolist() if not locations_df.empty else []

    tab1, tab2, tab3 = st.tabs(
        ["افزودن دستگاه", "ویرایش دستگاه", "حذف دستگاه"]
    )

    with tab1:
      if not expert_list or not location_list:
        st.warning(
            "ابتدا باید حداقل یک 'محل استقرار' و یک 'کارشناس مسئول' تعریف کنید."
        )
      else:
        with st.form("add_device_form"):
          d_name = st.text_input("نام دستگاه")
          d_loc = st.selectbox("محل استقرار", location_list)
          d_expert = st.selectbox("کارشناس مسئول", expert_list)
          d_temp = st.number_input("دمای پیش‌فرض (°C)", value=25.0)
          d_param = st.text_input("سایر پارامترهای پیش‌فرض")
          d_cal = st.text_input("اعتبار کالیبراسیون (مثلا 1403/12/10)")
          submit_add = st.form_submit_button("ثبت دستگاه جدید")

          if submit_add and d_name:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                            INSERT INTO devices (name, location, expert, default_temp, default_param, calibration_date, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'سالم')
                        """,
                (d_name, d_loc, d_expert, d_temp, d_param, d_cal),
            )
            conn.commit()
            conn.close()
            log_audit(st.session_state["user"], f"افزودن دستگاه {d_name}")
            st.success("دستگاه با موفقیت افزوده شد.")
            st.rerun()

    with tab2:
      if devices_df.empty:
        st.info("دستگاهی برای ویرایش وجود ندارد.")
      else:
        selected_dev_id = st.selectbox(
            "انتخاب دستگاه جهت ویرایش",
            devices_df["id"],
            format_func=lambda x: devices_df[devices_df["id"] == x][
                "name"
            ].values[0],
        )
        dev_row = devices_df[devices_df["id"] == selected_dev_id].iloc[0]

        with st.form("edit_device_form"):
          e_name = st.text_input("نام دستگاه", value=dev_row["name"])
          e_loc = st.selectbox(
              "محل استقرار",
              location_list,
              index=(
                  location_list.index(dev_row["location"])
                  if dev_row["location"] in location_list
                  else 0
              ),
          )
          e_expert = st.selectbox(
              "کارشناس مسئول",
              expert_list,
              index=(
                  expert_list.index(dev_row["expert"])
                  if dev_row["expert"] in expert_list
                  else 0
              ),
          )
          e_temp = st.number_input(
              "دمای پیش‌فرض", value=float(dev_row["default_temp"])
          )
          e_param = st.text_input(
              "پارامتر پیش‌فرض", value=str(dev_row["default_param"])
          )
          e_cal = st.text_input(
              "اعتبار کالیبراسیون", value=str(dev_row["calibration_date"])
          )
          e_status = st.selectbox(
              "وضعیت دستگاه",
              ["سالم", "خراب", "در دست تعمیر"],
              index=["سالم", "خراب", "در دست تعمیر"].index(dev_row["status"]),
          )

          submit_edit = st.form_submit_button("ذخیره تغییرات دستگاه")

          if submit_edit:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                            UPDATE devices SET name=?, location=?, expert=?, default_temp=?, default_param=?, calibration_date=?, status=?
                            WHERE id=?
                        """,
                (
                    e_name,
                    e_loc,
                    e_expert,
                    e_temp,
                    e_param,
                    e_cal,
                    e_status,
                    selected_dev_id,
                ),
            )
            conn.commit()
            conn.close()
            log_audit(st.session_state["user"], f"ویرایش دستگاه {e_name}")
            st.success("اطلاعات دستگاه به‌روزرسانی شد.")
            st.rerun()

    with tab3:
      if devices_df.empty:
        st.info("دستگاهی برای حذف وجود ندارد.")
      else:
        del_dev_id = st.selectbox(
            "انتخاب دستگاه جهت حذف",
            devices_df["id"],
            format_func=lambda x: devices_df[devices_df["id"] == x][
                "name"
            ].values[0],
            key="del_dev_box",
        )
        if st.button("حذف دستگاه انتخاب‌شده"):
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute("DELETE FROM devices WHERE id = ?", (del_dev_id,))
          conn.commit()
          conn.close()
          log_audit(
              st.session_state["user"], f"حذف دستگاه با شناسه {del_dev_id}"
          )
          st.success("دستگاه با موفقیت حذف شد.")
          st.rerun()

# --- بخش ۴: مدیریت محل‌های استقرار (ادمین) ---
elif menu == "📍 مدیریت محل‌های استقرار (ادمین)":
  if role != "مدیر سیستم (ادمین)":
    st.error("شما به این بخش دسترسی ندارید.")
  else:
    st.header("📍 مدیریت محل‌های استقرار (افزودن، ویرایش و حذف)")
    conn = sqlite3.connect(DB_NAME)
    locs_df = pd.read_sql("SELECT * FROM locations", conn)
    conn.close()

    with st.form("add_loc_form"):
      new_loc = st.text_input("نام محل استقرار جدید (مثلا آزمایشگاه شیمی)")
      sub_loc = st.form_submit_button("افزودن محل استقرار")
      if sub_loc and new_loc:
        try:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute("INSERT INTO locations (name) VALUES (?)", (new_loc,))
          conn.commit()
          conn.close()
          log_audit(st.session_state["user"], f"افزودن محل استقرار {new_loc}")
          st.success("محل استقرار افزوده شد.")
          st.rerun()
        except:
          st.error("این محل استقرار از قبل وجود دارد.")

    st.markdown("### لیست و مدیریت محل‌های موجود")
    if locs_df.empty:
      st.info("محیطی ثبت نشده است.")
    else:
      for idx, row in locs_df.iterrows():
        with st.form(f"loc_form_{row['id']}"):
          col1, col2, col3 = st.columns([3, 1, 1])
          updated_loc_name = col1.text_input(
              "ویرایش نام", value=row["name"], label_visibility="collapsed"
          )
          up_btn = col2.form_submit_button("بروزرسانی")
          del_btn = col3.form_submit_button("حذف")

          if up_btn:
            try:
              conn = sqlite3.connect(DB_NAME)
              cursor = conn.cursor()
              cursor.execute(
                  "UPDATE locations SET name = ? WHERE id = ?",
                  (updated_loc_name, row["id"]),
              )
              conn.commit()
              conn.close()
              log_audit(
                  st.session_state["user"],
                  f"ویرایش محل استقرار به {updated_loc_name}",
              )
              st.success("بروز شد.")
              st.rerun()
            except:
              st.error("خطا در نام‌گذاری یا تکراری بودن.")

          if del_btn:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM locations WHERE id = ?", (row["id"],))
            conn.commit()
            conn.close()
            log_audit(
                st.session_state["user"], f"حذف محل استقرار id:{row['id']}"
            )
            st.rerun()

# --- بخش ۵: مدیریت کارشناسان (ادمین) ---
elif menu == "👨‍🔬 مدیریت کارشناسان (ادمین)":
  if role != "مدیر سیستم (ادمین)":
    st.error("شما به این بخش دسترسی ندارید.")
  else:
    st.header("👨‍🔬 مدیریت کارشناسان مسئول (افزودن، ویرایش و حذف)")
    conn = sqlite3.connect(DB_NAME)
    experts_df = pd.read_sql("SELECT * FROM experts", conn)
    conn.close()

    with st.form("add_exp_form"):
      new_expert = st.text_input("نام کارشناس جدید")
      sub_exp = st.form_submit_button("افزودن کارشناس")
      if sub_exp and new_expert:
        try:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute("INSERT INTO experts (name) VALUES (?)", (new_expert,))
          conn.commit()
          conn.close()
          log_audit(st.session_state["user"], f"افزودن کارشناس {new_expert}")
          st.success("کارشناس افزوده شد.")
          st.rerun()
        except:
          st.error("این کارشناس از قبل وجود دارد.")

    st.markdown("### لیست و مدیریت کارشناسان موجود")
    if experts_df.empty:
      st.info("کارشناسی ثبت نشده است.")
    else:
      for idx, row in experts_df.iterrows():
        with st.form(f"exp_form_{row['id']}"):
          col1, col2, col3 = st.columns([3, 1, 1])
          updated_exp_name = col1.text_input(
              "ویرایش نام", value=row["name"], label_visibility="collapsed"
          )
          up_exp_btn = col2.form_submit_button("بروزرسانی")
          del_exp_btn = col3.form_submit_button("حذف")

          if up_exp_btn:
            try:
              conn = sqlite3.connect(DB_NAME)
              cursor = conn.cursor()
              cursor.execute(
                  "UPDATE experts SET name = ? WHERE id = ?",
                  (updated_exp_name, row["id"]),
              )
              conn.commit()
              conn.close()
              log_audit(
                  st.session_state["user"],
                  f"ویرایش کارشناس به {updated_exp_name}",
              )
              st.success("بروز شد.")
              st.rerun()
            except:
              st.error("خطا در بروزرسانی نام کارشناس.")

          if del_exp_btn:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM experts WHERE id = ?", (row["id"],))
            conn.commit()
            conn.close()
            log_audit(st.session_state["user"], f"حذف کارشناس id:{row['id']}")
            st.rerun()

# --- بخش ۶: مدیریت کاربران (ادمین) ---
elif menu == "👥 مدیریت کاربران (ادمین)":
  if role != "مدیر سیستم (ادمین)":
    st.error("شما دسترسی ندارید.")
  else:
    st.header("👥 کنترل دسترسی و کاربران سیستم")

    with st.form("add_user_form"):
      u_name = st.text_input("نام کاربری جدید")
      u_pass = st.text_input("رمز عبور", type="password")
      u_role = st.selectbox(
          "سطح دسترسی",
          [
              "مدیر سیستم (ادمین)",
              "کارشناس گزارش‌دهنده (ریپورت)",
              "مشاهده‌کننده",
          ],
      )
      sub_user = st.form_submit_button("ایجاد کاربر جدید")

      if sub_user and u_name and u_pass:
        try:
          conn = sqlite3.connect(DB_NAME)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (u_name, u_pass, u_role),
          )
          conn.commit()
          conn.close()
          log_audit(st.session_state["user"], f"ایجاد کاربر جدید {u_name}")
          st.success("کاربر با موفقیت ایجاد شد.")
          st.rerun()
        except sqlite3.IntegrityError:
          st.error("خطا: این نام کاربری قبلاً ثبت شده است.")

    st.subheader("لیست کاربران فعلی سیستم")
    conn = sqlite3.connect(DB_NAME)
    users_df = pd.read_sql("SELECT username, role FROM users", conn)
    conn.close()
    st.dataframe(users_df, use_container_width=True)

# --- بخش ۷: گزارشات و قابلیت پرینت بر اساس فیلتر ---
elif menu == "📊 گزارشات و قابلیت پرینت":
  if role not in ["مدیر سیستم (ادمین)", "کارشناس گزارش‌دهنده (ریپورت)"]:
    st.error("شما به این بخش دسترسی ندارید.")
  else:
    st.header("📊 گزارشات لاگ‌بوک و چاپ بر اساس فیلتر")

    conn = sqlite3.connect(DB_NAME)
    logs_df = pd.read_sql("SELECT * FROM logs", conn)
    devices_df = pd.read_sql("SELECT name FROM devices", conn)
    conn.close()

    if logs_df.empty:
      st.info("هیچ گزارشی برای فیلتر و پرینت وجود ندارد.")
    else:
      st.subheader("🔍 فیلتر پیشرفته گزارش‌ها")
      col1, col2, col3 = st.columns(3)

      device_filter_options = ["همه دستگاه‌ها"] + (
          devices_df["name"].tolist() if not devices_df.empty else []
      )
      selected_device_filter = col1.selectbox(
          "فیلتر بر اساس دستگاه", device_filter_options
      )

      warning_filter_options = ["همه", "فقط دارای اخطار (مغایرت)", "عادی"]
      selected_warning_filter = col2.selectbox(
          "فیلتر بر اساس وضعیت اخطار", warning_filter_options
      )

      broken_filter_options = ["همه", "فقط اعلام خرابی‌شده"]
      selected_broken_filter = col3.selectbox(
          "فیلتر بر اساس خرابی", broken_filter_options
      )

      filtered_df = logs_df.copy()
      if selected_device_filter != "همه دستگاه‌ها":
        filtered_df = filtered_df[
            filtered_df["device_name"] == selected_device_filter
        ]

      if selected_warning_filter == "فقط دارای اخطار (مغایرت)":
        filtered_df = filtered_df[filtered_df["is_warning"] == 1]
      elif selected_warning_filter == "عادی":
        filtered_df = filtered_df[filtered_df["is_warning"] == 0]

      if selected_broken_filter == "فقط اعلام خرابی‌شده":
        filtered_df = filtered_df[filtered_df["is_broken"] == 1]

      st.markdown(
          f"**تعداد نتایج یافت شده:** {len(filtered_df)} مورد گزارش"
      )
      st.dataframe(filtered_df, use_container_width=True)

      st.markdown("---")
      st.subheader("🖨️ خروجی و آماده‌سازی برای پرینت")

      if st.button("🖨️ ایجاد فایل HTML نسخه قابل چاپ"):
        html_content = f"""
                <html dir="rtl">
                <head>
                    <title>گزارش لاگ‌بوک آزمایشگاه</title>
                    <style>
                        body {{ font-family: Tahoma, sans-serif; direction: rtl; padding: 20px; }}
                        h2 {{ text-align: center; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; font-size: 12px; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h2>گزارش رسمی دستگاه‌های آزمایشگاهی</h2>
                    <p>تاریخ تهیه گزارش: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</p>
                    <p>فیلتر اعمال شده: دستگاه: {selected_device_filter} | اخطار: {selected_warning_filter}</p>
                    {filtered_df.to_html(index=False)}
                    <script>
                        window.print();
                    </script>
                </body>
                </html>
                """
        st.download_button(
            label="📥 دانلود فایل HTML جهت چاپ مستقیم",
            data=html_content,
            file_name="lab_report.html",
            mime="text/html",
        )

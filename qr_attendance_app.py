import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import os
import time
import threading

# -------- CONFIGURATION --------
# To make QR codes point to your deployed app, set an environment variable named "BASE_URL".
# On Streamlit Cloud you can set it in "Advanced settings" -> "Environment variables".
# Example: BASE_URL = "https://attendance-nfsu.streamlit.app"
BASE_URL = os.environ.get("BASE_URL", "https://REPLACE_WITH_YOUR_STREAMLIT_APP_URL")

EXCEL_FILE = "attendance.xlsx"
QR_CHANGE_INTERVAL_SECONDS = 5 * 60  # 5 minutes

# --------- HELPERS ----------
def get_qr_key(now=None):
    if now is None:
        now = datetime.now()
    slot_minute = (now.minute // 5) * 5
    slot = now.replace(minute=slot_minute, second=0, microsecond=0)
    return slot.strftime("%Y%m%d%H%M")

def generate_qr_image(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def save_attendance(name, email):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"Name": name.strip(), "Email": email.strip(), "Timestamp": timestamp}
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(EXCEL_FILE, index=False)

# --------- UI ----------
st.set_page_config(page_title="QR Attendance Marker", page_icon="🎯", layout="centered")
st.title("📋 QR Attendance Marker")

st.write("This app uses a time-based QR key (changes every 5 minutes).")
st.write("⚠️ Before deploying to Streamlit Cloud set the `BASE_URL` environment variable to your app URL.")

# Admin column: display QR and next refresh countdown
col1, col2 = st.columns([2,3])

with col1:
    st.subheader("🧾 Admin — Current QR")
    # compute current key & data
    current_key = get_qr_key()
    qr_url = f"{BASE_URL}?key={current_key}"
    buf = generate_qr_image(qr_url)
    st.image(buf, caption=f"Scan this QR (valid for the current 5-min slot: {current_key})", use_column_width=True)
    st.write("QR target URL:")
    st.code(qr_url, language="text")
    st.caption("Replace BASE_URL in Settings if you see the placeholder URL above.")

    # show countdown to next slot
    now = datetime.now()
    next_slot_minute = ((now.minute // 5) + 1) * 5
    if next_slot_minute >= 60:
        next_hour = now.replace(hour=(now.hour+1)%24, minute=0, second=0, microsecond=0)
        next_slot = next_hour
    else:
        next_slot = now.replace(minute=next_slot_minute, second=0, microsecond=0)
    secs_left = int((next_slot - now).total_seconds())
    st.write(f"Time until QR refresh: **{secs_left} seconds**")

with col2:
    st.subheader("🧍 Mark Your Attendance")
    query_params = st.experimental_get_query_params()
    key = query_params.get("key", [None])[0]

    if key is None:
        st.info("Scan the QR code shown on the admin screen. The form will accept the current slot's key.")
    if key is not None and key != current_key:
        st.warning("The QR you used is not the latest one. Please scan the latest QR to mark attendance.")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    if st.button("✅ Mark Attendance"):
        if not name.strip() or not email.strip():
            st.error("Please enter both Name and Email.")
        else:
            # basic duplicate prevention: same email + same day
            ok_to_save = True
            if os.path.exists(EXCEL_FILE):
                df_old = pd.read_excel(EXCEL_FILE, parse_dates=["Timestamp"])
                if not df_old.empty:
                    today = datetime.now().date()
                    same_day = df_old[
                        (df_old["Email"].astype(str).str.lower() == email.strip().lower()) &
                        (df_old["Timestamp"].dt.date == today)
                    ]
                    if not same_day.empty:
                        ok_to_save = False
                        st.warning("It looks like this email already marked attendance today.")
            if ok_to_save:
                save_attendance(name, email)
                st.success(f"Attendance marked for {name} at {datetime.now().strftime('%I:%M %p')}")
                st.experimental_rerun()

st.divider()
with st.expander("📊 View Attendance Records (Admin)"):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        st.dataframe(df)
        st.download_button("Download Excel", df.to_excel(index=False), file_name=EXCEL_FILE, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No attendance records yet.")

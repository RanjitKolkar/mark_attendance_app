import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import os

# -------- CONFIGURATION --------
BASE_URL = "https://mark-attendance.streamlit.app"  # ✅ Your deployed app URL
EXCEL_FILE = "attendance.xlsx"
QR_CHANGE_INTERVAL_MINUTES = 5  # QR changes every 5 minutes

# --------- HELPERS ----------
def get_qr_key(now=None):
    if now is None:
        now = datetime.now()
    slot_minute = (now.minute // QR_CHANGE_INTERVAL_MINUTES) * QR_CHANGE_INTERVAL_MINUTES
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

st.write("Scan the QR code or use the link to mark your attendance.")

# --- Admin QR Code Section ---
st.subheader("🧾 Admin — Current QR Code")

current_key = get_qr_key()
qr_url = f"{BASE_URL}?key={current_key}"

# Generate and display QR
qr_buf = generate_qr_image(qr_url)
st.image(qr_buf, caption=f"Scan this QR (valid until next 5-min slot: {current_key})", use_container_width=True)

st.info("This QR code refreshes automatically every 5 minutes.")
st.write(f"QR Link: {qr_url}")

# --- User Attendance Form ---
st.divider()
st.subheader("🧍 Mark Your Attendance")

query_params = st.query_params
key = query_params.get("key", None)

if key == current_key:
    name = st.text_input("Full Name")
    email = st.text_input("Email")

    if st.button("✅ Mark Attendance"):
        if not name.strip() or not email.strip():
            st.error("Please fill in both Name and Email.")
        else:
            save_attendance(name, email)
            st.success(f"Attendance marked successfully for {name} at {datetime.now().strftime('%I:%M %p')}")
else:
    st.warning("⚠️ Please scan the latest QR code to access the attendance form.")

# --- View Attendance Records ---
with st.expander("📊 View Attendance Records (Admin Only)"):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        st.dataframe(df)

        # ✅ FIXED DOWNLOAD BUTTON
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 Download Attendance Excel",
            data=output.getvalue(),
            file_name="attendance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No attendance records yet.")

# QR Attendance App

Simple Streamlit app to mark attendance by scanning a QR code that changes every 5 minutes.

## Files
- `qr_attendance_app.py` - main Streamlit app
- `requirements.txt` - Python dependencies

## Deployment (Streamlit Cloud)
1. Create a new GitHub repository and push these files.
2. In Streamlit Cloud, connect the repository and deploy.
3. IMPORTANT: In your Streamlit app settings, set an environment variable named `BASE_URL` to your deployed app URL.  
   Example: `https://attendance-nfsu.streamlit.app`  
   (This allows the QR code to encode a full link to your deployed app.)

Alternatively, you can edit `qr_attendance_app.py` and replace the placeholder `BASE_URL` value directly.

## Usage
- Admin opens the app and displays the QR code.
- Students scan the QR (or open the link) and fill Name & Email to mark attendance.
- The QR key is valid for a 5-minute slot.

## Notes & Enhancements
- You can protect the admin view with authentication.
- You can switch storage from Excel to Google Sheets for persistence across deployments.
- The app writes `attendance.xlsx` into the app's working directory.


import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import cv2
import numpy as np
import os
from datetime import datetime

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    severity TEXT,
    description TEXT,
    image_path TEXT,
    date TEXT
)
''')

conn.commit()

# -----------------------------
# CREATE UPLOAD FOLDER
# -----------------------------
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Smart Road Damage Reporting", layout="wide")

st.title("🚧 Smart Road Damage Reporting System")

menu = ["Report Damage", "View Reports", "Analytics"]

choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# IMAGE ANALYSIS FUNCTION
# -----------------------------
def detect_damage(image):

    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray, 100, 200)

    edge_count = np.sum(edges > 0)

    # Basic logic
    if edge_count > 15000:
        severity = "High"
    elif edge_count > 8000:
        severity = "Medium"
    else:
        severity = "Low"

    return severity, edges

# -----------------------------
# REPORT DAMAGE PAGE
# -----------------------------
if choice == "Report Damage":

    st.header("📍 Report Road Damage")

    location = st.text_input("Enter Location")

    description = st.text_area("Damage Description")

    uploaded_file = st.file_uploader(
        "Upload Road Image",
        type=['jpg', 'png', 'jpeg']
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        severity, processed = detect_damage(image)

        st.subheader(f"⚠️ Predicted Severity: {severity}")

        st.image(processed, caption="Detected Damage Edges")

        if st.button("Submit Report"):

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            image_path = f"uploads/{timestamp}.jpg"

            image.save(image_path)

            c.execute('''
            INSERT INTO reports
            (location, severity, description, image_path, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                location,
                severity,
                description,
                image_path,
                str(datetime.now())
            ))

            conn.commit()

            st.success("✅ Report Submitted Successfully!")

# -----------------------------
# VIEW REPORTS PAGE
# -----------------------------
elif choice == "View Reports":

    st.header("📋 Damage Reports")

    df = pd.read_sql_query("SELECT * FROM reports", conn)

    if len(df) > 0:

        st.dataframe(df)

        for index, row in df.iterrows():

            st.subheader(f"Report ID: {row['id']}")

            st.write(f"📍 Location: {row['location']}")
            st.write(f"⚠️ Severity: {row['severity']}")
            st.write(f"📝 Description: {row['description']}")
            st.write(f"📅 Date: {row['date']}")

            image = Image.open(row['image_path'])

            st.image(image, width=400)

            st.markdown("---")

    else:
        st.info("No reports available.")

# -----------------------------
# ANALYTICS PAGE
# -----------------------------
elif choice == "Analytics":

    st.header("📊 Road Damage Analytics")

    df = pd.read_sql_query("SELECT * FROM reports", conn)

    if len(df) > 0:

        severity_count = df['severity'].value_counts()

        st.bar_chart(severity_count)

        st.subheader("Damage Severity Distribution")
        st.write(severity_count)

    else:
        st.warning("No data available.")

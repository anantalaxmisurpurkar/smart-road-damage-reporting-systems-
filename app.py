import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image, ImageFilter
import numpy as np
import os
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Smart Road Damage Reporting",
    layout="wide"
)

st.title("🚧 Smart Road Damage Reporting System")

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    severity TEXT,
    description TEXT,
    image_path TEXT,
    date TEXT
)
""")

conn.commit()

# -----------------------------
# CREATE UPLOAD FOLDER
# -----------------------------
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -----------------------------
# SIDEBAR MENU
# -----------------------------
menu = ["Report Damage", "View Reports", "Analytics"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# IMAGE ANALYSIS FUNCTION
# -----------------------------
def detect_damage(image):

    # Convert image to grayscale
    gray = image.convert("L")

    # Apply edge filter
    edges = gray.filter(ImageFilter.FIND_EDGES)

    # Convert to numpy array
    edge_array = np.array(edges)

    # Count strong edges
    edge_count = np.sum(edge_array > 50)

    # Severity prediction
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
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        # Open image safely
        image = Image.open(uploaded_file).convert("RGB")

        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True
        )

        # Detect damage
        severity, processed = detect_damage(image)

        st.subheader(f"⚠️ Predicted Severity: {severity}")

        st.image(
            processed,
            caption="Detected Damage Edges",
            use_container_width=True
        )

        if st.button("Submit Report"):

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            image_path = os.path.join(
                UPLOAD_FOLDER,
                f"{timestamp}.jpg"
            )

            # Save image
            image.save(image_path)

            # Insert into database
            c.execute("""
            INSERT INTO reports
            (location, severity, description, image_path, date)
            VALUES (?, ?, ?, ?, ?)
            """, (
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

    df = pd.read_sql_query(
        "SELECT * FROM reports",
        conn
    )

    if not df.empty:

        st.dataframe(df)

        for _, row in df.iterrows():

            st.subheader(f"Report ID: {row['id']}")

            st.write(f"📍 Location: {row['location']}")
            st.write(f"⚠️ Severity: {row['severity']}")
            st.write(f"📝 Description: {row['description']}")
            st.write(f"📅 Date: {row['date']}")

            # Check if image exists
            if os.path.exists(row["image_path"]):

                image = Image.open(row["image_path"])

                st.image(
                    image,
                    width=400
                )

            else:
                st.warning("Image file not found.")

            st.markdown("---")

    else:
        st.info("No reports available.")


# -----------------------------
# ANALYTICS PAGE
# -----------------------------
elif choice == "Analytics":

    st.header("📊 Road Damage Analytics")

    df = pd.read_sql_query(
        "SELECT * FROM reports",
        conn
    )

    if not df.empty:

        severity_count = df["severity"].value_counts()

        st.subheader("Damage Severity Distribution")

        st.bar_chart(severity_count)

        st.write(severity_count)

    else:
        st.warning("No data available.")
        import streamlit as st

# Page Title
st.title("🚧 Smart Road Damage Reporting System")

# Project Description
st.markdown("""
### About the Project

Our project reduces the problem of unreported road damages by providing an easy reporting and tracking system.

Users can:
- Upload road damage images
- Report potholes and cracks
- Track complaint status
- Help authorities repair roads faster

This system improves road safety and public transportation.
""")

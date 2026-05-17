import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
import base64
import plotly.express as px

st.set_page_config(page_title="MediTrack", page_icon="💊", layout="wide")
st.title("💊 MediTrack")
st.markdown("**Your personal medication manager** — inspired by Medisafe")

# Initialize session state
if 'medications' not in st.session_state:
    st.session_state.medications = []
if 'history' not in st.session_state:
    st.session_state.history = []

today = datetime.date.today()

# Sidebar
page = st.sidebar.selectbox("Menu", ["Dashboard", "Add Medication", "My Medications", "Reports"])

# ====================== ADD MEDICATION ======================
if page == "Add Medication":
    st.header("➕ Add New Medication")
    with st.form("add_med"):
        name = st.text_input("Medication Name *", placeholder="e.g. Lisinopril")
        dosage = st.text_input("Dosage & Instructions", placeholder="e.g. 10mg once daily")
        times = st.text_input("Take at (comma separated)", "08:00,20:00")
        notes = st.text_area("Additional Notes")
        
        if st.form_submit_button("Add Medication"):
            if name:
                med = {
                    "id": len(st.session_state.medications) + 1,
                    "name": name,
                    "dosage": dosage,
                    "times": [t.strip() for t in times.split(",") if t.strip()],
                    "notes": notes
                }
                st.session_state.medications.append(med)
                st.success(f"✅ {name} added successfully!")
            else:
                st.error("Medication name is required")

# ====================== DASHBOARD ======================
elif page == "Dashboard":
    st.header(f"📅 Today's Doses — {today.strftime('%B %d, %Y')}")
    
    if not st.session_state.medications:
        st.info("No medications yet. Add some from the menu 👆")
    else:
        for med in st.session_state.medications:
            st.subheader(f"💊 {med['name']}")
            st.caption(med['dosage'])
            cols = st.columns(len(med['times']))
            for idx, t in enumerate(med['times']):
                with cols[idx]:
                    if st.button(f"✅ Taken at {t}", key=f"taken_{med['id']}_{t}"):
                        st.session_state.history.append({
                            "date": today,
                            "med_name": med['name'],
                            "time": t,
                            "status": "Taken"
                        })
                        st.toast(f"Logged {med['name']} at {t}", icon="✅")

# ====================== MY MEDICATIONS ======================
elif page == "My Medications":
    st.header("📋 My Medications")
    if st.session_state.medications:
        for med in st.session_state.medications:
            with st.expander(f"💊 {med['name']} — {med['dosage']}"):
                st.write("**Times:**", ", ".join(med['times']))
                if med['notes']:
                    st.write("**Notes:**", med['notes'])
                if st.button("Remove", key=f"del_{med['id']}"):
                    st.session_state.medications = [m for m in st.session_state.medications if m['id'] != med['id']]
                    st.rerun()
    else:
        st.info("No medications added yet.")

# ====================== REPORTS ======================
elif page == "Reports":
    st.header("📊 Adherence Report")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        taken = len(df[df['status'] == "Taken"])
        total = len(df)
        adherence = (taken / total * 100) if total > 0 else 0
        
        col1, col2 = st.columns(2)
        col1.metric("Overall Adherence", f"{adherence:.1f}%")
        col2.metric("Total Doses Logged", total)
        
        fig = px.histogram(df, x="date", color="status", title="Doses Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No doses logged yet.")

    if st.button("📄 Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "MediTrack Medication Report", ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {today}", ln=1)
        pdf.ln(10)
        
        pdf.cell(0, 10, "Current Medications:", ln=1)
        for med in st.session_state.medications:
            pdf.cell(0, 8, f"• {med['name']} — {med['dosage']}", ln=1)
        
        pdf.output("MediTrack_Report.pdf")
        with open("MediTrack_Report.pdf", "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name="MediTrack_Report.pdf")

st.sidebar.caption("💊 MediTrack — Medisafe Inspired")

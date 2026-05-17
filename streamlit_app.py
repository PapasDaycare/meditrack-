import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
import base64

st.set_page_config(page_title="MediTrack", page_icon="💊", layout="wide")
st.title("💊 MediTrack")
st.markdown("**Your personal medication manager** — inspired by Medisafe")

# Session State
if 'medications' not in st.session_state:
    st.session_state.medications = []
if 'history' not in st.session_state:
    st.session_state.history = []

today = datetime.date.today()
page = st.sidebar.selectbox("Menu", ["Dashboard", "Add Medication", "My Medications", "Reports"])

# Add Medication (same as before)
if page == "Add Medication":
    st.header("➕ Add New Medication")
    with st.form("add_med"):
        name = st.text_input("Medication Name *")
        dosage = st.text_input("Dosage & Instructions", "e.g. 500 mg oral tablet")
        times = st.text_input("Times (comma separated)", "08:00,20:00")
        notes = st.text_area("Notes / Instructions")
        
        if st.form_submit_button("Add Medication"):
            if name:
                med = {
                    "id": len(st.session_state.medications) + 1,
                    "name": name.strip(),
                    "dosage": dosage.strip(),
                    "times": [t.strip() for t in times.split(",") if t.strip()],
                    "notes": notes.strip()
                }
                st.session_state.medications.append(med)
                st.success(f"✅ {name} added!")
                st.rerun()

# Dashboard (same)
elif page == "Dashboard":
    st.header(f"📅 Today's Doses — {today.strftime('%B %d, %Y')}")
    if not st.session_state.medications:
        st.info("No medications yet.")
    else:
        for med in st.session_state.medications:
            with st.container(border=True):
                st.subheader(f"💊 {med['name']}")
                st.caption(med['dosage'])
                if med.get('notes'): st.caption(med['notes'])
                cols = st.columns(len(med['times']))
                for idx, t in enumerate(med['times']):
                    with cols[idx]:
                        if st.button(f"✅ Taken at {t}", key=f"taken_{med['id']}_{t}"):
                            st.session_state.history.append({"date": today, "med_name": med['name'], "time": t, "status": "Taken"})
                            st.toast(f"Logged {med['name']} at {t}", icon="✅")

# My Medications with bulk delete (same)
elif page == "My Medications":
    st.header("📋 My Medications")
    if st.session_state.medications:
        selected_ids = []
        for med in st.session_state.medications:
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.write(f"**{med['name']}** — {med['dosage']}")
            with col2:
                if st.checkbox("Select", key=f"sel_{med['id']}"):
                    selected_ids.append(med['id'])
            with col3:
                if st.button("🗑️", key=f"del_{med['id']}"):
                    st.session_state.medications = [m for m in st.session_state.medications if m['id'] != med['id']]
                    st.rerun()
        if selected_ids and st.button("🗑️ Delete Selected", type="primary"):
            st.session_state.medications = [m for m in st.session_state.medications if m['id'] not in selected_ids]
            st.success(f"Deleted {len(selected_ids)} medication(s)")
            st.rerun()

# ====================== IMPROVED PRINTABLE REPORT ======================
elif page == "Reports":
    st.header("📄 Printable Medication Schedule")

    if st.button("📥 Generate Printable PDF Schedule", type="primary"):
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "MediTrack - Medication Schedule", ln=1, align="C")
                self.set_font("Arial", size=12)
                self.cell(0, 10, f"Generated on: {today.strftime('%B %d, %Y')}", ln=1, align="C")
                self.ln(10)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)

        if st.session_state.medications:
            for med in st.session_state.medications:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"💊 {med['name']}", ln=1)
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 8, f"Dosage: {med['dosage']}", ln=1)
                if med.get('notes'):
                    pdf.cell(0, 8, f"Notes: {med['notes']}", ln=1)
                
                pdf.cell(0, 8, "Schedule:", ln=1)
                for t in med['times']:
                    pdf.cell(0, 8, f"   • {t} — Take {med['dosage']}", ln=1)
                pdf.ln(8)
        else:
            pdf.cell(0, 10, "No medications added yet.", ln=1)

        pdf_bytes = pdf.output(dest="S").encode("latin1")
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="My_Medication_Schedule.pdf">📥 Download Printable Schedule PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.info("Tip: After downloading, open the PDF and print it (Ctrl+P). It works great for fridge, wallet, or caregiver use.")

st.sidebar.caption("💊 MediTrack v2 — Printable Schedule Ready")

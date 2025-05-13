
import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from PIL import Image

@st.cache_data
def load_data():
    return pd.read_excel("Unified_Food_Compatibility_Table_With_Resonance.xlsx")

st.set_page_config(page_title="Dr. Tabbal Resonance App", layout="wide")

# Create three columns to center logo, title, and chart
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

        logo = Image.open("dowsing_chart.jpg")
        st.image(logo, width=80)

        st.markdown("<h2>Dr. Mahmoud Tabbal</h2>", unsafe_allow_html=True)
        st.markdown("<h3>Diabetes Endocrine Center</h3>", unsafe_allow_html=True)

        dowsing_chart = Image.open("clinic_logo.jpg")
        st.image(dowsing_chart, width=500)

        st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading images: {e}")

st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)

st.sidebar.header("Patient Information")
patient_name = st.sidebar.text_input("Full Name")
patient_email = st.sidebar.text_input("Email (optional)")
test_date = st.sidebar.date_input("Date of Testing")

if "index" not in st.session_state:
    st.session_state.index = 0
if "data" not in st.session_state:
    st.session_state.data = load_data()

df = st.session_state.data
current = df.iloc[st.session_state.index]
st.subheader(f"Food Item: {current['Item']}")

st.markdown(f"**Category:** {current['Category']} | **Super Category:** {current['Super Category']}")
st.markdown(f"**Dosha:** {current['Dosha Compatibility']} | **Metabolic Type:** {current['Metabolic Typing Compatibility']} | **Glandular Type:** {current['Glandular Compatibility']}")

resonance = st.selectbox("Select Resonance Compatibility", ["", "Compatible", "Incompatible", "Limited", "Neutral"])

if st.button("Save and Next"):
    st.session_state.data.at[st.session_state.index, "Resonance Compatibility"] = resonance
    if st.session_state.index < len(st.session_state.data) - 1:
        st.session_state.index += 1
    else:
        st.success("✅ All items processed!")

with st.expander("📤 Generate PDF Report"):
    dosha = st.selectbox("Filter by Dosha", ["All", "Vata", "Pitta", "Kapha", "Tridoshic"])
    metabolic_filter = st.selectbox("Filter by Metabolic Type", ["All", "Fast Oxidizer", "Slow Oxidizer", "Mixed Oxidizer"])
    resonance_filter = st.selectbox("Filter by Resonance", ["Compatible", "Incompatible", "Limited", "Neutral"])

    filtered = st.session_state.data.copy()
    if dosha != "All":
        filtered = filtered[filtered["Dosha Compatibility"].str.contains(dosha, na=False)]
    if metabolic_filter != "All":
        filtered = filtered[filtered["Metabolic Typing Compatibility"] == metabolic_filter]
    if resonance_filter:
        filtered = filtered[filtered["Resonance Compatibility"] == resonance_filter]

    st.dataframe(filtered)

    def create_pdf(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Dr. Mahmoud Tabbal - Personalized Food Resonance Report", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(5)
        pdf.cell(0, 10, f"Patient Name: {patient_name}", ln=True)
        if patient_email:
            pdf.cell(0, 10, f"Email: {patient_email}", ln=True)
        pdf.cell(0, 10, f"Test Date: {test_date}", ln=True)
        pdf.ln(5)
        for _, row in data.iterrows():
            pdf.cell(0, 10, f"{row['Item']} ({row['Category']}) - Resonance: {row['Resonance Compatibility']}", ln=True)
        return pdf.output(dest='S').encode('latin1')

    if st.button("Download PDF Report"):
        pdf_bytes = create_pdf(filtered)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Resonance_Food_Report.pdf">📥 Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

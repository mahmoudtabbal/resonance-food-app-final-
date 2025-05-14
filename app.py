import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from PIL import Image
from datetime import datetime

@st.cache_data
def load_data():
    return pd.read_excel(open("Unified_Food_Compatibility_Table_With_Resonance.xlsx", "rb"))

def classify_resonance(score):
    if score <= 20:
        return "Harmful"
    elif score <= 40:
        return "Severely Incompatible"
    elif score <= 50:
        return "Moderately Incompatible"
    elif score <= 60:
        return "Mildly Incompatible"
    elif score <= 70:
        return "Neutral"
    elif score <= 80:
        return "Mildly Compatible"
    elif score <= 90:
        return "Highly Compatible"
    else:
        return "Necessary"

st.set_page_config(page_title="Dr. Tabbal Resonance App", layout="wide")

try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image(Image.open("clinic_logo.jpg"), width=80)
        st.markdown("<h2>Dr. Mahmoud Tabbal</h2>", unsafe_allow_html=True)
        st.markdown("<h3>Diabetes Endocrine Center</h3>", unsafe_allow_html=True)
        st.image(Image.open("dowsing_chart.jpg"), width=500)
        st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading images: {e}")

st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)

st.sidebar.header("Patient Information")
patient_name = st.sidebar.text_input("Full Name")
patient_email = st.sidebar.text_input("Email (optional)")
test_date = st.sidebar.date_input("Date of Testing", value=datetime.today())

if not patient_name:
    st.warning("Please enter patient name to begin.")
    st.stop()

# Session setup
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "index" not in st.session_state:
    st.session_state.index = 0
if "results" not in st.session_state:
    st.session_state.results = {}
if "all_patients" not in st.session_state:
    st.session_state.all_patients = []

df = st.session_state.data
i = st.session_state.index
current = df.iloc[i]

st.progress(int((i + 1) / len(df) * 100), text=f"{i + 1} of {len(df)} items reviewed")
st.subheader(f"Food Item: {current['Item']}")
st.markdown(f"**Category:** {current['Category']} | **Super Category:** {current['Super Category']}")
st.markdown(f"**Dosha:** {current['Dosha Compatibility']} | **Metabolic Type:** {current['Metabolic Typing Compatibility']} | **Glandular Type:** {current['Glandular Compatibility']}")

score = st.slider("Select Resonance Score (0–100)", 0, 100, key=f"score_{i}")
category = classify_resonance(score)
st.markdown(f"**Category Detected:** `{category}`")

if st.button("Save Compatibility"):
    st.session_state.results[i] = {
        "Patient Name": patient_name,
        "Email": patient_email,
        "Test Date": test_date,
        "Item": current["Item"],
        "Category": current["Category"],
        "Super Category": current["Super Category"],
        "Dosha Compatibility": current["Dosha Compatibility"],
        "Metabolic Typing Compatibility": current["Metabolic Typing Compatibility"],
        "Glandular Compatibility": current["Glandular Compatibility"],
        "Resonance Score": score,
        "Resonance Category": category,
    }
    st.success("Saved. Now click ➡️ Next Item.")

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Back"):
        if i > 0:
            st.session_state.index -= 1
with col2:
    if st.button("➡️ Next Item"):
        if i < len(df) - 1:
            st.session_state.index += 1
        else:
            st.success("✅ All items reviewed!")

# Export with Filters
with st.expander("📤 Export Patient Report with Filters"):
    session_data = pd.DataFrame.from_dict(st.session_state.results, orient="index")

    if not session_data.empty:
        # Filters
        dosha_filter = st.selectbox("Filter by Dosha", ["All"] + sorted(session_data["Dosha Compatibility"].dropna().unique()))
        metabolic_filter = st.selectbox("Filter by Metabolic Typing", ["All"] + sorted(session_data["Metabolic Typing Compatibility"].dropna().unique()))
        glandular_filter = st.selectbox("Filter by Glandular Compatibility", ["All"] + sorted(session_data["Glandular Compatibility"].dropna().unique()))
        resonance_filter = st.selectbox("Filter by Resonance Category", ["All"] + sorted(session_data["Resonance Category"].dropna().unique()))

        filtered = session_data.copy()
        if dosha_filter != "All":
            filtered = filtered[filtered["Dosha Compatibility"] == dosha_filter]
        if metabolic_filter != "All":
            filtered = filtered[filtered["Metabolic Typing Compatibility"] == metabolic_filter]
        if glandular_filter != "All":
            filtered = filtered[filtered["Glandular Compatibility"] == glandular_filter]
        if resonance_filter != "All":
            filtered = filtered[filtered["Resonance Category"] == resonance_filter]

        st.dataframe(filtered)

        def generate_pdf(data):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Dr. Mahmoud Tabbal - Food Resonance Report", ln=True, align="C")
            pdf.set_font("Arial", "", 11)
            pdf.ln(4)
            pdf.cell(0, 10, f"Patient: {patient_name}", ln=True)
            if patient_email:
                pdf.cell(0, 10, f"Email: {patient_email}", ln=True)
            pdf.cell(0, 10, f"Date: {test_date}", ln=True)
            pdf.ln(5)
            for _, row in data.iterrows():
                pdf.cell(0, 10, f"{row['Item']} ({row['Category']}) - Score: {row['Resonance Score']} - {row['Resonance Category']}", ln=True)
            return pdf.output(dest='S').encode('latin1')

        def convert_df_to_excel(df):
            import io
            from pandas import ExcelWriter
            output = io.BytesIO()
            with ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Resonance Data')
                
            return output.getvalue()

        if st.button("📄 Download PDF"):
            pdf_bytes = generate_pdf(filtered)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{patient_name}_Resonance_Report.pdf">📥 Click to Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        if st.button("📊 Download Excel"):
            excel_bytes = convert_df_to_excel(filtered)
            b64 = base64.b64encode(excel_bytes).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{patient_name}_Resonance_Report.xlsx">📥 Click to Download Excel</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Save current session permanently
        if st.button("🗂️ Save This Patient to History"):
            full_entry = filtered.copy()
            full_entry["Session Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.all_patients.append(full_entry)
            st.success("✔️ Patient session saved to history.")
    else:
        st.info("No results saved yet for this patient.")

# View All Patient History
if st.session_state.all_patients:
    st.markdown("---")
    st.markdown("## 🧾 Full Patient History")
    history_df = pd.concat(st.session_state.all_patients, ignore_index=True)
    st.dataframe(history_df)

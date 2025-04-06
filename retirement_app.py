import streamlit as st
from fpdf import FPDF
from tempfile import NamedTemporaryFile
import base64
from PIL import Image
import matplotlib.pyplot as plt

# Example Data (Replace with your actual data)
la_current_age = 45
la_retirement_age = 65
investment = 1000000
la_return = 0.07
withdrawal_rate = 0.05
monthly_income = 4166.67
longevity_text = "30 years"

# Example Graph (Replace with your actual graph)
fig_la, ax = plt.subplots()
ax.plot([1, 2, 3], [10, 20, 30])
ax.set_title("Living Annuity Projection")

# Load Logo
def load_logo():
    try:
        return Image.open("bhjcf-logo.png")
    except Exception as e:
        st.error(f"⚠️ Logo loading failed: {str(e)}")
        st.stop()

logo = load_logo()

# Display Logo and Company Name
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(f"""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <img src="data:image/png;base64,{base64.b64encode(open("bhjcf-logo.png", "rb").read()).decode()}" width="65" style='margin-right: 10px;'>
        <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
            BHJCF Studio
        </p>
    </div>
    """, unsafe_allow_html=True)

# Living Annuity PDF Preview
if st.button("📄 Generate Living Annuity PDF Report"):
    try:
        with NamedTemporaryFile(delete=False, suffix=".png") as tmp_graph:
            fig_la.savefig(tmp_graph.name, dpi=300)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Centered Logo & Company Name
            pdf.image("bhjcf-logo.png", x=(210-30)/2, y=10, w=30)
            pdf.set_y(40)
            pdf.cell(0, 10, "BHJCF Studio", ln=1, align='C')
            
            # Report Title
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 15, "Living Annuity Report", ln=1, align='C')
            pdf.ln(10)
            
            # Client Info
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Client: Juanita Moolman", ln=1)
            pdf.ln(5)
            
            # Data Table
            pdf.set_font("Arial", size=12)
            data = [
                ("Current Age", la_current_age),
                ("Retirement Age", la_retirement_age),
                ("Total Investment", f"R{investment:,.2f}"),
                ("Annual Return", f"{la_return*100:.1f}%"),
                ("Withdrawal Rate", f"{withdrawal_rate*100:.1f}%"),
                ("Monthly Income", f"R{monthly_income:,.2f}"),
                ("Projection Outlook", longevity_text)
            ]
            
            for label, value in data:
                pdf.cell(90, 10, label, border=0)
                pdf.cell(0, 10, str(value), ln=1)
            
            # Add graph
            pdf.image(tmp_graph.name, x=10, y=140, w=190)
            
            # Save PDF
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                
                # Preview
                with open(tmp_pdf.name, "rb") as f:
                    encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_preview = f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="600px"></iframe>'
                    st.markdown(pdf_preview, unsafe_allow_html=True)
                    
                # Download
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f.read(),
                        file_name="Juanita_Living_Annuity_Report.pdf",
                        mime="application/pdf"
                    )
    except Exception as e:
        st.error(f"❌ PDF generation failed: {str(e)}")



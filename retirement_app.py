# Add these imports at the top
import base64
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')  # CRITICAL FOR STREAMLIT CLOUD
import streamlit as st
from numpy_financial import fv, pmt
import matplotlib.pyplot as plt
from PIL import Image
from fpdf import FPDF
import os

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(layout="wide")

# Custom CSS for colors
st.markdown("""<style>
.stSlider>div>div>div>div { background: #7FFF00 !important; }
.custom-r { 
    color: #FF5E00 !important; 
    font-size: 32px; 
    font-weight: 900;
    display: inline-block;
    margin: 0 2px;
}
.logo-column { 
    padding-right: 0px !important;
    display: flex;
    align-items: center;
}
.company-name { 
    margin-left: -25px !important;
    padding-left: 0 !important;
}
</style>""", unsafe_allow_html=True)

# ======================
# BRANDING (FIXED)
# ======================
def load_logo():
    try:
        return Image.open("bhjcf-logo.png")
    except Exception as e:
        st.error(f"⚠️ Logo loading failed: {str(e)}")
        st.stop()

logo = load_logo()

st.markdown("""
<h1 style='text-align: center; margin-bottom: 20px;'>
    <span class="custom-r">R</span>
    <span style='font-size: 32px; color: #00BFFF;'>Retirement Cash Flow Calculator</span>
</h1>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    container = st.container()
    cols = container.columns([2, 7])
    with cols[0]:
        st.image(logo, width=65)
    with cols[1]:
        st.markdown("""
        <div class="company-name" style='height: 70px; display: flex; align-items: center;'>
            <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
                BHJCF Studio
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<p style="color:#FF0000; font-size:20px; text-align: center;">Client: Juanita Moolman</p>', unsafe_allow_html=True)

# ======================
# CALCULATOR TABS 
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

# ======================
# RETIREMENT CASH FLOW TAB
# ======================
with tab1:
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    years_to_retirement = retirement_age - current_age
    future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)
    years_in_retirement = life_expectancy - retirement_age

    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    withdrawals = [future_value * withdrawal_rate * (1 + annual_return) ** year 
                  for year in range(years_in_retirement)]

    st.subheader("Your Spending Plan")
    st.markdown(f"""
    <div style='margin: 20px 0;'>
        <span class="custom-r">R</span> 
        <span style='font-size: 18px;'>At retirement value: </span>
        <span style='color: #00BFFF; font-weight: bold;'>R{future_value:,.2f}</span>
    </div>
    <div style='margin: 20px 0;'>
        <span class="custom-r">R</span> 
        <span style='font-size: 18px;'>Annual withdrawal: </span>
        <span style='color: #FF5E00; font-weight: bold;'>R{withdrawals[0]:,.2f}</span>
        <span style='font-size: 14px; color: #666;'>(3% annual growth)</span>
    </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF')
    ax.set_xlabel("Age", color='#228B22')
    ax.set_ylabel("Annual Income (R)", color='#FF5E00')
    st.pyplot(fig)
    plt.close()

    # Generate PDF with preview
    if st.button("📄 Generate PDF Report"):
        try:
            # Save graph to a temporary file
            with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                fig.savefig(tmpfile.name, dpi=300)

            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            if os.path.exists("bhjcf-logo.png"):
                pdf.image("bhjcf-logo.png", x=10, y=8, w=30)
            
            pdf.cell(200, 10, txt="Retirement Cash Flow Report", ln=True, align="C")
            pdf.ln(15)
            pdf.cell(0, 10, txt=f"Client: Juanita Moolman", ln=True)
            pdf.cell(0, 10, txt=f"Current Age: {current_age}", ln=True)
            pdf.cell(0, 10, txt=f"Retirement Age: {retirement_age}", ln=True)
            pdf.cell(0, 10, txt=f"Current Savings: R{retirement_savings:,.2f}", ln=True)
            pdf.cell(0, 10, txt=f"Annual Return: {annual_return*100:.1f}%", ln=True)
            pdf.cell(0, 10, txt=f"Life Expectancy: {life_expectancy}", ln=True)
            pdf.cell(0, 10, txt=f"Withdrawal Rate: {withdrawal_rate*100:.1f}%", ln=True)
            pdf.ln(10)
            pdf.cell(0, 10, txt=f"Projected Retirement Value: R{future_value:,.2f}", ln=True)
            pdf.cell(0, 10, txt=f"First Year Withdrawal: R{withdrawals[0]:,.2f}", ln=True)
            
            # Add graph to PDF
            pdf.image(tmpfile.name, x=10, y=100, w=190)
            pdf.output("retirement_report.pdf")
            
            # Preview PDF and provide download
            with open("retirement_report.pdf", "rb") as f:
                encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_preview = f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="500px"></iframe>'
                st.markdown(pdf_preview, unsafe_allow_html=True)
                
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f.read(),
                    file_name="Juanita_Retirement_Report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")

# ======================
# LIVING ANNUITY TAB
# ======================
with tab2:
    # Living Annuity Calculator Code...
    # Add Living Annuity PDF button after graph code
    if st.button("📄 Generate Living Annuity PDF Report"):
        try:
            # Save the graph image
            plt.savefig("living_annuity_projection.png", dpi=300)
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            if os.path.exists("bhjcf-logo.png"):
                pdf.image("bhjcf-logo.png", x=10, y=8, w=30)
            
            pdf.cell(200, 10, txt="Living Annuity Report", ln=True, align="C")
            pdf.ln(15)
            pdf.cell(0, 10, txt=f"Client: Juanita Moolman", ln=True)
            pdf.cell(0, 10, txt=f"Current Age: {la_current_age}", ln=True)
            pdf.cell(0, 10, txt=f"Retirement Age: {la_retirement_age}", ln=True)
            pdf.cell(0, 10, txt=f"Total Investment: R{investment:,.2f}", ln=True)
            pdf.cell(0, 10, txt=f"Annual Return: {la_return*100:.1f}%", ln=True)
            pdf.cell(0, 10, txt=f"Withdrawal Rate: {withdrawal_rate*100:.1f}%", ln=True)
            pdf.ln(10)
            pdf.cell(0, 10, txt=f"Monthly Income: R{monthly_income:,.2f}", ln=True)
            pdf.cell(0, 10, txt=f"Projection: {longevity_text}", ln=True)
            
            # Add graph to PDF
            pdf.image("living_annuity_projection.png", x=10, y=100, w=190)
            
            pdf.output("living_annuity_report.pdf")
            with open("living_annuity_report.pdf", "rb") as f:
                st.download_button(
                    label="⬇️ Download Living Annuity Report",
                    data=f.read(),
                    file_name="Juanita_Living_Annuity_Report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")

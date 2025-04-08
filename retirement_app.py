# ======================
# IMPORTS
# ======================
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
import io
import numpy as np
import time

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(layout="wide", page_title="Retirement Calculator")

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
# BRANDING & LOGO FUNCTIONS
# ======================
def get_logo_path():
    """Find the path to the logo image."""
    logo_paths = ["static/bhjcf-logo.png", "attached_assets/IMG_0019.png", "bhjcf-logo.png"]
    for path in logo_paths:
        if os.path.exists(path):
            return path
    return None

def get_logo_as_base64(logo_path):
    """Convert the logo to base64 for embedding in HTML/PDF."""
    with open(logo_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Get logo path
logo_path = get_logo_path()
if not logo_path:
    st.error("⚠️ Logo not found in any of the expected locations")
    logo_path = "attached_assets/IMG_0019.png"  # Default to this if it exists

# ======================
# APP HEADER
# ======================
# Centered Logo and Company Name on the Same Line
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    # Only try to load and display logo if the file exists
    if os.path.exists(logo_path):
        try:
            logo_base64 = get_logo_as_base64(logo_path)
            st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center;'>
                <img src="data:image/png;base64,{logo_base64}" width="65" style='margin-right: 10px;'>
                <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
                    BHJCF Studio
                </p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying logo: {str(e)}")
    else:
        st.markdown(f"""
        <div style='display: flex; justify-content: center; align-items: center;'>
            <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
                BHJCF Studio
            </p>
        </div>
        """, unsafe_allow_html=True)

# App Title with Custom Styling
st.markdown("""
<h1 style='text-align: center; margin-bottom: 20px;'>
    📊 <span class="custom-r">R</span>
    <span style='font-size: 32px; color: #00BFFF;'>Retirement Cash Flow Calculator</span>
</h1>
""", unsafe_allow_html=True)

# Client Watermark
st.markdown('<p style="color:#FF0000; font-size:20px; text-align: center;">Client: Juanita Moolman</p>', unsafe_allow_html=True)

# ======================
# CALCULATOR TABS 
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

# ======================
# RETIREMENT CASH FLOW TAB (FIXED)
# ======================
with tab1:
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    # Add inflation protection
    with st.expander("🛡️ Inflation Protection"):
        inflation_rate = st.slider("Annual Inflation (%)", 0.0, 5.0, 2.5) / 100
        real_return = annual_return - inflation_rate

    years_to_retirement = retirement_age - current_age
    future_value = fv(real_return, years_to_retirement, 0, -retirement_savings)
    years_in_retirement = life_expectancy - retirement_age

    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    withdrawals = [future_value * withdrawal_rate * (1 + real_return) ** year 
                  for year in range(years_in_retirement)]

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF', fontsize=14)
    ax.set_xlabel("Age", color='#228B22', fontsize=12)
    ax.set_ylabel("Annual Income (R)", color='#FF5E00', fontsize=12)
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    # PDF Generation (FIXED)
    if st.button("📄 Generate PDF Report"):
        with st.spinner("Generating professional report..."):
            try:
                # Save graph with proper styling
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
                img_buf.seek(0)
                
                # Create PDF with all branding elements
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # Header Section
                logo_width = 25
                pdf.image(logo_path, x=20, y=15, w=logo_width)
                pdf.set_font("Arial", 'B', 24)
                pdf.set_xy(50, 20)
                pdf.cell(0, 10, "BHJCF Studio", align='L')
                
                # Client Information
                pdf.set_font("Arial", 'B', 16)
                pdf.set_xy(20, 40)
                pdf.cell(0, 10, "Client: Juanita Moolman", align='L')
                
                # Title with underline
                pdf.set_font("Arial", 'B', 20)
                pdf.set_xy(0, 60)
                pdf.cell(0, 10, "Retirement Cash Flow Report", align='C')
                pdf.set_draw_color(0, 191, 255)
                pdf.line(50, 70, 160, 70)
                
                # Parameters Table
                pdf.set_font("Arial", 'B', 12)
                pdf.set_xy(20, 80)
                data = [
                    ("Current Age:", f"{current_age}"),
                    ("Retirement Age:", f"{retirement_age}"),
                    ("Current Savings:", f"R{retirement_savings:,.2f}"),
                    ("Annual Return:", f"{annual_return*100:.1f}%"),
                    ("Inflation Rate:", f"{inflation_rate*100:.1f}%"),
                    ("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
                    ("Projected Value:", f"R{future_value:,.2f}"),
                    ("First Year Withdrawal:", f"R{withdrawals[0]:,.2f}")
                ]
                
                for i, (label, value) in enumerate(data):
                    pdf.set_fill_color(240, 240, 240 if i%2==0 else 255)
                    pdf.cell(90, 10, label, 1, 0, 'L', fill=True)
                    pdf.cell(90, 10, value, 1, 1, 'R', fill=True)
                    pdf.set_x(20)
                
                # Add graph
                pdf.image(img_buf, x=20, y=140, w=170)
                
                # Disclaimer Section
                pdf.set_font("Arial", 'I', 8)
                pdf.set_xy(20, 260)
                pdf.multi_cell(170, 4, 
                    "Disclaimer: This projection is for illustrative purposes only. Actual results may vary. " 
                    "Consult a financial advisor before making decisions. BHJCF Studio does not guarantee accuracy.")
                
                # Generate PDF
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_data = pdf_output.getvalue()
                
                # Download button
                st.success("Professional PDF generated!")
                st.download_button(
                    label="⬇️ Download Full Report",
                    data=pdf_data,
                    file_name="Juanita_Retirement_Report.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"PDF generation failed: {str(e)}")

# ======================
# LIVING ANNUITY TAB (FIXED)
# ======================
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        la_current_age = st.slider("Current Age", 25, 100, 45, key="la_age")
    with col2:
        la_retirement_age = st.slider("Retirement Age", 55, 100, 65, key="la_retire")  
    
    if la_retirement_age <= la_current_age:
        st.error("❌ Retirement age must be AFTER current age!")
        st.stop()

    investment = st.number_input("Total Investment (R)", value=5000000, key="la_invest")
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return")/100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw")/100

    if st.button("🚀 CALCULATE LIVING ANNUITY PROJECTIONS"):
        # Simulation calculations
        monthly_income = investment * withdrawal_rate / 12
        balance = investment
        year_count = 0
        depletion_years = []
        balances = []
        withdrawal_amounts = []
        
        while balance > 0 and year_count < 50:
            withdrawal = balance * withdrawal_rate
            withdrawal_amounts.append(withdrawal)
            balance = (balance - withdrawal) * (1 + la_return)
            depletion_years.append(la_retirement_age + year_count)
            balances.append(balance)
            year_count += 1

        # Store results in session state
        st.session_state.simulation_results = {
            'depletion_years': depletion_years,
            'balances': balances,
            'withdrawal_amounts': withdrawal_amounts,
            'monthly_income': monthly_income,
            'year_count': year_count
        }

    if 'simulation_results' in st.session_state:
        # Display results
        st.subheader("Projection Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Monthly Income", f"R{st.session_state.simulation_results['monthly_income']:,.2f}")
        with col2:
            status = "✅ Sustainable" if st.session_state.simulation_results['year_count'] >= 30 else "⚠️ Needs Review"
            st.metric("Longevity", f"{st.session_state.simulation_results['year_count']} Years", status)
        
        # Generate PDF report
        if st.button("📄 Generate Living Annuity PDF"):
            with st.spinner("Creating professional report..."):
                try:
                    # Create PDF with branding
                    pdf = FPDF(orientation='P', format='A4')
                    pdf.add_page()
                    
                    # Header Section
                    pdf.image(logo_path, x=20, y=15, w=25)
                    pdf.set_font("Arial", 'B', 24)
                    pdf.set_xy(50, 20)
                    pdf.cell(0, 10, "BHJCF Studio", align='L')
                    
                    # Client Information
                    pdf.set_font("Arial", 'B', 16)
                    pdf.set_xy(20, 40)
                    pdf.cell(0, 10, "Client: Juanita Moolman", align='L')
                    
                    # Title with underline
                    pdf.set_font("Arial", 'B', 20)
                    pdf.set_xy(0, 60)
                    pdf.cell(0, 10, "Living Annuity Report", align='C')
                    pdf.set_draw_color(0, 191, 255)
                    pdf.line(50, 70, 160, 70)
                    
                    # Parameters Table
                    pdf.set_font("Arial", 'B', 12)
                    pdf.set_xy(20, 80)
                    data = [
                        ("Current Age:", f"{la_current_age}"),
                        ("Retirement Age:", f"{la_retirement_age}"),
                        ("Total Investment:", f"R{investment:,.2f}"),
                        ("Annual Return:", f"{la_return*100:.1f}%"),
                        ("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
                        ("Monthly Income:", f"R{st.session_state.simulation_results['monthly_income']:,.2f}"),
                        ("Projected Longevity:", f"{st.session_state.simulation_results['year_count']} Years")
                    ]
                    
                    for i, (label, value) in enumerate(data):
                        pdf.set_fill_color(240, 240, 240 if i%2==0 else 255)
                        pdf.cell(90, 10, label, 1, 0, 'L', fill=True)
                        pdf.cell(90, 10, value, 1, 1, 'R', fill=True)
                        pdf.set_x(20)
                    
                    # Disclaimer Section
                    pdf.set_font("Arial", 'I', 8)
                    pdf.set_xy(20, 260)
                    pdf.multi_cell(170, 4, 
                        "Disclaimer: Projections based on stated assumptions. Market performance may vary. " 
                        "Consult a financial advisor before making decisions.")
                    
                    # Generate PDF
                    pdf_output = io.BytesIO()
                    pdf.output(pdf_output)
                    pdf_data = pdf_output.getvalue()
                    
                    # Download button
                    st.success("Professional PDF generated!")
                    st.download_button(
                        label="⬇️ Download Full Report",
                        data=pdf_data,
                        file_name="Juanita_Living_Annuity_Report.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")

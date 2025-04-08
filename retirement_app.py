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
from html import escape

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
    align-items: center !important;  /* Perfect vertical align */
    padding-top: 2px;
    margin-top: -28px;  /* Adjusted */
    margin-bottom: -18px;  /* Adjusted */
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
                <img src="data:image/png;base64,{logo_base64}" width="65" style='margin-right: 10px; vertical-align: middle;'>
                <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0; position: relative; top: 3px;'>
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
# RETIREMENT CASH FLOW TAB 
# ======================
with tab1:
    # Inputs for Retirement Cash Flow
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000, min_value=1000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    # Retirement Cash Flow Calculations
    years_to_retirement = retirement_age - current_age
    future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)

    years_in_retirement = life_expectancy - retirement_age
    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    withdrawals = []
    depletion_age = None
    balance = future_value
    for year in range(years_in_retirement):
        withdrawal = round(balance * withdrawal_rate, 2)
        withdrawals.append(withdrawal)
        balance = max(0, (balance - withdrawal) * (1 + annual_return))
        if balance == 0 and not depletion_age:
            depletion_age = retirement_age + year

    # PDF Generation
    if st.button("📄 Generate PDF Report"):
        with st.spinner("Generating report..."):
            try:
                # Save graph to memory buffer
                fig, ax = plt.subplots()
                ax.plot(range(retirement_age, life_expectancy), withdrawals, label="Withdrawals")
                ax.set_title("Retirement Income Over Time")
                ax.set_xlabel("Age")
                ax.set_ylabel("Yearly Withdrawals (R)")
                ax.grid(True)
                plt.legend()
                plt.tight_layout()

                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', dpi=300)
                img_buf.seek(0)
                plt.close(fig)  # Prevent memory leaks

                # PDF Creation
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Retirement Cash Flow Report", ln=True, align="C")
                pdf.image(img_buf, x=10, y=30, w=190)
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_data = pdf_output.getvalue()

                st.success("PDF generated successfully! Click below to download.")
                st.download_button(
                    label="⬇️ Download Report",
                    data=pdf_data,
                    file_name="retirement_report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

# ======================
# LIVING ANNUITY TAB
# ======================
with tab2:
    # Inputs for Living Annuity
    col1, col2, col3 = st.columns(3)
    with col1:
        current_age = st.number_input("Current Age", 45, 100, 65, key="la_age")
    with col2:
        retirement_age = st.number_input("Retirement Age", 55, 100, 65, key="la_retire")
    with col3:
        life_expectancy = st.number_input("Life Expectancy", 75, 120, 90, key="la_life")

    # Validate inputs
    if current_age >= life_expectancy:
        st.error("Life expectancy must be greater than current age")
        st.stop()

    investment = st.number_input("Annuity Value (R)", value=5000000, min_value=100000, step=50000, key="la_invest")
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw") / 100

    with st.expander("⚙️ Market Parameters"):
        la_return = st.slider("Expected Annual Return (%)", -10.0, 20.0, 7.0) / 100
        inflation_rate = st.slider("Annual Inflation (%)", 0.0, 10.0, 4.5) / 100
        volatility = st.slider("Market Volatility (Std Dev)", 0.0, 0.3, 0.15)
        monte_carlo_runs = st.number_input("Simulation Runs", 100, 10000, 1000)

    # Add calculate button and simulation
    if st.button("🚀 Run Simulation", key="la_calculate"):
        with st.spinner("Running 1,000 retirement scenarios..."):
            years = life_expectancy - current_age
            simulations = np.zeros((years, monte_carlo_runs))
            simulations[0] = investment

            for year in range(1, years):
                market_return = np.random.normal(la_return, volatility, monte_carlo_runs)
                simulations[year] = (simulations[year - 1] * (1 + market_return)) * (1 - withdrawal_rate)
                simulations[year] = np.where(simulations[year] < 0, 0, simulations[year])

            # Plot results
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(simulations, color='blue', alpha=0.1)
            ax.plot(np.median(simulations, axis=1), color='red', linewidth=2, label="Median")
            ax.set_title("Monte Carlo Retirement Projections")
            ax.set_xlabel("Years into Retirement")
            ax.set_ylabel("Portfolio Value (R)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)  # Prevent memory leaks

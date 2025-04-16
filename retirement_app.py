# ====================== IMPORTS ======================
import base64
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')  # CRITICAL FOR STREAMLIT CLOUD
import streamlit as st
from numpy_financial import fv
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
# TAB DEFINITIONS
# ======================
tab1, tab2 = st.tabs(["Retirement Cash Flow", "Living Annuity"])

# ======================
# RETIREMENT CASH FLOW TAB (UPDATED)
# ======================
with tab1:
    # User Inputs
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    years_to_retirement = retirement_age - current_age
    future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)
    years_in_retirement = life_expectancy - retirement_age

    # Validate Inputs
    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    # Calculate Withdrawals
    withdrawals = [future_value * withdrawal_rate * (1 + annual_return) ** year 
                   for year in range(years_in_retirement)]

    # Display Spending Plan
    st.subheader("Your Spending Plan")
    st.markdown(f"""
    <div style='margin: 20px 0; font-family: "Times New Roman", serif;'>
        <span class="custom-r">R</span>
        <span style='font-size: 18px;'>At retirement value: </span>
        <span style='color: #00BFFF; font-weight: bold;'>R{future_value:,.2f}</span>
    </div>
    <div style='margin: 20px 0; font-family: "Times New Roman", serif;'>
        <span class="custom-r">R</span>
        <span style='font-size: 18px;'>Annual withdrawal: </span>
        <span style='color: #FF5E00; font-weight: bold;'>R{withdrawals[0]:,.2f}</span>
        <span style='font-size: 14px; color: #666;'>(3% annual growth)</span>
    </div>
    <h4 style='font-family: "Times New Roman", serif; text-align: center;'>Current Data</h4>
    <p style='font-family: "Times New Roman", serif; text-align: center;'>
        Current Age: {current_age} years<br/>
        Retirement Age: {retirement_age} years<br/>
        Total Savings: R{retirement_savings:,.2f}<br/>
        Annual Return: {annual_return * 100:.1f}%<br/>
        Life Expectancy: {life_expectancy} years<br/>
        Withdrawal Rate: {withdrawal_rate * 100:.1f}%
    </p>
    """, unsafe_allow_html=True)

    # Plotting the Cash Flow
    years = np.arange(years_in_retirement)
    balances = [future_value]
    for withdrawal in withdrawals:
        next_balance = balances[-1] * (1 + annual_return) - withdrawal
        balances.append(next_balance)

    # Plot the cash flow
    plt.figure(figsize=(10, 5))
    plt.plot(years, balances[:-1], marker='o', label='Balance')
    plt.plot(years, withdrawals, marker='x', label='Annual Withdrawals')
    
    plt.title("Projected Cash Flow Over Retirement")
    plt.xlabel("Years in Retirement")
    plt.ylabel("Amount (R)")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save graph to temporary location
    graph_buf = io.BytesIO()
    plt.savefig(graph_buf, format='png', dpi=300, bbox_inches='tight')
    graph_buf.seek(0)

    # Display the graph in the Streamlit app
    st.image(graph_buf, caption='Projected Cash Flow', use_column_width=True)

    # Add PDF generation button for Cash Flow tab
    if st.button("📄 Generate Cash Flow PDF Report", key="cf_pdf_btn"):
        try:
            # Create PDF
            pdf = FPDF(orientation='P', format='A4')
            pdf.add_page()

            # Set font for the entire PDF
            pdf.set_font("Arial", 'B', 16)

            # Add title to the PDF
            pdf.cell(0, 10, "Retirement Cash Flow Report", ln=True, align='C')

            # Add user input values to the PDF
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Client: Juanita Moolman", ln=True)
            pdf.cell(0, 10, f"Current Age: {current_age} years", ln=True)
            pdf.cell(0, 10, f"Retirement Age: {retirement_age} years", ln=True)
            pdf.cell(0, 10, f"Total Savings: R{retirement_savings:,.2f}", ln=True)
            pdf.cell(0, 10, f"Annual Return: {annual_return * 100:.1f}%", ln=True)
            pdf.cell(0, 10, f"Life Expectancy: {life_expectancy} years", ln=True)
            pdf.cell(0, 10, f"Withdrawal Rate: {withdrawal_rate * 100:.1f}%", ln=True)

            # Save the graph image to a new page in the PDF
            pdf.add_page()
            pdf.cell(0, 10, "Projected Cash Flow Graph", ln=True, align='C')
            pdf.image(graph_buf, x=10, w=pdf.w - 20)  # Adjust the width and position

            # Save PDF to memory
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_data = pdf_output.getvalue()

            # Download button for PDF report
            st.download_button(
                label="📥 Download Cash Flow PDF Report",
                data=pdf_data,
                file_name="Retirement_Cash_Flow_Report.pdf",
                mime="application/pdf"
            )

            st.success("PDF generated successfully!")
        
        except Exception as e:
            st.error(f"❌ An error occurred while generating the PDF: {str(e)}")

# ====================== LIVING ANNUITY TAB (FINAL TESTED VERSION) ======================
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
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return") / 100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw") / 100

    calculate_btn = st.button("🚀 CALCULATE LIVING ANNUITY PROJECTIONS", key="la_btn")

    if calculate_btn:
        monthly_income = investment * withdrawal_rate / 12

        # Simulation
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
        st.session_state.la_data = {
            'la_current_age': la_current_age,
            'la_retirement_age': la_retirement_age,
            'investment': investment,
            'la_return': la_return,
            'withdrawal_rate': withdrawal_rate,
            'monthly_income': monthly_income,
            'year_count': year_count,
            'longevity_text': longevity_text,
            'balances': balances,
            'withdrawal_amounts': withdrawal_amounts,
            'depletion_years': depletion_years
        }

        # Generate graph buffers
        balance_buf = io.BytesIO()
        ax1.figure.savefig(balance_buf, format='png', dpi=150)
        balance_buf.seek(0)
        
        withdrawal_buf = io.BytesIO()
        ax2.figure.savefig(withdrawal_buf, format='png', dpi=150)
        withdrawal_buf.seek(0)

        # PDF Generation (Full working version)
        if st.button("📄 Generate Living Annuity PDF Report"):
            try:
                pdf = FPDF(orientation='P', format='A4')
                
                # ===== PAGE 1: OVERVIEW & BALANCE CHART =====
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # Header
                pdf.set_font("Arial", 'B', 16)
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=8, w=25)
                pdf.cell(0, 10, "BHJCF Studio", ln=True, align='C')
                
                # Title
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 10, "Living Annuity Projection", ln=True, align='C')
                
                # Client Info
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: Juanita Moolman", ln=True, align='C')
                
                # Data Table
                pdf.set_font("Arial", '', 11)
                col_width = pdf.w / 2.2
                for label, value in [
                    ("Current Age:", f"{la_current_age} years"),
                    ("Retirement Age:", f"{la_retirement_age} years"),
                    ("Investment:", f"R{investment:,.2f}"),
                    ("Annual Return:", f"{la_return*100:.1f}%"),
                    ("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
                    ("Monthly Income:", f"R{monthly_income:,.2f}"),
                    ("Status:", f"Funds {'last beyond age 95' if year_count >=50 else f'deplete at age {la_retirement_age+year_count}'}")
                ]:
                    pdf.cell(col_width, 10, label)
                    pdf.cell(0, 10, value, ln=True)
                
                # Balance Graph
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Investment Balance Timeline", ln=True, align='C')
                pdf.image(balance_buf, x=10, w=pdf.w-20)

                # ===== PAGE 2: WITHDRAWALS & ANALYSIS =====
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Annual Withdrawals", ln=True, align='C')
                pdf.image(withdrawal_buf, x=10, w=pdf.w-20)
                
                # Tax Info
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Tax Considerations", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 5, """• Withdrawals taxed as ordinary income\n• First R500k tax-free (lifetime)\n• Annual tax-free allowance applies""")

                # Footer
                pdf.set_y(-20)
                pdf.set_font("Arial", 'I', 8)
                pdf.cell(0, 10, f"Generated {time.strftime('%Y-%m-%d')} | Page {pdf.page_no()}", 0, 0, 'C')

                # Finalize PDF
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                
                st.download_button(
                    label="⬇️ Download Full Report",
                    data=pdf_bytes,
                    file_name=f"Living_Annuity_Report_{time.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF generated successfully!")

            except Exception as e:
                st.error(f"PDF generation failed: {str(e)}")


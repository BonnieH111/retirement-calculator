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

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(page_title="Retirement Planner", layout="wide")

# ======================
# BRANDING CONFIGURATION
# ======================
BRANDING = {
    "company_name": "BHJCF Studio",
    "tagline": "Plan Your Future with Confidence",
    "logo_path": "static/bhjcf-logo.png",  # Update this to your logo path
    "primary_color": "#00BFFF",
    "secondary_color": "#FF5E00"
}

def show_branding():
    """Display the logo, company name, and tagline."""
    col1, col2 = st.columns([1, 6])
    with col1:
        if os.path.exists(BRANDING["logo_path"]):
            st.image(BRANDING["logo_path"], width=60)
    with col2:
        st.markdown(
            f"<h2 style='color:{BRANDING['primary_color']}; margin-bottom:0;'>{BRANDING['company_name']}</h2>"
            f"<p style='color:{BRANDING['secondary_color']}; margin-top:0;'>{BRANDING['tagline']}</p>",
            unsafe_allow_html=True
        )

# ======================
# UTILITY FUNCTIONS
# ======================
def save_chart_to_image(fig):
    """Convert a Matplotlib figure to an image buffer."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

def calculate_final_value(pv, rate, nper):
    """Calculate the future value of a present amount."""
    return fv(rate, nper, 0, -pv)

# ======================
# PDF CLASS
# ======================
class CustomPDF(FPDF):
    def header(self):
        """Add a header to the PDF."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Retirement Planning Report", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        """Add a chapter title to the PDF."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, body):
        """Add body text to the PDF."""
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, body)
        self.ln()

# ======================
# APP HEADER
# ======================
show_branding()

# App Title
st.markdown(f"""
<h1 style='text-align: center; margin-bottom: 20px;'>
    📊 <span style="color:{BRANDING['secondary_color']};">Retirement Cash Flow Calculator</span>
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
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    # Calculate future value at retirement
    years_to_retirement = retirement_age - current_age
    future_value = calculate_final_value(retirement_savings, annual_return, years_to_retirement)
    years_in_retirement = life_expectancy - retirement_age

    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    withdrawals = [
        future_value * withdrawal_rate * (1 + annual_return) ** year
        for year in range(years_in_retirement)
    ]

    # Display Spending Plan
    st.subheader("Your Spending Plan")
    st.markdown(f"""
    <div style='margin: 20px 0;'>
        <span style='font-size: 18px;'>At retirement value: </span>
        <span style='color: {BRANDING['primary_color']}; font-weight: bold;'>R{future_value:,.2f}</span>
    </div>
    <div style='margin: 20px 0;'>
        <span style='font-size: 18px;'>Annual withdrawal: </span>
        <span style='color: {BRANDING['secondary_color']}; font-weight: bold;'>R{withdrawals[0]:,.2f}</span>
        <span style='font-size: 14px; color: #666;'>(3% annual growth)</span>
    </div>
    """, unsafe_allow_html=True)

    # Generate Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color=BRANDING['primary_color'], fontsize=14)
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Annual Income (R)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # Generate PDF
    if st.button("📄 Generate PDF Report"):
        pdf = CustomPDF()
        pdf.add_page()
        pdf.chapter_title("Retirement Cash Flow Report")
        pdf.chapter_body(f"Client: Juanita Moolman\n\nFuture Value: R{future_value:,.2f}\n"
                         f"Initial Annual Withdrawal: R{withdrawals[0]:,.2f}")
        buf = save_chart_to_image(fig)
        pdf.image(buf, x=10, y=None, w=190)
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_output.getvalue(),
            file_name="retirement_cashflow_report.pdf",
            mime="application/pdf"
        ) 

# ======================
# LIVING ANNUITY TAB (ENHANCED)
# ======================
with tab2:
    # Input fields for Living Annuity Simulator
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

    # Button to calculate projections
    calculate_btn = st.button("🚀 CALCULATE LIVING ANNUITY PROJECTIONS", key="la_btn")

    if calculate_btn:
        monthly_income = investment * withdrawal_rate / 12

        # Simulation Logic
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

        # Longevity Assessment
        if balance <= 0:
            longevity_text = f"⚠️ Funds depleted after {year_count} years (age {la_retirement_age + year_count})"
            longevity_color = "#FF0000"
        else:
            longevity_text = f"✅ Funds sustainable beyond {year_count} years"
            longevity_color = "#00FF00"

        # Display Results
        st.markdown(f"""
        <div style='margin: 20px 0;'>
            <h3>Monthly Income</h3>
            <p style='font-size: 24px; color: #00BFFF;'>R{monthly_income:,.2f}</p>
            <p style='color: {longevity_color};'>{longevity_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # Create and display graphs
        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.plot(depletion_years, balances, color='#228B22', linewidth=2.5)
            ax1.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
            ax1.set_title("Investment Balance Timeline", color='#00BFFF', fontsize=14)
            ax1.set_xlabel("Age", color='#228B22', fontsize=12)
            ax1.set_ylabel("Remaining Balance (R)", color='#FF5E00', fontsize=12)
            ax1.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2.5)
            ax2.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
            ax2.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=14)
            ax2.set_xlabel("Age", color='#228B22', fontsize=12)
            ax2.set_ylabel("Withdrawal Amount (R)", color='#FF5E00', fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig2)

    # Check for data in session state to enable PDF button
    if 'la_data' in st.session_state:
        generate_pdf_btn = st.button("📄 Generate Living Annuity PDF Report", key="la_pdf_btn")
        if generate_pdf_btn:
            try:
                st.info("Generating PDF report... please wait.")

                # Retrieve data from session state
                la_data = st.session_state.la_data
                depletion_years = la_data['depletion_years']
                balances = la_data['balances']
                withdrawal_amounts = la_data['withdrawal_amounts']
                monthly_income = la_data['monthly_income']
                longevity_text = la_data['longevity_text']
                investment = la_data['investment']
                la_return = la_data['la_return']
                withdrawal_rate = la_data['withdrawal_rate']
                la_current_age = la_data['la_current_age']
                la_retirement_age = la_data['la_retirement_age']
                year_count = la_data['year_count']

                # Create PDF
                pdf = CustomPDF()
                pdf.add_page()
                pdf.chapter_title("Living Annuity Report")
                pdf.chapter_body(f"""
                Client: Juanita Moolman

                Current Age: {la_current_age} years
                Retirement Age: {la_retirement_age} years
                Investment Amount: R{investment:,.2f}
                Annual Return: {la_return * 100:.1f}%
                Withdrawal Rate: {withdrawal_rate * 100:.1f}%

                Monthly Income: R{monthly_income:,.2f}
                Longevity Assessment: {longevity_text}
                """)

                # Add Balance Chart
                buf1 = save_chart_to_image(fig1)
                pdf.image(buf1, x=10, y=None, w=190)

                # Add Withdrawal Chart
                buf2 = save_chart_to_image(fig2)
                pdf.image(buf2, x=10, y=None, w=190)

                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                st.download_button(
                    label="⬇️ Download Living Annuity PDF Report",
                    data=pdf_output.getvalue(),
                    file_name="living_annuity_report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.exception(e) 

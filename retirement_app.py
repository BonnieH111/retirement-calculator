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

# Custom CSS for colors and PDF preview
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
.pdf-preview {
    width: 100%;
    height: 800px;
    border: none;
}
</style>""", unsafe_allow_html=True)

def get_logo_path():
    """Find the path to the logo image."""
    logo_paths = [
        "static/bhjcf-logo.png", 
        "attached_assets/IMG_0019.png", 
        "bhjcf-logo.png",
        "generated-icon.png"
    ]
    for path in logo_paths:
        if os.path.exists(path):
            return path
    return "attached_assets/IMG_0019.png"

def get_logo_as_base64(logo_path):
    """Convert the logo to base64 for embedding in HTML/PDF."""
    try:
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        pass
    return None

def save_temp_logo():
    """Create a temporary file with the logo for FPDF to use safely."""
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        try:
            temp_file = NamedTemporaryFile(delete=False, suffix=".png")
            img = Image.open(logo_path)
            img.save(temp_file.name)
            temp_file.close()
            return temp_file.name
        except Exception:
            pass
    return None

def display_pdf(pdf_bytes):
    """Display PDF preview in Streamlit."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" class="pdf-preview"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Get logo path
logo_path = get_logo_path()

# ======================
# APP HEADER
# ======================
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
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
        st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center;'>
            <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
                BHJCF Studio
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; margin-bottom: 20px;'>
    📊 <span class="custom-r">R</span>
    <span style='font-size: 32px; color: #00BFFF;'>Retirement Cash Flow Calculator</span>
</h1>
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
        st.error("Error: Life expectancy must be GREATER than retirement age!")
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

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF', fontsize=14)
    ax.set_xlabel("Age", color='#228B22', fontsize=12)
    ax.set_ylabel("Annual Income (R)", color='#FF5E00', fontsize=12)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    if st.button("📄 Generate PDF Report", key="rcf_pdf_btn"):
        try:
            details = [
                ["Client:", "Juanita Moolman"],
                ["Current Age:", f"{current_age} years"],
                ["Retirement Age:", f"{retirement_age} years"],
                ["Life Expectancy:", f"{life_expectancy} years"],
                ["Current Savings:", f"R{retirement_savings:,.2f}"],
                ["Future Value:", f"R{future_value:,.2f}"],
                ["Initial Annual Withdrawal:", f"R{withdrawals[0]:,.2f}"]
            ]

            pdf = generate_styled_pdf("Retirement Cash Flow Report", details, [fig]) # Assuming generate_styled_pdf is defined elsewhere
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # Display preview
            st.success("PDF generated successfully!")
            display_pdf(pdf_output.getvalue())

            # Download button
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_output.getvalue(),
                file_name="retirement_cashflow_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

# ======================
# LIVING ANNUITY TAB
# ======================
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        la_current_age = st.slider("Current Age", 25, 100, 45, key="la_age")
    with col2:
        la_retirement_age = st.slider("Retirement Age", 55, 100, 65, key="la_retire")

    if la_retirement_age <= la_current_age:
        st.error("Error: Retirement age must be AFTER current age!")
        st.stop()

    investment = st.number_input("Total Investment (R)", value=5000000, key="la_invest")
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return")/100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw")/100

    if st.button("🚀 Calculate Projections", key="la_calc_btn"):
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

        # Longevity Assessment
        if balance <= 0:
            display_text = f"⚠️ Funds depleted after {year_count} years (age {la_retirement_age + year_count})"
            longevity_text = f"[WARNING] Funds depleted after {year_count} years (age {la_retirement_age + year_count})"
            longevity_color = "#FF0000"
        else:
            display_text = f"✅ Funds sustainable beyond {year_count} years"
            longevity_text = f"[GOOD] Funds sustainable beyond {year_count} years"
            longevity_color = "#00FF00"

        # Use display_text for the web display, longevity_text for PDF
        st.markdown(f"""
        <div style='margin: 20px 0;'>
            <h3>Monthly Income</h3>
            <p style='font-size: 24px; color: #00BFFF;'>R{monthly_income:,.2f}</p>
            <p style='color: {longevity_color};'>{display_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # Store data in session state
        st.session_state.la_data = {
            'depletion_years': depletion_years,
            'balances': balances,
            'withdrawal_amounts': withdrawal_amounts,
            'monthly_income': monthly_income,
            'longevity_text': longevity_text,
            'investment': investment,
            'la_return': la_return,
            'withdrawal_rate': withdrawal_rate,
            'la_current_age': la_current_age,
            'la_retirement_age': la_retirement_age,
            'year_count': year_count
        }

        # Create and display graphs
        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.plot(depletion_years, balances, color='#228B22', linewidth=2)
            ax1.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
            ax1.set_title("Investment Balance Timeline", color='#00BFFF', fontsize=14)
            ax1.set_xlabel("Age", color='#228B22', fontsize=12)
            ax1.set_ylabel("Balance (R)", color='#FF5E00', fontsize=12)
            ax1.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            )
            ax1.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2)
            ax2.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
            ax2.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=14)
            ax2.set_xlabel("Age", color='#228B22', fontsize=12)
            ax2.set_ylabel("Withdrawal (R)", color='#FF5E00', fontsize=12)
            ax2.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            )
            ax2.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig2)

        if st.button("📄 Generate PDF Report", key="la_pdf_btn"):
            try:
                details = [
                    ["Client:", "Juanita Moolman"],
                    ["Current Age:", f"{la_current_age} years"],
                    ["Retirement Age:", f"{la_retirement_age} years"],
                    ["Investment Amount:", f"R{investment:,.2f}"],
                    ["Annual Return:", f"{la_return * 100:.1f}%"],
                    ["Withdrawal Rate:", f"{withdrawal_rate * 100:.1f}%"],
                    ["Monthly Income:", f"R{monthly_income:,.2f}"],
                    ["Longevity Assessment:", longevity_text.replace("⚠️", "[WARNING]").replace("✅", "[GOOD]")]
                ]

                pdf = generate_styled_pdf("Living Annuity Report", details, [fig1, fig2]) # Assuming generate_styled_pdf is defined elsewhere
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_output.seek(0)

                # Display preview
                st.success("PDF generated successfully!")
                display_pdf(pdf_output.getvalue())

                # Download button
                st.download_button(
                    label="⬇️ Download Living Annuity PDF Report",
                    data=pdf_output.getvalue(),
                    file_name="living_annuity_report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

def generate_styled_pdf(title, details, figures):
    """Generates a styled PDF report."""
    pdf = FPDF(orientation='P', format='A4')
    pdf.add_page()

    # Add logo
    temp_logo = save_temp_logo()
    if temp_logo:
        pdf.image(temp_logo, x=10, y=10, w=30)
        os.unlink(temp_logo)

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    # Details
    pdf.set_font('Arial', '', 12)
    for detail in details:
        pdf.cell(80, 8, detail[0], 0, 0)
        pdf.cell(0, 8, detail[1], 0, 1)
    pdf.ln(10)

    # Figures
    for fig in figures:
        with NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            fig.savefig(tmpfile.name, dpi=300, bbox_inches='tight')
            pdf.image(tmpfile.name, x=10, y=None, w=190)
            os.unlink(tmpfile.name)
        pdf.add_page()


    # Add disclaimer
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128)
    pdf.multi_cell(0, 4, "Disclaimer: This report is based on provided information and assumptions. Actual results may vary.", 0, 'L')

    return pdf 

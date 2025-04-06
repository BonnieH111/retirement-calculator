# retirement_app.py

# ====================== ADD THIS AT VERY TOP ======================
import matplotlib
import base64
import tempfile
matplotlib.use('Agg')  # CRITICAL FOR STREAMLIT CLOUD
# ===================================================================

import streamlit as st
from numpy_financial import fv, pmt
import matplotlib.pyplot as plt  # KEEP THIS AFTER matplotlib.use()
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
# PDF GENERATION FUNCTION (Reusable)
# ======================
def create_pdf_report(client_name, current_age, retirement_age, retirement_savings, annual_return, life_expectancy, withdrawal_rate, future_value, withdrawals, tab_name):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Logo handling
        if os.path.exists("bhjcf-logo.png"):
            pdf.image("bhjcf-logo.png", x=10, y=8, w=30)

        # Report content
        pdf.cell(200, 10, txt=f"{tab_name} Report", ln=True, align="C")
        pdf.ln(15)
        pdf.cell(0, 10, txt=f"Client: {client_name}", ln=True)
        pdf.cell(0, 10, txt=f"Current Age: {current_age}", ln=True)
        pdf.cell(0, 10, txt=f"Retirement Age: {retirement_age}", ln=True)
        pdf.cell(0, 10, txt=f"Current Savings: R{retirement_savings:,.2f}", ln=True)
        pdf.cell(0, 10, txt=f"Annual Return: {annual_return*100:.1f}%", ln=True)
        pdf.cell(0, 10, txt=f"Life Expectancy: {life_expectancy}", ln=True)
        pdf.cell(0, 10, txt=f"Withdrawal Rate: {withdrawal_rate*100:.1f}%", ln=True)
        pdf.ln(10)
        pdf.cell(0, 10, txt=f"Projected Retirement Value: R{future_value:,.2f}", ln=True)
        pdf.cell(0, 10, txt=f"First Year Withdrawal: R{withdrawals[0]:,.2f}", ln=True)
        
        # Save to tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdf.output(temp_pdf.name)
            return temp_pdf.name
    except Exception as e:
        st.error(f"❌ PDF generation failed: {str(e)}")
        return None

# ======================
# CALCULATOR TABS 
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

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
    plt.close()  # Fixes graph display issues

    if st.button("📄 Generate PDF Report"):
        pdf_file = create_pdf_report(
            client_name="Juanita Moolman",
            current_age=current_age,
            retirement_age=retirement_age,
            retirement_savings=retirement_savings,
            annual_return=annual_return,
            life_expectancy=life_expectancy,
            withdrawal_rate=withdrawal_rate,
            future_value=future_value,
            withdrawals=withdrawals,
            tab_name="Retirement Cash Flow"
        )
        if pdf_file:
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f.read(),
                    file_name="Juanita_Retirement_Report.pdf",
                    mime="application/pdf"
                )

with tab2:
    # ======================
    # LIVING ANNUITY CALCULATOR 
    # ======================
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

    calculate_btn = st.button("🚀 CALCULATE LIVING ANNUITY PROJECTIONS", key="la_btn")
    
    if calculate_btn:
        monthly_income = investment * withdrawal_rate / 12
        
        # Simulation
        balance = investment
        year_count = 0
        depletion_years = []
        balances = []
        
        while balance > 0 and year_count < 50:
            withdrawal = balance * withdrawal_rate
            balance = (balance - withdrawal) * (1 + la_return)
            depletion_years.append(la_retirement_age + year_count)
            balances.append(balance)
            year_count += 1

        # Results 
        st.subheader("Projection Results")
        st.markdown(f"""
        <div style='margin: 20px 0;'>
            <span class="custom-r">R</span> 
            <span style='font-size: 18px;'>Monthly income: </span>
            <span style='color: #FF5E00; font-weight: bold;'>R{monthly_income:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)

        longevity_text = f"✅ Funds last beyond age {la_retirement_age + 50}" if year_count >= 50 \
            else f"⚠️ Funds depleted at age {la_retirement_age + year_count}"
        
        st.markdown(f"""
        <div style='margin: 25px 0; padding: 15px; border-radius: 8px; 
                    background-color: {"#e6f4ea" if year_count >=50 else "#fff3cd"};'>
            <span style='font-size: 16px;'>{longevity_text}</span>
        </div>
        """, unsafe_allow_html=True)

        # Visualization
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(depletion_years, balances, color='#228B22', linewidth=2)
        ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
        ax.set_title("Investment Balance Timeline", color='#00BFFF')
        ax.set_xlabel("Age", color='#228B22')
        ax.set_ylabel("Remaining Balance (R)", color='#FF5E00')
        st.pyplot(fig)

        # Living Annuity PDF
        if st.button("📄 Generate PDF Report"):
            pdf_file = create_pdf_report(
                client_name="Juanita Moolman",
                current_age=la_current_age,
                retirement_age=la_retirement_age,
                retirement_savings=investment,
                annual_return=la_return,
                life_expectancy=la_retirement_age + 50,  # Or other value
                withdrawal_rate=withdrawal_rate,
                future_value=investment,
                withdrawals=[monthly_income],  # Simulated value
                tab_name="Living Annuity"
            )
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f.read(),
                        file_name="Juanita_Living_Annuity_Report.pdf",
                        mime="application/pdf"
                    )

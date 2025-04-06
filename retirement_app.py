# retirement_app.py
# ====================== IMPORTS ======================
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
    📊 <span class="custom-r">R</span>
    <span style='font-size: 32px; color: #00BFFF;'>Retirement Cash Flow Calculator</span>
</h1>
""", unsafe_allow_html=True)

# Centered Logo and Company Name on the Same Line
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <img src="bhjcf-logo.png" width="65" style='margin-right: 10px;'>
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

    fig, ax = plt.subplots(figsize=(10, 6))  # Adjusted height to prevent cutoff
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF')
    ax.set_xlabel("Age", color='#228B22')
    ax.set_ylabel("Annual Income (R)", color='#FF5E00')
    plt.tight_layout()  # Ensures the graph fits properly
    st.pyplot(fig)
    plt.close()

    # Generate PDF with preview
    if st.button("📄 Generate PDF Report"):
        try:
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp_graph:
                fig.savefig(tmp_graph.name, dpi=300)
                
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                
                # Centered Logo & Company Name
                pdf.image("bhjcf-logo.png", x=(210-30)/2, y=10, w=30)
                pdf.set_y(40)
                pdf.cell(0, 10, "BHJCF Studio", ln=1, align='C')
                
                # Report Title
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 15, "Retirement Cash Flow Report", ln=1, align='C')
                pdf.ln(10)
                
                # Client Info
pdf.set_font("Arial", 'B', 12)
pdf.cell(0, 10, "Client: Juanita Moolman", ln=1)
pdf.ln(5)
        
                # Data Table
                pdf.set_font("Arial", size=12)
                data = [
                    ("Current Age", current_age),
                    ("Retirement Age", retirement_age),
                    ("Current Savings", f"R{retirement_savings:,.2f}"),
                    ("Annual Return", f"{annual_return*100:.1f}%"),
                    ("Life Expectancy", life_expectancy),
                    ("Withdrawal Rate", f"{withdrawal_rate*100:.1f}%"),
                    ("Projected Value", f"R{future_value:,.2f}"),
                    ("First Year Withdrawal", f"R{withdrawals[0]:,.2f}")
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
                            file_name="Juanita_Retirement_Report.pdf",
                            mime="application/pdf"
                        )
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")

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
        fig_la, ax_la = plt.subplots(figsize=(10,6))
        ax_la.plot(depletion_years, balances, color='#228B22', linewidth=2)
        ax_la.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
        ax_la.set_title("Investment Balance Timeline", color='#00BFFF')
        ax_la.set_xlabel("Age", color='#228B22')
        ax_la.set_ylabel("Remaining Balance (R)", color='#FF5E00')
        plt.tight_layout()  # Ensures the graph fits properly
        st.pyplot(fig_la)
        plt.close()

        # PDF Generation
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


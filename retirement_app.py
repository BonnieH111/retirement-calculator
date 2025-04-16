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

## ====================== CASH FLOW PDF GENERATION ======================
if st.button("📄 Generate Cash Flow PDF Report", key="cf_pdf_btn"):
    try:
        # Initialize PDF
        pdf = FPDF(orientation='P', format='A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # ---- Header with Logo ----
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=25)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "BHJCF Studio", ln=True, align='C')
        
        # ---- Title Section ----
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 15, "Retirement Cash Flow Report", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Generated: {time.strftime('%Y-%m-%d')}", ln=True, align='C')
        pdf.ln(10)

        # ---- Client Information ----
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Client: Juanita Moolman", ln=True)
        pdf.ln(5)

        # ---- Data Display ----
        pdf.set_font("Arial", '', 12)
        col_width = pdf.w / 3
        data_rows = [
            ("Current Age:", f"{current_age} years"),
            ("Retirement Age:", f"{retirement_age} years"),
            ("Current Savings:", f"R{retirement_savings:,.2f}"),
            ("Annual Return:", f"{annual_return*100:.1f}%"),
            ("Life Expectancy:", f"{life_expectancy} years"),
            ("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
            ("Projected Balance:", f"R{future_value:,.2f}"),
            ("First Year Withdrawal:", f"R{withdrawals[0]:,.2f}")
        ]
        
        for label, value in data_rows:
            pdf.cell(col_width, 10, label)
            pdf.cell(0, 10, value, ln=True)

        # ---- Graph Page ----
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Projected Cash Flow", ln=True, align='C')
        pdf.image(graph_buf, x=10, y=25, w=pdf.w-20)

        # ---- Footer ----
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')

        # Generate download
        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="📥 Download Full Report",
            data=pdf_output,
            file_name=f"Cash_Flow_Report_{time.strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        st.success("✅ PDF generated with professional styling!")
    
    except Exception as e:
        st.error(f"❌ PDF generation failed: {str(e)}")

# 🆕 TOGGLE FOR GRAPH VISIBILITY (NEW)
if st.checkbox("📊 Display Interactive Graph", True, key="graph_toggle"):
    st.image(graph_buf, caption='Projected Cash Flow', use_container_width=True)

# ====================== LIVING ANNUITY SIMULATOR ======================
with tab2:
    # -------------------- USER INPUT PANEL --------------------
    with st.container(border=True):
        st.subheader("🧮 Simulation Parameters")
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

        calculate_btn = st.button("🚀 CALCULATE PROJECTIONS", key="la_btn", type="primary")

    # -------------------- CORE CALCULATION ENGINE --------------------
    if calculate_btn:
        with st.status("⚙️ Running simulation...", expanded=True) as status:
            monthly_income = investment * withdrawal_rate / 12
            
            balance = investment
            year_count = 0
            balances = []
            withdrawal_amounts = []
            
            while balance > 0 and year_count < 50:
                withdrawal = balance * withdrawal_rate
                withdrawal_amounts.append(withdrawal)
                balance = (balance - withdrawal) * (1 + la_return)
                balances.append(balance)
                year_count += 1
            
            longevity_status = "🟢 Sustainable beyond age 95" if year_count >=50 else f"🔴 Depletes at age {la_retirement_age+year_count}"
            status.update(label=f"✅ Simulation complete! {longevity_status}", state="complete")

        # -------------------- VISUALIZATION DASHBOARD --------------------
        st.subheader("📈 Projection Dashboard")
        
        with st.spinner("Generating visualizations..."):
            plt.style.use('seaborn')
            
            fig1, ax1 = plt.subplots(figsize=(10,4))
            ax1.plot(range(year_count), balances, color='#4e79a7', linewidth=2.5)
            ax1.set_title("Investment Balance Over Time", pad=15)
            ax1.set_xlabel("Years Since Retirement")
            ax1.set_ylabel("Balance (R)")
            ax1.grid(alpha=0.3)
            balance_buf = io.BytesIO()
            fig1.savefig(balance_buf, format='png', dpi=150, bbox_inches='tight')
            balance_buf.seek(0)
            
            fig2, ax2 = plt.subplots(figsize=(10,4))
            ax2.bar(range(year_count), withdrawal_amounts, color='#e15759', alpha=0.7)
            ax2.set_title("Annual Withdrawals", pad=15)
            ax2.set_xlabel("Years Since Retirement")
            ax2.set_ylabel("Amount (R)")
            ax2.grid(alpha=0.3)
            withdrawal_buf = io.BytesIO()
            fig2.savefig(withdrawal_buf, format='png', dpi=150, bbox_inches='tight')
            withdrawal_buf.seek(0)

        # -------------------- INTERACTIVE RESULTS DISPLAY --------------------
        with st.expander("🔍 Detailed Findings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.image(balance_buf, caption="Investment Balance", use_column_width=True)
            with col2:
                st.image(withdrawal_buf, caption="Annual Withdrawals", use_column_width=True)
            
            st.divider()
            st.write(f"""
            **🌡️ Sustainability Analysis**  
            - **Projection Period**: {year_count} years ({la_retirement_age} → {la_retirement_age+year_count})  
            - **Initial Monthly Income**: R{monthly_income:,.2f}  
            - **Final Annual Withdrawal**: R{withdrawal_amounts[-1]:,.2f}  
            - **Peak Balance**: R{max(balances):,.2f} (Year {balances.index(max(balances))})  
            """)
            
            sustainability_ratio = min(year_count/50, 1.0)
            st.progress(sustainability_ratio, 
                       text=f"Sustainability Rating: {'🟢 Excellent' if sustainability_ratio >0.8 else '🟠 Moderate' if sustainability_ratio>0.5 else '🔴 Critical'}")

        # -------------------- PROFESSIONAL REPORT GENERATOR --------------------
        st.subheader("📄 Export Options")
        report_col1, report_col2 = st.columns(2)
        
        with report_col1:
            if st.button("👁️ Preview Report"):
                with st.spinner("🖨️ Preparing preview..."):
                    from fpdf import FPDF
                    import time
                    
                    pdf = FPDF(orientation='P', format='A4')
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Page 1: Cover
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "BHJCF Financial Advisory", ln=True, align='C')
                    pdf.set_font("Arial", 'B', 22)
                    pdf.cell(0, 15, "LIVING ANNUITY PROJECTION REPORT", ln=True, align='C')
                    pdf.ln(8)
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(0, 8, f"Prepared for: Juanita Moolman", ln=True)
                    pdf.cell(0, 8, f"Report Date: {time.strftime('%d %b %Y')}", ln=True)
                    pdf.ln(15)
                    
                    # Key Metrics Table
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(90, 10, "PARAMETER", border=1, fill=True)
                    pdf.cell(0, 10, "VALUE", border=1, fill=True, ln=True)
                    
                    pdf.set_font("Arial", '', 11)
                    for label, value in [
                        ("Current Age", f"{la_current_age} years"),
                        ("Retirement Age", f"{la_retirement_age} years"),
                        ("Total Investment", f"R{investment:,.2f}"),
                        ("Annual Return Rate", f"{la_return*100:.1f}%"),
                        ("Withdrawal Rate", f"{withdrawal_rate*100:.1f}%"),
                        ("Projected Monthly Income", f"R{monthly_income:,.2f}"),
                        ("Sustainability Status", f"{'🟢 SUSTAINABLE' if year_count >=50 else '🔴 DEPLETES AT AGE '+str(la_retirement_age+year_count)}")
                    ]:
                        pdf.cell(90, 8, label, border=1)
                        pdf.cell(0, 8, value, border=1, ln=True)
                    
                    # Page 2: Balance Graph
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "Investment Balance Trajectory", ln=True, align='C')
                    pdf.image(balance_buf, x=10, y=30, w=pdf.w-20)
                    pdf.set_y(100)
                    pdf.set_font("Arial", 'I', 10)
                    pdf.multi_cell(0, 5, 
                        f"Note: Assumes {withdrawal_rate*100:.1f}% annual withdrawals adjusted for returns. "
                        f"Final balance at year {year_count}: R{balances[-1]:,.2f}."
                    )
                    
                    # Page 3: Withdrawals
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "Withdrawal Analysis & Tax Implications", ln=True, align='C')
                    pdf.image(withdrawal_buf, x=10, y=30, w=pdf.w-20)
                    pdf.set_y(100)
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 8, "TAX CONSIDERATIONS", ln=True)
                    pdf.set_font("Arial", '', 10)
                    pdf.multi_cell(0, 5, """
                    • Withdrawals taxed as ordinary income (marginal rate applies)\n
                    • First R500,000 cumulative withdrawals tax-free (lifetime allowance)\n
                    • Annual tax-free portion: R128,900 (2025 tax year)\n
                    • Compulsory annual withdrawals between 2.5%-17.5% of capital
                    """)
                    
                    # Footer
                    pdf.set_y(-15)
                    pdf.set_font("Arial", 'I', 8)
                    pdf.cell(0, 10, f"Generated by BHJCF Studio | {time.strftime('%Y-%m-%d %H:%M')}", 0, 0, 'C')
                    
                    pdf_bytes = pdf.output(dest='S').encode('latin1')
                    st.download_button(
                        label="⬇️ Download Full Report (3 Pages)",
                        data=pdf_bytes,
                        file_name=f"Living_Annuity_Report_{time.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.balloons()

        with report_col2:
            if st.button("📊 Export Data to CSV"):
                import pandas as pd
                df = pd.DataFrame({
                    'Year': range(year_count),
                    'Age': range(la_retirement_age, la_retirement_age+year_count),
                    'Balance': balances,
                    'Withdrawal': withdrawal_amounts
                })
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"living_annuity_simulation_{time.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.toast("CSV exported successfully!", icon="📊")


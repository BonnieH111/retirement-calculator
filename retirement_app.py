# ======================
# ADD THIS NEW IMPORT AT THE TOP
# ======================
from fpdf import FPDF

import streamlit as st
from numpy_financial import fv, pmt
import matplotlib.pyplot as plt
from PIL import Image

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(layout="wide")

# ======================
# ADD PDF FUNCTION HERE
# ======================
def generate_pdf_report(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.set_font_size(24)
    pdf.cell(200, 10, txt="BHJCF Retirement Report", ln=1, align='C')
    pdf.set_font_size(12)
    pdf.cell(200, 10, txt=f"Client: {data['client_name']}", ln=2)
    
    # Calculator Results
    pdf.set_font('', 'B')
    pdf.cell(200, 10, txt="Retirement Calculator Results:", ln=1)
    pdf.set_font('')
    pdf.cell(200, 10, txt=f"At Retirement Value: R{data['future_value']:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Annual Withdrawal: R{data['withdrawal']:,.2f}", ln=1)
    
    # Save PDF
    pdf.output("retirement_report.pdf")
    return open("retirement_report.pdf", "rb").read()

# Rest of your existing CSS and branding code remains unchanged here...
# ======================
# CALCULATOR TABS 
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

with tab1:
    # ======================
    # RETIREMENT CALCULATOR 
    # ======================
    # [ALL YOUR EXISTING CODE HERE UNTIL RESULTS]
    
    # Results 
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

    # ======================
    # ADD PDF BUTTON HERE
    # ======================
    report_data = {
        "client_name": "Juanita Moolman",
        "future_value": future_value,
        "withdrawal": withdrawals[0]
    }
    pdf_bytes = generate_pdf_report(report_data)
    st.download_button(
        label="📑 Download PDF Report",
        data=pdf_bytes,
        file_name="retirement_report.pdf",
        mime="application/pdf",
        key="retire_pdf"
    )

    # [YOUR EXISTING PLOT CODE HERE]

with tab2:
    # ======================
    # LIVING ANNUITY CALCULATOR
    # ======================
    # [ALL YOUR EXISTING CODE HERE UNTIL BUTTON SECTION]
    
    # ======================
    # REPLACE BUTTON SECTION WITH THIS
    # ======================
    st.markdown("""
    <div style='margin: 15px 0; text-align: center;'>
        <p style='color: #666; font-size:14px;'>
        Click the orange button below to calculate projections ▼
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    calculate_btn = st.button("🔥 GENERATE LIVING ANNUITY PLAN", 
                            key="la_btn",
                            help="Click here to run calculations",
                            type="primary")

    if calculate_btn:
        # [YOUR EXISTING CALCULATION CODE HERE]
        
        # Results 
        st.subheader("Projection Results")
        st.markdown(f"""
        <div style='margin: 20px 0;'>
            <span class="custom-r">R</span> 
            <span style='font-size: 18px;'>Monthly income: </span>
            <span style='color: #FF5E00; font-weight: bold;'>R{monthly_income:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)

        # ======================
        # ADD PDF BUTTON HERE
        # ======================
        la_report_data = {
            "client_name": "Juanita Moolman",
            "future_value": monthly_income * 12,
            "withdrawal": monthly_income
        }
        la_pdf = generate_pdf_report(la_report_data)
        st.download_button(
            label="📑 Download PDF Report",
            data=la_pdf,
            file_name="living_annuity_report.pdf",
            mime="application/pdf",
            key="la_pdf"
        )
        # Visualization
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(depletion_years, balances, color='#228B22', linewidth=2)
        ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
        ax.set_title("Investment Balance Timeline", color='#00BFFF')
        ax.set_xlabel("Age", color='#228B22')
        ax.set_ylabel("Remaining Balance (R)", color='#FF5E00')
        st.pyplot(fig)

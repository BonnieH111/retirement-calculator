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

# Centered Logo and Company Name on the Same Line
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(f"""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <img src="data:image/png;base64,{base64.b64encode(open("bhjcf-logo.png", "rb").read()).decode()}" width="65" style='margin-right: 10px;'>
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

        # Generate PDF with preview (FINAL CENTERED VERSION)
    if st.button("📄 Generate PDF Report"):
        try:
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp_graph:
                fig.savefig(tmp_graph.name, dpi=300)
                
                # PDF Setup with Hybrid Layout
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                page_width = pdf.w
                left_margin = 25  # Unified margin for alignment

                # --- Centered Header Section ---
                # Logo and Name on same line
                logo_width = 30
                text_width = pdf.get_string_width("BHJCF Studio")
                total_width = logo_width + text_width + 5  # 5mm spacing
                
                # Calculate starting X position
                x_start = (page_width - total_width) / 2
                pdf.image("bhjcf-logo.png", x=x_start, y=15, w=logo_width)
                pdf.set_xy(x_start + logo_width + 5, 15)
                pdf.cell(0, 10, "BHJCF Studio", align='L')
                
                # --- Centered Title Section ---
                pdf.set_font("Arial", 'B', 20)
                pdf.set_y(40)
                pdf.cell(0, 15, "Retirement Cash Flow Report", align='C')
                
                # --- Client Info ---
                pdf.set_font("Arial", 'B', 12)
                pdf.set_y(60)
                pdf.cell(0, 10, "Client: Juanita Moolman", align='C')

                # --- Data Table ---
                pdf.set_font("Arial", size=12)
                pdf.set_y(75)
                col_width = 80
                data = [
                    # ... keep existing data items ...
                ]
                
                # Aligned to unified left margin
                for label, value in data:
                    pdf.set_x(left_margin)
                    pdf.cell(col_width, 10, label, border=0, align='L')
                    pdf.cell(col_width, 10, str(value), align='L')
                    pdf.ln(10)

                # --- Graph Alignment ---
                img_width = page_width - (left_margin * 2)  # Full width with margins
                pdf.image(tmp_graph.name, 
                         x=left_margin,
                         y=pdf.get_y() + 10, 
                         w=img_width)
                
                # Save PDF
                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    pdf.output(tmp_pdf.name)
                    
                    # Preview
                    with open(tmp_pdf.name, "rb") as f:
                        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
                        pdf_preview = f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="1000px" style="border:none;"></iframe>'
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
        plt.tight_layout()
        st.pyplot(fig_la)
        plt.close()

        # Store calculation results in session state
        st.session_state.la_data = {
            'depletion_years': depletion_years,
            'balances': balances,
            'monthly_income': monthly_income,
            'longevity_text': longevity_text.replace("✅", "[SUCCESS]").replace("⚠️", "[WARNING]"),
            'investment': investment,
            'la_return': la_return,
            'withdrawal_rate': withdrawal_rate,
            'la_current_age': la_current_age,
            'la_retirement_age': la_retirement_age
        }

    # PDF Generation (Landscape A4 Centered)
if st.button("📄 Generate Living Annuity PDF Report"):
    if 'la_data' in st.session_state:
        try:
            data = st.session_state.la_data
            
            # Create new figure for PDF with adjusted size
            fig_pdf, ax_pdf = plt.subplots(figsize=(12,5))  # Shorter height
            ax_pdf.plot(data['depletion_years'], data['balances'], 
                       color='#228B22', linewidth=2)
            ax_pdf.fill_between(data['depletion_years'], data['balances'], 
                              color='#7FFF00', alpha=0.3)
            ax_pdf.set_title("Investment Balance Timeline", color='#00BFFF')
            ax_pdf.set_xlabel("Age", color='#228B22')
            ax_pdf.set_ylabel("Remaining Balance (R)", color='#FF5E00')
            plt.tight_layout()
            
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp_graph:
                fig_pdf.savefig(tmp_graph.name, dpi=300)
                
                pdf = FPDF(orientation='L')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                page_width = pdf.w
                left_margin = 20  # Unified left margin

                # --- Header Section ---
                pdf.image("bhjcf-logo.png", x=left_margin, y=15, w=30)
                pdf.set_xy(left_margin, 40)
                pdf.cell(0, 10, "BHJCF Studio", ln=1, align='L')
                
                # --- Title Section ---
                pdf.set_font("Arial", 'B', 20)
                pdf.set_y(60)
                pdf.cell(0, 15, "Living Annuity Report", align='L')
                
                # --- Client Info ---
                pdf.set_font("Arial", 'B', 12)
                pdf.set_y(80)
                pdf.cell(0, 10, "Client: Juanita Moolman", align='L')

                # --- Expanded Data Table ---
                pdf.set_font("Arial", size=12)
                pdf.set_y(95)
                col_width = 80
                
                data_table = [
                    ("Current Age:", data['la_current_age']),
                    ("Retirement Age:", data['la_retirement_age']),
                    ("Total Investment:", f"R{data['investment']:,.2f}"),
                    ("Annual Return:", f"{data['la_return']*100:.1f}%"),
                    ("Withdrawal Rate:", f"{data['withdrawal_rate']*100:.1f}%"),
                    ("Monthly Income:", f"R{data['monthly_income']:,.2f}"),
                    ("Projection Years:", f"{len(data['balances'])} years"),
                    ("Final Balance:", f"R{data['balances'][-1]:,.2f}" if data['balances'][-1] > 0 else "Depleted"),
                    ("Outlook:", data['longevity_text'])
                ]
                
                # Aligned to left margin
                for label, value in data_table:
                    pdf.set_x(left_margin)
                    pdf.cell(col_width, 10, label, border=0, align='L')
                    pdf.cell(col_width, 10, str(value), align='L')
                    pdf.ln(10)

                # --- Graph Positioning ---
                img_width = page_width - (left_margin * 2)  # Account for margins
                img_height = 100  # Fixed height for visibility
                pdf.image(tmp_graph.name, 
                         x=left_margin,
                         y=pdf.get_y() + 15,  # Extra spacing
                         w=img_width,
                         h=img_height)  # Constrained height
                
                # Save PDF
                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    pdf.output(tmp_pdf.name)
                    
                    # Preview
                    with open(tmp_pdf.name, "rb") as f:
                        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
                        pdf_preview = f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="1000px" style="border:none;"></iframe>'
                        st.markdown(pdf_preview, unsafe_allow_html=True)
                        
                    # Download
                    with open(tmp_pdf.name, "rb") as f:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=f.read(),
                            file_name="Juanita_Living_Annuity_Report.pdf",
                            mime="application/pdf"
                        )
            plt.close(fig_pdf)
        except Exception as e:
            st.error(f"❌ PDF generation failed: {str(e)}")
    else:
        st.warning("⚠️ Please calculate projections first!")

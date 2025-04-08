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
    align-items: baseline !important;  /* Perfect vertical align */
    padding-top: 2px;
    margin-bottom: -4px;
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
# RETIREMENT CASH FLOW TAB 
# ======================
with tab1:
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000, min_value=1000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    with st.expander("🛡️ Inflation Protection"):
        inflation_rate = st.slider("Annual Inflation (%)", 0.0, 5.0, 2.5) / 100
        real_return = annual_return - inflation_rate

    if real_return < 0:
        st.warning("⚠️ Negative real returns may lead to accelerated portfolio depletion")

    years_to_retirement = retirement_age - current_age
    future_value = fv(real_return, years_to_retirement, 0, -retirement_savings)
    years_in_retirement = life_expectancy - retirement_age

    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    # ======================
    # CORRECTED WITHDRAWAL CALCULATION
    # ======================
    balance = future_value
    withdrawals = []
    depletion_age = None
    withdrawal_ages = []
    
    for year in range(years_in_retirement):
        current_age = retirement_age + year
        withdrawal = max(0, round(balance * withdrawal_rate, 2))  # Prevent microscopic withdrawals
        if withdrawal < 10:  # R10 minimum
            st.warning("Withdrawals below R10 detected - consider adjusting parameters")
            break  # Prevent negative withdrawals
        withdrawals.append(withdrawal)
        withdrawal_ages.append(current_age)
        
        # Update balance after withdrawal and growth
        balance = max(0, (balance - withdrawal) * (1 + real_return))  # Never negative
        
        # Track depletion age
        if balance <= 0 and not depletion_age:
            depletion_age = current_age
            balance = 0  # Prevent negative values
            break  # Stop calculations once depleted
    
    # ======================
    # CRITICAL WARNINGS 
    # ======================
    warning_html = ""
    if depletion_age:
        if depletion_age < life_expectancy:
            warning_html = f"""
            <div style='margin: 25px 0; padding: 15px; border-radius: 8px;
                        background-color: #ffe6e6; border-left: 6px solid #ff0000;'>
                <h4 style='color: #ff0000; margin:0;'>⚠️ WARNING: Portfolio Depletion</h4>
                <p style='margin: 10px 0 0 0;'>Funds will run out at age {depletion_age}, 
                {life_expectancy - depletion_age} years before life expectancy!</p>
            </div>
            """
    else:
        warning_html = f"""
        <div style='margin: 25px 0; padding: 15px; border-radius: 8px;
                    background-color: #e6ffe6; border-left: 6px solid #00cc00;'>
            <h4 style='color: #008000; margin:0;'>✅ Sustainable Withdrawals</h4>
            <p style='margin: 10px 0 0 0;'>Portfolio remains stable through life expectancy</p>
        </div>
        """
    
    st.markdown(warning_html, unsafe_allow_html=True)

    if not withdrawals:
        st.error("No withdrawals possible with current parameters")
        st.stop()
    
    # ======================
    # UPDATED VISUALIZATION 
    # ======================
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(withdrawal_ages, withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(withdrawal_ages, withdrawals, color='#7FFF00', alpha=0.3)
    
    if depletion_age:  # Add depletion warning to graph
        ax.axvline(x=depletion_age, color='#000000', linestyle='--', linewidth=1.5)
        ax.text(depletion_age+0.5, withdrawals[0]*0.9, 
                f'Depletion Age: {depletion_age}',
                rotation=90, verticalalignment='top')
    
    ax.set_title("Retirement Income Projection", color='#00BFFF', fontsize=14)
    ax.set_xlabel("Age", color='#228B22', fontsize=12)
    ax.set_ylabel("Annual Income (R)", color='#FF5E00', fontsize=12)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    # ======================
    # PDF UPDATES 
    # ======================
    # Generate PDF with preview (IMPROVED PORTRAIT A4)
    if st.button("📄 Generate PDF Report"):
        with st.spinner("Generating report..."):
            try:
                # Save graph to memory buffer with high DPI
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
                img_buf.seek(0)
                
                # Create PDF in portrait A4 format
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Arial", 'B', 16)
                page_width = pdf.w
                left_margin = 15  # Unified left margin
                right_margin = 15  # Right margin
                usable_width = page_width - left_margin - right_margin

                # --- Header with Logo & Name ---
                logo_width = 25  # Reduced size
                company_name = "BHJCF Studio"
                
                # Calculate centered position
                text_width = pdf.get_string_width(company_name)
                total_width = logo_width + text_width + 5  # 5mm gap
                x_start = (page_width - total_width) / 2
                
                # Draw elements - only add logo if it exists
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=x_start, y=18, w=logo_width)
                
                pdf.set_xy(x_start + logo_width + 5, 20)  # Vertically aligned
                pdf.cell(0, 10, company_name)
                
                # --- Title with decorative underline ---
                pdf.set_font("Arial", 'B', 20)
                pdf.set_y(45)  # Below header
                title = "Retirement Cash Flow Report"
                pdf.cell(0, 10, title, align='C')
                
                # Add decorative underline
                title_width = pdf.get_string_width(title)
                pdf.set_line_width(0.5)
                pdf.set_draw_color(0, 191, 255)  # Light Blue
                pdf.line((page_width - title_width) / 2, 57, (page_width + title_width) / 2, 57)
                
                # --- Client Info ---
                pdf.set_font("Arial", 'B', 12)
                pdf.set_y(65)
                safe_client_name = escape("Juanita Moolman")  # Prevent XSS
                pdf.cell(0, 10, f"Client: {safe_client_name}", align='C')

                # --- Data Table with alternating colors ---
                pdf.set_y(80)  # Below client info
                data = [
                    ("Current Age:", f"{current_age} years"),
                    ("Retirement Age:", f"{retirement_age} years"),
                    ("Current Savings:", f"R{retirement_savings:,.2f}"),
                    ("Annual Return:", f"{annual_return*100:.1f}%"),
                    ("Life Expectancy:", f"{life_expectancy} years"),
                    ("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
                    ("Projected Value at Retirement:", f"R{future_value:,.2f}"),
                    ("First Year Withdrawal:", f"R{withdrawals[0]:,.2f}"),
                    ("Depletion Age:", f"{depletion_age if depletion_age else 'N/A'}")
                ]
                
                # Create a professional table with alternating row colors
                col_width = 60  # Updated column width
                row_height = 10
                
                for i, (label, value) in enumerate(data):
                    # Set background color for alternating rows
                    if i % 2 == 0:
                        pdf.set_fill_color(240, 240, 240)  # Light gray
                    else:
                        pdf.set_fill_color(255, 255, 255)  # White
                    
                    pdf.set_x(left_margin)
                    pdf.set_font("Arial", 'B', 11)
                    pdf.cell(col_width, row_height, label, 0, 0, 'L', True)
                    
                    pdf.set_font("Arial", '', 11)
                    pdf.cell(col_width, row_height, value, 0, 1, 'R', True)

                # --- Graph ---
                graph_y = pdf.get_y() + 10
                
                # Add a title for the graph section
                pdf.set_font("Arial", 'B', 14)
                pdf.set_y(graph_y)
                pdf.cell(0, 10, "Retirement Income Projection", 0, 1, 'C')
                graph_y = pdf.get_y() + 5
                
                # Insert the graph image
                graph_width = usable_width  # Full width within margins
                img = Image.open(img_buf)
                aspect_ratio = img.height / img.width
                pdf.image(img_buf, 
                        x=left_margin, 
                        y=graph_y,
                        w=graph_width,
                        h=graph_width * aspect_ratio)  # Maintain aspect ratio
                
                # Add explanatory note below graph
                pdf.set_y(graph_y + graph_width * aspect_ratio)  # Position below graph
                pdf.set_font("Arial", 'I', 9)
                pdf.set_text_color(100, 100, 100)  # Gray text
                pdf.multi_cell(0, 5, "This projection shows your expected annual income during retirement, adjusted for the specified annual return rate. The green shaded area represents your potential withdrawal amounts over time.", 0, 'L')
                
                # Add a disclaimer
                remaining_space = pdf.h - pdf.get_y() - 40  # 40mm buffer
                if remaining_space < 20:
                    pdf.add_page()
                pdf.set_y(pdf.get_y() + 10)  # Ensure breathing room
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(150, 150, 150)  # Light gray
                pdf.multi_cell(0, 4, "Disclaimer: This projection is for illustrative purposes only and is based on the information provided. Actual results may vary depending on market conditions, inflation, and other economic factors. Please consult with a financial advisor before making investment decisions.", 0, 'C')
                
                # Footer with page number and date
                pdf.set_y(-20)
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(0, 0, 0)  # Black
                pdf.cell(0, 10, f"BHJCF Studio Retirement Calculator | Page {pdf.page_no()}", 0, 0, 'C')
                
                # Save PDF to memory
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_data = pdf_output.getvalue()
                
                # Create columns for success message and download button
                st.success("PDF generated successfully! Click below to download")
                
                # Add direct download button with clear instructions
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_data,
                    file_name="Juanita_Retirement_Report.pdf",
                    mime="application/pdf",
                    help="The PDF is ready! Click to save your personalized report",
                    key="retirement_pdf"  # Unique key for this button
                )
            except Exception as e:
                st.error(f"❌ PDF generation failed: {str(e)}")

# ======================
# LIVING ANNUITY TAB - COMPLETED TAX FUNCTION
# ======================
with tab2:
    # Input columns with validation
    col1, col2, col3 = st.columns(3)
    with col1:
        current_age = st.number_input("Current Age", 45, 100, 65, key="la_age")
    with col2:
        retirement_age = st.number_input("Retirement Age", 55, 100, 65, key="la_retire")
    with col3:
        life_expectancy = st.number_input("Life Expectancy", 75, 120, 90, key="la_life")

    # Validate ages
    if current_age >= life_expectancy:
        st.error("Life expectancy must be greater than current age")
        st.stop()

    # Core parameters
    investment = st.number_input("Annuity Value (R)", value=5_000_000, min_value=100_000, step=50_000, key="la_invest")
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw")/100

    # Market assumptions
    with st.expander("⚙️ Market Parameters"):
        la_return = st.slider("Expected Annual Return (%)", -10.0, 20.0, 7.0)/100
        inflation_rate = st.slider("Annual Inflation (%)", 0.0, 10.0, 4.5)/100
        volatility = st.slider("Market Volatility (Std Dev)", 0.0, 0.3, 0.15)
        monte_carlo_runs = st.selectbox("Simulation Runs", [100, 500, 1000], index=1)

    # COMPLETE TAX FUNCTION (2024 SARS RATES)
    def calculate_tax(withdrawal):
        # 2024 Tax Brackets (Under 65)
        brackets = [
            (237100, 0.18),
           

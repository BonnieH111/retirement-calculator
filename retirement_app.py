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
    logo_paths = [
        "static/bhjcf-logo.png", 
        "attached_assets/IMG_0019.png", 
        "bhjcf-logo.png",
        "generated-icon.png"  # Added as last resort
    ]

    # Debug: print current directory and check all potential paths
    import logging
    logging.info(f"Current directory: {os.getcwd()}")
    for path in logo_paths:
        exists = os.path.exists(path)
        logging.info(f"Checking logo path: {path} - Exists: {exists}")
        if exists:
            return path

    # If we get here, none of the paths worked, so use the attachment directly
    return "attached_assets/IMG_0019.png"  # Return this path even if it doesn't exist

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

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF', fontsize=14)
    ax.set_xlabel("Age", color='#228B22', fontsize=12)
    ax.set_ylabel("Annual Income (R)", color='#FF5E00', fontsize=12)

    # Add proper y-axis formatting for large numbers
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    # Generate PDF with preview (IMPROVED PORTRAIT A4)
    if st.button("📄 Generate PDF Report"):
        try:
            # Create a new figure specifically for the PDF
            fig_pdf = plt.figure(figsize=(10, 6))
            ax_pdf = fig_pdf.add_subplot(111)
            ax_pdf.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
            ax_pdf.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
            ax_pdf.set_title("Retirement Income Projection", color='#00BFFF')
            ax_pdf.set_xlabel("Age", color='#228B22')
            ax_pdf.set_ylabel("Annual Income (R)", color='#FF5E00')
            plt.tight_layout()

            # Save figure to a temporary file (not BytesIO)
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp_graph:
                fig_pdf.savefig(tmp_graph.name, dpi=300)
                plt.close(fig_pdf)

            # Create PDF in portrait A4 format
            pdf = FPDF(orientation='P', format='A4')
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", 'B', 16)
            page_width = pdf.w
            left_margin = 15  # Unified left margin
            right_margin = 15  # Right margin
            usable_width = page_width - left_margin - right_margin

            # Add logo and title
            temp_logo = save_temp_logo()
            if temp_logo:
                logo_width = 20  # mm
                logo_height = 20  # mm
                pdf.image(temp_logo, x=left_margin, y=15, w=logo_width, h=logo_height)
                os.unlink(temp_logo)  # Clean up temporary file

                # Title next to logo
                pdf.set_xy(left_margin + logo_width + 5, 15)
                pdf.cell(0, 10, "BHJCF Studio", ln=True)

                # Subtitle
                pdf.set_font("Arial", '', 12)
                pdf.set_xy(left_margin + logo_width + 5, 25)
                pdf.cell(0, 10, "Retirement Calculator Report", ln=True)
            else:
                # Centered title if no logo
                pdf.cell(0, 10, "BHJCF Studio", 0, 1, 'C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, "Retirement Calculator Report", 0, 1, 'C')

            # Add horizontal line
            pdf.ln(5)
            pdf.line(left_margin, pdf.get_y(), page_width - right_margin, pdf.get_y())
            pdf.ln(10)

            # Client information section
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Client Information", 0, 1, 'L')
            pdf.ln(5)

            # Two-column layout for client details
            pdf.set_font("Arial", '', 11)
            details = [
                ["Current Age:", f"{current_age} years"],
                ["Retirement Age:", f"{retirement_age} years"],
                ["Life Expectancy:", f"{life_expectancy} years"],
                ["Current Savings:", f"R{retirement_savings:,.2f}"],
                ["Annual Return:", f"{annual_return*100:.1f}%"],
                ["Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"]
            ]

            col_width = usable_width / 2
            for detail in details:
                pdf.set_x(left_margin)
                pdf.cell(col_width, 8, detail[0], 0, 0)
                pdf.cell(col_width, 8, detail[1], 0, 1)

            # Add key figures section
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Key Figures", 0, 1, 'L')
            pdf.ln(5)

            pdf.set_font("Arial", '', 11)
            pdf.set_x(left_margin)
            pdf.cell(0, 8, f"Future Value at Retirement: R{future_value:,.2f}", 0, 1)
            pdf.cell(0, 8, f"Initial Annual Withdrawal: R{withdrawals[0]:,.2f}", 0, 1)
            pdf.cell(0, 8, f"Years in Retirement: {years_in_retirement} years", 0, 1)

            # --- Graph ---
            graph_y = pdf.get_y() + 10

            # Add a title for the graph section
            pdf.set_font("Arial", 'B', 14)
            pdf.set_y(graph_y)
            pdf.cell(0, 10, "Retirement Income Projection", 0, 1, 'C')
            graph_y = pdf.get_y() + 5

            # Calculate available vertical space for graph (with room for explanation + disclaimer)
            available_height = pdf.h - graph_y - 60  # Reserve 60mm for explanation, disclaimer, and footer
            graph_height = min(available_height * 0.75, 100)  # Limit max height to 100mm

            # Insert the graph image with dynamic height
            graph_width = usable_width  # Full width within margins
            pdf.image(tmp_graph.name, 
                     x=left_margin, 
                     y=graph_y,
                     w=graph_width,
                     h=graph_height)

            # Add explanatory note below graph (dynamic positioning)
            explanation_y = graph_y + graph_height + 5  # 5mm below the actual graph
            pdf.set_y(explanation_y)
            pdf.set_font("Arial", 'I', 9)
            pdf.set_text_color(100, 100, 100)  # Gray text
            pdf.multi_cell(0, 5, "This projection shows your expected annual income during retirement, adjusted for the specified annual return rate. The green shaded area represents your potential withdrawal amounts over time.", 0, 'L')

            # Add disclaimer at the bottom
            pdf.set_y(-30)  # 30mm from bottom
            pdf.set_font("Arial", 'I', 8)
            pdf.set_text_color(150, 150, 150)  # Light gray
            pdf.multi_cell(0, 4, "Disclaimer: This retirement calculator provides estimates based on the information you've provided and various assumptions about the future. Actual results may vary significantly. Please consult with a qualified financial advisor before making any investment decisions.", 0, 'L')

            # Clean up temporary files
            os.unlink(tmp_graph.name)

            # Save PDF to BytesIO
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_bytes = pdf_output.getvalue()

            # Create download button
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name="retirement_report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.exception(e)

# ======================
# LIVING ANNUITY TAB (ENHANCED)
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

        # Store data in session state for PDF generation
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
            ax1.plot(depletion_years, balances, color='#228B22', linewidth=2.5)
            ax1.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
            ax1.set_title("Investment Balance Timeline", color='#00BFFF', fontsize=14)
            ax1.set_xlabel("Age", color='#228B22', fontsize=12)
            ax1.set_ylabel("Remaining Balance (R)", color='#FF5E00', fontsize=12)
            ax1.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            )
            ax1.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2.5)
            ax2.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
            ax2.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=14)
            ax2.set_xlabel("Age", color='#228B22', fontsize=12)
            ax2.set_ylabel("Withdrawal Amount (R)", color='#FF5E00', fontsize=12)
            ax2.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            )
            ax2.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig2)

    # Check for data in session state to enable PDF button outside the calculate block
    if 'la_data' in st.session_state:
        # Generate PDF button placed outside the calculate block
        generate_pdf_btn = st.button("📄 Generate Living Annuity PDF Report", key="la_pdf_btn")
        if generate_pdf_btn:
            try:
                st.info("Generating PDF report... please wait.")
                # Get data from session state
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

                # Create separate figures for each graph and save to temporary files
                # Balance chart
                fig_balance = plt.figure(figsize=(10, 6))
                ax_balance = fig_balance.add_subplot(111)
                ax_balance.plot(depletion_years, balances, color='#228B22', linewidth=2.5)
                ax_balance.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
                ax_balance.set_title("Investment Balance Timeline", color='#00BFFF', fontsize=14)
                ax_balance.set_xlabel("Age", color='#228B22', fontsize=12)
                ax_balance.set_ylabel("Remaining Balance (R)", color='#FF5E00', fontsize=12)
                ax_balance.get_yaxis().set_major_formatter(
                    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
                )
                ax_balance.grid(True, linestyle='--', alpha=0.7)
                fig_balance.tight_layout()

                # Save balance chart to temporary file
                balance_file = NamedTemporaryFile(delete=False, suffix=".png")
                fig_balance.savefig(balance_file.name, dpi=300, bbox_inches='tight')
                plt.close(fig_balance)

                # Withdrawal chart
                fig_withdrawal = plt.figure(figsize=(10, 6))
                ax_withdrawal = fig_withdrawal.add_subplot(111)
                ax_withdrawal.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2.5)
                ax_withdrawal.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
                ax_withdrawal.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=14)
                ax_withdrawal.set_xlabel("Age", color='#228B22', fontsize=12)
                ax_withdrawal.set_ylabel("Withdrawal Amount (R)", color='#FF5E00', fontsize=12)
                ax_withdrawal.get_yaxis().set_major_formatter(
                    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
                )
                ax_withdrawal.grid(True, linestyle='--', alpha=0.7)
                fig_withdrawal.tight_layout()

                # Save withdrawal chart to temporary file
                withdrawal_file = NamedTemporaryFile(delete=False, suffix=".png")
                fig_withdrawal.savefig(withdrawal_file.name, dpi=300, bbox_inches='tight')
                plt.close(fig_withdrawal)

                # Create PDF
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Add logo and title
                temp_logo = save_temp_logo()
                if temp_logo:
                    pdf.image(temp_logo, x=15, y=15, w=20)
                    os.unlink(temp_logo)

                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Living Annuity Simulation Report", ln=True, align='C')
                pdf.ln(10)

                # Client Information
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Client Information", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", '', 11)
                info_items = [
                    ["Current Age:", f"{la_current_age} years"],
                    ["Retirement Age:", f"{la_retirement_age} years"],
                    ["Investment Amount:", f"R{investment:,.2f}"],
                    ["Annual Return:", f"{la_return*100:.1f}%"],
                    ["Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"]
                ]

                for item in info_items:
                    pdf.cell(60, 8, item[0], 0, 0)
                    pdf.cell(0, 8, item[1], 0, 1)

                pdf.ln(10)

                # Key Results
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Key Results", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", '', 11)
                pdf.cell(0, 8, f"Monthly Income: R{monthly_income:,.2f}", ln=True)
                pdf.cell(0, 8, longevity_text, ln=True)
                pdf.ln(10)

                # Add charts
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Investment Balance Projection", ln=True)
                pdf.image(balance_file.name, x=15, y=None, w=180)
                pdf.ln(120)  # Space for the graph

                pdf.cell(0, 10, "Withdrawal Amount Projection", ln=True)
                pdf.image(withdrawal_file.name, x=15, y=None, w=180)

                # Add disclaimer
                pdf.ln(130)  # Space for the second graph
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(128)
                pdf.multi_cell(0, 4, "Disclaimer: This simulation provides estimates based on the information provided and various assumptions about the future. Actual results may vary significantly. Please consult with a qualified financial advisor before making any investment decisions.", 0, 'L')

                # Clean up temporary files
                os.unlink(balance_file.name)
                os.unlink(withdrawal_file.name)

                # Save and provide download
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_bytes = pdf_output.getvalue()

                st.download_button(
                    label="⬇️ Download Living Annuity PDF Report",
                    data=pdf_bytes,
                    file_name="living_annuity_report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.exception(e)

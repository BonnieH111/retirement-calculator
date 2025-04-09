# ======================
# IMPORTS
# ======================

# Standard Library Imports
import base64
import os
import io
import time
from tempfile import NamedTemporaryFile, TemporaryDirectory

# Third-Party Library Imports
import matplotlib
matplotlib.use('Agg')  # CRITICAL FOR STREAMLIT CLOUD
import matplotlib.pyplot as plt
import numpy as np
from numpy_financial import fv, pmt
from PIL import Image
from fpdf import FPDF
from fpdf.enums import XPos, YPos  # Added for Unicode font support
import streamlit as st

# ======================
# APP CONFIGURATION
# ======================

# Set the page layout and title for the Streamlit app
st.set_page_config(layout="wide", page_title="Retirement Calculator")

# Custom CSS for styling the app
st.markdown("""
<style>
/* Customize slider background color */
.stSlider>div>div>div>div { 
    background: #7FFF00 !important; 
}

/* Custom styling for highlighted text */
.custom-r { 
    color: #FF5E00 !important; 
    font-size: 32px; 
    font-weight: 900;
    display: inline-block;
    margin: 0 2px;
}

/* Styling for the logo column in the header */
.logo-column { 
    padding-right: 0px !important;
    display: flex;
    align-items: center;
}

/* Styling for the company name section */
.company-name { 
    margin-left: -25px !important;
    padding-left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# BRANDING & LOGO FUNCTIONS
# ======================

# Define the default fallback path for the logo
DEFAULT_LOGO_PATH = "attached_assets/IMG_0019.png"

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

    # If no valid path is found, return the default fallback path
    return DEFAULT_LOGO_PATH

def get_logo_as_base64(logo_path):
    """Convert the logo to base64 for embedding in HTML/PDF."""
    try:
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        import logging
        logging.error(f"Error converting logo to Base64: {e}")
    return None

def save_temp_logo():
    """Create a temporary file with the logo for FPDF to use safely."""
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        temp_file = None
        try:
            temp_file = NamedTemporaryFile(delete=False, suffix=".png")
            img = Image.open(logo_path)
            img.save(temp_file.name)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            import logging
            logging.error(f"Error saving temporary logo file: {e}")
            if temp_file:
                os.unlink(temp_file.name)  # Cleanup if file was created but not saved properly
    return None

# Get logo path
logo_path = get_logo_path()
if not logo_path or not os.path.exists(logo_path):
    st.error("⚠️ Logo not found in any of the expected locations")
    logo_path = DEFAULT_LOGO_PATH  # Default to this if it exists

# ======================
# PDF PREVIEW FUNCTION
# ======================
def embed_pdf_preview(pdf_bytes, iframe_height=800):
    """
    Display PDF preview in Streamlit.

    Args:
        pdf_bytes (bytes): The PDF file content in bytes.
        iframe_height (int): The height of the iframe in pixels (default is 800).

    Returns:
        None: Displays the PDF in the Streamlit app.
    """
    if not pdf_bytes:
        st.error("⚠️ No PDF content available to preview.")
        return

    try:
        # Convert PDF bytes to Base64
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Embed PDF in an iframe
        pdf_display = f'''
        <div style="border: 2px solid #00BFFF; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="{iframe_height}px" 
                    style="border: none;">
            </iframe>
        </div>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        # Handle unexpected errors
        st.error(f"⚠️ An error occurred while generating the PDF preview: {str(e)}")
        import logging
        logging.error(f"PDF Preview Error: {e}")

# ======================
# PDF GENERATION: RETIREMENT CASH FLOW
# ======================
def generate_retirement_pdf(client_name, current_age, retirement_age, life_expectancy, future_value, withdrawals):
    """
    Generate a Retirement Cash Flow PDF with client details and income projection graph.

    Args:
        client_name (str): The name of the client.
        current_age (int): The current age of the client.
        retirement_age (int): The retirement age of the client.
        life_expectancy (int): The expected lifespan of the client.
        future_value (float): The future value of savings.
        withdrawals (list): Annual withdrawal amounts over time.

    Returns:
        None: Displays the PDF preview in the Streamlit app.
    """
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

            # Save figure to a temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                graph_path = os.path.join(tmpdir, "graph.png")
                fig_pdf.savefig(graph_path, dpi=300)
                plt.close(fig_pdf)

                # Create PDF in portrait A4 format
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Add Unicode font for emoji support
                pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
                pdf.set_font("DejaVu", "", 11)

                # Add logo and title
                temp_logo = save_temp_logo()
                if temp_logo:
                    pdf.image(temp_logo, x=15, y=15, w=20)
                    os.unlink(temp_logo)  # Clean up temporary file

                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "BHJCF Studio", ln=True, align='C')
                pdf.ln(10)
                pdf.cell(0, 10, "Retirement Calculator Report", ln=True, align='C')
                pdf.ln(20)

                # Add client details
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Client: {client_name}", ln=True)
                pdf.cell(0, 10, f"Current Age: {current_age}", ln=True)
                pdf.cell(0, 10, f"Retirement Age: {retirement_age}", ln=True)
                pdf.cell(0, 10, f"Life Expectancy: {life_expectancy}", ln=True)
                pdf.cell(0, 10, f"Future Savings Value: R{future_value:,.2f}", ln=True)
                pdf.ln(10)

                # Add graph
                pdf.cell(0, 10, "Retirement Income Projection", ln=True, align='C')
                pdf.image(graph_path, x=15, w=180)

                # Add disclaimer
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(128)
                pdf.ln(10)
                pdf.multi_cell(0, 10, "Disclaimer: This report is for informational purposes only. Consult a qualified financial advisor before making any decisions.")

                # Save PDF to BytesIO
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_bytes = pdf_output.getvalue()

                # Embed PDF preview in Streamlit
                embed_pdf_preview(pdf_bytes)

        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            import logging
            logging.error(f"Error in Retirement PDF Generation: {e}")

# ======================
# TAB DEFINITIONS
# ======================

# Create tabs for the app
tab1, tab2, tab3 = st.tabs(["Retirement Calculator", "Living Annuity Simulator", "About"])

# Retirement Calculator Tab
with tab1:
    st.header("Retirement Calculator")
    st.markdown("Use this tool to calculate your retirement savings and withdrawals.")

# Living Annuity Simulator Tab
with tab2:
    st.header("Living Annuity Simulator")
    st.markdown("Simulate your living annuity to determine how long your funds will last.")

# About Tab
with tab3:
    st.header("About")
    st.markdown("""
    This application was developed by **BHJCF Studio** to assist users in planning their retirement.
    For support, please contact us at [support@bhjcfstudio.com](mailto:support@bhjcfstudio.com).
    """)

# ======================
# LIVING ANNUITY SIMULATOR TAB
# ======================

with tab2:
    st.header("Living Annuity Simulator")
    st.markdown("Simulate your living annuity to assess how long your funds will last.")

    # Inputs
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

    # Calculate Projections
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
        longevity_text = (
            f"[DEPLETED] Funds after {year_count} years (age {la_retirement_age + year_count})"
            if balance <= 0
            else f"[SUSTAINABLE] Funds beyond {year_count} years"
        )
        longevity_color = "#FF0000" if balance <= 0 else "#00FF00"

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

# ======================
# LIVING ANNUITY PDF GENERATION
# ======================
if 'la_data' in st.session_state:
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

            # Generate charts and save to temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                balance_path = os.path.join(tmpdir, "balance_chart.png")
                withdrawal_path = os.path.join(tmpdir, "withdrawal_chart.png")

                # Balance chart
                fig1.savefig(balance_path, dpi=300)
                plt.close(fig1)

                # Withdrawal chart
                fig2.savefig(withdrawal_path, dpi=300)
                plt.close(fig2)

                # Create PDF
                pdf = FPDF(orientation='P', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Add Unicode font for emoji support
                pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
                pdf.set_font("DejaVu", "", 11)

                # Add logo and title
                temp_logo = save_temp_logo()
                if temp_logo:
                    pdf.image(temp_logo, x=15, y=15, w=20)
                    os.unlink(temp_logo)

                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Living Annuity Simulation Report", ln=True, align='C')
                pdf.ln(10)

                # Add client information
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Investment Amount: R{investment:,.2f}", ln=True)
                pdf.cell(0, 10, f"Monthly Income: R{monthly_income:,.2f}", ln=True)
                pdf.cell(0, 10, longevity_text, ln=True)
                pdf.ln(10)

                # Add charts
                pdf.cell(0, 10, "Investment Balance Projection", ln=True, align='C')
                pdf.image(balance_path, x=15, w=180)
                pdf.ln(10)
                pdf.cell(0, 10, "Withdrawal Amount Projection", ln=True, align='C')
                pdf.image(withdrawal_path, x=15, w=180)

                # Save PDF to BytesIO
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_bytes = pdf_output.getvalue()

                # Embed PDF preview
                embed_pdf_preview(pdf_bytes)

                # Add download button
                st.download_button(
                    label="⬇️ Download Full Report",
                    data=pdf_bytes,
                    file_name="living_annuity_report.pdf",
                    mime="application/pdf",
                    key="la_download"
                )

        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.exception(e)

# ======================
# RETIREMENT CALCULATOR TAB
# ======================

with tab1:
    st.header("Retirement Calculator")
    st.markdown("Plan your retirement by calculating how your savings and withdrawals align with your goals.")

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        current_age = st.slider("Current Age", 25, 100, 45, key="rc_age")
    with col2:
        retirement_age = st.slider("Retirement Age", 55, 100, 65, key="rc_retire")

    if retirement_age <= current_age:
        st.error("❌ Retirement age must be AFTER current age!")
        st.stop()

    # Financial Inputs
    future_savings = st.number_input("Future Value of Savings (R)", value=1000000, step=10000, key="rc_savings")
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 1.0, 10.0, 4.0, key="rc_withdraw") / 100
    annual_return = st.slider("Expected Annual Return (%)", 1.0, 20.0, 7.0, key="rc_return") / 100

    # Calculate Projections
    calculate_btn = st.button("🚀 CALCULATE RETIREMENT PROJECTIONS", key="rc_btn")
    if calculate_btn:
        try:
            # Annual Withdrawal Calculation
            annual_withdrawal = future_savings * withdrawal_rate
            monthly_withdrawal = annual_withdrawal / 12

            # Simulation
            balance = future_savings
            year_count = 0
            depletion_years = []
            balances = []

            while balance > 0 and year_count < 50:
                withdrawal = annual_withdrawal
                balance = (balance - withdrawal) * (1 + annual_return)
                depletion_years.append(retirement_age + year_count)
                balances.append(balance)
                year_count += 1

            # Longevity Assessment
            longevity_text = (
                f"[DEPLETED] Funds after {year_count} years (age {retirement_age + year_count})"
                if balance <= 0
                else f"[SUSTAINABLE] Funds beyond {year_count} years"
            )
            longevity_color = "#FF0000" if balance <= 0 else "#00FF00"

            # Display Results
            st.markdown(f"""
            <div style='margin: 20px 0;'>
                <h3>Annual Withdrawal</h3>
                <p style='font-size: 24px; color: #00BFFF;'>R{annual_withdrawal:,.2f}</p>
                <h3>Monthly Withdrawal</h3>
                <p style='font-size: 24px; color: #00BFFF;'>R{monthly_withdrawal:,.2f}</p>
                <p style='color: {longevity_color};'>{longevity_text}</p>
            </div>
            """, unsafe_allow_html=True)

            # Store data in session state for PDF generation
            st.session_state.rc_data = {
                'depletion_years': depletion_years,
                'balances': balances,
                'annual_withdrawal': annual_withdrawal,
                'monthly_withdrawal': monthly_withdrawal,
                'longevity_text': longevity_text,
                'future_savings': future_savings,
                'withdrawal_rate': withdrawal_rate,
                'annual_return': annual_return,
                'current_age': current_age,
                'retirement_age': retirement_age,
                'year_count': year_count
            }

            # Create and display graph
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(depletion_years, balances, color='#228B22', linewidth=2.5)
            ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
            ax.set_title("Retirement Savings Projection", color='#00BFFF', fontsize=16)
            ax.set_xlabel("Age", color='#228B22', fontsize=12)
            ax.set_ylabel("Remaining Balance (R)", color='#FF5E00', fontsize=12)
            ax.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
            )
            ax.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error("An error occurred during calculation. Please check your inputs.")
            st.exception(e)

    # PDF Generation for Retirement Calculator
    if 'rc_data' in st.session_state:
        generate_pdf_btn = st.button("📄 Generate Retirement Calculator PDF Report", key="rc_pdf_btn")
        if generate_pdf_btn:
            st.info("Generating PDF report... please wait.")
            # Call a function to generate the PDF (reuse PDF generation logic)
            generate_retirement_pdf(
                client_name="Client",
                current_age=st.session_state.rc_data['current_age'],
                retirement_age=st.session_state.rc_data['retirement_age'],
                life_expectancy=st.session_state.rc_data['retirement_age'] + st.session_state.rc_data['year_count'],
                future_value=st.session_state.rc_data['future_savings'],
                withdrawals=[st.session_state.rc_data['annual_withdrawal']] * st.session_state.rc_data['year_count']
            )

# ======================
# APP CONFIGURATION
# ======================

# Set the page layout and title for the Streamlit app
st.set_page_config(layout="wide", page_title="Retirement Calculator")

# Custom CSS for styling the app
st.markdown("""
<style>
/* Customize slider background color */
.stSlider>div>div>div>div { 
    background: #7FFF00 !important; 
}

/* Custom styling for highlighted text */
.custom-r { 
    color: #FF5E00 !important; 
    font-size: 32px; 
    font-weight: 900;
    display: inline-block;
    margin: 0 2px;
}

/* Styling for the logo column in the header */
.logo-column { 
    padding-right: 0px !important;
    display: flex;
    align-items: center;
}

/* Styling for the company name section */
.company-name { 
    margin-left: -25px !important;
    padding-left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE MANAGEMENT
# ======================

# Initialize session state variables if they don't exist
if "la_data" not in st.session_state:
    st.session_state.la_data = {}

if "rc_data" not in st.session_state:
    st.session_state.rc_data = {}

# Debugging: Log the current session state
import logging
logging.info(f"Session State: {st.session_state}")

# ======================
# UTILITIES
# ======================

import os
import base64
from tempfile import NamedTemporaryFile
from PIL import Image
import io

def get_logo_path():
    """Find the path to the logo image."""
    logo_paths = [
        "static/bhjcf-logo.png", 
        "attached_assets/IMG_0019.png", 
        "bhjcf-logo.png",
        "generated-icon.png"  # Added as last resort
    ]

    for path in logo_paths:
        if os.path.exists(path):
            return path
    return "attached_assets/IMG_0019.png"  # Default fallback

def get_logo_as_base64(logo_path):
    """Convert the logo to base64 for embedding in HTML/PDF."""
    try:
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting logo to Base64: {e}")
    return None

def save_temp_logo():
    """Create a temporary file with the logo for safe use with FPDF."""
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        try:
            temp_file = NamedTemporaryFile(delete=False, suffix=".png")
            img = Image.open(logo_path)
            img.save(temp_file.name)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Error saving temporary logo file: {e}")
    return None

def embed_pdf_preview(pdf_bytes):
    """Display PDF preview in Streamlit."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'''
    <div style="border: 2px solid #00BFFF; border-radius: 10px; padding: 20px; margin: 20px 0;">
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="800px" 
                style="border: none;">
        </iframe>
    </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# ======================
# MAIN SCRIPT
# ======================

# Import necessary modules and components
import streamlit as st
from matplotlib import pyplot as plt
import matplotlib.ticker
from utilities import embed_pdf_preview, save_temp_logo, get_logo_path
from retirement_cashflow_pdf import generate_retirement_pdf
from session_state_management import *  # Initialize session state
from app_configuration import *        # Apply app configuration

# Header Section
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div>
        <h1 style="color: #00BFFF; margin-bottom: 0;">Retirement Calculator App</h1>
        <p style="font-size: 18px; color: #228B22;">Plan your financial future with confidence.</p>
    </div>
    <div style="text-align: right;">
        <img src="data:image/png;base64,{}" alt="Logo" style="width: 100px; height: auto;"/>
    </div>
</div>
""".format(get_logo_as_base64(get_logo_path())), unsafe_allow_html=True)

# Tabs Section
tab1, tab2, tab3 = st.tabs(["Retirement Calculator", "Living Annuity Simulator", "About"])

# Include functionality for each tab
from retirement_calculator_tab import *  # Retirement Calculator
from living_annuity_simulator_tab import *  # Living Annuity Simulator
from about_tab import *  # About Tab

# ======================
# ERROR HANDLING AND LOGGING
# ======================

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs during development
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # Output logs to the console
        logging.FileHandler("app_logs.log", mode="a")  # Save logs to a file
    ]
)

# Global error handler
def log_and_display_error(error_message, exception=None):
    """
    Logs an error and displays it to the user in Streamlit.
    
    Args:
        error_message (str): The error message to display.
        exception (Exception, optional): The exception object to log (if any).
    """
    logging.error(error_message)
    if exception:
        logging.exception(exception)
    st.error(f"🚨 {error_message}")
    if exception:
        st.exception(exception)

# ======================
# PDF GENERATION
# ======================

from fpdf import FPDF
import os
import matplotlib.pyplot as plt

def generate_retirement_pdf(client_name, current_age, retirement_age, life_expectancy, future_value, withdrawals):
    """
    Generates a PDF report for the retirement cash flow simulation.

    Args:
        client_name (str): The name of the client.
        current_age (int): Current age of the client.
        retirement_age (int): Retirement age of the client.
        life_expectancy (int): Estimated age when the funds are depleted.
        future_value (float): Future value of savings or investments.
        withdrawals (list): Annual withdrawal amounts.
    """
    try:
        # Create a PDF instance
        pdf = FPDF(orientation='P', format='A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Add Unicode font for emoji support
        pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
        pdf.set_font("DejaVu", "", 11)

        # Add logo and title
        temp_logo = save_temp_logo()
        if temp_logo:
            pdf.image(temp_logo, x=15, y=15, w=20)
            os.unlink(temp_logo)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Retirement Cash Flow Simulation Report", ln=True, align='C')
        pdf.ln(10)

        # Add client information
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Client Name: {client_name}", ln=True)
        pdf.cell(0, 10, f"Current Age: {current_age}", ln=True)
        pdf.cell(0, 10, f"Retirement Age: {retirement_age}", ln=True)
        pdf.cell(0, 10, f"Life Expectancy (Funds Depleted): {life_expectancy}", ln=True)
        pdf.cell(0, 10, f"Future Value of Savings: R{future_value:,.2f}", ln=True)
        pdf.ln(10)

        # Add withdrawal chart
        pdf.cell(0, 10, "Annual Withdrawal Projection", ln=True, align='C')
        withdrawal_chart_path = generate_withdrawal_chart(withdrawals, retirement_age)
        if withdrawal_chart_path:
            pdf.image(withdrawal_chart_path, x=15, w=180)

        # Save PDF to BytesIO
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_bytes = pdf_output.getvalue()

        # Return the PDF bytes for downloading or preview
        return pdf_bytes

    except Exception as e:
        log_and_display_error("Failed to generate the PDF report.", e)

def generate_withdrawal_chart(withdrawals, retirement_age):
    """
    Creates a chart for annual withdrawals and saves it as a temporary image.

    Args:
        withdrawals (list): Annual withdrawal amounts.
        retirement_age (int): Retirement age of the client.

    Returns:
        str: Path to the saved chart image.
    """
    try:
        # Generate chart
        fig, ax = plt.subplots(figsize=(8, 5))
        years = [retirement_age + i for i in range(len(withdrawals))]
        ax.plot(years, withdrawals, color='#FF0000', linewidth=2.5)
        ax.fill_between(years, withdrawals, color='#FFAA33', alpha=0.3)
        ax.set_title("Annual Withdrawals", color='#FF5E00', fontsize=14)
        ax.set_xlabel("Age", color='#228B22', fontsize=12)
        ax.set_ylabel("Withdrawal Amount (R)", color='#FF5E00', fontsize=12)
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"R{int(x):,}")
        )
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save as a temporary file
        temp_file = NamedTemporaryFile(delete=False, suffix=".png")
        chart_path = temp_file.name
        plt.savefig(chart_path, dpi=300)
        plt.close(fig)

        return chart_path

    except Exception as e:
        log_and_display_error("Failed to generate the withdrawal chart.", e)
        return None

# ======================
# PDF PREVIEW
# ======================

import base64

def display_pdf_preview(pdf_bytes):
    """
    Displays a PDF preview within the Streamlit app.

    Args:
        pdf_bytes (bytes): The PDF content as bytes.
    """
    try:
        # Convert PDF bytes to Base64 for embedding
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Create an iframe to display the PDF preview
        st.markdown(f"""
        <div style="border: 2px solid #00BFFF; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <h4 style="text-align:center; color:#228B22;">PDF Preview</h4>
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="800px" 
                    style="border: none;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        log_and_display_error("Failed to display the PDF preview.", e)

# Example Usage (inside tabs or app flow)
if 'rc_data' in st.session_state:  # Example for Retirement Calculator
    if st.session_state.get('rc_pdf_bytes'):  # Check if PDF bytes exist
        st.markdown("---")  # Add a divider for better UI
        display_pdf_preview(st.session_state['rc_pdf_bytes'])
    else:
        st.info("No PDF generated yet. Please calculate and generate the PDF to view the preview.")

# ======================
# HELPER FUNCTIONS & UTILITIES
# ======================

def format_currency(value):
    """Format numbers as currency (e.g., R1,000,000.00)."""
    return f"R{value:,.2f}"

def render_error(message):
    """Render a styled error message in Streamlit."""
    st.markdown(f"""
    <div style='border: 2px solid #FF0000; padding: 10px; margin: 10px 0; border-radius: 5px; background: #FFE6E6;'>
        <p style='color: #FF0000; font-weight: bold;'>{message}</p>
    </div>
    """, unsafe_allow_html=True)

def render_success(message):
    """Render a styled success message in Streamlit."""
    st.markdown(f"""
    <div style='border: 2px solid #00FF00; padding: 10px; margin: 10px 0; border-radius: 5px; background: #E6FFE6;'>
        <p style='color: #228B22; font-weight: bold;'>{message}</p>
    </div>
    """, unsafe_allow_html=True)

# ======================
# CLEANUP FUNCTIONALITY
# ======================

def cleanup_temp_files():
    """Delete temporary files to avoid clutter or locking issues."""
    try:
        temp_dir = tempfile.gettempdir()
        for temp_file in os.listdir(temp_dir):
            if temp_file.endswith(".png") or temp_file.endswith(".pdf"):
                os.remove(os.path.join(temp_dir, temp_file))
    except Exception as e:
        st.warning(f"⚠️ Cleanup encountered an issue: {str(e)}")

# ======================
# SESSION STATE MANAGEMENT
# ======================

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['la_data'] = {}

# ======================
# FOOTER SECTION
# ======================

def render_footer():
    """Display footer with acknowledgment."""
    st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 14px; color: #555;">
        Developed by <strong>BHJCF Studio</strong>. For assistance, contact support at <a href="mailto:support@bhjcfstudio.com">support@bhjcfstudio.com</a>.
    </p>
    <p style="text-align: center; font-size: 12px; color: #888;">
        © 2025 BHJCF Studio. All rights reserved.
    </p>
    """, unsafe_allow_html=True)

# Render Footer
render_footer()

# ======================
# FINAL INTEGRATION
# ======================

# Perform Cleanup
cleanup_temp_files()

# Final Message

# Final Message with consistent styling
st.markdown("""
<div style='border: 2px solid #4CAF50; 
            padding: 15px; 
            border-radius: 5px;
            background: #E8F5E9;
            margin: 20px 0;
            text-align: center;
            font-size: 16px;
            color: #1B5E20;'>
    ✅ Your Retirement Calculator is ready to use! 🎉
</div>
""", unsafe_allow_html=True) 



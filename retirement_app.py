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
from fpdf.enums import XPos, YPos  # Added for Unicode font support
import os
import io
import numpy as np
import time
import tempfile  # Added to handle temporary files safely

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
# PDF PREVIEW FUNCTION
# ======================
def embed_pdf_preview(pdf_bytes):
    """Display PDF preview in Streamlit"""
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
# PDF GENERATION: RETIREMENT CASH FLOW
# ======================
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
            pdf.cell(0, 10, f"Client: Juanita Moolman", ln=True)
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
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return") / 100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw") / 100

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
            longevity_text = f"[DEPLETED] Funds after {year_count} years (age {la_retirement_age + year_count})"
            longevity_color = "#FF0000"
        else:
            longevity_text = f"[SUSTAINABLE] Funds beyond {year_count} years"
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
                with tempfile.TemporaryDirectory() as tmpdir:
                    balance_path = os.path.join(tmpdir, "balance_graph.png")
                    withdrawal_path = os.path.join(tmpdir, "withdrawal_graph.png")

                    # Save Balance chart
                    fig1.savefig(balance_path, dpi=300, bbox_inches='tight')
                    plt.close(fig1)

                    # Save Withdrawal chart
                    fig2.savefig(withdrawal_path, dpi=300, bbox_inches='tight')
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
# LIVING ANNUITY SIMULATOR TAB
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
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return") / 100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw") / 100

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
            longevity_text = f"[DEPLETED] Funds after {year_count} years (age {la_retirement_age + year_count})"
            longevity_color = "#FF0000"
        else:
            longevity_text = f"[SUSTAINABLE] Funds beyond {year_count} years"
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

    # PDF Generation for Living Annuity
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

# ======================
# FINAL INTEGRATION
# ======================

# Render Footer
render_footer()

# Perform Cleanup
cleanup_temp_files()

# Final Message
st.success("Your Retirement Calculator is ready to use! 🎉")



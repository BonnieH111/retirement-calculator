# retirement_app.py
# ====================== IMPORTS ======================
import base64
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg') # CRITICAL FOR STREAMLIT CLOUD
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
logo_path = "attached_assets/IMG_0019.png" # Default to this if it exists

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

fig, ax = plt.subplots(figsize=(10, 6)) # Adjusted height to prevent cutoff
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
plt.tight_layout() # Ensures the graph fits properly
st.pyplot(fig)

# Generate PDF with preview (IMPROVED PORTRAIT A4)
if st.button("📄 Generate PDF Report"):
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
left_margin = 15 # Unified left margin
right_margin = 15 # Right margin
usable_width = page_width - left_margin - right_margin

# --- Header with Logo & Name ---
logo_width = 25 # Reduced size
company_name = "BHJCF Studio"

# Calculate centered position
text_width = pdf.get_string_width(company_name)
total_width = logo_width + text_width + 5 # 5mm gap
x_start = (page_width - total_width) / 2

# Draw elements - only add logo if it exists
if os.path.exists(logo_path):
pdf.image(logo_path, x=x_start, y=15, w=logo_width)

pdf.set_xy(x_start + logo_width + 5, 17) # Vertically aligned
pdf.cell(0, 10, company_name)

# --- Title with decorative underline ---
pdf.set_font("Arial", 'B', 20)
pdf.set_y(45) # Below header
title = "Retirement Cash Flow Report"
pdf.cell(0, 10, title, align='C')

# Add decorative underline
title_width = pdf.get_string_width(title)
pdf.set_line_width(0.5)
pdf.set_draw_color(0, 191, 255) # Light Blue
pdf.line((page_width - title_width) / 2, 57, (page_width + title_width) / 2, 57)

# --- Client Info ---
pdf.set_font("Arial", 'B', 12)
pdf.set_y(65)
pdf.cell(0, 10, "Client: Juanita Moolman", align='C')

# --- Data Table with alternating colors ---
pdf.set_y(80) # Below client info
data = [
("Current Age:", f"{current_age} years"),
("Retirement Age:", f"{retirement_age} years"),
("Current Savings:", f"R{retirement_savings:,.2f}"),
("Annual Return:", f"{annual_return*100:.1f}%"),
("Life Expectancy:", f"{life_expectancy} years"),
("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
("Projected Value at Retirement:", f"R{future_value:,.2f}"),
("First Year Withdrawal:", f"R{withdrawals[0]:,.2f}")
]

# Create a professional table with alternating row colors
col_width = usable_width / 2
row_height = 10

for i, (label, value) in enumerate(data):
# Set background color for alternating rows
if i % 2 == 0:
pdf.set_fill_color(240, 240, 240) # Light gray
else:
pdf.set_fill_color(255, 255, 255) # White

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
graph_width = usable_width # Full width within margins
pdf.image(img_buf,
x=left_margin,
y=graph_y,
w=graph_width)

# Add explanatory note below graph
pdf.set_y(graph_y + 85) # Position below graph
pdf.set_font("Arial", 'I', 9)
pdf.set_text_color(100, 100, 100) # Gray text
pdf.multi_cell(0, 5, "This projection shows your expected annual income during retirement, adjusted for the specified annual return rate. The green shaded area represents your potential withdrawal amounts over time.", 0, 'L')

# Add a disclaimer
pdf.set_y(-40) # 40mm from bottom
pdf.set_font("Arial", 'I', 8)
pdf.set_text_color(150, 150, 150) # Light gray
pdf.multi_cell(0, 4, "Disclaimer: This projection is for illustrative purposes only and is based on the information provided. Actual results may vary depending on market conditions, inflation, and other economic factors. Please consult with a financial advisor before making investment decisions.", 0, 'C')

# Footer with page number and date
pdf.set_y(-20)
pdf.set_font("Arial", 'I', 8)
pdf.set_text_color(0, 0, 0) # Black
pdf.cell(0, 10, f"BHJCF Studio Retirement Calculator | Page {pdf.page_no()}", 0, 0, 'C')

# Save PDF to memory
pdf_output = io.BytesIO()
pdf.output(pdf_output)
pdf_data = pdf_output.getvalue()

# Create columns for success message and download button
col1, col2 = st.columns([1, 1])
with col1:
st.success("PDF generated successfully!")
with col2:
# Download button
st.download_button(
label="⬇️ Download PDF Report",
data=pdf_data,
file_name="Juanita_Retirement_Report.pdf",
mime="application/pdf",
help="Click to download your PDF report"
)
except Exception as e:
st.error(f"❌ PDF generation failed: {str(e)}")

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

# Enhanced visualization with two subplots
fig_la = plt.figure(figsize=(12, 10))

# Create a 2-row layout
gs = fig_la.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.3)

# First subplot: Investment Balance
ax1 = fig_la.add_subplot(gs[0])
ax1.plot(depletion_years, balances, color='#228B22', linewidth=2.5)
ax1.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
ax1.set_title("Investment Balance Timeline", color='#00BFFF', fontsize=16)
ax1.set_xlabel("Age", color='#228B22', fontsize=12)
ax1.set_ylabel("Remaining Balance (R)", color='#FF5E00', fontsize=12)

# Add proper formatting to y-axis for large numbers
ax1.get_yaxis().set_major_formatter(
matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
)

# Add grid for better readability
ax1.grid(True, linestyle='--', alpha=0.7)

# Second subplot: Annual Withdrawal
ax2 = fig_la.add_subplot(gs[1])
ax2.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2.5)
ax2.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
ax2.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=16)
ax2.set_xlabel("Age", color='#228B22', fontsize=12)
ax2.set_ylabel("Withdrawal Amount (R)", color='#FF0000', fontsize=12)

# Add proper formatting to y-axis for large numbers
ax2.get_yaxis().set_major_formatter(
matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
)

# Add grid for better readability
ax2.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
st.pyplot(fig_la)

# Summary metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
st.metric(
label="Initial Annual Withdrawal",
value=f"R{withdrawal_amounts[0]:,.2f}"
)

with col2:
final_withdrawal = withdrawal_amounts[-1] if withdrawal_amounts else 0
st.metric(
label=f"Final Withdrawal (Age {depletion_years[-1] if depletion_years else 0})",
value=f"R{final_withdrawal:,.2f}"
)

with col3:
st.metric(
label="Longevity",
value=f"{year_count} years",
delta="Good" if year_count >= 30 else "Review" if year_count >= 20 else "Warning"
)

# Store calculation results in session state
st.session_state.la_data = {
'depletion_years': depletion_years,
'balances': balances,
'withdrawal_amounts': withdrawal_amounts,
'monthly_income': monthly_income,
'longevity_text': longevity_text.replace("✅", "[SUCCESS]").replace("⚠️", "[WARNING]"),
'investment': investment,
'la_return': la_return,
'withdrawal_rate': withdrawal_rate,
'la_current_age': la_current_age,
'la_retirement_age': la_retirement_age,
'year_count': year_count
}

# Generate PDF button placed directly in the annuity section
if st.button("📄 Generate Living Annuity PDF Report", key="la_pdf_btn"):
try:
# Save both graphs to memory buffers with high DPI
balance_buf = io.BytesIO()
withdrawal_buf = io.BytesIO()

# Create separate figures for each graph for better PDF layout
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
fig_balance.savefig(balance_buf, format='png', dpi=300, bbox_inches='tight')
balance_buf.seek(0)

# Withdrawal chart
fig_withdrawal = plt.figure(figsize=(10, 6))
ax_withdrawal = fig_withdrawal.add_subplot(111)
ax_withdrawal.plot(depletion_years, withdrawal_amounts, color='#FF0000', linewidth=2.5)
ax_withdrawal.fill_between(depletion_years, withdrawal_amounts, color='#FFAA33', alpha=0.3)
ax_withdrawal.set_title("Annual Withdrawal Amounts", color='#FF5E00', fontsize=14)
ax_withdrawal.set_xlabel("Age", color='#228B22', fontsize=12)
ax_withdrawal.set_ylabel("Withdrawal Amount (R)", color='#FF0000', fontsize=12)
ax_withdrawal.get_yaxis().set_major_formatter(
matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
)
ax_withdrawal.grid(True, linestyle='--', alpha=0.7)
fig_withdrawal.tight_layout()
fig_withdrawal.savefig(withdrawal_buf, format='png', dpi=300, bbox_inches='tight')
withdrawal_buf.seek(0)

# Create PDF in portrait A4 format
pdf = FPDF(orientation='P', format='A4')

# ===== PAGE 1: OVERVIEW & BALANCE CHART =====
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", 'B', 16)
page_width = pdf.w
left_margin = 15
right_margin = 15
usable_width = page_width - left_margin - right_margin

# --- Header with Logo & Name ---
logo_width = 25 # Reduced size
company_name = "BHJCF Studio"

# Calculate centered position
text_width = pdf.get_string_width(company_name)
total_width = logo_width + text_width + 5 # 5mm gap
x_start = (page_width - total_width) / 2

# Draw elements - ensure logo exists
if os.path.exists(logo_path):
pdf.image(logo_path, x=x_start, y=15, w=logo_width)
pdf.set_xy(x_start + logo_width + 5, 17) # Vertically aligned
pdf.cell(0, 10, company_name)

# --- Title with decorative underline ---
pdf.set_font("Arial", 'B', 20)
pdf.set_y(45) # Below header
title = "Living Annuity Projection Report"
pdf.cell(0, 10, title, align='C')

# Add decorative underline
title_width = pdf.get_string_width(title)
pdf.set_line_width(0.5)
pdf.set_draw_color(0, 191, 255) # Light Blue
pdf.line((page_width - title_width) / 2, 57, (page_width + title_width) / 2, 57)

# --- Client Info ---
pdf.set_font("Arial", 'B', 12)
pdf.set_y(65)
pdf.cell(0, 10, "Client: Juanita Moolman", align='C')

# --- Data Table with alternating colors ---
pdf.set_y(80) # Below client info
data = [
("Current Age:", f"{la_current_age} years"),
("Retirement Age:", f"{la_retirement_age} years"),
("Total Investment:", f"R{investment:,.2f}"),
("Annual Return:", f"{la_return*100:.1f}%"),
("Withdrawal Rate:", f"{withdrawal_rate*100:.1f}%"),
("Monthly Income:", f"R{monthly_income:,.2f}"),
("Longevity:", f"{year_count} years"),
("Status:", f"{longevity_text.replace('✅', '').replace('⚠️', '')}")
]

# Create a professional table with alternating row colors
col_width = usable_width / 2
row_height = 10

for i, (label, value) in enumerate(data):
# Set background color for alternating rows
if i % 2 == 0:
pdf.set_fill_color(240, 240, 240) # Light gray
else:
pdf.set_fill_color(255, 255, 255) # White

pdf.set_x(left_margin)
pdf.set_font("Arial", 'B', 11)
pdf.cell(col_width, row_height, label, 0, 0, 'L', True)

pdf.set_font("Arial", '', 11)
pdf.cell(col_width, row_height, value, 0, 1, 'R', True)

# --- Balance Graph ---
graph_y = pdf.get_y() + 10

# Add a title for the graph section
pdf.set_font("Arial", 'B', 14)
pdf.set_y(graph_y)
pdf.cell(0, 10, "Investment Balance Timeline", 0, 1, 'C')
graph_y = pdf.get_y() + 5

# Insert the graph image
graph_width = usable_width # Full width within margins
pdf.image(balance_buf,
x=left_margin,
y=graph_y,
w=graph_width)

# Add explanatory note below graph
pdf.set_y(graph_y + 85) # Position below graph
pdf.set_font("Arial", 'I', 9)
pdf.set_text_color(100, 100, 100) # Gray text
pdf.multi_cell(0, 5, "This chart shows your projected investment balance over time. The green area represents your remaining capital as you age.", 0, 'L')

# ===== PAGE 2: WITHDRAWAL CHART & TAX INFO =====
pdf.add_page()

# --- Header with Logo & Name (repeated for page 2) ---
pdf.set_font("Arial", 'B', 16)
if os.path.exists(logo_path):
pdf.image(logo_path, x=x_start, y=15, w=logo_width)
pdf.set_xy(x_start + logo_width + 5, 17)
pdf.cell(0, 10, company_name)

# --- Page 2 Title ---
pdf.set_font("Arial", 'B', 16)
pdf.set_y(40)
pdf.cell(0, 10, "Annual Withdrawal Projection", align='C')

# --- Withdrawal Graph ---
graph_y = 55

# Insert the withdrawal graph image
pdf.image(withdrawal_buf,
x=left_margin,
y=graph_y,
w=graph_width)

# Add explanatory note below graph
pdf.set_y(graph_y + 85)
pdf.set_font("Arial", 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 5, "This chart shows your projected annual withdrawal amounts. The orange area represents the money available for your yearly expenses.", 0, 'L')

# --- Tax Information Section (Optional, added for value) ---
pdf.set_y(graph_y + 100)
pdf.set_font("Arial", 'B', 14)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 10, "Tax Considerations", 0, 1, 'L')

pdf.set_font("Arial", '', 10)
tax_info = """
Withdrawals from living annuities are taxed as income in South Africa. The applicable tax rates depend on your total taxable income for the year. Here's a general overview:

1. Your withdrawals are added to your other income and taxed according to SARS income tax tables.
2. At retirement, you may receive a portion of your retirement interest tax-free (up to R500,000 lifetime limit).
3. The withdrawal rate you choose (between 2.5% and 17.5%) affects your long-term tax efficiency.
4. Lower withdrawal rates may lead to estate duty implications, while higher rates may deplete your capital.

Consult with a tax professional for personalized advice based on your specific situation.
"""
pdf.multi_cell(0, 5, tax_info, 0, 'L')

# Add a disclaimer to both pages
pdf.set_y(-40)
pdf.set_font("Arial", 'I', 8)
pdf.set_text_color(150, 150, 150)
pdf.multi_cell(0, 4, "Disclaimer: This projection is for illustrative purposes only and is based on the information provided. Actual results may vary depending on market conditions, inflation, and other economic factors. Please consult with a financial advisor before making investment decisions.", 0, 'C')

# Footer with page number
pdf.set_y(-20)
pdf.set_font("Arial", 'I', 8)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 10, f"BHJCF Studio Living Annuity Calculator | Page {pdf.page_no()} of 2", 0, 0, 'C')

# Save PDF to memory
pdf_output = io.BytesIO()
pdf.output(pdf_output)
pdf_data = pdf_output.getvalue()

# Create columns for success message and download button
col1, col2 = st.columns([1, 1])
with col1:
st.success("Living Annuity PDF generated successfully!")
with col2:
# Download button
st.download_button(
label="⬇️ Download Living Annuity Report",
data=pdf_data,
file_name="Juanita_Living_Annuity_Report.pdf",
mime="application/pdf",
help="Click to download your detailed Living Annuity PDF report"
)
except Exception as e:
st.error(f"❌ PDF generation failed: {str(e)}")
st.error(f"Details: {type(e).__name__}") 


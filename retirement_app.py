# retirement_app.py
# ====================== IMPORTS ======================
import base64
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')  # CRITICAL FOR STREAMLIT CLOUD

import streamlit as st
from numpy_financial import fv, pmt
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from PIL import Image
from fpdf import FPDF
import os
import io

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(layout="wide", page_title="BHJCF Retirement Calculator")

# ----------------------
# CUSTOM CSS
# ----------------------
st.markdown("""
<style>
  .stSlider>div>div>div>div { background: #7FFF00 !important; }
  .custom-r { color: #FF5E00 !important; font-size: 32px; font-weight: 900;
              display: inline-block; margin: 0 2px; }
</style>
""", unsafe_allow_html=True)

# ======================
# LOGO & BRANDING
# ======================
def get_logo_path():
    for p in ["static/bhjcf-logo.png","attached_assets/IMG_0019.png","bhjcf-logo.png"]:
        if os.path.exists(p): return p
    return None

def get_logo_base64(path):
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()

logo_path = get_logo_path()
logo_b64  = get_logo_base64(logo_path) if logo_path else None

# Centered logo + company name
col1,col2,col3 = st.columns([1,3,1])
with col2:
    if logo_b64:
        st.markdown(f"""
          <div style="display:flex;justify-content:center;align-items:center">
            <img src="data:image/png;base64,{logo_b64}" width="60" style="margin-right:10px;">
            <span style="font-size:24px;color:#00BFFF;font-weight:bold;">
              BHJCF Studio
            </span>
          </div>
        """,unsafe_allow_html=True)
    else:
        st.markdown('<h2 style="text-align:center;color:#00BFFF">BHJCF Studio</h2>',unsafe_allow_html=True)

# App title
st.markdown("""
<h1 style='text-align: center; margin-bottom: 5px;'>
  📊 <span class="custom-r">R</span>
  <span style='font-size:32px;color:#00BFFF;'>Retirement Calculator</span>
</h1>
""", unsafe_allow_html=True)

# Client watermark
st.markdown('<p style="text-align:center;color:#FF0000;font-size:18px">Client: Juanita Moolman</p>',
            unsafe_allow_html=True)

# ======================
# REUSABLE PDF FUNCTION
# ======================
def create_pdf(client, details, key_figures, graph_png_path, title):
    pdf = FPDF(orientation='P', format='A4')
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    # Logo & heading
    pdf.set_font("Arial","B",16)
    left_margin = 15
    if logo_path:
        pdf.image(logo_path, x=left_margin, y=10, w=20)
        pdf.set_xy(left_margin+25,10)
    else:
        pdf.set_xy(left_margin,10)
    pdf.cell(0,10, "BHJCF Studio", ln=1)
    pdf.set_font("Arial","",12)
    pdf.set_x(left_margin+25 if logo_path else left_margin)
    pdf.cell(0,8, title, ln=1)
    pdf.ln(5)
    pdf.line(left_margin, pdf.get_y(), 210-left_margin, pdf.get_y())
    pdf.ln(8)

    # Client info
    pdf.set_font("Arial","B",14)
    pdf.cell(0,8,"Client Information",ln=1)
    pdf.set_font("Arial","",11)
    for k,v in details.items():
        pdf.cell(60,8,f"{k}",0,0)
        pdf.cell(0,8,f"{v}",0,1)
    pdf.ln(5)

    # Key figures
    pdf.set_font("Arial","B",14)
    pdf.cell(0,8,"Key Figures",ln=1)
    pdf.set_font("Arial","",11)
    for k,v in key_figures.items():
        pdf.cell(0,8,f"{k} {v}",ln=1)
    pdf.ln(5)

    # Graph
    pdf.set_font("Arial","B",14)
    pdf.cell(0,8,title + " Projection",ln=1,'C')
    pdf.image(graph_png_path, x=left_margin, w=180)
    pdf.ln(5)

    # Footer disclaimer
    pdf.set_y(-30)
    pdf.set_font("Arial","I",8)
    pdf.set_text_color(128)
    pdf.multi_cell(0,4,
      "Disclaimer: Estimates based on provided inputs and assumptions. "
      "Actual results may vary. Consult a financial advisor.",0,'L')

    # Output to bytes
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()

# ======================
# TABS
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow","📈 Living Annuity Simulator"])

# --- TAB 1 ---
with tab1:
    # Inputs
    current_age      = st.slider("Current Age",25,100,45)
    retirement_age   = st.slider("Retirement Age",50,100,65)
    retirement_savings = st.number_input("Current Savings (R)",500000)
    annual_return    = st.slider("Annual Return (%)",1.0,15.0,7.0)/100
    life_expectancy  = st.slider("Life Expectancy",70,120,85)
    withdrawal_rate  = st.slider("Withdrawal Rate (%)",2.0,6.0,4.0)/100

    # Calc
    yrs_to_retire = retirement_age - current_age
    future_value  = fv(annual_return, yrs_to_retire, 0, -retirement_savings)
    yrs_in_retire = life_expectancy - retirement_age
    if yrs_in_retire<=0:
        st.error("Life expectancy must exceed retirement age"); st.stop()

    withdrawals = [future_value*withdrawal_rate*(1+annual_return)**i
                   for i in range(yrs_in_retire)]

    # Display
    st.subheader("Your Spending Plan")
    st.markdown(f"- **Value at Retirement:** R{future_value:,.2f}")
    st.markdown(f"- **1st Year Withdrawal:** R{withdrawals[0]:,.2f}")

    # Graph
    fig,ax=plt.subplots(figsize=(8,4))
    ax.plot(range(retirement_age,life_expectancy),withdrawals,color='red',lw=2)
    ax.fill_between(range(retirement_age,life_expectancy),withdrawals,color='green',alpha=0.3)
    ax.set_title("Retirement Income Projection")
    ax.set_xlabel("Age"); ax.set_ylabel("Annual Income (R)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p: f"{int(x):,}"))
    plt.tight_layout()
    st.pyplot(fig)

    # PDF button
    if st.button("📄 Download Retirement PDF"):
        # save graph
        with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            fig.savefig(tmp.name,dpi=200)
        details = {
            "Client:": "Juanita Moolman",
            "Current Age:": f"{current_age}",
            "Retirement Age:": f"{retirement_age}",
            "Life Expectancy:": f"{life_expectancy}"
        }
        key_figures = {
            "Value at Retirement:": f"R{future_value:,.2f}",
            "1st Year Withdrawal:": f"R{withdrawals[0]:,.2f}"
        }
        pdf_bytes = create_pdf(
            client="Juanita",
            details=details,
            key_figures=key_figures,
            graph_png_path=tmp.name,
            title="Retirement Cash Flow"
        )
        # preview
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="400px"></iframe>',unsafe_allow_html=True)
        st.download_button("⬇️ Download PDF",pdf_bytes,"retirement_report.pdf","application/pdf")

# --- TAB 2 ---
with tab2:
    la_current_age  = st.slider("Current Age",25,100,45,key="la1")
    la_retirement_age = st.slider("Retirement Age",55,100,65,key="la2")
    if la_retirement_age<=la_current_age:
        st.error("Retirement age must be after current age"); st.stop()
    investment      = st.number_input("Total Investment (R)",1_000_000,key="la3")
    la_return       = st.slider("Annual Return (%)",1.0,20.0,7.0,key="la4")/100
    withdrawal_rate_la = st.slider("Withdrawal Rate (%)",2.5,17.5,5.0,key="la5")/100

    if st.button("🚀 Calculate Living Annuity"):
        # compute
        monthly_income=investment*withdrawal_rate_la/12
        balance=investment; yrs=0
        yrs_list=[];bal_list=[];wd_list=[]
        while balance>0 and yrs<50:
            wd=balance*withdrawal_rate_la
            wd_list.append(wd)
            balance=(balance-wd)*(1+la_return)
            yrs_list.append(la_retirement_age+yrs)
            bal_list.append(balance)
            yrs+=1
        # longevity
        msg = f"⚠️ Depleted at age {yrs_list[-1]}" if balance<=0 else f"✅ Sustainable beyond {yrs} years"
        # display
        st.subheader("Results")
        st.write(f"- Monthly Income: **R{monthly_income:,.2f}**")
        st.write(f"- {msg}")

        # graphs
        fig1,ax1=plt.subplots(figsize=(6,4))
        ax1.plot(yrs_list,bal_list,color='green',lw=2)
        ax1.fill_between(yrs_list,bal_list,color='lightgreen',alpha=0.3)
        ax1.set_title("Balance Over Time");ax1.set_xlabel("Age");ax1.set_ylabel("Balance (R)")
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda x,p: f"{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig1)

        fig2,ax2=plt.subplots(figsize=(6,4))
        ax2.plot(yrs_list,wd_list,color='orange',lw=2)
        ax2.fill_between(yrs_list,wd_list,color='peachpuff',alpha=0.3)
        ax2.set_title("Annual Withdrawals");ax2.set_xlabel("Age");ax2.set_ylabel("Withdrawal (R)")
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda x,p: f"{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig2)

        # store for PDF
        st.session_state.la = dict(
          yrs=yrs_list,bal=bal_list,wd=wd_list,
          mi=monthly_income,msg=msg,
          invest=investment,ret=la_return,wr=withdrawal_rate_la,
          age=la_current_age,rage=la_retirement_age
        )

    # PDF button (only after calculation)
    if "la" in st.session_state:
        if st.button("📄 Download Living Annuity PDF",key="la_pdf"):
            data=st.session_state.la
            # save graphs
            tmp1=NamedTemporaryFile(delete=False,suffix=".png"); plt.figure(data=True)
            fig1.savefig(tmp1.name,dpi=200); plt.close(fig1)
            tmp2=NamedTemporaryFile(delete=False,suffix=".png"); fig2.savefig(tmp2.name,dpi=200); plt.close(fig2)
            # build PDF
            details_la = {
              "Current Age:":f"{data['age']}",
              "Retirement Age:":f"{data['rage']}",
              "Investment:":f"R{data['invest']:,.2f}"
            }
            key_la = {
              "Monthly Income:":f"R{data['mi']:,.2f}",
              "Longevity:":data['msg']
            }
            pdfb = create_pdf("Juanita",details_la,key_la,tmp1.name,"Living Annuity")
            b64=base64.b64encode(pdfb).decode()
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="400px"></iframe>',unsafe_allow_html=True)
            st.download_button("⬇️ Download PDF",pdfb,"living_annuity_report.pdf","application/pdf") 


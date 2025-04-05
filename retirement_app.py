import streamlit as st
from numpy_financial import fv, pmt
import matplotlib.pyplot as plt
from PIL import Image

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(layout="wide")

# Custom CSS for colors
st.markdown("""<style>
.stSlider>div>div>div>div { background: #7FFF00 !important; }
.st-b7 { color: #FF5E00; }
.st-c0 { background-color: #00BFFF; }
</style>""", unsafe_allow_html=True)

# ======================
# BRANDING
# ======================
col_logo, col_name = st.columns([1, 3])
with col_logo:
    try:
        logo = Image.open("bhjcf-logo.png")
        st.image(logo, width=100)
    except:
        st.warning("⚠️ Logo missing!")
with col_name:
    st.markdown("""<div style='height: 100px; display: flex; align-items: center; margin-left: -20px;'>
        <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>BHJCF Studio</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<p style="color:#FF0000; font-size:20px;">Client: Juanita Moolman</p>', unsafe_allow_html=True)

# ======================
# CALCULATOR TABS
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

with tab1:  # START OF TAB1 CONTENT
    # ======================
    # ORIGINAL RETIREMENT CALCULATOR CODE
    # ======================
    current_age = st.slider("Current Age", 25, 100, 45)
    retirement_age = st.slider("Retirement Age", 50, 100, 65)
    retirement_savings = st.number_input("Current Savings (R)", value=500000)
    annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
    life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

    # Calculations
    years_to_retirement = retirement_age - current_age
    future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)
    years_in_retirement = life_expectancy - retirement_age

    if years_in_retirement <= 0:
        st.error("❌ Life expectancy must be GREATER than retirement age!")
        st.stop()

    withdrawals = [future_value * withdrawal_rate * (1 + annual_return) ** year for year in range(years_in_retirement)]

    # Results
    st.subheader("Your Spending Money:")
    st.write(f"💰 **At retirement, you'll have:** R{future_value:,.2f}")
    st.write(f"💸 **You can spend this much per year:** R{withdrawals[0]:,.2f} (grows with returns!)")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Post-Retirement Cash Flow", color='#00BFFF')
    ax.set_xlabel("Age", color='#228B22')
    ax.set_ylabel("Annual Income (R)", color='#FF5E00')
    st.pyplot(fig)

with tab2:  # START OF TAB2 CONTENT
    # ======================
    # LIVING ANNUITY INPUTS
    # ======================
    col1, col2 = st.columns(2)
    with col1:
        la_current_age = st.slider("Current Age", 25, 100, 45, key="la_age")
    with col2:
        la_retirement_age = st.slider("Retirement Age", 50, 100, 65, key="la_retire")
    
    # Immediate validation check
    if la_retirement_age <= la_current_age:
        st.error("❌ Retirement age must be AFTER current age!")
        st.stop()

    investment = st.number_input("Total Investment Savings (R)", value=5000000, key="la_invest")
    la_return = st.slider("Annual Investment Return (%)", 1.0, 20.0, 7.0, key="la_return")/100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw")/100

    # ======================
    # CALCULATIONS
    # ======================
    if st.button("🚀 Calculate Income", key="la_btn"):
        # Monthly income calculation
        monthly_income = investment * withdrawal_rate / 12
        
        # Depletion simulation
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

        # ======================
        # RESULTS DISPLAY
        # ======================
        st.subheader("💰 Monthly Income Estimate")
        st.write(f"**Initial Monthly Drawdown:** R{monthly_income:,.2f}")
        
        st.subheader("⏳ Savings Longevity")
        if year_count >= 50:
            st.success(f"✅ Savings projected to last beyond age {la_retirement_age + 50}")
        else:
            st.warning(f"⚠️ Savings depleted at age {la_retirement_age + year_count}")
        
        # Longevity visualization
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(depletion_years, balances, color='#228B22', linewidth=2)
        ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
        ax.set_title("Investment Balance Projection", color='#00BFFF')
        ax.set_xlabel("Age", color='#228B22')
        ax.set_ylabel("Remaining Balance (R)", color='#FF5E00')
        st.pyplot(fig)
            
            # Longevity visualization
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(depletion_years, balances, color='#228B22', linewidth=2)
            ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
            ax.set_title("Investment Balance Projection", color='#00BFFF')
            ax.set_xlabel("Age", color='#228B22')
            ax.set_ylabel("Remaining Balance (R)", color='#FF5E00')
            st.pyplot(fig)

# [KEEP YOUR EXISTING RETIREMENT PLOT CODE]

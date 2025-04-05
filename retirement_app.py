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
/* New Enhancements */
[data-testid="column"]:nth-of-type(1) { 
    justify-content: center !important;
}
h1 { 
    letter-spacing: -0.5px !important; 
    margin-bottom: 12px !important;
}
img:hover {
    transform: scale(1.03);
    transition: transform 0.2s ease-in-out;
}
.certification-badge {
    padding: 4px 12px;
    border-radius: 15px;
    background: linear-gradient(45deg, #00BFFF, #7FFF00);
    color: white !important;
    font-weight: 600;
    display: inline-block;
    margin-top: -8px;
}
</style>""", unsafe_allow_html=True)

# ======================
# BRANDING (OPTIMIZED SPACING)
# ======================
st.markdown("""
<h1 style='text-align: center; margin-bottom: 20px;'>
    <span class="custom-r">R</span>
    <span style='font-size: 32px; color: #00BFFF;'>Retirement Cash Flow Calculator</span>
</h1>
""", unsafe_allow_html=True)

# Logo and company name - tighter spacing
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    container = st.container()
    cols = container.columns([2, 7])  # Adjusted column ratio
    with cols[0]:
        try:
            logo = Image.open("bhjcf-logo.png")
            st.image(logo, width=65)  # Slightly smaller logo
        except:
            st.warning("⚠️ Logo missing!")
    with cols[1]:
        st.markdown("""
        <div class="company-name" style='height: 70px; display: flex; align-items: center;'>
            <p style='color: #00BFFF; font-size:24px; font-weight: bold; margin: 0;'>
                BHJCF Studio
            </p>
        </div>
        """, unsafe_allow_html=True)

# Client info with certification badge
st.markdown("""
<div style='text-align: center; margin-bottom: 25px;'>
    <p style='color:#FF0000; font-size:20px; margin: 0;'>Client: Juanita Moolman</p>
    <div class="certification-badge">Version 2.1 | Certified Retirement Specialist</div>
</div>
""", unsafe_allow_html=True)

# Rest of your calculator tabs remain unchanged...
# ======================
# CALCULATOR TABS 
# ======================
tab1, tab2 = st.tabs(["💼 Retirement Cash Flow", "📈 Living Annuity Simulator"])

with tab1:
    # ======================
    # RETIREMENT CALCULATOR 
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

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
    ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
    ax.set_title("Retirement Income Projection", color='#00BFFF')
    ax.set_xlabel("Age", color='#228B22')
    ax.set_ylabel("Annual Income (R)", color='#FF5E00')
    st.pyplot(fig)

with tab2:
    # ======================
    # LIVING ANNUITY CALCULATOR (FIXED 🔴)
    # ======================
    col1, col2 = st.columns(2)
    with col1:
        la_current_age = st.slider("Current Age", 25, 100, 45, key="la_age")
    with col2:
        la_retirement_age = st.slider("Retirement Age", 55, 100, 65, key="la_retire")  # Min 55
    
    if la_retirement_age <= la_current_age:
        st.error("❌ Retirement age must be AFTER current age!")
        st.stop()

    investment = st.number_input("Total Investment (R)", value=5000000, key="la_invest")
    la_return = st.slider("Annual Return (%)", 1.0, 20.0, 7.0, key="la_return")/100
    withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.5, 17.5, 4.0, key="la_withdraw")/100

    # 🔴 MADE BUTTON MORE VISIBLE
    calculate_btn = st.button("🚀 CALCULATE LIVING ANNUITY PROJECTIONS", 
                            key="la_btn",
                            help="Click to generate your retirement income plan")
    
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
                    background-color: {"#e6f4ea" if year_count >=50 else "#fff3cd"};">
            <span style='font-size: 16px;'>{longevity_text}</span>
        </div>
        """, unsafe_allow_html=True)

        # Visualization
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(depletion_years, balances, color='#228B22', linewidth=2)
        ax.fill_between(depletion_years, balances, color='#7FFF00', alpha=0.3)
        ax.set_title("Investment Balance Timeline", color='#00BFFF')
        ax.set_xlabel("Age", color='#228B22')
        ax.set_ylabel("Remaining Balance (R)", color='#FF5E00')
        st.pyplot(fig)

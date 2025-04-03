import streamlit as st
from numpy_financial import fv
import matplotlib.pyplot as plt

# Custom CSS for colors
st.markdown("""
<style>
.stSlider>div>div>div>div { background: #7FFF00 !important; }  /* Neon Green slider */
.st-b7 { color: #FF5E00; }  /* Orange labels */
.st-c0 { background-color: #00BFFF; }  /* Light Blue */
</style>
""", unsafe_allow_html=True)

# Title
st.title("💰 Retirement Cash Flow Calculator")
st.markdown('<p style="color:#FF0000; font-size:20px;">Client: Juanita Mool</p>', unsafe_allow_html=True)

# Inputs
current_age = st.slider("Current Age", 25, 100, 45)
retirement_age = st.slider("Retirement Age", 50, 100, 65)
retirement_savings = st.number_input("Current Savings ($)", value=500000)
annual_return = st.slider("Annual Return (%)", 1.0, 15.0, 7.0) / 100
life_expectancy = st.slider("Life Expectancy", 70, 120, 85)
withdrawal_rate = st.slider("Withdrawal Rate (%)", 2.0, 6.0, 4.0) / 100

# Calculations
years_to_retirement = retirement_age - current_age
future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)
years_in_retirement = life_expectancy - retirement_age
withdrawals = [future_value * withdrawal_rate * (1.03 ** year) for year in range(years_in_retirement)]

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(range(retirement_age, life_expectancy), withdrawals, color='#FF0000', linewidth=2)
ax.fill_between(range(retirement_age, life_expectancy), withdrawals, color='#7FFF00', alpha=0.3)
ax.set_title("Post-Retirement Cash Flow", color='#00BFFF')
ax.set_xlabel("Age", color='#228B22')
ax.set_ylabel("Annual Income ($)", color='#FF5E00')
st.pyplot(fig)

# Calculations  
years_to_retirement = retirement_age - current_age  
future_value = fv(annual_return, years_to_retirement, 0, -retirement_savings)  
years_in_retirement = life_expectancy - retirement_age  
withdrawals = [future_value * withdrawal_rate * (1.03 ** year) for year in range(years_in_retirement)]  

# ADD THESE LINES HERE 👇  
st.subheader("Your Spending Money:")  
st.write(f"💰 **At retirement, you'll have:** ${future_value:,.2f}")  
st.write(f"💸 **You can spend this much per year:** ${withdrawals[0]:,.2f} (and it grows 3% yearly!)")  

# Plot  
fig, ax = plt.subplots(figsize=(10, 5))

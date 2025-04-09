# Retirement Calculator App

Plan your financial future with confidence using the **Retirement Calculator App**. This interactive app helps you simulate your retirement savings, withdrawals, and living annuity projections, complete with PDF reports and visual insights.

---

## 🚀 Features
- **Retirement Calculator**: Analyze how your savings and withdrawal plans align with your goals.
- **Living Annuity Simulator**: Simulate your living annuity to assess how long your funds will last.
- **Dynamic Graphs**: Visualize investment balances and withdrawals over time.
- **PDF Reports**: Generate professional PDF reports for your financial planning.
- **Interactive Interface**: Easily configure inputs like age, savings, withdrawal rates, and more.

---

## 🛠️ Tech Stack
- **Streamlit**: For building the app's interactive user interface.
- **Matplotlib**: For creating dynamic charts and graphs.
- **FPDF**: For generating PDF reports.
- **Python**: Core programming language for logic and calculations.

---

## 📋 Prerequisites
- Python 3.8 or higher
- Required Python libraries:
  - `streamlit`
  - `matplotlib`
  - `fpdf`
  - `pillow`

Install dependencies using:
```bash
pip install -r requirements.txt
```

---

## 🖥️ How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/BonnieH111/retirement-calculator-app.git
   ```
2. Navigate to the project directory:
   ```bash
   cd retirement-calculator-app
   ```
3. Run the app:
   ```bash
   streamlit run main_script.py
   ```
4. Open the app in your browser at `http://localhost:8501`.

---

## 📂 Project Structure
```plaintext
retirement-calculator-app/
├── app_configuration.py          # Configures the app layout and theme
├── session_state_management.py   # Handles session states
├── retirement_calculator_tab.py  # Retirement Calculator functionality
├── living_annuity_simulator_tab.py # Living Annuity Simulator functionality
├── about_tab.py                  # About tab content
├── utilities.py                  # Helper functions for charts, PDFs, etc.
├── retirement_cashflow_pdf.py    # PDF generation logic
├── pdf_preview.py                # PDF preview logic
├── error_handling_and_logging.py # Error handling and logging
├── main_script.py                # Main app script
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## 📑 Example Use Cases
1. **Planning Retirement**: Assess if your savings will last through retirement based on withdrawal rates and expected returns.
2. **Simulating Living Annuities**: Explore how long your funds will sustain you with different withdrawal strategies.
3. **Generating Reports**: Create detailed PDF reports to share with financial advisors or for personal record-keeping.

---

## 🧩 Future Enhancements
- Add support for custom tax calculations.
- Include inflation adjustments in projections.
- Enable multi-language support for international users.

---

## 🧑‍💻 Contributors
- **BonnieH111** - [GitHub Profile](https://github.com/BonnieH111)

---

## 🛡️ License
This project is licensed under the MIT License.

---

## 📞 Contact
Have questions or feedback? Reach out to us:
- **Email**: [brumbollharding@icloud.com](mailto:brumbollharding@icloud.com)

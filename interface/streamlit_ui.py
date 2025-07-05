import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_collection import fetch_financials
from models.dcf_model import calculate_dcf, project_fcf
from agents.report_generator import generate_report
from agents.assumption_explainer import explain_assumptions
from visualizations.valuation_chart import plot_fcf_projection
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()

# --- UI STARTS ---
st.set_page_config(page_title="ValueX: DCF Valuation", layout="centered")
st.title("📈 ValueX - DCF Equity Valuation Tool")

# Sidebar: DCF Term Explanations
st.sidebar.title("📘 DCF Term Explanations")
st.sidebar.markdown("""
**FCF Growth Rate (%):**
- How much the company's free cash flow is expected to grow each year.
- Example: 7% means cash flow grows by 7% annually.

**WACC (%):**
- Weighted Average Cost of Capital. The average rate the company pays to finance its assets (mix of debt and equity).
- Used as the discount rate in DCF. Higher WACC = higher risk.

**Terminal Growth Rate (%):**
- The long-term growth rate expected after the forecast period (usually after 5 years).
- Should be close to long-term inflation or GDP growth (2–3%).

**Intrinsic Value per Share:**
- The estimated true value of one share based on future cash flows.

**Enterprise Value:**
- The total value of the company, including debt and cash, based on projected cash flows.

**Discounted FCF:**
- The present value of each year's projected free cash flow, adjusted for risk and time.

**Terminal Value:**
- The value of all future cash flows beyond the forecast period, assuming the company grows at the terminal rate forever.

**PV of Explicit FCFs:**
- The sum of all discounted cash flows during the forecast period (e.g., first 5 years).

**PV of Terminal Value:**
- The present value of the terminal value, discounted back to today.

---
*These terms help you understand how a company's future performance is valued today. Adjust the parameters to see how they affect the estimated value!*
""")

# Input Section
st.subheader("📊 Company Information")
ticker = st.text_input("Enter Ticker Symbol", value="AAPL", 
                      help="Examples: AAPL (Apple), MSFT (Microsoft), TCS.NS (Indian stocks), GOOGL (Google)")

# Show common ticker examples
with st.expander("💡 Common Ticker Examples"):
    st.markdown("""
    **US Stocks:**
    - AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon)
    - TSLA (Tesla), META (Meta), NVDA (NVIDIA), NFLX (Netflix)
    
    **Indian Stocks:**
    - TCS.NS (Tata Consultancy), INFY.NS (Infosys), RELIANCE.NS (Reliance)
    - HDFCBANK.NS (HDFC Bank), ICICIBANK.NS (ICICI Bank)
    
    **Note:** Add .NS suffix for Indian stocks listed on NSE
    """)

st.subheader("📈 Valuation Parameters")
growth = st.slider("FCF Growth Rate (%)", 1, 30, 10) / 100
wacc = st.slider("WACC (%)", 5, 20, 10) / 100
terminal = st.slider("Terminal Growth Rate (%)", 1, 6, 3) / 100

# Run Button
if st.button("Run Valuation"):
    with st.spinner("Fetching data and calculating valuation..."):
        try:
            # Validate ticker first
            if not ticker.strip():
                st.error("❌ Please enter a ticker symbol")
                st.stop()
            
            # Show ticker being analyzed
            st.info(f"🔍 Analyzing: {ticker.upper()}")
            
            data = fetch_financials(ticker)
            
            if 'error' in data:
                st.error(f"❌ Error fetching data: {data['error']}")
                st.stop()
            
            if data["fcf"] <= 0:
                st.warning("⚠️ Warning: Free Cash Flow is zero or negative. Results may be unreliable.")
            
            # Display company info
            st.subheader("🏢 Company Information")
            col1, col2, col3 = st.columns(3)
            col1.metric("Company", data.get("company_name", "N/A"))
            col2.metric("Sector", data.get("sector", "N/A"))
            col3.metric("Market Cap", f"₹{data.get('market_cap', 0):,.0f} Cr")
            
            fcf_proj = project_fcf(data["fcf"], growth)
            results = calculate_dcf(fcf_proj, wacc, terminal, data["shares_outstanding"])
            
            if 'error' in results:
                st.error(f"❌ Error in DCF calculation: {results['error']}")
                st.stop()
                
            discount = (1 - data["current_price"] / results["intrinsic_value"]) * 100

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.stop()

        # Display Valuation Results
        st.subheader("📊 Valuation Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Intrinsic Value per Share", f"₹{results['intrinsic_value']:.2f}")
        col2.metric("Enterprise Value", f"₹{results['enterprise_value']:,.0f}")
        col3.metric("PV of Explicit FCFs", f"₹{results['pv_explicit_fcf']:,.0f}")
        st.metric("PV of Terminal Value", f"₹{results['discounted_terminal']:,.0f}")
        st.metric("Terminal Value", f"₹{results['terminal_value']:,.0f}")
        # Show Discounted FCFs as a table
        import pandas as pd
        discounted_fcf = results.get('discounted_fcf', [])
        if discounted_fcf:
            st.write("Discounted FCFs (Year 1-5):")
            st.table(pd.DataFrame({
                "Year": [f"Year {i+1}" for i in range(len(discounted_fcf))],
                "Discounted FCF": [f"₹{v:,.0f}" for v in discounted_fcf]
            }))
        # Show Terminal FCF
        terminal_fcf = results.get('terminal_fcf', None)
        if terminal_fcf is not None:
            st.write(f"Terminal FCF (Year 5): ₹{terminal_fcf:,.0f}")

        # Chart
        st.subheader("🔮 Projected FCF Over 5 Years")
        try:
            # Create chart for Streamlit
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            years = [f"Year {i+1}" for i in range(len(fcf_proj))]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(years, fcf_proj, marker='o', linestyle='-', color='blue', label='Projected FCF')
            ax.fill_between(years, fcf_proj, alpha=0.1, color='blue')
            ax.set_title("Projected Free Cash Flow (5-Year Forecast)", fontsize=14)
            ax.set_xlabel("Future Years")
            ax.set_ylabel("FCF (₹ Crores)")
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()
            plt.tight_layout()
            
            # Display in Streamlit
            st.pyplot(fig)
            plt.close()
            
        except Exception as e:
            st.error(f"Could not display chart: {str(e)}")
            # Show data as table instead
            st.write("FCF Projection Data:")
            for i, fcf in enumerate(fcf_proj):
                st.write(f"Year {i+1}: ₹{fcf:,.0f}")

        # Assumption Explanation
        st.subheader("🧠 Assumption Analysis")
        st.markdown("Explains if your inputs are realistic or risky.")
        try:
            explanation = explain_assumptions(growth, wacc, terminal)
            st.info(explanation)
        except Exception as e:
            st.warning(f"⚠️ Could not generate AI insights: {str(e)}")

        # AI-Powered Report
        st.subheader("📄 Investment Summary Report")
        try:
            report = generate_report(
                company=ticker,
                intrinsic_value=results["intrinsic_value"],
                market_price=data["current_price"],
                discount=discount,
                assumptions={"growth": growth, "wacc": wacc, "terminal": terminal}
            )
            st.markdown(report)
        except Exception as e:
            st.warning(f"⚠️ Could not generate AI report: {str(e)}")

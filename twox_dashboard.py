# Fix indentation error by removing unnecessary whitespace in the multi-line string block
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import mibian

# --- CONFIG ---
START_NAV = 25.00
CAP_NAV = 30.00
START_DATE = pd.to_datetime("2024-04-01")
END_DATE = pd.to_datetime("2024-06-30")
CURRENT_DATE = pd.to_datetime("today")

# --- LIVE PRICE FETCH (ALPHA VANTAGE EXAMPLE) ---


def get_ivv_price(api_key):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IVV&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    try:
        price = float(data["Global Quote"]["05. price"])
        return price
    except:
        return None

# --- RETURN CALCULATIONS ---


def calculate_returns(ivv_start, ivv_current):
    return (ivv_current - ivv_start) / ivv_start


# --- STREAMLIT UI ---
st.set_page_config(layout="wide")
st.title("TWOX Monitoring Dashboard")
st.markdown(
    "Track the performance, cap exposure, and risk metrics of the TWOX ETF (Accelerated Return).")

# --- INPUT SECTION ---
api_key = st.text_input("Enter your Alpha Vantage API Key:", type="password")
ivv_start_price = st.number_input(
    "IVV Starting Price on April 1", value=505.00)
cap_level = st.slider("Strategy Cap (%)", min_value=5.0,
                      max_value=25.0, value=15.0)

# --- MAIN CALCULATION BLOCK ---
if api_key:
    ivv_current_price = get_ivv_price(api_key)

    if ivv_current_price:
        ivv_return = calculate_returns(ivv_start_price, ivv_current_price)
        twox_return = min(2 * ivv_return, cap_level / 100)
        nav = START_NAV * (1 + twox_return)
        percent_to_cap = max(
            0, ((CAP_NAV - nav) / (CAP_NAV - START_NAV)) * 100)
        days_remaining = (END_DATE - CURRENT_DATE).days

        st.subheader("📈 Performance Snapshot")
        st.metric("IVV Price", f"${ivv_current_price:,.2f}")
        st.metric("IVV Return", f"{ivv_return * 100:.2f}%")
        st.metric("TWOX NAV Estimate", f"${nav:.2f}")
        st.metric("% to Cap", f"{percent_to_cap:.1f}%")
        st.metric("Days Remaining", days_remaining)

        st.subheader("📉 Stress Test: -5% in IVV")
        stress_ivv = ivv_current_price * 0.95
        stress_return = calculate_returns(ivv_start_price, stress_ivv)
        stress_twox_return = 2 * stress_return
        stress_nav = START_NAV * (1 + stress_twox_return)
        st.write(f"If IVV drops 5% → Estimated NAV: ${stress_nav:.2f}")

        st.subheader("🧮 Option Value (BS Model)")
        st.text("Use this in a Jupyter Notebook to estimate option value:")
        st.code(
            "import mibian\\nbs = mibian.BS([505, 530, 5, 30], volatility=20)\\nprint(bs.callPrice, bs.delta)")

    else:
        st.error("Unable to fetch IVV price. Check your API key or try again later.")
else:
    st.info("Enter your API key above to begin monitoring.")

# # Save to file
# file_path = "/Users/jesse_leal/Desktop/Projects/MachineLearningProjects/twox_dashboard.py"
# with open(file_path, "w") as f:
#     f.write(streamlit_template)

# file_path

import streamlit as st
import pandas as pd
import yfinance as yf
from groq import Groq
import os
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable SSL verification - let curl_cffi handle it
os.environ['CURL_CA_BUNDLE'] = ''

# 1. Setup
st.set_page_config(page_title="AI Investment Advisor", layout="wide")
st.title("🤖 AI Personal Investment Advisor (Free Tier)")

# Access the Free Key from secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing Groq API Key in secrets.toml")

st.warning("⚠️ DISCLAIMER: Educational simulation only. Not financial advice.")

# Sidebar for User Profile
with st.sidebar:
    st.header("👤 Your Financial Profile")
    income = st.number_input("Annual Income ($)", min_value=0, value=50000)
    risk_appetite = st.select_slider("Risk Appetite", options=["Low", "Medium", "High"])
    goals = st.selectbox("Investment Goal", ["Retirement", "Buying a House", "Wealth Growth", "Education"])
    
    st.header("🔮 What-If Scenario")
    market_crash = st.slider("Simulate Market Change (%)", -50, 50, 0)

# Main Logic: Fetch real data
st.subheader("📊 Current Market Insights")
tickers = {'S&P 500': 'SPY', 'Nasdaq': 'QQQ', 'Bonds': 'AGG', 'Bitcoin': 'BTC-USD'}
market_data = {}

for name, t in tickers.items():
    try:
        stock = yf.Ticker(t)
        market_data[name] = stock.history(period="1d", timeout=10)['Close'].iloc[-1]
    except Exception as e:
        st.warning(f"Could not fetch {name}. Using placeholder price.")
        market_data[name] = 100  # Placeholder

cols = st.columns(4)
for i, (name, price) in enumerate(market_data.items()):
    cols[i].metric(name, f"${price:.2f}")

# Generate Recommendation
if st.button("Generate My Portfolio Recommendation"):
    prompt = f"""
    Act as a professional financial advisor. 
    User Profile: Income ${income}, Risk: {risk_appetite}, Goal: {goals}.
    Current Market: {market_data}.
    Simulation: What if market changes by {market_crash}%?
    
    Provide a clear percentage allocation and reasoning.
    """
    
    try:
        with st.spinner("AI thinking (Powered by Groq)..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            st.success("Analysis Complete!")
            st.markdown("---")
            st.write(chat_completion.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}. Check your Groq API key or internet connection.")

# Follow-up Chat
st.markdown("---")
user_query = st.text_input("💬 Ask a follow-up question:")
if user_query:
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_query}],
            model="llama-3.3-70b-versatile",
        )
        st.info(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}. Check your Groq API key or internet connection.")
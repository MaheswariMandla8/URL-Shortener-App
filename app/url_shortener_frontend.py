import streamlit as st
import requests

st.set_page_config(page_title="URL Shortener", layout="centered")
st.title("🔗 URL Shortener Frontend")

API_BASE = "http://localhost:5000"

# ─── Input Section ───
st.header("1. Shorten a URL")
long_url = st.text_input("Enter a long URL to shorten")

if st.button("Shorten URL"):
    if not long_url:
        st.warning("Please enter a URL.")
    else:
        response = requests.post(f"{API_BASE}/api/shorten", json={"url": long_url})
        if response.status_code == 200:
            result = response.json()
            st.success("Shortened URL:")
            st.write(f"[🔗 {result['short_url']}]({result['short_url']})")
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# ─── Redirect Section ───
st.header("2. Test Redirect")
short_code = st.text_input("Enter short code to test redirect")
if st.button("Go to Original URL"):
    if short_code:
        redirect_url = f"{API_BASE}/{short_code}"
        st.markdown(f"[Click here to go →]({redirect_url})")
    else:
        st.warning("Enter a short code to redirect")

# ─── Analytics Section ───
st.header("3. Get Analytics")
analytics_code = st.text_input("Enter short code for stats")
if st.button("Fetch Stats"):
    if analytics_code:
        stats_url = f"{API_BASE}/api/stats/{analytics_code}"
        resp = requests.get(stats_url)
        if resp.status_code == 200:
            stats = resp.json()
            st.info("🔍 Analytics")
            st.write(f"**Original URL**: {stats['url']}")
            st.write(f"**Clicks**: {stats['clicks']}")
            st.write(f"**Created At**: {stats['created_at']}")
        else:
            st.error(f"Error: {resp.json().get('error', 'Unknown error')}")
    else:
        st.warning("Please enter a short code to fetch stats")

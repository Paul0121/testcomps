import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def zillow_scraper(zipcode, repair_costs=0):
    url = f"https://www.zillow.com/homes/recently_sold/{zipcode}_rb/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    # Fetch the page content
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.warning(f"❌ Failed to retrieve page. Status code: {response.status_code}")
        return [], 0, 0

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("article")
    comps = []

    for card in cards:
        try:
            address = card.find("address").text
            price_text = card.find("div", {"data-test": "property-card-price"}).text
            price = int(price_text.replace("$", "").replace(",", "").split("+")[0])
            comps.append({"address": address, "price": price})
        except Exception:
            continue

    if not comps:
        st.warning("❌ No comps found.")
        return [], 0, 0

    # ARV & MAO
    prices = [c["price"] for c in comps]
    arv = sum(prices) / len(prices)
    mao = (arv * 0.6) - repair_costs

    return comps, arv, mao

# Streamlit UI
st.title("🏡 Zillow Scraper & Comps Calculator")

with st.form("comp_form"):
    zipcode = st.text_input("Enter ZIP code (e.g., 33701):")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Run Comps")

if submitted:
    if zipcode:
        with st.spinner("Fetching comps..."):
            comps, arv, mao = zillow_scraper(zipcode, repair_costs)

        if comps:
            st.subheader(f"📍 Comps for ZIP: {zipcode}")
            df = pd.DataFrame(comps)
            st.write(df)

            st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
    else:
        st.error("Please enter a ZIP code.")

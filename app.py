import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

def zillow_scraper(zipcode, repair_costs=0):
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    url = f"https://www.zillow.com/homes/recently_sold/{zipcode}_rb/"
    driver.get(url)
    time.sleep(5)  # Wait for page to load

    # Scroll to load more results
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

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
        return []

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

import streamlit as st
import requests
import pandas as pd

def scrape_zillow_property(zillow_url, repair_costs=0):
    apikey = 'cc6dacb609744c0a8aa02180495b2e7be88d4b34'  # ZenRows API key
    endpoint = 'https://api.zenrows.com/v1/'

    params = {
        'apikey': apikey,
        'url': zillow_url,
        'js_render': 'true'
    }

    response = requests.get(endpoint, params=params)

    if response.status_code != 200:
        st.warning(f"❌ Failed to scrape Zillow page. Status code: {response.status_code}")
        return None, 0, 0

    try:
        html = response.text
        # You can now use BeautifulSoup to extract specific data if needed
        # For now we just mock ARV as we’d parse price in a real scenario
        arv = 400000  # Replace this after parsing from HTML
        mao = (arv * 0.6) - repair_costs
        comps = [{"address": zillow_url, "price": arv}]
        return comps, arv, mao

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None, 0, 0

# Streamlit UI
st.title("🏠 Zillow Property Analyzer (ZenRows Scraper Mode)")

with st.form("property_form"):
    zillow_url = st.text_input("Enter full Zillow property URL", help="e.g. https://www.zillow.com/homedetails/...")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Scrape Property & Run MAO")

if submitted:
    if zillow_url:
        with st.spinner("Scraping Zillow page using ZenRows..."):
            comps, arv, mao = scrape_zillow_property(zillow_url, repair_costs)

        if comps:
            st.subheader("📍 Scraped Property")
            df = pd.DataFrame(comps)
            st.write(df)

            st.markdown(f"### 💰 Estimated ARV (mocked): `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
        else:
            st.warning("No comps retrieved.")
    else:
        st.error("Please enter a valid Zillow URL.")

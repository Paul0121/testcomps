import streamlit as st
import requests
import pandas as pd

# Function to fetch property details from ZenRows API and calculate ARV dynamically
def fetch_property_details(zillow_url, repair_costs=0):
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
        
        # Using BeautifulSoup to parse and extract relevant data
        # Extract square footage and price for ARV calculation
        # Note: You may need to fine-tune this parsing to match actual HTML structure
        arv = calculate_arv_from_comps(html)  # Function to calculate ARV from comparables (not shown here)
        
        # Calculate MAO using 60% rule
        mao = (arv * 0.6) - repair_costs
        
        comps = [{"address": zillow_url, "price": arv}]
        return comps, arv, mao

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None, 0, 0

# Function to calculate ARV based on comparables
def calculate_arv_from_comps(html):
    # You can parse the page and extract prices per square foot of comparable properties
    # For simplicity, let's assume we fetch the price per sq ft from a set of listings in the same area
    comps_data = [
        {"price_per_sqft": 350, "sqft": 1000},  # Example comp
        {"price_per_sqft": 375, "sqft": 1200},
        {"price_per_sqft": 390, "sqft": 1100}
    ]
    
    avg_price_per_sqft = sum(comp["price_per_sqft"] for comp in comps_data) / len(comps_data)
    subject_property_sqft = 1100  # Adjust this to the actual sqft of the subject property
    
    arv = avg_price_per_sqft * subject_property_sqft
    return arv

# Streamlit UI
st.title("C2 Creative Comps")

with st.form("property_form"):
    zillow_url = st.text_input("Enter full Zillow property URL", help="e.g. https://www.zillow.com/homedetails/...")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Scrape Property & Run MAO")

if submitted:
    if zillow_url:
        with st.spinner("Scraping Zillow page using ZenRows..."):
            comps, arv, mao = fetch_property_details(zillow_url, repair_costs)

        if comps:
            st.subheader("📍 Scraped Property")
            df = pd.DataFrame(comps)
            st.write(df)

            st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
        else:
            st.warning("No comps retrieved.")
    else:
        st.error("Please enter a valid Zillow URL.")

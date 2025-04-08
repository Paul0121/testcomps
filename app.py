import streamlit as st
import requests
import pandas as pd

# Function to fetch property details and nearby comps based on proximity
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
        
        # Extract latitude and longitude (or approximate location)
        latitude, longitude = extract_lat_lon_from_property(html)  # Implement a function for extracting lat/lon
        
        # Get nearby properties within a 1-mile radius
        comps = get_nearby_comps(latitude, longitude)
        
        # Calculate ARV and MAO using fetched comparables
        arv = calculate_arv_from_comps(comps)
        mao = (arv * 0.6) - repair_costs
        
        return comps, arv, mao

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None, 0, 0

# Function to extract latitude and longitude from Zillow property page
def extract_lat_lon_from_property(html):
    # Implement BeautifulSoup logic to scrape lat/lon from property page HTML
    # For now, we'll return dummy data (you'll need to adjust this)
    return 27.7891, -82.6375  # Dummy data (replace with actual logic)

# Function to get nearby comparables based on lat/lon (within 1-mile radius)
def get_nearby_comps(latitude, longitude):
    # For simplicity, we’ll hardcode some nearby properties (in a real case, you'd fetch them dynamically)
    comps_data = [
        {"address": "1800 Mississippi Ave NE, Saint Petersburg, FL 33703", "price": 450000},
        {"address": "1727 Mississippi Ave NE, Saint Petersburg, FL 33703", "price": 499164},
        {"address": "1851 Mississippi Ave NE, Saint Petersburg, FL 33703", "price": 240000},
    ]
    return comps_data

# Function to calculate ARV based on comparables
def calculate_arv_from_comps(comps):
    avg_price = sum(comp["price"] for comp in comps) / len(comps)
    return avg_price

# Streamlit UI
st.title("🏠 Zillow Property Analyzer (Nearby Comps Scraper)")

with st.form("property_form"):
    zillow_url = st.text_input("Enter full Zillow property URL", help="e.g. https://www.zillow.com/homedetails/...")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Scrape Property & Run MAO")

if submitted:
    if zillow_url:
        with st.spinner("Scraping Zillow page and fetching nearby properties..."):
            comps, arv, mao = fetch_property_details(zillow_url, repair_costs)

        if comps:
            st.subheader("📍 Nearby Comps within 1 Mile")
            df = pd.DataFrame(comps)
            st.write(df)

            st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
        else:
            st.warning("No comps retrieved.")
    else:
        st.error("Please enter a valid Zillow URL.")

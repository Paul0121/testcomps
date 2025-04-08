import streamlit as st
import requests
import pandas as pd

# Function to fetch property details from ZenRows API
def fetch_property_details(zpid, repair_costs=0):
    apikey = 'cc6dacb609744c0a8aa02180495b2e7be88d4b34'  # ZenRows free API key
    endpoint = 'https://realestate.api.zenrows.com/v1/targets/zillow/properties/'

    params = {
        'apikey': apikey,
        'zpid': zpid
    }

    response = requests.get(endpoint, params=params)

    if response.status_code != 200:
        st.warning(f"❌ Failed to fetch property details. Status code: {response.status_code}")
        return None, 0, 0

    try:
        data = response.json()
        address = data.get("address", {}).get("streetAddress", "Unknown address")
        price = data.get("price", {}).get("amount", 0)

        comps = [{"address": address, "price": price}]

        # Calculate ARV and MAO
        arv = price
        mao = (arv * 0.6) - repair_costs

        return comps, arv, mao

    except Exception as e:
        st.error(f"Error parsing response: {e}")
        return None, 0, 0

# Streamlit UI
st.title("🏠 Zillow Property Analyzer (via ZenRows API)")

with st.form("property_form"):
    zpid = st.text_input("Enter Zillow Property ID (ZPID)", help="e.g. 45733877 for 3808 6th Ave W")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Fetch Property & Run MAO")

if submitted:
    if zpid:
        with st.spinner("Fetching property data from Zillow via ZenRows..."):
            comps, arv, mao = fetch_property_details(zpid, repair_costs)

        if comps:
            st.subheader("📍 Property Details")
            df = pd.DataFrame(comps)
            st.write(df)

            st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
        else:
            st.warning("No comps retrieved.")
    else:
        st.error("Please enter a valid ZPID.")

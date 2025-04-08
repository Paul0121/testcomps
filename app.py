# pip install requests
import requests
import streamlit as st

def get_property_details(zpid):
    # API key for ZenRows
    apikey = 'cc6dacb609744c0a8aa02180495b2e7be88d4b34'

    # Construct the Zillow URL using the ZPID
    url = f'https://www.zillow.com/homedetails/{zpid}_zpid'

    # Parameters to send in the API request
    params = {
        'apikey': apikey,
        'url': url,
    }

    # Send the request to ZenRows API
    response = requests.get('https://realestate.api.zenrows.com/v1/targets/zillow/properties/', params=params)

    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()
        return data
    else:
        st.warning(f"❌ Failed to fetch property details. Status code: {response.status_code}")
        return None

def calculate_comps_and_mao(comps, repair_costs):
    # Calculate ARV (average price of the comps)
    prices = [comp["price"] for comp in comps]
    arv = sum(prices) / len(prices) if prices else 0

    # Calculate the Maximum Allowable Offer (60% Rule)
    mao = (arv * 0.6) - repair_costs
    return arv, mao

# Streamlit UI
st.title("🏡 Zillow Property Details & Comps Calculator")

with st.form("property_form"):
    zpid = st.text_input("Enter ZPID (e.g., 46978274):")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Get Property Details and Run Comps")

if submitted:
    if zpid:
        with st.spinner("Fetching property details and comps..."):
            data = get_property_details(zpid)

        if data:
            # Display fetched property details
            st.subheader(f"Property Details for ZPID: {zpid}")
            st.write(data)  # Display the raw property data (you can customize this)

            # Get comps from the fetched data (assuming the data includes a list of comps)
            comps = data.get("comps", [])
            if comps:
                st.subheader("Comparable Properties (Comps)")

                # Display the comps
                for comp in comps:
                    st.write(f"Address: {comp['address']}, Price: ${comp['price']:,.2f}")

                # Calculate ARV and MAO
                arv, mao = calculate_comps_and_mao(comps, repair_costs)

                st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
                st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
            else:
                st.warning("❌ No comps found in the data.")
    else:
        st.error("Please enter a valid ZPID.")

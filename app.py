# pip install requests beautifulsoup4 streamlit
import requests
from bs4 import BeautifulSoup
import streamlit as st

def get_property_details(url):
    # Set up headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    # Send GET request to fetch the page content
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract the relevant property details (address, price, etc.)
        try:
            address = soup.find("h1", {"class": "ds-address-container"}).get_text(strip=True)
            price = soup.find("span", {"class": "ds-value"}).get_text(strip=True)
            details = {
                'address': address,
                'price': price,
            }
            return details
        except Exception as e:
            st.warning(f"❌ Failed to parse property details: {e}")
            return None
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
st.title("C2 Creative Comps")

with st.form("property_form"):
    url = st.text_input("Enter Zillow Property URL (e.g., https://www.zillow.com/homedetails/1876-Mississippi-Ave-NE-Saint-Petersburg-FL-33703/46978274_zpid/):")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Get Property Details and Run Comps")

if submitted:
    if url:
        with st.spinner("Fetching property details and comps..."):
            property_details = get_property_details(url)

        if property_details:
            # Display fetched property details
            st.subheader(f"Property Details for: {property_details['address']}")
            st.write(f"Price: {property_details['price']}")

            # Get comps data from the user or your logic (for now we'll use placeholder data)
            comps = [
                {'address': '1800 Mississippi Ave NE, Saint Petersburg, FL', 'price': 380000},
                {'address': '1727 Mississippi Ave NE, Saint Petersburg, FL', 'price': 375000},
                {'address': '1851 Mississippi Ave NE, Saint Petersburg, FL', 'price': 390000},
            ]

            # Display the comps
            st.subheader("Comparable Properties (Comps)")

            for comp in comps:
                st.write(f"Address: {comp['address']}, Price: ${comp['price']:,.2f}")

            # Calculate ARV and MAO
            arv, mao = calculate_comps_and_mao(comps, repair_costs)

            st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
            st.markdown(f"### 🏷️ Maximum Allowable Offer (60% Rule): `${mao:,.2f}`")
    else:
        st.error("Please enter a valid Zillow URL.")

# pip install requests beautifulsoup4 streamlit
import requests
from bs4 import BeautifulSoup
import streamlit as st
import re

def get_property_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.warning(f"❌ Failed to fetch property details. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        address = soup.find("h1", {"class": "ds-address-container"}).get_text(strip=True)
        price_str = soup.find("span", {"class": "ds-value"}).get_text(strip=True).replace("$", "").replace(",", "")
        price = int(float(price_str))

        zip_match = re.search(r"(\d{5})", address)
        zip_code = zip_match.group(1) if zip_match else ""

        return {'address': address, 'price': price, 'zip_code': zip_code}
    except Exception as e:
        st.warning(f"❌ Failed to parse property details: {e}")
        return None

def get_nearby_comps(zip_code):
    comps_url = f"https://www.zillow.com/homes/{zip_code}_rb/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(comps_url, headers=headers)
    if response.status_code != 200:
        st.warning("❌ Could not fetch nearby comps.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script")

    raw_json = ""
    for script in scripts:
        if "searchResults" in script.text:
            raw_json = script.text
            break

    addresses = re.findall(r'"streetAddress":"(.*?)"', raw_json)
    prices = re.findall(r'"price":([0-9]+)', raw_json)

    comps = []
    for addr, price in zip(addresses, prices):
        comps.append({'address': addr, 'price': int(price)})

    return comps[:5]  # return top 5 comps

def calculate_comps_and_mao(comps, repair_costs):
    prices = [comp["price"] for comp in comps]
    arv = sum(prices) / len(prices) if prices else 0
    mao = (arv * 0.6) - repair_costs
    return arv, mao

# Streamlit UI
st.title("📍 Real-Time Zillow Comps + MAO Calculator")

with st.form("property_form"):
    url = st.text_input("Zillow Property URL")
    repair_costs = st.number_input("Estimated Repair Costs", min_value=0, value=0, step=1000)
    submitted = st.form_submit_button("Run Analysis")

if submitted:
    if url:
        with st.spinner("Fetching data..."):
            property_details = get_property_details(url)

        if property_details:
            st.subheader(f"📌 Property Details: {property_details['address']}")
            st.write(f"Price: ${property_details['price']:,.2f}")

            with st.spinner("Finding nearby comparables..."):
                comps = get_nearby_comps(property_details['zip_code'])

            if comps:
                st.subheader("🏠 Nearby Comparable Properties")
                for comp in comps:
                    st.write(f"Address: {comp['address']}, Price: ${comp['price']:,.2f}")

                arv, mao = calculate_comps_and_mao(comps, repair_costs)
                st.markdown(f"### 💰 Estimated ARV: `${arv:,.2f}`")
                st.markdown(f"### 🏷️ Maximum Allowable Offer (MAO): `${mao:,.2f}`")
            else:
                st.error("No comparables found.")
        else:
            st.error("Unable to fetch property details.")
    else:
        st.error("Please enter a valid Zillow URL.")

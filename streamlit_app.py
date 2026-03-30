import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Smoothie App", page_icon="🥤", layout="centered")

# =========================
# TITLE
# =========================
st.title("🥤 Customize your Smoothie")
st.write("Choose up to 5 fruits for your smoothie.")

# =========================
# NAME INPUT
# =========================
name_on_order = st.text_input("Name on Smoothie")

# =========================
# LOAD ALL FRUITS FROM API
# =========================
@st.cache_data
def load_fruit_data():
    response = requests.get("https://my.smoothiefroot.com/api/fruit", timeout=5)
    data = response.json()

    df = pd.DataFrame(data)

    # Build mapping for UI vs API
    df["FRUIT_NAME"] = df["name"].str.title()
    df["SEARCH_ON"] = df["name"]

    return df[["FRUIT_NAME", "SEARCH_ON"]]

fruit_data = load_fruit_data()

# =========================
# MULTISELECT
# =========================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_data["FRUIT_NAME"].tolist(),
    max_selections=5
)

# =========================
# FUNCTION: GET NUTRITION
# =========================
@st.cache_data
def get_nutrition(search_value):
    encoded_value = quote(search_value)
    url = f"https://my.smoothiefroot.com/api/fruit/{encoded_value}"

    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return None

# =========================
# MAIN LOGIC
# =========================
ingredients_string = ''

if ingredients_list:

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = fruit_data.loc[
            fruit_data["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Display mapping (matches training UI)
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Section header
        st.subheader(fruit_chosen + ' Nutrition Information')

        try:
            df = get_nutrition(search_on)

            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No nutrition data available")

        except requests.exceptions.RequestException:
            st.error("API request failed. Check internet or API availability.")

# =========================
# ORDER BUTTON
# =========================
if ingredients_list and name_on_order:

    if st.button("Submit Order"):

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        st.write("Ingredients:", ingredients_string)

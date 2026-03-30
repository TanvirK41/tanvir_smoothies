# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# =========================
# SNOWFLAKE CONNECTION
# =========================
cnx = st.connection("snowflake")
session = cnx.session()

# =========================
# TITLE + INSTRUCTIONS
# =========================
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# =========================
# NAME INPUT
# =========================
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# =========================
# LOAD DATA FROM SNOWFLAKE
# =========================
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# =========================
# MULTISELECT
# =========================
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# =========================
# MAIN LOGIC
# =========================
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        # Show mapping
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Nutrition section
        st.subheader(fruit_chosen + ' Nutrition Information')

        # =========================
        # SAFE API CALL
        # =========================
        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            if smoothiefroot_response.status_code == 200:
                st.dataframe(
                    data=smoothiefroot_response.json(),
                    use_container_width=True
                )
            else:
                st.warning("API returned no data")

        except Exception:
            st.warning("External API not accessible in Snowflake environment")
            st.info(f"Simulated search value used: {search_on}")

# =========================
# INSERT ORDER
# =========================
if ingredients_list:

    if st.button('Submit Order'):

        session.sql("""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (?, ?)
        """, params=[ingredients_string, name_on_order]).collect()

        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

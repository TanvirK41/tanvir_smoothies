# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Snowflake connection (Streamlit Cloud compatible)
cnx = st.connection("snowflake")
session = cnx.session()

# Title and instructions
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load fruit data
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
    .select(col("FRUIT_NAME")) \
    .to_pandas()

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# IF block
if ingredients_list:

    # Build ingredients string
    ingredients_string = ' '.join(ingredients_list)

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql("""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (?, ?)
        """, params=[ingredients_string, name_on_order]).collect()

        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

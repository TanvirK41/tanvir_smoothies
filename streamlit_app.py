# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title and instructions
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get Snowflake session
session = get_active_session()

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
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Correct INSERT (2 columns, 2 values)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # Submit button
    time_to_insert = st.button('Submit Order')

    # Insert only on click
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        # Success message with name
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

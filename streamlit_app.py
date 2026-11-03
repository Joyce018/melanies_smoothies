# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Application title
st.title(":cup_with_straw: Customize your Favourite Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Customer name input
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Retrieve fruit options from Snowflake
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

# Convert Snowpark DataFrame into a Python list
fruit_options = [
    row["FRUIT_NAME"]
    for row in my_dataframe.collect()
]

# Allow customers to select up to 5 ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5
)

# Submit order
if st.button("Submit Order"):

    if not name_on_order.strip():
        st.warning("Please enter your name.")

    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")

    else:
        ingredients_string = " ".join(ingredients_list)

        # Insert order into Snowflake
        my_insert_stmt = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """

        session.sql(
            my_insert_stmt,
            params=[ingredients_string, name_on_order.strip()]
        ).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
# New section to display smoothiefruit nutrition information

smoothiefruit_response = requests.get(
    "https://my.smoothiefruit.com/api/fruit/watermelon"
)

st.text(smoothiefruit_response)

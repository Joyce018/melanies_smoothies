
# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col('FRUIT_NAME'))

# Convert the Snowpark Dataframe to a Python list
fruit_options = [
    row["FRUIT_NAME"]
    for row in my_dataframe.collect()
]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Generate API search value from fruit name
        search_on = fruit_chosen.lower().replace(" ", "")

        st.subheader(fruit_chosen + ' Nutrition Information')

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}",
            timeout=15
        )

        smoothiefroot_response.raise_for_status()

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # st.write(ingredients_string)

    my_insert_stmt = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES (?, ?)
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(
            my_insert_stmt,
            params=[ingredients_string.strip(), name_on_order.strip()]
        ).collect()

        st.success(
            f'Your Smoothie is ordered, {name_on_order}!',
            icon="✅"
        )

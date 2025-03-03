import streamlit as st
from authentication import authentication_ui
from units_conversion import convert_units, conversion_factors
from database import execute_query, fetch_data
import pandas as pd

# Initialize Authentication
authentication_ui()

# -------- UNIT CONVERTER -------- #
st.title("🔄 Unit Converter App")
st.write("Select a category, enter a value, and get real-time conversions.")

categories = list(conversion_factors.keys())  # Get available categories
category = st.selectbox("📌 Choose a Category", categories)

if category:  # Ensure a category is selected
    unit_options = list(conversion_factors[category].keys())  # Get available unit conversions
    unit = st.selectbox("🔁 Select Conversion", unit_options)
    value = st.number_input("📝 Enter Value")

    if st.button("Convert"):
        if not st.session_state["logged_in"] and st.session_state["guest_conversions"] >= 5:
            st.warning("⚠ You have reached the guest limit! Please sign up or log in to save your Conversions History!")
        else:
            result = convert_units(value, category, unit)

            if st.session_state["logged_in"]:
                execute_query(
                    "INSERT INTO history (username, category, conversion, input_value, converted_value) VALUES (?, ?, ?, ?, ?)",
                    (st.session_state["username"], category, unit, str(value), str(result))  # Ensure values are stored as strings
                )
            else:
                st.session_state["guest_conversions"] += 1

            st.text(f"Converted Value: {result}")

    # Fetch data from the database
    # Debugging: Check the raw fetched data
history_data = fetch_data(
    "SELECT category, conversion, input_value, converted_value FROM history WHERE username=?", 
    (st.session_state["username"],)
)

# st.write("🔍 Debug Data (Raw from DB):", history_data)  # 👀 Debug output

if st.session_state["logged_in"]:
    st.subheader("📜 Your Conversion History")

    # Fetch data from the database
    history_data = fetch_data(
        "SELECT category, conversion, input_value, converted_value FROM history WHERE username=?", 
        (st.session_state["username"],)
    )

    if history_data and isinstance(history_data, list) and len(history_data) > 0:
        # Ensure data is a list of tuples
        if isinstance(history_data[0], dict):
            # Convert list of dictionaries to list of tuples
            history_data = [(row["category"], row["conversion"], row["input_value"], row["converted_value"]) for row in history_data]

        # Convert history_data to a DataFrame
        df = pd.DataFrame(history_data, columns=["Category", "Conversion", "Input Value", "Converted Value"])

        # Handle None values
        df.fillna("N/A", inplace=True)  # Replace NaN with "N/A"

        # Convert all values to strings for safe display
        df = df.astype(str)  

        # Display the table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No history found.")  # ❌ This will now only show for logged-in users

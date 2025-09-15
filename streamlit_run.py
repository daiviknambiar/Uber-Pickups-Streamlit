# ---
# lambda-test: false  # auxiliary-file
# ---
# ## Demo Streamlit application.
#
# Streamlit is designed to run its apps as Python scripts, not functions, so we separate the Streamlit
# code into this module, away from the Modal application code.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from supabase import create_client, Client
import os


def get_client() -> Client:
    """Initialize Supabase client using .env credentials"""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

    return create_client(url, key)


def main():
    supabase = get_client()
    response = supabase.table("game_stats").select("*").limit(5).execute()

    st.subheader("NBA Game Stats from Supabase")
    if response.data:
        nba_df = pd.DataFrame(response.data)
        st.dataframe(nba_df)
    else:
        st.write("No data found in the 'game_stats' table.")
    
    # Streamlit selector for player that displays their points per game visually
    if response.data:
        player_names = nba_df["player"].unique()
        selected_player = st.selectbox("Select a player:", player_names)
        player_data = nba_df[nba_df["player"] == selected_player]
        st.subheader(f"Points in game for {selected_player}")
        st.bar_chart(player_data.set_index("game_date")["points"])

    st.title("Uber pickups in NYC!")

    DATE_COLUMN = "date/time"
    DATA_URL = (
        "https://s3-us-west-2.amazonaws.com/"
        "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
    )

    @st.cache_data
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows)

        def lowercase(x):
            return str(x).lower()

        data.rename(lowercase, axis="columns", inplace=True)
        data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
        return data

    data_load_state = st.text("Loading data...")
    data = load_data(10000)
    data_load_state.text("Done! (using st.cache_data)")

    if st.checkbox("Show raw data"):
        st.subheader("Raw data")
        st.write(data)

    st.subheader("Number of pickups by hour")
    hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

    # Some number in the range 0-23
    hour_to_filter = st.slider("hour", 0, 23, 17)
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    st.subheader(f"Map of all pickups at {hour_to_filter}:00")
    st.map(filtered_data)

    # Pickup counts for each date
    st.subheader("Count of pickups by date")
    date_counts = data[DATE_COLUMN].dt.date.value_counts().sort_index()
    st.bar_chart(date_counts)

    # Pickups by day of the week
    st.subheader("Pickups by day of week")
    day_choice = st.selectbox(
        "Choose a day:",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    )
    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(
        day_choice
    )
    day_selection = data[data[DATE_COLUMN].dt.dayofweek == day]
    st.map(day_selection)


if __name__ == "__main__":
    main()

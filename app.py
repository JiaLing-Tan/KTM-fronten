import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="KTMB Live Tracker", layout="wide")

BACKEND_URL = "https://ktm-backend-846g.onrender.com"  # change this after deploying backend

st.title("🚆 KTMB Live Train Tracker")

placeholder = st.empty()

while True:
    try:
        response = requests.get(BACKEND_URL, timeout=10)
        data = response.json()
        timestamp = data.get("timestamp")
        trains = data.get("data", {}).get("data", [])

        if not trains:
            st.warning("No train data found.")
            time.sleep(10)
            continue

        df = pd.DataFrame([
            {
                "Train": t["vehicle"]["label"],
                "Trip ID": t["trip"]["tripId"],
                "Lat": t["position"]["latitude"],
                "Lon": t["position"]["longitude"],
                "Speed (km/h)": t["position"]["speed"],
            } for t in trains
        ])

        # Center map
        avg_lat, avg_lon = df["Lat"].mean(), df["Lon"].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7)

        # Add markers
        for _, row in df.iterrows():
            folium.Marker(
                [row["Lat"], row["Lon"]],
                popup=f"{row['Train']} ({row['Speed (km/h)']} km/h)",
                tooltip=row["Train"]
            ).add_to(m)

        st.markdown(f"**Last updated:** {timestamp}")
        st_folium(m, width=900, height=600)

    except Exception as e:
        st.error(f"Error: {e}")

    # refresh every 10s
    time.sleep(10)

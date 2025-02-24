import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import base64
# Set Page Config
st.set_page_config(page_title="Weather Analysis", page_icon="📊", layout="wide")

# 🎨 Background Styling
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    bg_image = f"""
    <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
    </style>
    """
    st.markdown(bg_image, unsafe_allow_html=True)

# Call the function
set_background("p2.jpg")


# Title
st.title("📊 Weather Analysis")

# Check if City Exists in Session State
if "city" not in st.session_state:
    st.warning("⚠️ No city entered! Go to the Home page and enter a city.")
    st.stop()

# Get City Name from Session
city = st.text_input("Enter City Name:", st.session_state.get("city", ""), key="city_input")

st.subheader(f"🌆 Weather Forecast for {city}")

# 🔹 API Key & URL
API_KEY = "0c9912cc56bec91725713fc60d19d385"
URL = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}"

# Fetch Data
response = requests.get(URL)
if response.status_code != 200:
    st.error("⚠️ Error fetching weather data! Please try a different city.")
    st.stop()

data = response.json()

# Extract Forecast Data
days, temp, humidity, wind_speed = [], [], [], []
for forecast in data["list"]:
    if "12:00:00" in forecast["dt_txt"]:
        days.append(forecast["dt_txt"].split()[0])
        temp.append(forecast["main"]["temp"])
        humidity.append(forecast["main"]["humidity"])
        wind_speed.append(forecast["wind"]["speed"])

# Create DataFrame
df = pd.DataFrame({
    "Day": days,
    "Temperature (°C)": temp,
    "Humidity (%)": humidity,
    "Wind Speed (km/h)": wind_speed
})

# 📈 Temperature Trend
st.subheader("📈 Temperature Trend")
fig_temp = px.line(df, x="Day", y="Temperature (°C)", markers=True, title="Temperature Variation")
st.plotly_chart(fig_temp, use_container_width=True)

# 💦 Humidity Levels
st.subheader("💦 Humidity Levels")
fig_humidity = px.bar(df, x="Day", y="Humidity (%)", title="Humidity Levels", color="Humidity (%)")
st.plotly_chart(fig_humidity, use_container_width=True)

# 🌪️ Wind Speed
st.subheader("🌪️ Wind Speed")
fig_wind = px.scatter(df, x="Day", y="Wind Speed (km/h)", size="Wind Speed (km/h)", color="Wind Speed (km/h)")
st.plotly_chart(fig_wind, use_container_width=True)

# 📊 Data Table
st.subheader("📊 Weather Data")
st.dataframe(df)


st.sidebar.title("🎯 Weather Insights")  # Sidebar title with an emoji

st.sidebar.subheader("🌦Explore 5-day weather trends!")

st.sidebar.markdown(
    """
    - View *temperature, humidity, and wind speed* trends over the next 5 days.  
    - Interactive *line charts* show daily variations.  
    - A *scatter plot* compares *temperature vs. humidity*.  
    - Analyze weather conditions to plan your days better! ✈😎  
    """
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #64b5f6, #1976d2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



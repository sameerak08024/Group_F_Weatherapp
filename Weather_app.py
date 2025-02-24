import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import datetime

# OpenWeatherMap API Key
API_KEY = "0c9912cc56bec91725713fc60d19d385"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to convert UTC time to local time
def convert_utc_to_local(utc_time, timezone_offset):
    local_time = datetime.datetime.utcfromtimestamp(utc_time) + datetime.timedelta(seconds=timezone_offset)
    return local_time.strftime("%I:%M %p")  # Convert to 12-hour format

# Function to fetch weather data
def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "City": data["name"],
            "Temperature": f"{data['main']['temp']}°C",
            "Temperature_Value": data["main"]["temp"],  # Numeric value for recommendations
            "Humidity": f"{data['main']['humidity']}%",
            "Weather": data["weather"][0]["description"].title(),
            "Wind Speed": f"{data['wind']['speed']} m/s",
            "Sunrise": convert_utc_to_local(data["sys"]["sunrise"], data["timezone"]),
            "Sunset": convert_utc_to_local(data["sys"]["sunset"], data["timezone"])
        }
    else:
        return None

# Function to fetch 5-day forecast
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        forecast_list = data["list"]
        dates = [forecast["dt_txt"] for forecast in forecast_list]
        temps = [forecast["main"]["temp"] for forecast in forecast_list]
        return dates, temps
    else:
        return None, None

# Function to provide recommendations
def weather_recommendations(weather):
    temp = weather.get("Temperature_Value", 0)  # Using numeric temp value
    conditions = weather.get("Weather", "").lower()

    recommendations = []

    # Temperature-based recommendations
    if temp < 10:
        recommendations.append("🥶 Wear a heavy jacket and stay warm.")
    elif 10 <= temp < 20:
        recommendations.append("🧥 Wear a light jacket or sweater.")
    else:
        recommendations.append("☀️ Wear comfortable summer clothes.")

    # Weather conditions
    if "rain" in conditions:
        recommendations.append("🌧️ Carry an umbrella or a raincoat.")
    if "snow" in conditions:
        recommendations.append("❄️ Wear boots and a warm coat.")
    if "clear" in conditions:
        recommendations.append("🌞 A great day for outdoor activities!")

    return recommendations

# Streamlit UI with Icons
st.set_page_config(page_title="Weather App", page_icon="🌦️", layout="centered")

# Sidebar with Home Button and Link
with st.sidebar:
    st.markdown("### 🏠 **Navigation**")
    if st.button("🏠 Home"):
        st.rerun()  # Reloads the app
    st.link_button('🌍 Weather Forecasting Info', "https://en.wikipedia.org/wiki/Weather_forecasting")

    

# Main Title with Icon
st.title("🌤️ **Weather App**")
st.write("🔍 **Enter a city name to get real-time weather updates & recommendations.**")

# Initialize session state for city
if "city" not in st.session_state:
    st.session_state["city"] = ""

# User input for city
city = st.text_input("🏙️ **Enter City Name:**", st.session_state["city"], key="city_input")
weather_data = get_weather(city)
# Button to fetch weather
if st.button("🌡️ Get Weather"):
    if city.strip():
        
        if weather_data:
            st.success(f"🌆 Weather in {weather_data['City']}")
            st.write(f"🌡️ **Temperature:** {weather_data['Temperature']}")
            st.write(f"💧 **Humidity:** {weather_data['Humidity']}")
            st.write(f"🌥️ **Condition:** {weather_data['Weather']}")
            st.write(f"💨 **Wind Speed:** {weather_data['Wind Speed']}")
            st.write(f"🌅 **Sunrise:** {weather_data['Sunrise']} 🌞")
            st.write(f"🌇 **Sunset:** {weather_data['Sunset']} 🌆")

            # Display Recommendations
            st.write("📌 **Weather Recommendations:**")
            for rec in weather_recommendations(weather_data):
                st.write(f"- {rec}")
        else:
            st.error("❌ City not found! Please enter a valid city name.")
    else:
        st.warning("⚠️ Please enter a city name!")



# Custom Styling
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(to right, #5B86E5, #36D1DC);
            color: black;
        }
        h1, h2, h3, h4, h5, h6, p {
            color: black;
        }
    </style>
    """,
    unsafe_allow_html=True
)
 

# Forecast Section with Icon
st.title("📅 **5-Day Weather Forecast**")

if st.button("📊 Get Forecast"):
    if city.strip():
        dates, temps = get_forecast(city)  # Unpack tuple

        if dates and temps:  # Ensure data is not empty
            # Convert to DataFrame
            forecast_df = pd.DataFrame({"Date": dates, "Temperature": temps})

            st.success(f"📊 5-Day Forecast for {city}")

            # Save CSV
            csv_file = "weather_forecast.csv"
            forecast_df.to_csv(csv_file, index=False)

            # Layout: 5 columns for 5-day forecast
            cols = st.columns(5)  # Create 5 columns

            for i in range(min(5, len(forecast_df))):  # Ensure at most 5 days are displayed
                with cols[i]:
                    st.markdown(f"**📅 {forecast_df.iloc[i]['Date']}**", unsafe_allow_html=True)
                    st.write(f"🌡 *{forecast_df.iloc[i]['Temperature']}°C*")

            # Download CSV Button
            st.download_button(
                label="📥 Download Forecast Data",
                data=forecast_df.to_csv(index=False).encode('utf-8'),
                file_name="weather_forecast.csv",
                mime="text/csv"
            )

        else:
            st.error("❌ Failed to fetch forecast data. Check API key or city name.")
    else:
        st.warning("⚠️ Please enter a valid city name!")
# Forecast Section with Icon
st.title("📅 **5-Day Weather Forecast Chart**")

if st.button("📊 Get Forecast Chart", key="forecast_button"):
    if city.strip():
        st.session_state["city"] = city  # Store city in session
        dates, temps = get_forecast(city)

        if dates and temps:
            df = pd.DataFrame({"Date": dates, "Temperature": temps})
            fig = go.Figure([go.Scatter(x=df["Date"], y=df["Temperature"], mode='lines+markers', name="Temperature (°C)")])
            fig.update_layout(title="📊 5-Day Temperature Forecast", xaxis_title="Date & Time", yaxis_title="Temperature (°C)", xaxis=dict(tickangle=-45))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Failed to fetch data. Check API key or city name.")
    else:
        st.warning("⚠️ Please enter a valid city name!")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #64b5f6, #1976d2);
        color: white;
        padding: 20px;
    }
    [data-testid="stSidebar"] .css-1d391kg {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

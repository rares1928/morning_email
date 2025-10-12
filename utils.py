"""
Utility functions for the morning email system.
Includes functions for fetching weather, quotes, facts, and sending emails.
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json


def get_weather_info(city="Goettingen"):
    """
    Fetch weather information for a given city using Open-Meteo API.
    
    Args:
        city (str): City name (default: "Goettingen")
    
    Returns:
        dict: Weather information including temperature range, forecast, and precipitation
    """
    # Coordinates for Goettingen, Germany
    # For other cities, you can use a geocoding API to get coordinates
    city_coords = {
        "Goettingen": {"lat": 51.5412, "lon": 9.9158}
    }
    
    if city not in city_coords:
        return {"error": f"City {city} not found in database"}
    
    lat = city_coords[city]["lat"]
    lon = city_coords[city]["lon"]
    
    # Open-Meteo API endpoint
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode",
        "timezone": "Europe/Berlin",
        "forecast_days": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract today's weather
        daily = data["daily"]
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        precipitation_sum = daily["precipitation_sum"][0]
        precipitation_prob = daily["precipitation_probability_max"][0]
        weather_code = daily["weathercode"][0]
        
        # Interpret weather code
        forecast = interpret_weather_code(weather_code)
        
        return {
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precipitation_sum": precipitation_sum,
            "precipitation_prob": precipitation_prob,
            "forecast": forecast,
            "city": city
        }
    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}


def interpret_weather_code(code):
    """
    Interpret WMO weather codes from Open-Meteo API.
    
    Args:
        code (int): Weather code
    
    Returns:
        str: Human-readable weather description
    """
    weather_codes = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌦️",
        53: "Moderate drizzle 🌦️",
        55: "Dense drizzle 🌧️",
        61: "Slight rain 🌧️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Slight snow 🌨️",
        73: "Moderate snow 🌨️",
        75: "Heavy snow ❄️",
        77: "Snow grains ❄️",
        80: "Slight rain showers 🌦️",
        81: "Moderate rain showers 🌧️",
        82: "Violent rain showers ⛈️",
        85: "Slight snow showers 🌨️",
        86: "Heavy snow showers 🌨️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with slight hail ⛈️",
        99: "Thunderstorm with heavy hail ⛈️"
    }
    return weather_codes.get(code, "Unknown weather condition")


def get_clothing_recommendation(weather_info):
    """
    Generate clothing recommendations based on weather conditions.
    
    Args:
        weather_info (dict): Weather information dictionary
    
    Returns:
        str: Clothing recommendation
    """
    if "error" in weather_info:
        return "Check the weather before heading out!"
    
    temp_max = weather_info["temp_max"]
    temp_min = weather_info["temp_min"]
    avg_temp = (temp_max + temp_min) / 2
    precipitation_prob = weather_info["precipitation_prob"]
    
    recommendations = []
    
    # Temperature-based recommendations
    if avg_temp < 0:
        recommendations.append("Heavy winter coat and warm layers 🧥")
    elif avg_temp < 5:
        recommendations.append("Thick jacket and sweater 🧥")
    elif avg_temp < 10:
        recommendations.append("Jacket and light sweater 🧥")
    elif avg_temp < 15:
        recommendations.append("Light jacket or hoodie 👕")
    elif avg_temp < 20:
        recommendations.append("Hoodie or light cardigan 👕")
    else:
        recommendations.append("Light clothing, t-shirt is fine 👕")
    
    # Precipitation recommendations
    if precipitation_prob > 50:
        recommendations.append("Don't forget your umbrella! ☔")
    elif precipitation_prob > 30:
        recommendations.append("Bring an umbrella just in case ☂️")
    
    return " | ".join(recommendations)


def get_science_quote():
    """
    Fetch a random science or philosophy quote using the Quotable API.
    
    Returns:
        dict: Quote text and author
    """
    try:
        # Quotable API with science/mathematics tags
        url = "https://api.quotable.io/quotes/random"
        params = {
            "tags": "science|technology|philosophy",
            "maxLength": 200
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            quote = data[0]
            return {
                "text": quote["content"],
                "author": quote["author"]
            }
        else:
            # Fallback quote
            return {
                "text": "The important thing is not to stop questioning. Curiosity has its own reason for existing.",
                "author": "Albert Einstein"
            }
    except Exception as e:
        # Fallback quote in case of API failure
        return {
            "text": "Science is not only a disciple of reason but also one of romance and passion.",
            "author": "Stephen Hawking"
        }


def get_fun_fact():
    """
    Fetch a random fun fact for the day.
    
    Returns:
        str: A fun fact
    """
    try:
        # Using uselessfacts API
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return data["text"]
    except Exception as e:
        # Fallback to a static fun fact
        return "The heart of a shrimp is located in its head."


def build_email(recipient_name, fun_fact, weather_info, quote):
    """
    Build the HTML email content with all the daily information.
    
    Args:
        recipient_name (str): Name of the recipient
        fun_fact (str): Fun fact of the day
        weather_info (dict): Weather information dictionary
        quote (dict): Quote dictionary with 'text' and 'author'
    
    Returns:
        str: HTML formatted email content
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # Build weather section
    if "error" in weather_info:
        weather_section = f"""
        <div class="weather-section">
            <h2>🌤️ Weather Update</h2>
            <p style="color: #e74c3c;">{weather_info['error']}</p>
        </div>
        """
    else:
        clothing = get_clothing_recommendation(weather_info)
        weather_section = f"""
        <div class="weather-section">
            <h2>🌤️ Weather in {weather_info['city']}</h2>
            <p><strong>Forecast:</strong> {weather_info['forecast']}</p>
            <p><strong>Temperature:</strong> {weather_info['temp_min']:.1f}°C - {weather_info['temp_max']:.1f}°C</p>
            <p><strong>Chance of rain:</strong> {weather_info['precipitation_prob']}%</p>
            <div class="clothing-recommendation">
                <h3>👔 What to wear today:</h3>
                <p>{clothing}</p>
            </div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                margin-top: 25px;
            }}
            h3 {{
                color: #27ae60;
                margin-top: 15px;
            }}
            .greeting {{
                font-size: 1.2em;
                color: #555;
                margin-bottom: 20px;
            }}
            .fun-fact {{
                background-color: #fff3cd;
                padding: 15px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .quote {{
                background-color: #e8f4f8;
                padding: 15px;
                border-left: 4px solid #3498db;
                margin: 20px 0;
                font-style: italic;
                border-radius: 5px;
            }}
            .quote-author {{
                text-align: right;
                font-weight: bold;
                color: #2980b9;
                margin-top: 10px;
            }}
            .weather-section {{
                background-color: #e8f8f5;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .clothing-recommendation {{
                background-color: #fef5e7;
                padding: 10px;
                border-radius: 5px;
                margin-top: 15px;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Good Morning, {recipient_name}! ☀️</h1>
            <p class="greeting">{current_date}</p>
            
            <div class="fun-fact">
                <h2>💡 Fun Fact of the Day</h2>
                <p>{fun_fact}</p>
            </div>
            
            <div class="quote">
                <h2>📚 Quote of the Day</h2>
                <p>"{quote['text']}"</p>
                <p class="quote-author">— {quote['author']}</p>
            </div>
            
            {weather_section}
            
            <div class="footer">
                <p>Have a wonderful day! 🌟</p>
                <p style="font-size: 0.8em;">Sent with ❤️ from your Raspberry Pi</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def send_email(recipient_email, recipient_name, email_content, sender_email, sender_password, smtp_server, smtp_port):
    """
    Send an email using SMTP.
    
    Args:
        recipient_email (str): Recipient's email address
        recipient_name (str): Recipient's name (for subject line)
        email_content (str): HTML content of the email
        sender_email (str): Sender's email address
        sender_password (str): Sender's email password/app password
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP port number
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Good Morning {recipient_name}! ☀️ {datetime.now().strftime('%b %d')}"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Attach HTML content
        html_part = MIMEText(email_content, "html")
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print(f"✓ Email sent successfully to {recipient_name} ({recipient_email})")
        return True
    
    except Exception as e:
        print(f"✗ Failed to send email to {recipient_name} ({recipient_email}): {str(e)}")
        return False


"""
Utility functions for the morning email system.
Includes functions for fetching weather, quotes, facts, and sending emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from apis import get_weather_info, get_random_quote, get_random_fact

cities_locations = {
    "Goettingen": {"latitude": 51.5413, "longitude": 9.9158},
    "Bucharest": {"latitude": 44.4268, "longitude": 26.1025},
}

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


def build_email_body(recipient_name="Boss", weather_info=True, random_quote=True, random_fact=True, quote_data=None, fact_text=None):
    """
    Build the HTML email body with optional weather info, quote, and fact.
    
    Args:
        recipient_name (str): Name of the email recipient
        weather_info (bool): Whether to include weather information
        random_quote (bool): Whether to include a random quote
        random_fact (bool): Whether to include a random fact
        quote_data (dict): Pre-fetched quote data (optional, will fetch if None)
        fact_text (str): Pre-fetched fact text (optional, will fetch if None)
    
    Returns:
        str: HTML formatted email body
    """
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
            .section h2 {{ color: #667eea; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #667eea; color: white; }}
            .quote {{ font-style: italic; font-size: 1.1em; margin: 10px 0; }}
            .author {{ text-align: right; color: #666; }}
            .fact {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #667eea; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Good Morning {recipient_name}! ☀️</h1>
                <p>Here's your daily dose of information</p>
            </div>
    """
    
    # Add weather information if requested
    if weather_info:
        try:
            weather_data = get_weather_info(
                cities_locations["Goettingen"]["latitude"], 
                cities_locations["Goettingen"]["longitude"]
            )
            
            html_body += f"""
            <div class="section">
                <h2>🌤️ Weather in Göttingen - {weather_data['date']}</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Day Min</th>
                        <th>Day Max</th>
                    </tr>
            """
            
            # Group weather data by metric type
            metrics = {
                "Temperature (°C)": ["max_temperature_day", "min_temperature_day"],
                "Relative Humidity (%)": ["max_relative_humidity_day", "min_relative_humidity_day"],
                "Apparent Temperature (°C)": ["max_apparent_temperature_day", "min_apparent_temperature_day"],
                "Precipitation Probability (%)": ["max_precipitation_probability_day", "min_precipitation_probability_day"]
            }
            
            for metric_name, keys in metrics.items():
                min_key = keys[1]  # min key
                max_key = keys[0]  # max key
                html_body += f"""
                    <tr>
                        <td>{metric_name}</td>
                        <td>{weather_data[min_key]:.1f}</td>
                        <td>{weather_data[max_key]:.1f}</td>
                    </tr>
                """
            
            html_body += """
                </table>
            </div>
            """
        except Exception as e:
            html_body += f"""
            <div class="section">
                <h2>🌤️ Weather</h2>
                <p>Sorry, weather information is currently unavailable.</p>
            </div>
            """
    
    # Add random quote if requested
    if random_quote:
        try:
            # Use provided quote_data or fetch a new one
            if quote_data is None:
                quote_data = get_random_quote()
            html_body += f"""
            <div class="section">
                <h2>💭 Daily Quote</h2>
                <div class="quote">"{quote_data['quote']}"</div>
                <div class="author">- {quote_data['author']}</div>
            </div>
            """
        except Exception as e:
            html_body += """
            <div class="section">
                <h2>💭 Daily Quote</h2>
                <p>Sorry, no quote available today.</p>
            </div>
            """
    
    # Add random fact if requested
    if random_fact:
        try:
            # Use provided fact_text or fetch a new one
            if fact_text is None:
                fact_text = get_random_fact()
            html_body += f"""
            <div class="section">
                <h2>🤓 Did You Know?</h2>
                <div class="fact">{fact_text}</div>
            </div>
            """
        except Exception as e:
            html_body += """
            <div class="section">
                <h2>🤓 Did You Know?</h2>
                <p>Sorry, no fun fact available today.</p>
            </div>
            """
    
    html_body += """
        </div>
    </body>
    </html>
    """
    
    return html_body


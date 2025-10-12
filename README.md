# Morning Email System 📧☀️

A Raspberry Pi-based automated email system that sends daily morning emails with fun facts, science quotes, weather information, and clothing recommendations.

## Features

- 📚 **Fun Fact of the Day**: Random interesting facts to start your morning
- 💡 **Science Quote**: Inspirational quotes from scientists and philosophers
- 🌤️ **Weather Forecast**: Temperature range and forecast for Goettingen, Germany
- 👔 **Clothing Recommendations**: Smart suggestions based on weather conditions
- 📧 **Beautiful HTML Emails**: Professional, responsive email design

## Setup Instructions

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configure Email Credentials

Edit `emails.py` and update the following:

- **SENDER_EMAIL**: Your Gmail address
- **SENDER_PASSWORD**: Your Gmail App Password (see below)
- **RECIPIENTS**: Dictionary of names and email addresses

#### Getting a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to Security → 2-Step Verification (enable if not already)
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password and paste it in `emails.py`

### 3. Test the Script

Before setting up the cron job, test that everything works:

```bash
python3 main.py
```

You should see output showing the email being sent, and recipients should receive their morning emails.

### 4. Set Up the Cron Job

See `setup_cron.txt` for detailed instructions on setting up the automated daily email.

Quick version:
```bash
# Open crontab editor
crontab -e

# Add this line to send emails at 7:00 AM daily
0 7 * * * /usr/bin/python3 /home/pi/morning_emails_pi/main.py >> /home/pi/morning_emails_pi/logs/cron.log 2>&1

# Create logs directory
mkdir -p logs
```

## File Structure

```
morning_emails_pi/
├── main.py              # Main script that orchestrates everything
├── utils.py             # Utility functions (APIs, email building, sending)
├── emails.py            # Email configuration and credentials
├── requirements.txt     # Python dependencies
├── setup_cron.txt       # Detailed cron setup instructions
├── README.md            # This file
└── logs/                # Log files from cron jobs
```

## APIs Used

- **Weather**: [Open-Meteo](https://open-meteo.com/) - Free, no API key required
- **Quotes**: [Quotable API](https://github.com/lukePeavey/quotable) - Free, no API key required
- **Fun Facts**: [Useless Facts API](https://uselessfacts.jsph.pl/) - Free, no API key required

## Customization

### Change the City

Edit the coordinates in `utils.py` function `get_weather_info()`:

```python
city_coords = {
    "YourCity": {"lat": YOUR_LATITUDE, "lon": YOUR_LONGITUDE}
}
```

### Adjust Clothing Recommendations

Modify the temperature thresholds in `utils.py` function `get_clothing_recommendation()`.

### Change Email Design

Edit the HTML template in `utils.py` function `build_email()`.

### Schedule Different Times

Edit your crontab with different time values. See `setup_cron.txt` for examples.

## Troubleshooting

### Emails Not Sending

1. Check your credentials in `emails.py`
2. Make sure you're using an App Password, not your regular Gmail password
3. Check that 2-Step Verification is enabled on your Google account
4. Run `python3 main.py` manually to see error messages

### Cron Job Not Running

1. Check cron service: `sudo systemctl status cron`
2. Check logs: `tail -f logs/cron.log`
3. Check system logs: `grep CRON /var/log/syslog`
4. Make sure the Pi is on and has internet at the scheduled time

### Weather API Not Working

- Check your internet connection
- The Open-Meteo API is free and doesn't require authentication
- If it's down, the script will use cached/fallback data

## Future Enhancements

- Web interface to manage recipients and settings
- Support for multiple cities
- Add more content types (news, holidays, etc.)
- Email preferences per recipient
- Manual trigger via web UI or SMS
- Email delivery confirmation

## License

MIT License - Feel free to use and modify as you wish!

---

Made with ❤️ on Raspberry Pi Zero 2W


#!/usr/bin/env python3
"""
Morning Email System - Main Script
Sends daily morning emails with fun facts, quotes, and weather information.
"""

import sys
from datetime import datetime
from utils import (
    get_weather_info,
    get_science_quote,
    get_fun_fact,
    build_email,
    send_email
)
from emails import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECIPIENTS
)


def main():
    """
    Main function to orchestrate the morning email sending process.
    """
    print(f"\n{'='*60}")
    print(f"Morning Email System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Check if credentials are configured
    if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_app_password_here":
        print("⚠️  ERROR: Please configure your email credentials in emails.py")
        print("   - Set SENDER_EMAIL to your email address")
        print("   - Set SENDER_PASSWORD to your app password")
        sys.exit(1)
    
    # Fetch data once for all recipients
    print("Fetching daily content...")
    print("  → Getting fun fact...")
    fun_fact = get_fun_fact()
    print(f"    ✓ Got it!")
    
    print("  → Getting science quote...")
    quote = get_science_quote()
    print(f"    ✓ Quote by {quote['author']}")
    
    print("  → Getting weather for Goettingen...")
    weather_info = get_weather_info("Goettingen")
    if "error" in weather_info:
        print(f"    ⚠️  {weather_info['error']}")
    else:
        print(f"    ✓ {weather_info['temp_min']:.1f}°C - {weather_info['temp_max']:.1f}°C, {weather_info['forecast']}")
    
    print(f"\nSending emails to {len(RECIPIENTS)} recipient(s)...\n")
    
    # Send emails to all recipients
    success_count = 0
    fail_count = 0
    
    for name, email in RECIPIENTS.items():
        print(f"Processing email for {name}...")
        
        # Build personalized email
        email_content = build_email(name, fun_fact, weather_info, quote)
        
        # Send email
        if send_email(
            recipient_email=email,
            recipient_name=name,
            email_content=email_content,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT
        ):
            success_count += 1
        else:
            fail_count += 1
        
        print()  # Empty line for readability
    
    # Summary
    print(f"{'='*60}")
    print(f"Summary: {success_count} successful, {fail_count} failed")
    print(f"{'='*60}\n")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


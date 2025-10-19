#!/usr/bin/env python3
"""
Morning Email System - Main Script
Sends daily morning emails with fun facts, quotes, and weather information.
"""

from utils import build_email_body, send_email
from emails import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECIPIENTS
)


def main():
    """
    Main function to send morning emails to all recipients.
    """
    print("🌅 Starting Morning Email System...")
    print(f"📧 Sending emails to {len(RECIPIENTS)} recipients")
    
    # Send emails to all recipients
    for recipient_name, recipient_email in RECIPIENTS.items():
        print(f"\n📤 Preparing email for {recipient_name} ({recipient_email})...")
        
        # Build personalized email body
        html_body = build_email_body(
            recipient_name=recipient_name,
            weather_info=True,
            random_quote=True,
            random_fact=True
        )
        
        # Send the email
        success = send_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            email_content=html_body,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT
        )
        
        if success:
            print(f"✅ Email sent successfully to {recipient_name}")
        else:
            print(f"❌ Failed to send email to {recipient_name}")
    
    print(f"\n🎉 Morning email process completed!")


if __name__ == "__main__":
    main()


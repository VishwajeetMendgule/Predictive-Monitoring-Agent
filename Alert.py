import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email(payload, recipient_email):
    """
    Sends an HTML-formatted email alert containing system metrics and AI RCA.
    """
    # 1. Grab credentials from environment variables (NEVER hardcode passwords!)
    sender_email = os.environ.get("ALERT_EMAIL") 
    sender_password = os.environ.get("ALERT_APP_PASSWORD") 
    
    if not sender_email or not sender_password:
        print("⚠️ Email credentials missing. Skipping email alert.")
        return

    # 2. Set up the email headers
    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"🚨 CRITICAL ALERT: AIOps Anomaly Detected at {payload['timestamp']}"
    msg['From'] = "AIOps Predictive Agent <" + sender_email + ">"
    msg['To'] = recipient_email

    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="border-left: 4px solid #d9534f; padding-left: 15px;">
                <h2 style="color: #d9534f; margin-bottom: 5px;">🚨 System  Alert</h2>
                <p style="margin-top: 0; color: #666;">Automated alert triggered by the Predictive Agent.</p>
            </div>
            
            <h3 style="border-bottom: 1px solid #eee; padding-bottom: 5px;">1. Current System State</h3>
            <ul>
                <li><b>Timestamp:</b> {payload['timestamp']}</li>
                <li><b>CPU:</b> {payload['cpu']}%</li>
                <li><b>Memory:</b> {payload['memory']}%</li>
                <li><b>Network:</b> {payload['network']} Mbps</li>
            </ul>

            <h3 style="border-bottom: 1px solid #eee; padding-bottom: 5px;">2. AI Root Cause Analysis</h3>
            <ul>
                <li><b>Severity:</b> <span style="color: #d9534f; font-weight: bold;">{payload['llm_response']['severity']}</span></li>
                <li><b>Failure Type:</b> {payload['llm_response']['failure_type']}</li>
                <li><b>Root Cause:</b> {payload['llm_response']['RootCause']}</li>
                <li><b>Estimated Impact Time:</b> {payload['llm_response']['impactmins']} minutes</li>
            </ul>

            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h4 style="margin-top: 0; color: #0275d8;">🛠️ Recommended Action</h4>
                <p style="margin-bottom: 0;">{payload['llm_response']['RecommendedAction']}</p>
            </div>
        </body>
    </html>
    """
    
    # Attach the HTML to the email
    msg.attach(MIMEText(html, "html"))

    # 4. Send the email via Gmail's SMTP server
    try:
        # If using Outlook/Office365, the server is 'smtp.office365.com' and port is 587
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            
        print(f"📧 Alert email successfully delivered to {recipient_email}")
        
    except Exception as e:
        print(f"⚠️ Failed to send alert email: {e}")

     
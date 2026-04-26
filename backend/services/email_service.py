import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    async def send_order_confirmation(self, to_email: str, order_data: dict):
        subject = f"Order Confirmation - #{order_data['order_id']}"
        body = f"""
        Thank you for your order!
        
        Order ID: {order_data['order_id']}
        Total: ${order_data['total']:.2f}
        Status: {order_data['status']}
        
        We'll notify you when your order ships.
        """
        
        await self._send_email(to_email, subject, body)
    
    async def _send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
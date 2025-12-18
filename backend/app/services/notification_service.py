"""Notification service for sending alerts"""
from typing import Dict, List, Optional
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


class NotificationService:
    """Service for sending notifications across channels"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict:
        """Send an email notification"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            return {"success": True, "channel": "email", "recipient": to_email}
        except Exception as e:
            return {"success": False, "channel": "email", "error": str(e)}
    
    async def send_order_notification(
        self,
        notification_type: str,
        order: Dict,
        customer: Dict,
        channel: str = "email"
    ) -> Dict:
        """Send order-related notification"""
        templates = {
            "order_created": {
                "subject": f"Order Confirmation - #{order.get('id', '')[:8]}",
                "template": "order_confirmation"
            },
            "order_updated": {
                "subject": f"Order Update - #{order.get('id', '')[:8]}",
                "template": "order_update"
            },
            "payment_received": {
                "subject": f"Payment Received - #{order.get('id', '')[:8]}",
                "template": "payment_confirmation"
            },
            "shipped": {
                "subject": f"Your Order Has Shipped - #{order.get('id', '')[:8]}",
                "template": "order_shipped"
            },
            "delivered": {
                "subject": f"Order Delivered - #{order.get('id', '')[:8]}",
                "template": "order_delivered"
            }
        }
        
        template_info = templates.get(notification_type, {})
        subject = template_info.get("subject", "Order Notification")
        
        html_content = self._render_order_template(
            template_info.get("template", "default"),
            order,
            customer
        )
        
        if channel == "email" and customer.get("email"):
            return await self.send_email(
                to_email=customer["email"],
                subject=subject,
                html_content=html_content
            )
        
        return {"success": False, "error": "Unsupported channel or missing contact"}
    
    def _render_order_template(self, template_name: str, order: Dict, customer: Dict) -> str:
        """Render order email template"""
        order_id = str(order.get("id", ""))[:8].upper()
        customer_name = customer.get("name", "Customer")
        total = order.get("total", 0)
        status = order.get("status", "pending").title()
        
        templates = {
            "order_confirmation": f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #003366;">Order Confirmed!</h1>
                    <p>Hi {customer_name},</p>
                    <p>Thank you for your order! We've received your order and are processing it now.</p>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Order Details</h3>
                        <p><strong>Order ID:</strong> #{order_id}</p>
                        <p><strong>Total:</strong> ${total:.2f}</p>
                        <p><strong>Status:</strong> {status}</p>
                    </div>
                    <p>We'll send you another email when your order ships.</p>
                    <p>Thank you for shopping with us!</p>
                </body>
                </html>
            """,
            "order_shipped": f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #003366;">Your Order Has Shipped!</h1>
                    <p>Hi {customer_name},</p>
                    <p>Great news! Your order #{order_id} is on its way.</p>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Order ID:</strong> #{order_id}</p>
                        <p><strong>Status:</strong> Shipped</p>
                    </div>
                    <p>You'll receive a notification when it's delivered.</p>
                </body>
                </html>
            """,
            "payment_confirmation": f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #003366;">Payment Received</h1>
                    <p>Hi {customer_name},</p>
                    <p>We've received your payment of ${total:.2f} for order #{order_id}.</p>
                    <p>Thank you!</p>
                </body>
                </html>
            """
        }
        
        return templates.get(template_name, templates["order_confirmation"])
    
    async def send_bulk_notification(
        self,
        recipients: List[Dict],
        subject: str,
        content: str,
        channel: str = "email"
    ) -> Dict:
        """Send bulk notifications"""
        results = {"sent": 0, "failed": 0, "errors": []}
        
        for recipient in recipients:
            if channel == "email" and recipient.get("email"):
                result = await self.send_email(
                    to_email=recipient["email"],
                    subject=subject,
                    html_content=content
                )
                if result.get("success"):
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(result.get("error"))
        
        return results


# Singleton instance
notification_service = NotificationService()

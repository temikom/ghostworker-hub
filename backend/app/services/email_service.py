"""Email Service for sending transactional emails"""
import smtplib
import structlog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from jinja2 import Template

from app.core.config import settings

logger = structlog.get_logger()


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_name = settings.SMTP_FROM_NAME
        self.from_email = settings.SMTP_FROM_EMAIL
    
    def _get_smtp_connection(self):
        """Create SMTP connection"""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        if self.smtp_user and self.smtp_password:
            server.login(self.smtp_user, self.smtp_password)
        return server
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML content
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f"attachment; filename={attachment['filename']}"
                    )
                    msg.attach(part)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info("email_sent", to=to_email, subject=subject)
            return True
            
        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e))
            return False
    
    async def send_verification_email(self, to_email: str, name: str, token: str) -> bool:
        """Send email verification"""
        verify_url = f"{settings.API_BASE_URL}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to GhostWorker!</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>
                    <p>Thank you for signing up! Please verify your email address to get started.</p>
                    <p style="text-align: center;">
                        <a href="{verify_url}" class="button">Verify Email</a>
                    </p>
                    <p>Or copy and paste this link:</p>
                    <p style="word-break: break-all; color: #6366f1;">{verify_url}</p>
                    <p>This link expires in 24 hours.</p>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify your GhostWorker email",
            html_content=html_content
        )
    
    async def send_password_reset_email(self, to_email: str, name: str, token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.API_BASE_URL}/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password.</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link:</p>
                    <p style="word-break: break-all; color: #6366f1;">{reset_url}</p>
                    <p>This link expires in 1 hour. If you didn't request this, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset your GhostWorker password",
            html_content=html_content
        )
    
    async def send_team_invitation_email(
        self,
        to_email: str,
        team_name: str,
        inviter_name: str,
        token: str
    ) -> bool:
        """Send team invitation email"""
        invite_url = f"{settings.API_BASE_URL}/accept-invite?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>You're Invited!</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p><strong>{inviter_name}</strong> has invited you to join <strong>{team_name}</strong> on GhostWorker.</p>
                    <p style="text-align: center;">
                        <a href="{invite_url}" class="button">Accept Invitation</a>
                    </p>
                    <p>This invitation expires in 7 days.</p>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Join {team_name} on GhostWorker",
            html_content=html_content
        )
    
    async def send_order_notification(
        self,
        to_email: str,
        customer_name: str,
        order_id: str,
        order_status: str,
        order_total: float
    ) -> bool:
        """Send order status notification"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .order-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Update</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p>Your order status has been updated.</p>
                    <div class="order-info">
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Status:</strong> {order_status}</p>
                        <p><strong>Total:</strong> ${order_total:.2f}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Order {order_id} - {order_status}",
            html_content=html_content
        )
    
    async def send_invoice_email(
        self,
        to_email: str,
        customer_name: str,
        invoice_number: str,
        amount: float,
        due_date: str,
        pdf_attachment: Optional[bytes] = None
    ) -> bool:
        """Send invoice email with optional PDF attachment"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .invoice-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Invoice {invoice_number}</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p>Please find your invoice details below.</p>
                    <div class="invoice-info">
                        <p><strong>Invoice Number:</strong> {invoice_number}</p>
                        <p><strong>Amount Due:</strong> ${amount:.2f}</p>
                        <p><strong>Due Date:</strong> {due_date}</p>
                    </div>
                    <p>Please make payment by the due date to avoid any late fees.</p>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        attachments = None
        if pdf_attachment:
            attachments = [{
                'filename': f'{invoice_number}.pdf',
                'content': pdf_attachment
            }]
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Invoice {invoice_number} from GhostWorker",
            html_content=html_content,
            attachments=attachments
        )
    
    async def send_2fa_enabled_alert(self, to_email: str, name: str) -> bool:
        """Send 2FA enabled notification"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 2FA Enabled</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>
                    <p>Two-factor authentication has been successfully enabled on your account.</p>
                    <p>Your account is now more secure. You'll need to enter a verification code from your authenticator app each time you log in.</p>
                    <p>If you didn't enable this, please contact support immediately.</p>
                </div>
                <div class="footer">
                    <p>© 2024 GhostWorker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Two-factor authentication enabled",
            html_content=html_content
        )


# Singleton instance
email_service = EmailService()

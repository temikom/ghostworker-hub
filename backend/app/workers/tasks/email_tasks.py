"""Email background tasks"""
import asyncio
from celery import shared_task
from sqlalchemy import select

from app.db.session import SyncSessionLocal
from app.models import User, Invoice, Customer, Order
from app.services.email_service import email_service


def run_async(coro):
    """Run async function in sync context"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, max_retries=3)
def send_verification_email_task(self, user_id: str, token: str):
    """Send email verification in background"""
    try:
        with SyncSessionLocal() as db:
            user = db.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            
            if user:
                run_async(email_service.send_verification_email(
                    to_email=user.email,
                    name=user.name,
                    token=token
                ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_password_reset_task(self, user_id: str, token: str):
    """Send password reset email in background"""
    try:
        with SyncSessionLocal() as db:
            user = db.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            
            if user:
                run_async(email_service.send_password_reset_email(
                    to_email=user.email,
                    name=user.name,
                    token=token
                ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_team_invitation_task(
    self,
    email: str,
    team_name: str,
    inviter_name: str,
    token: str
):
    """Send team invitation email in background"""
    try:
        run_async(email_service.send_team_invitation_email(
            to_email=email,
            team_name=team_name,
            inviter_name=inviter_name,
            token=token
        ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_order_notification_task(self, order_id: str, status: str):
    """Send order status notification in background"""
    try:
        with SyncSessionLocal() as db:
            order = db.execute(
                select(Order).where(Order.id == order_id)
            ).scalar_one_or_none()
            
            if order:
                customer = db.execute(
                    select(Customer).where(Customer.id == order.customer_id)
                ).scalar_one_or_none()
                
                if customer and customer.email:
                    run_async(email_service.send_order_notification(
                        to_email=customer.email,
                        customer_name=customer.name,
                        order_id=str(order.id)[:8],
                        order_status=status,
                        order_total=float(order.total)
                    ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_invoice_email_task(self, invoice_id: str):
    """Send invoice email in background"""
    try:
        with SyncSessionLocal() as db:
            invoice = db.execute(
                select(Invoice).where(Invoice.id == invoice_id)
            ).scalar_one_or_none()
            
            if invoice:
                customer = db.execute(
                    select(Customer).where(Customer.id == invoice.customer_id)
                ).scalar_one_or_none()
                
                if customer and customer.email:
                    run_async(email_service.send_invoice_email(
                        to_email=customer.email,
                        customer_name=customer.name,
                        invoice_number=invoice.invoice_number,
                        amount=float(invoice.total),
                        due_date=str(invoice.due_date) if invoice.due_date else "On receipt"
                    ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_2fa_alert_task(self, user_id: str):
    """Send 2FA enabled alert in background"""
    try:
        with SyncSessionLocal() as db:
            user = db.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            
            if user:
                run_async(email_service.send_2fa_enabled_alert(
                    to_email=user.email,
                    name=user.name
                ))
    except Exception as e:
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))

"""Payment service for Stripe integration"""
import stripe
from typing import Optional, Dict, Any
from decimal import Decimal
from app.core.config import settings
from app.core.encryption import decrypt_value


class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None
    
    def configure(self, secret_key: str):
        """Configure Stripe with decrypted secret key"""
        stripe.api_key = secret_key
    
    async def create_customer(self, email: str, name: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a Stripe customer"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
        return {
            "id": customer.id,
            "email": customer.email,
            "name": customer.name
        }
    
    async def create_checkout_session(
        self,
        order_id: str,
        line_items: list,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a Stripe Checkout session"""
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                "order_id": order_id,
                **(metadata or {})
            }
        )
        return {
            "session_id": session.id,
            "checkout_url": session.url
        }
    
    async def create_payment_intent(
        self,
        amount: int,  # Amount in cents
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a payment intent for custom payment flows"""
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency.lower(),
            customer=customer_id,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True}
        )
        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status
        }
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict:
        """Confirm a payment intent"""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "id": intent.id,
            "status": intent.status,
            "amount": intent.amount,
            "currency": intent.currency
        }
    
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Refund a payment (full or partial)"""
        refund_params = {"payment_intent": payment_intent_id}
        if amount:
            refund_params["amount"] = amount
        if reason:
            refund_params["reason"] = reason
        
        refund = stripe.Refund.create(**refund_params)
        return {
            "id": refund.id,
            "status": refund.status,
            "amount": refund.amount
        }
    
    async def create_invoice(
        self,
        customer_id: str,
        line_items: list,
        auto_advance: bool = True,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a Stripe invoice"""
        invoice = stripe.Invoice.create(
            customer=customer_id,
            auto_advance=auto_advance,
            metadata=metadata or {}
        )
        
        for item in line_items:
            stripe.InvoiceItem.create(
                customer=customer_id,
                invoice=invoice.id,
                description=item.get("description"),
                quantity=item.get("quantity", 1),
                unit_amount=item.get("unit_amount"),
                currency=item.get("currency", "usd")
            )
        
        return {
            "id": invoice.id,
            "status": invoice.status,
            "hosted_invoice_url": invoice.hosted_invoice_url,
            "pdf": invoice.invoice_pdf
        }
    
    async def send_invoice(self, invoice_id: str) -> Dict:
        """Send an invoice to customer"""
        invoice = stripe.Invoice.send_invoice(invoice_id)
        return {
            "id": invoice.id,
            "status": invoice.status,
            "hosted_invoice_url": invoice.hosted_invoice_url
        }
    
    async def get_payment_methods(self, customer_id: str) -> list:
        """Get customer's saved payment methods"""
        methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )
        return [
            {
                "id": m.id,
                "brand": m.card.brand,
                "last4": m.card.last4,
                "exp_month": m.card.exp_month,
                "exp_year": m.card.exp_year
            }
            for m in methods.data
        ]
    
    def verify_webhook_signature(self, payload: bytes, signature: str, webhook_secret: str) -> Dict:
        """Verify Stripe webhook signature"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return {"valid": True, "event": event}
        except stripe.error.SignatureVerificationError:
            return {"valid": False, "event": None}
    
    async def handle_webhook_event(self, event: Dict) -> Dict:
        """Process webhook events"""
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(data)
        
        return {"processed": False, "message": f"Unhandled event type: {event_type}"}
    
    async def _handle_checkout_completed(self, data: Dict) -> Dict:
        """Handle successful checkout"""
        return {
            "processed": True,
            "order_id": data.get("metadata", {}).get("order_id"),
            "payment_status": "paid",
            "amount": data.get("amount_total"),
            "customer_email": data.get("customer_email")
        }
    
    async def _handle_payment_succeeded(self, data: Dict) -> Dict:
        """Handle successful payment"""
        return {
            "processed": True,
            "payment_intent_id": data.get("id"),
            "status": "succeeded",
            "amount": data.get("amount")
        }
    
    async def _handle_payment_failed(self, data: Dict) -> Dict:
        """Handle failed payment"""
        return {
            "processed": True,
            "payment_intent_id": data.get("id"),
            "status": "failed",
            "error": data.get("last_payment_error", {}).get("message")
        }
    
    async def _handle_invoice_paid(self, data: Dict) -> Dict:
        """Handle paid invoice"""
        return {
            "processed": True,
            "invoice_id": data.get("id"),
            "status": "paid",
            "amount": data.get("amount_paid")
        }
    
    async def _handle_invoice_failed(self, data: Dict) -> Dict:
        """Handle failed invoice payment"""
        return {
            "processed": True,
            "invoice_id": data.get("id"),
            "status": "failed"
        }


# Singleton instance
payment_service = PaymentService()

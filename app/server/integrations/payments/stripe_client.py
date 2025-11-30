"""Stripe payment client."""

import stripe
from typing import Dict, Any, Optional
import structlog

from core.config import settings

logger = structlog.get_logger()

# Configure Stripe
stripe.api_key = settings.stripe_secret_key


class StripeClient:
    """Stripe payment client."""
    
    def __init__(self):
        self.secret_key = settings.stripe_secret_key
        self.publishable_key = settings.stripe_publishable_key
        self.webhook_secret = settings.stripe_webhook_secret
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create payment intent."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            logger.info(
                "Payment intent created",
                payment_intent_id=intent.id,
                amount=amount,
                currency=currency
            )
            
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe payment intent error", error=str(e))
            raise Exception(f"Stripe error: {str(e)}")
    
    async def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve payment intent."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "metadata": intent.metadata
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe retrieve error", error=str(e), payment_intent_id=payment_intent_id)
            raise Exception(f"Stripe error: {str(e)}")
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            logger.info("Customer created", customer_id=customer.id, email=email)
            
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe customer creation error", error=str(e))
            raise Exception(f"Stripe error: {str(e)}")
    
    async def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create checkout session."""
        try:
            session_params = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {}
            }
            
            if customer_id:
                session_params["customer"] = customer_id
            
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info("Checkout session created", session_id=session.id)
            
            return {
                "id": session.id,
                "url": session.url,
                "payment_status": session.payment_status
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe checkout session error", error=str(e))
            raise Exception(f"Stripe error: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> Dict[str, Any]:
        """Verify webhook signature."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            logger.info("Webhook signature verified", event_type=event.type, event_id=event.id)
            return event
            
        except ValueError as e:
            logger.error("Invalid webhook payload", error=str(e))
            raise Exception("Invalid webhook payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid webhook signature", error=str(e))
            raise Exception("Invalid webhook signature")
    
    async def refund_payment(self, payment_intent_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Refund payment."""
        try:
            refund_params = {"payment_intent": payment_intent_id}
            if amount:
                refund_params["amount"] = amount
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info("Payment refunded", refund_id=refund.id, payment_intent_id=payment_intent_id)
            
            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount,
                "payment_intent": refund.payment_intent
            }
            
        except stripe.error.StripeError as e:
            logger.error("Stripe refund error", error=str(e))
            raise Exception(f"Stripe error: {str(e)}")


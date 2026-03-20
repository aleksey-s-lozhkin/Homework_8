import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, metadata=None):
    """Создаёт продукт в Stripe"""

    return stripe.Product.create(name=name, metadata=metadata or {})


def create_stripe_price(amount, currency='rub', product_id=None):
    """Создаёт цену"""

    unit_amount = int(amount * 100)
    return stripe.Price.create(
        unit_amount=unit_amount,
        currency=currency,
        product=product_id,
    )


def create_stripe_checkout_session(price_id, success_url, cancel_url, metadata=None):
    """Создаёт сессию Checkout"""

    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata or {},
    )

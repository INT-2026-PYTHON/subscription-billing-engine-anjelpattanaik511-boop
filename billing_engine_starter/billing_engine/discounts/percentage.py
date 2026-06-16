"""
PercentageDiscount — e.g., 20% off the subtotal.

Examples:
    PercentageDiscount(Decimal("0.20")).apply(Money(1000, "INR"), ctx)  ->  Money(200, "INR")
    PercentageDiscount(Decimal("1.00")).apply(Money(500, "INR"), ctx)   ->  Money(500, "INR")  # 100% off
"""

from decimal import Decimal

from billing_engine.money import Money
from billing_engine.discounts.base import Discount, DiscountContext


class PercentageDiscount(Discount):
    def __init__(self, percentage: Decimal) -> None:
        if isinstance(percentage, float):
            raise TypeError("Percentage must be Decimal, not float")
        if not isinstance(percentage, Decimal):
            raise TypeError("Percentage must be a Decimal")
        if percentage < 0 or percentage > 1:
            raise ValueError("Percentage must be between 0 and 1 inclusive")
        self.percentage = percentage

    def apply(self, subtotal: Money, context: DiscountContext) -> Money:
        if not isinstance(subtotal, Money):
            raise TypeError("subtotal must be Money")
        if not isinstance(context, DiscountContext):
            raise TypeError("context must be DiscountContext")
        discount_amount = subtotal * self.percentage
        return discount_amount

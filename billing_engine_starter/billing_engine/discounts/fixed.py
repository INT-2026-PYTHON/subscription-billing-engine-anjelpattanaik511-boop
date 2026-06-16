"""
FixedAmountDiscount — e.g., flat ₹500 off.

CAPPING RULE: if the fixed amount exceeds the subtotal, return subtotal
(so the discounted total never goes below zero).
"""

from billing_engine.money import Money
from billing_engine.discounts.base import Discount, DiscountContext


class FixedAmountDiscount(Discount):
    def __init__(self, amount: Money) -> None:
        if not isinstance(amount, Money):
            raise TypeError("FixedAmountDiscount amount must be Money")
        if amount.is_negative():
            raise ValueError("FixedAmountDiscount amount must be non-negative")
        self.amount = amount

    def apply(self, subtotal: Money, context: DiscountContext) -> Money:
        if not isinstance(subtotal, Money):
            raise TypeError("subtotal must be Money")
        if not isinstance(context, DiscountContext):
            raise TypeError("context must be DiscountContext")
        if subtotal.currency != self.amount.currency:
            raise ValueError("Currency mismatch between subtotal and discount amount")
        if self.amount >= subtotal:
            return subtotal
        return self.amount

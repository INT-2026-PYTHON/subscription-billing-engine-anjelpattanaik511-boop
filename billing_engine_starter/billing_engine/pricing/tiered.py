"""
TieredPricing — different price per unit depending on the tier the quantity falls into.

This is the "cumulative" / "stacked" tier model, NOT the "volume" model:
    Tiers: [(0, 1000, ₹2.00), (1000, 5000, ₹1.50), (5000, None, ₹1.00)]
    Quantity = 6000:
        First 1000 units  @ ₹2.00 = ₹2000
        Next  4000 units  @ ₹1.50 = ₹6000
        Last  1000 units  @ ₹1.00 = ₹1000
        ------------------------------------
        Total                     = ₹9000

A tier with `to_units = None` is the open-ended top tier.

Tier boundaries are HALF-OPEN on the right: a tier (from, to, price)
covers units strictly less than `to` (i.e. [from, to)).
"""

from dataclasses import dataclass
from typing import Optional

from billing_engine.money import Money
from billing_engine.pricing.base import PricingStrategy


@dataclass(frozen=True)
class Tier:
    from_units: int
    to_units: Optional[int]   # None means "unlimited" / open-ended
    unit_price: Money


class TieredPricing(PricingStrategy):
    """Charges across multiple price tiers based on cumulative quantity."""

    def __init__(self, tiers: list[Tier]) -> None:
        if not tiers:
            raise ValueError("TieredPricing requires at least one tier")
        if any(not isinstance(tier, Tier) for tier in tiers):
            raise TypeError("All items in tiers must be Tier instances")

        self.tiers = list(tiers)
        self.tiers.sort(key=lambda tier: tier.from_units)

        if self.tiers[0].from_units != 0:
            raise ValueError("TieredPricing tiers must start at 0")

        currency = self.tiers[0].unit_price.currency
        last_to = 0
        for index, tier in enumerate(self.tiers):
            if not isinstance(tier.from_units, int) or tier.from_units < 0:
                raise ValueError("Tier from_units must be a non-negative integer")
            if tier.to_units is not None:
                if not isinstance(tier.to_units, int) or tier.to_units <= tier.from_units:
                    raise ValueError("Tier to_units must be an integer greater than from_units")
            if tier.unit_price.is_negative():
                raise ValueError("Tier unit_price must be non-negative")
            if tier.unit_price.currency != currency:
                raise ValueError("All tier prices must share the same currency")
            if tier.from_units != last_to:
                raise ValueError("TieredPricing tiers must be contiguous")
            last_to = tier.to_units if tier.to_units is not None else last_to

        if self.tiers[-1].to_units is not None:
            raise ValueError("TieredPricing top tier must be open-ended")

    def calculate(self, quantity: int) -> Money:
        if not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer")
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")

        total = Money.zero(self.tiers[0].unit_price.currency)
        remaining = quantity
        for tier in self.tiers:
            if remaining <= 0:
                break

            tier_start = tier.from_units
            tier_end = tier.to_units if tier.to_units is not None else quantity
            if quantity <= tier_start:
                continue

            upper_bound = min(quantity, tier_end) if tier.to_units is not None else quantity
            units_in_tier = upper_bound - tier_start
            total += tier.unit_price * units_in_tier

        return total

"""
VATCalculator — single-rate VAT (e.g. 19% in Germany).
"""

from decimal import Decimal

from billing_engine.money import Money
from billing_engine.taxes.base import TaxCalculator, TaxContext, TaxBreakdown


class VATCalculator(TaxCalculator):
    def __init__(self, rate: Decimal) -> None:
        if isinstance(rate, float):
            raise TypeError("VAT rate must be Decimal, not float")
        if not isinstance(rate, Decimal):
            raise TypeError("VAT rate must be a Decimal")
        if rate < 0 or rate > 1:
            raise ValueError("VAT rate must be between 0 and 1 inclusive")
        self.rate = rate

    def apply(self, taxable: Money, context: TaxContext) -> TaxBreakdown:
        if not isinstance(taxable, Money):
            raise TypeError("taxable must be Money")
        if not isinstance(context, TaxContext):
            raise TypeError("context must be TaxContext")

        vat_amount = taxable * self.rate
        label = f"VAT {self._format_percent(self.rate)}%"
        return TaxBreakdown(components=[(label, vat_amount)], total=vat_amount)

    @staticmethod
    def _format_percent(rate: Decimal) -> str:
        amount = (rate * Decimal("100")).normalize()
        return format(amount, 'f').rstrip('0').rstrip('.') if '.' in format(amount, 'f') else format(amount, 'f')

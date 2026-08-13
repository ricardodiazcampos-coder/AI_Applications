"""Utilidades compartidas entre la app de escritorio y la web."""

CURRENCY = "₡"
OTHER_UNEXPECTED_LABEL = "Otro imprevisto"


def format_money(amount: float) -> str:
    return f"{CURRENCY}{amount:,.2f}"

"""Lógica de presentación para la aplicación web."""

from typing import Any, Dict, List, Optional, Tuple

from models import FinancialProfile
from utils import OTHER_UNEXPECTED_LABEL, format_money
from validators import parse_positive_amount, parse_required_text


def resolve_unexpected_name(category: str, custom_name: str) -> Tuple[Optional[str], Optional[str]]:
    category = category.strip()
    if not category:
        return None, "Concepto es obligatorio."
    if category == OTHER_UNEXPECTED_LABEL:
        return parse_required_text(custom_name, "Nombre del gasto")
    return category, None


def get_warning(profile: FinancialProfile) -> str:
    if profile.available_balance < 0:
        return (
            "Gastas más de lo que ingresas. Revisa gastos fijos, imprevistos o aumenta ingresos."
        )
    if profile.money_left_after_savings < 0:
        return "El ahorro planificado supera el balance disponible."
    if profile.total_goal_contributions > profile.effective_savings and profile.planned_monthly_savings <= 0:
        return "Los aportes mensuales a metas superan lo que puedes ahorrar este mes."
    return ""


def get_summary_cards(profile: FinancialProfile) -> List[Dict[str, Any]]:
    items = [
        ("income", "Ingresos totales", profile.total_income, "success"),
        ("expenses", "Gastos totales (fijos + imprevistos)", profile.total_expenses, "primary"),
        ("balance", "Dinero restante (antes de ahorro)", profile.available_balance, "success"),
        ("savings", "Cantidad destinada al ahorro", profile.effective_savings, "info"),
        ("free", "Disponible tras ahorrar", profile.money_left_after_savings, "success"),
        ("saved_goals", "Total en metas", profile.total_saved_in_goals, "secondary"),
    ]
    cards = []
    for key, title, amount, tone in items:
        css = tone
        if key == "balance" and amount < 0:
            css = "danger"
        elif key == "free" and amount < 0:
            css = "danger"
        cards.append({"key": key, "title": title, "amount": format_money(amount), "tone": css})
    return cards


def get_chart_data(profile: FinancialProfile) -> Dict[str, Any]:
    income = profile.total_income
    fixed = profile.total_fixed_expenses
    unexpected = profile.total_unexpected_expenses
    savings = min(profile.effective_savings, max(0.0, profile.available_balance))
    other = max(0.0, profile.available_balance - savings)

    pie_parts = [
        ("Gastos fijos", fixed),
        ("Imprevistos", unexpected),
        ("Ahorro", savings),
        ("Disponible", other),
    ]
    pie_labels = [label for label, value in pie_parts if value > 0]
    pie_values = [value for _, value in pie_parts if value > 0]

    return {
        "pie": {"labels": pie_labels, "values": pie_values},
        "bar": {
            "labels": ["Ingresos", "Fijos", "Imprevistos", "Ahorro", "Libre"],
            "values": [
                income,
                fixed,
                unexpected,
                savings,
                max(0.0, profile.money_left_after_savings),
            ],
        },
        "has_data": income > 0 or profile.total_expenses > 0 or savings > 0,
    }


def build_view_context(profile: FinancialProfile, active_tab: str = "income") -> Dict[str, Any]:
    return {
        "active_tab": active_tab,
        "profile": profile,
        "format_money": format_money,
        "other_unexpected": OTHER_UNEXPECTED_LABEL,
        "preview": {
            "income": format_money(profile.total_income),
            "fixed": format_money(profile.total_fixed_expenses),
            "unexpected": format_money(profile.total_unexpected_expenses),
            "balance": format_money(profile.available_balance),
        },
        "summary_cards": get_summary_cards(profile),
        "warning": get_warning(profile),
        "chart_data": get_chart_data(profile),
        "goals_progress": [
            {
                "name": g.name,
                "saved": format_money(g.saved),
                "target": format_money(g.target),
                "percent": g.progress_percent,
                "remaining": format_money(g.remaining),
            }
            for g in profile.savings_goals
        ],
    }

"""Serialización del perfil financiero para sesión web."""

from typing import Any, Dict, List

from models import (
    FinancialProfile,
    FixedExpense,
    SavingsGoal,
    UnexpectedExpense,
)


def _expenses_to_dict(items: List[Any]) -> List[Dict[str, Any]]:
    return [{"name": item.name, "amount": item.amount} for item in items]


def _goals_to_dict(items: List[SavingsGoal]) -> List[Dict[str, Any]]:
    return [
        {
            "name": g.name,
            "target": g.target,
            "saved": g.saved,
            "monthly_contribution": g.monthly_contribution,
        }
        for g in items
    ]


def profile_to_dict(profile: FinancialProfile) -> Dict[str, Any]:
    return {
        "monthly_salary": profile.monthly_salary,
        "additional_income": profile.additional_income,
        "planned_monthly_savings": profile.planned_monthly_savings,
        "fixed_expenses": _expenses_to_dict(profile.fixed_expenses),
        "unexpected_expenses": _expenses_to_dict(profile.unexpected_expenses),
        "savings_goals": _goals_to_dict(profile.savings_goals),
    }


def profile_from_dict(data: Dict[str, Any]) -> FinancialProfile:
    return FinancialProfile(
        monthly_salary=float(data.get("monthly_salary", 0)),
        additional_income=float(data.get("additional_income", 0)),
        planned_monthly_savings=float(data.get("planned_monthly_savings", 0)),
        fixed_expenses=[
            FixedExpense(name=e["name"], amount=float(e["amount"]))
            for e in data.get("fixed_expenses", [])
        ],
        unexpected_expenses=[
            UnexpectedExpense(name=e["name"], amount=float(e["amount"]))
            for e in data.get("unexpected_expenses", [])
        ],
        savings_goals=[
            SavingsGoal(
                name=g["name"],
                target=float(g["target"]),
                saved=float(g.get("saved", 0)),
                monthly_contribution=float(g.get("monthly_contribution", 0)),
            )
            for g in data.get("savings_goals", [])
        ],
    )

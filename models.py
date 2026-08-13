"""Modelos de datos y lógica de cálculo financiero."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FixedExpense:
    name: str
    amount: float


@dataclass
class UnexpectedExpense:
    name: str
    amount: float


@dataclass
class SavingsGoal:
    name: str
    target: float
    saved: float = 0.0
    monthly_contribution: float = 0.0

    @property
    def progress_percent(self) -> float:
        if self.target <= 0:
            return 100.0 if self.saved > 0 else 0.0
        return min(100.0, (self.saved / self.target) * 100.0)

    @property
    def remaining(self) -> float:
        return max(0.0, self.target - self.saved)


@dataclass
class FinancialProfile:
    monthly_salary: float = 0.0
    additional_income: float = 0.0
    fixed_expenses: List[FixedExpense] = field(default_factory=list)
    unexpected_expenses: List[UnexpectedExpense] = field(default_factory=list)
    savings_goals: List[SavingsGoal] = field(default_factory=list)
    planned_monthly_savings: float = 0.0

    @property
    def total_income(self) -> float:
        return self.monthly_salary + self.additional_income

    @property
    def total_fixed_expenses(self) -> float:
        return sum(e.amount for e in self.fixed_expenses)

    @property
    def total_unexpected_expenses(self) -> float:
        return sum(e.amount for e in self.unexpected_expenses)

    @property
    def total_expenses(self) -> float:
        return self.total_fixed_expenses + self.total_unexpected_expenses

    @property
    def available_balance(self) -> float:
        return self.total_income - self.total_expenses

    @property
    def total_goal_contributions(self) -> float:
        return sum(g.monthly_contribution for g in self.savings_goals)

    @property
    def effective_savings(self) -> float:
        """Ahorro mensual efectivo: planificado o suma de aportes a metas, limitado al balance."""
        if self.planned_monthly_savings > 0:
            planned = self.planned_monthly_savings
        else:
            planned = self.total_goal_contributions
        if planned <= 0 and self.available_balance > 0:
            return max(0.0, self.available_balance)
        return min(planned, max(0.0, self.available_balance))

    @property
    def money_left_after_savings(self) -> float:
        return self.available_balance - self.effective_savings

    @property
    def total_saved_in_goals(self) -> float:
        return sum(g.saved for g in self.savings_goals)

    def summary_lines(self) -> List[tuple]:
        return [
            ("Ingresos totales", self.total_income),
            ("Gastos fijos", self.total_fixed_expenses),
            ("Gastos imprevistos", self.total_unexpected_expenses),
            ("Gastos totales", self.total_expenses),
            ("Balance (ingresos − gastos)", self.available_balance),
            ("Ahorro mensual planificado", self.effective_savings),
            ("Dinero libre tras ahorro", self.money_left_after_savings),
            ("Total acumulado en metas", self.total_saved_in_goals),
        ]

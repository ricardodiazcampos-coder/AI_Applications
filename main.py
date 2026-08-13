"""
Aplicación de gestión financiera personal con interfaz gráfica (Tkinter).
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Tuple

from models import FinancialProfile, FixedExpense, SavingsGoal, UnexpectedExpense
from utils import CURRENCY, OTHER_UNEXPECTED_LABEL, format_money
from validators import parse_positive_amount, parse_required_text

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class FinanzasPersonalesApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Gestión financiera personal")
        self.root.minsize(820, 620)
        self.profile = FinancialProfile()

        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")

        self._build_ui()
        self.refresh_all_views()

    def _build_ui(self) -> None:
        header = ttk.Label(
            self.root,
            text="Control de ingresos, gastos y metas de ahorro",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(pady=(12, 4))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.tab_income = ttk.Frame(self.notebook, padding=12)
        self.tab_expenses = ttk.Frame(self.notebook, padding=12)
        self.tab_unexpected = ttk.Frame(self.notebook, padding=12)
        self.tab_goals = ttk.Frame(self.notebook, padding=12)
        self.tab_summary = ttk.Frame(self.notebook, padding=12)
        self.tab_charts = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_income, text="Ingresos")
        self.notebook.add(self.tab_expenses, text="Gastos fijos")
        self.notebook.add(self.tab_unexpected, text="Gastos imprevistos")
        self.notebook.add(self.tab_goals, text="Metas de ahorro")
        self.notebook.add(self.tab_summary, text="Resumen")
        self.notebook.add(self.tab_charts, text="Gráficos")

        self._build_income_tab()
        self._build_expenses_tab()
        self._build_unexpected_tab()
        self._build_goals_tab()
        self._build_summary_tab()
        self._build_charts_tab()

        btn_bar = ttk.Frame(self.root)
        btn_bar.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(btn_bar, text="Actualizar resumen", command=self.refresh_all_views).pack(
            side=tk.RIGHT
        )

    def _build_income_tab(self) -> None:
        form = ttk.LabelFrame(self.tab_income, text="Datos de ingresos mensuales", padding=12)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Salario mensual:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.var_salary = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_salary, width=24).grid(row=0, column=1, sticky=tk.W, pady=4)

        ttk.Label(form, text="Ingresos adicionales (opcional):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.var_extra = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_extra, width=24).grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(form, text="Ahorro mensual planificado (opcional):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.var_planned_savings = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_planned_savings, width=24).grid(
            row=2, column=1, sticky=tk.W, pady=4
        )
        ttk.Label(
            form,
            text="Si lo deja vacío, se usa la suma de aportes a metas o el balance disponible.",
            font=("Segoe UI", 8),
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W)

        ttk.Button(form, text="Guardar ingresos", command=self.save_income).grid(
            row=4, column=0, columnspan=2, pady=(12, 0), sticky=tk.W
        )

        self.lbl_income_preview = ttk.Label(self.tab_income, text="", font=("Segoe UI", 10))
        self.lbl_income_preview.pack(anchor=tk.W, pady=12)

    def _build_expenses_tab(self) -> None:
        presets = ttk.LabelFrame(self.tab_expenses, text="Agregar gasto fijo", padding=12)
        presets.pack(fill=tk.X)

        ttk.Label(presets, text="Concepto:").grid(row=0, column=0, sticky=tk.W)
        self.var_expense_name = tk.StringVar()
        expense_combo = ttk.Combobox(
            presets,
            textvariable=self.var_expense_name,
            values=[
                "Alquiler o hipoteca",
                "Agua",
                "Electricidad",
                "Internet",
                "Préstamo o crédito",
                "Transporte",
                "Otros gastos fijos",
            ],
            width=28,
        )
        expense_combo.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(presets, text="Monto mensual:").grid(row=1, column=0, sticky=tk.W)
        self.var_expense_amount = tk.StringVar()
        ttk.Entry(presets, textvariable=self.var_expense_amount, width=20).grid(row=1, column=1, sticky=tk.W, pady=4)

        btns = ttk.Frame(presets)
        btns.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        ttk.Button(btns, text="Agregar", command=self.add_expense).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="Eliminar seleccionado", command=self.remove_expense).pack(side=tk.LEFT)

        table_frame = ttk.Frame(self.tab_expenses)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=12)

        cols = ("name", "amount")
        self.tree_expenses = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree_expenses.heading("name", text="Gasto")
        self.tree_expenses.heading("amount", text="Monto mensual")
        self.tree_expenses.column("name", width=320)
        self.tree_expenses.column("amount", width=140, anchor=tk.E)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_expenses.yview)
        self.tree_expenses.configure(yscrollcommand=scroll.set)
        self.tree_expenses.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_expenses_total = ttk.Label(self.tab_expenses, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_expenses_total.pack(anchor=tk.W)

    def _build_unexpected_tab(self) -> None:
        form = ttk.LabelFrame(
            self.tab_unexpected,
            text="Registrar gasto no previsto (este mes)",
            padding=12,
        )
        form.pack(fill=tk.X)

        ttk.Label(
            form,
            text="Use esta sección para imprevistos: médicos, mantenimiento, emergencias, etc.",
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        ttk.Label(form, text="Concepto:").grid(row=1, column=0, sticky=tk.W)
        self.var_unexpected_name = tk.StringVar()
        self.var_unexpected_name.trace_add("write", self._on_unexpected_type_changed)
        ttk.Combobox(
            form,
            textvariable=self.var_unexpected_name,
            values=[
                "Gastos médicos",
                "Mantenimiento casa",
                "Mantenimiento vehículo",
                "Emergencias",
                OTHER_UNEXPECTED_LABEL,
            ],
            width=28,
        ).grid(row=1, column=1, sticky=tk.W, pady=4)

        self.lbl_unexpected_custom = ttk.Label(form, text="Nombre del gasto:")
        self.lbl_unexpected_custom.grid(row=2, column=0, sticky=tk.W)
        self.var_unexpected_custom = tk.StringVar()
        self.entry_unexpected_custom = ttk.Entry(
            form, textvariable=self.var_unexpected_custom, width=28
        )
        self.entry_unexpected_custom.grid(row=2, column=1, sticky=tk.W, pady=4)
        self.lbl_unexpected_custom.grid_remove()
        self.entry_unexpected_custom.grid_remove()

        ttk.Label(form, text="Monto:").grid(row=3, column=0, sticky=tk.W)
        self.var_unexpected_amount = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_unexpected_amount, width=20).grid(
            row=3, column=1, sticky=tk.W, pady=4
        )

        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        ttk.Button(btns, text="Agregar", command=self.add_unexpected_expense).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="Eliminar seleccionado", command=self.remove_unexpected_expense).pack(side=tk.LEFT)

        table_frame = ttk.Frame(self.tab_unexpected)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=12)

        cols = ("name", "amount")
        self.tree_unexpected = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree_unexpected.heading("name", text="Gasto imprevisto")
        self.tree_unexpected.heading("amount", text="Monto")
        self.tree_unexpected.column("name", width=320)
        self.tree_unexpected.column("amount", width=140, anchor=tk.E)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_unexpected.yview)
        self.tree_unexpected.configure(yscrollcommand=scroll.set)
        self.tree_unexpected.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_unexpected_total = ttk.Label(self.tab_unexpected, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_unexpected_total.pack(anchor=tk.W)

    def _on_unexpected_type_changed(self, *_args) -> None:
        if self.var_unexpected_name.get().strip() == OTHER_UNEXPECTED_LABEL:
            self.lbl_unexpected_custom.grid()
            self.entry_unexpected_custom.grid()
        else:
            self.lbl_unexpected_custom.grid_remove()
            self.entry_unexpected_custom.grid_remove()
            self.var_unexpected_custom.set("")

    def _resolve_unexpected_name(self) -> Tuple[Optional[str], Optional[str]]:
        category = self.var_unexpected_name.get().strip()
        if not category:
            return None, "Concepto es obligatorio."
        if category == OTHER_UNEXPECTED_LABEL:
            name, err = parse_required_text(
                self.var_unexpected_custom.get(), "Nombre del gasto"
            )
            return (name, err)
        return category, None

    def _build_goals_tab(self) -> None:
        form = ttk.LabelFrame(self.tab_goals, text="Nueva meta de ahorro", padding=12)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Meta:").grid(row=0, column=0, sticky=tk.W)
        self.var_goal_name = tk.StringVar()
        goal_combo = ttk.Combobox(
            form,
            textvariable=self.var_goal_name,
            values=["Viaje", "Compra de artículo", "Vehículo", "Fondo de emergencia", "Meta personalizada"],
            width=28,
        )
        goal_combo.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Monto objetivo:").grid(row=1, column=0, sticky=tk.W)
        self.var_goal_target = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_goal_target, width=20).grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(form, text="Ya ahorrado:").grid(row=2, column=0, sticky=tk.W)
        self.var_goal_saved = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.var_goal_saved, width=20).grid(row=2, column=1, sticky=tk.W, pady=4)

        ttk.Label(form, text="Aporte mensual:").grid(row=3, column=0, sticky=tk.W)
        self.var_goal_monthly = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_goal_monthly, width=20).grid(row=3, column=1, sticky=tk.W, pady=4)

        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=2, pady=(8, 0), sticky=tk.W)
        ttk.Button(btns, text="Agregar meta", command=self.add_goal).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="Eliminar seleccionada", command=self.remove_goal).pack(side=tk.LEFT)

        list_frame = ttk.LabelFrame(self.tab_goals, text="Metas registradas", padding=8)
        list_frame.pack(fill=tk.X, pady=(8, 4))
        cols = ("name", "target", "saved", "monthly")
        self.tree_goals_manage = ttk.Treeview(list_frame, columns=cols, show="headings", height=4)
        for col, title, w in [
            ("name", "Meta", 220),
            ("target", "Objetivo", 100),
            ("saved", "Ahorrado", 100),
            ("monthly", "Aporte/mes", 100),
        ]:
            self.tree_goals_manage.heading(col, text=title)
            self.tree_goals_manage.column(col, width=w, anchor=tk.E if col != "name" else tk.W)
        self.tree_goals_manage.pack(fill=tk.X)

        self.goals_container = ttk.LabelFrame(self.tab_goals, text="Progreso visual", padding=8)
        self.goals_container.pack(fill=tk.BOTH, expand=True, pady=8)

    def _build_summary_tab(self) -> None:
        self.summary_labels: dict[str, ttk.Label] = {}
        cards = ttk.Frame(self.tab_summary)
        cards.pack(fill=tk.X)

        for i, key in enumerate(
            ["income", "expenses", "balance", "savings", "free", "saved_goals"]
        ):
            frame = ttk.LabelFrame(cards, text="", padding=8)
            frame.grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky=tk.NSEW)
            cards.columnconfigure(i % 3, weight=1)
            lbl = ttk.Label(frame, text="—", font=("Segoe UI", 11, "bold"))
            lbl.pack()
            self.summary_labels[key] = lbl

        self.summary_titles = {
            "income": "Ingresos totales",
            "expenses": "Gastos totales (fijos + imprevistos)",
            "balance": "Dinero restante (antes de ahorro)",
            "savings": "Cantidad destinada al ahorro",
            "free": "Disponible tras ahorrar",
            "saved_goals": "Total en metas",
        }

        split = ttk.Panedwindow(self.tab_summary, orient=tk.VERTICAL)
        split.pack(fill=tk.BOTH, expand=True, pady=12)

        unexpected_detail = ttk.LabelFrame(split, text="Gastos imprevistos del mes", padding=8)
        split.add(unexpected_detail, weight=1)
        cols_u = ("name", "amount")
        self.tree_unexpected_summary = ttk.Treeview(
            unexpected_detail, columns=cols_u, show="headings", height=4
        )
        self.tree_unexpected_summary.heading("name", text="Concepto")
        self.tree_unexpected_summary.heading("amount", text="Monto")
        self.tree_unexpected_summary.column("name", width=280)
        self.tree_unexpected_summary.column("amount", width=120, anchor=tk.E)
        self.tree_unexpected_summary.pack(fill=tk.BOTH, expand=True)
        self.lbl_unexpected_summary = ttk.Label(unexpected_detail, text="")
        self.lbl_unexpected_summary.pack(anchor=tk.W, pady=(4, 0))

        detail = ttk.LabelFrame(split, text="Detalle de metas", padding=8)
        split.add(detail, weight=2)

        cols = ("name", "saved", "target", "progress", "monthly")
        self.tree_goals = ttk.Treeview(detail, columns=cols, show="headings", height=8)
        for col, title, width in [
            ("name", "Meta", 200),
            ("saved", "Ahorrado", 100),
            ("target", "Objetivo", 100),
            ("progress", "Progreso", 90),
            ("monthly", "Aporte/mes", 100),
        ]:
            self.tree_goals.heading(col, text=title)
            self.tree_goals.column(col, width=width, anchor=tk.E if col != "name" else tk.W)
        self.tree_goals.pack(fill=tk.BOTH, expand=True)

        self.lbl_warning = ttk.Label(self.tab_summary, text="", foreground="#b45309")
        self.lbl_warning.pack(anchor=tk.W, pady=4)

    def _build_charts_tab(self) -> None:
        if not HAS_MATPLOTLIB:
            ttk.Label(
                self.tab_charts,
                text="Instale matplotlib (pip install -r requirements.txt) para ver gráficos.",
            ).pack(pady=20)
            return

        self.fig = Figure(figsize=(7.5, 4.5), dpi=100)
        self.ax_pie = self.fig.add_subplot(121)
        self.ax_bar = self.fig.add_subplot(122)
        self.fig.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_income(self) -> None:
        salary, err = parse_positive_amount(self.var_salary.get(), allow_zero=False)
        if err:
            messagebox.showerror("Validación", f"Salario: {err}")
            return
        extra, err = parse_positive_amount(self.var_extra.get(), allow_zero=True)
        if err:
            messagebox.showerror("Validación", f"Ingresos adicionales: {err}")
            return
        planned, err = parse_positive_amount(self.var_planned_savings.get(), allow_zero=True)
        if err:
            messagebox.showerror("Validación", f"Ahorro planificado: {err}")
            return

        self.profile.monthly_salary = salary or 0.0
        self.profile.additional_income = extra or 0.0
        self.profile.planned_monthly_savings = planned or 0.0
        messagebox.showinfo("Guardado", "Ingresos actualizados correctamente.")
        self.refresh_all_views()

    def add_expense(self) -> None:
        name, err = parse_required_text(self.var_expense_name.get(), "Concepto")
        if err:
            messagebox.showerror("Validación", err)
            return
        amount, err = parse_positive_amount(self.var_expense_amount.get(), allow_zero=False)
        if err:
            messagebox.showerror("Validación", f"Monto: {err}")
            return

        self.profile.fixed_expenses.append(FixedExpense(name=name, amount=amount or 0.0))
        self.var_expense_amount.set("")
        self.refresh_all_views()

    def remove_expense(self) -> None:
        selected = self.tree_expenses.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un gasto de la tabla.")
            return
        index = self.tree_expenses.index(selected[0])
        del self.profile.fixed_expenses[index]
        self.refresh_all_views()

    def add_unexpected_expense(self) -> None:
        name, err = self._resolve_unexpected_name()
        if err:
            messagebox.showerror("Validación", err)
            return
        amount, err = parse_positive_amount(self.var_unexpected_amount.get(), allow_zero=False)
        if err:
            messagebox.showerror("Validación", f"Monto: {err}")
            return

        self.profile.unexpected_expenses.append(
            UnexpectedExpense(name=name or "", amount=amount or 0.0)
        )
        self.var_unexpected_amount.set("")
        if self.var_unexpected_name.get().strip() == OTHER_UNEXPECTED_LABEL:
            self.var_unexpected_custom.set("")
        self.refresh_all_views()

    def remove_unexpected_expense(self) -> None:
        selected = self.tree_unexpected.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione un gasto imprevisto de la tabla.")
            return
        index = self.tree_unexpected.index(selected[0])
        del self.profile.unexpected_expenses[index]
        self.refresh_all_views()

    def add_goal(self) -> None:
        name, err = parse_required_text(self.var_goal_name.get(), "Meta")
        if err:
            messagebox.showerror("Validación", err)
            return
        target, err = parse_positive_amount(self.var_goal_target.get(), allow_zero=False)
        if err:
            messagebox.showerror("Validación", f"Monto objetivo: {err}")
            return
        saved, err = parse_positive_amount(self.var_goal_saved.get(), allow_zero=True)
        if err:
            messagebox.showerror("Validación", f"Ya ahorrado: {err}")
            return
        monthly, err = parse_positive_amount(self.var_goal_monthly.get(), allow_zero=True)
        if err:
            messagebox.showerror("Validación", f"Aporte mensual: {err}")
            return
        if saved and target and saved > target:
            messagebox.showerror("Validación", "Lo ahorrado no puede superar el objetivo.")
            return

        self.profile.savings_goals.append(
            SavingsGoal(
                name=name,
                target=target or 0.0,
                saved=saved or 0.0,
                monthly_contribution=monthly or 0.0,
            )
        )
        self.var_goal_target.set("")
        self.var_goal_saved.set("0")
        self.var_goal_monthly.set("")
        self.refresh_all_views()

    def remove_goal(self) -> None:
        selected = self.tree_goals_manage.selection()
        if not selected:
            messagebox.showwarning("Selección", "Seleccione una meta de la tabla.")
            return
        index = self.tree_goals_manage.index(selected[0])
        del self.profile.savings_goals[index]
        self.refresh_all_views()

    def refresh_all_views(self) -> None:
        self._refresh_income_preview()
        self._refresh_expenses_table()
        self._refresh_unexpected_table()
        self._refresh_goals_progress()
        self._refresh_summary()
        self._refresh_charts()

    def _refresh_income_preview(self) -> None:
        p = self.profile
        self.lbl_income_preview.config(
            text=(
                f"Total ingresos: {format_money(p.total_income)}  |  "
                f"Gastos fijos: {format_money(p.total_fixed_expenses)}  |  "
                f"Imprevistos: {format_money(p.total_unexpected_expenses)}  |  "
                f"Balance: {format_money(p.available_balance)}"
            )
        )

    def _refresh_expenses_table(self) -> None:
        for item in self.tree_expenses.get_children():
            self.tree_expenses.delete(item)
        for exp in self.profile.fixed_expenses:
            self.tree_expenses.insert("", tk.END, values=(exp.name, format_money(exp.amount)))
        self.lbl_expenses_total.config(
            text=f"Total gastos fijos: {format_money(self.profile.total_fixed_expenses)}"
        )

    def _refresh_unexpected_table(self) -> None:
        for item in self.tree_unexpected.get_children():
            self.tree_unexpected.delete(item)
        for exp in self.profile.unexpected_expenses:
            self.tree_unexpected.insert("", tk.END, values=(exp.name, format_money(exp.amount)))

        self.lbl_unexpected_total.config(
            text=(
                f"Total imprevistos: {format_money(self.profile.total_unexpected_expenses)}  |  "
                f"Gastos totales (fijos + imprevistos): {format_money(self.profile.total_expenses)}"
            )
        )

        for item in self.tree_unexpected_summary.get_children():
            self.tree_unexpected_summary.delete(item)
        for exp in self.profile.unexpected_expenses:
            self.tree_unexpected_summary.insert(
                "", tk.END, values=(exp.name, format_money(exp.amount))
            )
        if self.profile.unexpected_expenses:
            self.lbl_unexpected_summary.config(
                text=f"Subtotal imprevistos: {format_money(self.profile.total_unexpected_expenses)}"
            )
        else:
            self.lbl_unexpected_summary.config(text="No hay gastos imprevistos registrados.")

    def _refresh_goals_progress(self) -> None:
        for item in self.tree_goals_manage.get_children():
            self.tree_goals_manage.delete(item)
        for g in self.profile.savings_goals:
            self.tree_goals_manage.insert(
                "",
                tk.END,
                values=(
                    g.name,
                    format_money(g.target),
                    format_money(g.saved),
                    format_money(g.monthly_contribution),
                ),
            )

        for widget in self.goals_container.winfo_children():
            widget.destroy()

        if not self.profile.savings_goals:
            ttk.Label(self.goals_container, text="Agregue metas para ver su progreso.").pack(anchor=tk.W)
            return

        for goal in self.profile.savings_goals:
            row = ttk.Frame(self.goals_container)
            row.pack(fill=tk.X, pady=6)
            ttk.Label(row, text=f"{goal.name} ({format_money(goal.saved)} / {format_money(goal.target)})").pack(
                anchor=tk.W
            )
            bar = ttk.Progressbar(row, length=400, mode="determinate", maximum=100)
            bar.pack(anchor=tk.W, pady=2)
            bar["value"] = goal.progress_percent
            ttk.Label(row, text=f"{goal.progress_percent:.1f}% — Falta {format_money(goal.remaining)}").pack(
                anchor=tk.W
            )

    def _refresh_summary(self) -> None:
        p = self.profile
        values = {
            "income": p.total_income,
            "expenses": p.total_expenses,
            "balance": p.available_balance,
            "savings": p.effective_savings,
            "free": p.money_left_after_savings,
            "saved_goals": p.total_saved_in_goals,
        }
        for key, amount in values.items():
            title = self.summary_titles[key]
            color = "#15803d" if amount >= 0 or key in ("expenses", "savings") else "#b91c1c"
            if key == "expenses":
                color = "#1e40af"
            self.summary_labels[key].config(text=f"{title}\n{format_money(amount)}", foreground=color)

        for item in self.tree_goals.get_children():
            self.tree_goals.delete(item)
        for g in p.savings_goals:
            self.tree_goals.insert(
                "",
                tk.END,
                values=(
                    g.name,
                    format_money(g.saved),
                    format_money(g.target),
                    f"{g.progress_percent:.1f}%",
                    format_money(g.monthly_contribution),
                ),
            )

        if p.available_balance < 0:
            self.lbl_warning.config(
                text=(
                    "⚠ Gastas más de lo que ingresas. Revisa gastos fijos, imprevistos o aumenta ingresos."
                )
            )
        elif p.money_left_after_savings < 0:
            self.lbl_warning.config(
                text="⚠ El ahorro planificado supera el balance disponible."
            )
        elif p.total_goal_contributions > p.effective_savings and p.planned_monthly_savings <= 0:
            self.lbl_warning.config(
                text="Los aportes mensuales a metas superan lo que puedes ahorrar este mes."
            )
        else:
            self.lbl_warning.config(text="")

    def _refresh_charts(self) -> None:
        if not HAS_MATPLOTLIB:
            return

        p = self.profile
        self.ax_pie.clear()
        self.ax_bar.clear()

        income = p.total_income
        fixed = p.total_fixed_expenses
        unexpected = p.total_unexpected_expenses
        expenses = p.total_expenses
        savings = min(p.effective_savings, max(0.0, p.available_balance))
        other = max(0.0, p.available_balance - savings)

        if income <= 0 and expenses <= 0 and savings <= 0:
            self.ax_pie.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            self.ax_bar.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        else:
            pie_parts = [("Gastos fijos", fixed), ("Imprevistos", unexpected), ("Ahorro", savings), ("Disponible", other)]
            pie_vals = [v for _, v in pie_parts if v > 0]
            pie_labels = [label for label, v in pie_parts if v > 0]
            if pie_vals:
                self.ax_pie.pie(pie_vals, labels=pie_labels, autopct="%1.1f%%", startangle=90)
            self.ax_pie.set_title("Distribución del ingreso")

            bars_x = ["Ingresos", "Fijos", "Imprevistos", "Ahorro", "Libre"]
            bars_y = [
                income,
                fixed,
                unexpected,
                savings,
                max(0.0, p.money_left_after_savings),
            ]
            colors = ["#22c55e", "#ef4444", "#f97316", "#3b82f6", "#a855f7"]
            self.ax_bar.bar(bars_x, bars_y, color=colors)
            self.ax_bar.set_title("Comparación mensual")
            self.ax_bar.set_ylabel("Monto")

        self.canvas.draw()


def main() -> None:
    root = tk.Tk()
    FinanzasPersonalesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Aplicación web de gestión financiera personal (Flask)."""

import os
import secrets

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.middleware.proxy_fix import ProxyFix

from auth_service import get_user_by_id, iniciar_sesion, registrar_usuario
from models import FinancialProfile, FixedExpense, SavingsGoal, UnexpectedExpense
from persistence import cargar_datos_usuario, guardar_datos_usuario, init_db, reiniciar_datos_usuario
from validators import parse_positive_amount, parse_required_text
from web_logic import build_view_context, resolve_unexpected_name

login_manager = LoginManager()


def create_app() -> Flask:
    application = Flask(__name__)
    application.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))

    application.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=bool(os.environ.get("NETLIFY")),
    )

    if os.environ.get("NETLIFY"):
        application.wsgi_app = ProxyFix(
            application.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1,
        )

    login_manager.init_app(application)
    login_manager.login_view = "login"
    login_manager.login_message = "Inicie sesión para acceder a su información financiera."
    login_manager.login_message_category = "warning"

    init_db()
    _register_routes(application)
    return application


@login_manager.user_loader
def load_user(user_id: str):
    return get_user_by_id(int(user_id))


def _register_routes(application: Flask) -> None:
    application.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    application.add_url_rule("/register", view_func=register, methods=["GET", "POST"])
    application.add_url_rule("/logout", view_func=logout, methods=["POST"])
    application.add_url_rule("/", view_func=index, methods=["GET"])
    application.add_url_rule("/income", view_func=save_income, methods=["POST"])
    application.add_url_rule("/expenses/add", view_func=add_expense, methods=["POST"])
    application.add_url_rule("/expenses/delete", view_func=delete_expense, methods=["POST"])
    application.add_url_rule("/unexpected/add", view_func=add_unexpected, methods=["POST"])
    application.add_url_rule("/unexpected/delete", view_func=delete_unexpected, methods=["POST"])
    application.add_url_rule("/goals/add", view_func=add_goal, methods=["POST"])
    application.add_url_rule("/goals/delete", view_func=delete_goal, methods=["POST"])
    application.add_url_rule("/reset", view_func=reset_data, methods=["POST"])


def _load_profile() -> FinancialProfile:
    return cargar_datos_usuario(current_user.id)


def _save_profile(profile: FinancialProfile) -> None:
    guardar_datos_usuario(current_user.id, profile)


def _redirect_tab(tab: str):
    return redirect(url_for("index", tab=tab))


def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        user, err = iniciar_sesion(
            request.form.get("username", ""),
            request.form.get("password", ""),
        )
        if err:
            flash(err, "danger")
            return render_template("login.html")
        login_user(user)
        flash("Inicio de sesión exitoso.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")
        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("register.html")

        ok, err = registrar_usuario(
            request.form.get("username", ""),
            password,
        )
        if not ok:
            flash(err, "danger")
            return render_template("register.html")

        flash("Registro exitoso. Ya puede iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


@login_required
def index():
    tab = request.args.get("tab", "income")
    profile = _load_profile()
    return render_template("index.html", **build_view_context(profile, tab))


@login_required
def save_income():
    profile = _load_profile()
    salary, err = parse_positive_amount(request.form.get("salary", ""), allow_zero=False)
    if err:
        flash(f"Salario: {err}", "danger")
        return _redirect_tab("income")
    extra, err = parse_positive_amount(request.form.get("extra", ""), allow_zero=True)
    if err:
        flash(f"Ingresos adicionales: {err}", "danger")
        return _redirect_tab("income")
    planned, err = parse_positive_amount(request.form.get("planned_savings", ""), allow_zero=True)
    if err:
        flash(f"Ahorro planificado: {err}", "danger")
        return _redirect_tab("income")

    profile.monthly_salary = salary or 0.0
    profile.additional_income = extra or 0.0
    profile.planned_monthly_savings = planned or 0.0
    _save_profile(profile)
    flash("Ingresos actualizados correctamente.", "success")
    return _redirect_tab("income")


@login_required
def add_expense():
    profile = _load_profile()
    name, err = parse_required_text(request.form.get("name", ""), "Concepto")
    if err:
        flash(err, "danger")
        return _redirect_tab("expenses")
    amount, err = parse_positive_amount(request.form.get("amount", ""), allow_zero=False)
    if err:
        flash(f"Monto: {err}", "danger")
        return _redirect_tab("expenses")

    profile.fixed_expenses.append(FixedExpense(name=name, amount=amount or 0.0))
    _save_profile(profile)
    flash("Gasto fijo agregado.", "success")
    return _redirect_tab("expenses")


@login_required
def delete_expense():
    profile = _load_profile()
    try:
        index = int(request.form.get("index", -1))
    except ValueError:
        flash("Selección inválida.", "warning")
        return _redirect_tab("expenses")
    if 0 <= index < len(profile.fixed_expenses):
        del profile.fixed_expenses[index]
        _save_profile(profile)
        flash("Gasto fijo eliminado.", "success")
    else:
        flash("Seleccione un gasto de la tabla.", "warning")
    return _redirect_tab("expenses")


@login_required
def add_unexpected():
    profile = _load_profile()
    name, err = resolve_unexpected_name(
        request.form.get("category", ""),
        request.form.get("custom_name", ""),
    )
    if err:
        flash(err, "danger")
        return _redirect_tab("unexpected")
    amount, err = parse_positive_amount(request.form.get("amount", ""), allow_zero=False)
    if err:
        flash(f"Monto: {err}", "danger")
        return _redirect_tab("unexpected")

    profile.unexpected_expenses.append(UnexpectedExpense(name=name or "", amount=amount or 0.0))
    _save_profile(profile)
    flash("Gasto imprevisto registrado.", "success")
    return _redirect_tab("unexpected")


@login_required
def delete_unexpected():
    profile = _load_profile()
    try:
        index = int(request.form.get("index", -1))
    except ValueError:
        flash("Selección inválida.", "warning")
        return _redirect_tab("unexpected")
    if 0 <= index < len(profile.unexpected_expenses):
        del profile.unexpected_expenses[index]
        _save_profile(profile)
        flash("Gasto imprevisto eliminado.", "success")
    else:
        flash("Seleccione un gasto imprevisto de la tabla.", "warning")
    return _redirect_tab("unexpected")


@login_required
def add_goal():
    profile = _load_profile()
    name, err = parse_required_text(request.form.get("name", ""), "Meta")
    if err:
        flash(err, "danger")
        return _redirect_tab("goals")
    target, err = parse_positive_amount(request.form.get("target", ""), allow_zero=False)
    if err:
        flash(f"Monto objetivo: {err}", "danger")
        return _redirect_tab("goals")
    saved, err = parse_positive_amount(request.form.get("saved", "0"), allow_zero=True)
    if err:
        flash(f"Ya ahorrado: {err}", "danger")
        return _redirect_tab("goals")
    monthly, err = parse_positive_amount(request.form.get("monthly", ""), allow_zero=True)
    if err:
        flash(f"Aporte mensual: {err}", "danger")
        return _redirect_tab("goals")
    if saved and target and saved > target:
        flash("Lo ahorrado no puede superar el objetivo.", "danger")
        return _redirect_tab("goals")

    profile.savings_goals.append(
        SavingsGoal(
            name=name,
            target=target or 0.0,
            saved=saved or 0.0,
            monthly_contribution=monthly or 0.0,
        )
    )
    _save_profile(profile)
    flash("Meta de ahorro agregada.", "success")
    return _redirect_tab("goals")


@login_required
def delete_goal():
    profile = _load_profile()
    try:
        index = int(request.form.get("index", -1))
    except ValueError:
        flash("Selección inválida.", "warning")
        return _redirect_tab("goals")
    if 0 <= index < len(profile.savings_goals):
        del profile.savings_goals[index]
        _save_profile(profile)
        flash("Meta eliminada.", "success")
    else:
        flash("Seleccione una meta de la tabla.", "warning")
    return _redirect_tab("goals")


@login_required
def reset_data():
    reiniciar_datos_usuario(current_user.id)
    flash("Datos financieros reiniciados.", "info")
    return _redirect_tab("income")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

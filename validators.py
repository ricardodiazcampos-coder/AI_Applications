"""Validación de entradas numéricas y de texto."""

from typing import Optional, Tuple


def parse_positive_amount(value: str, allow_zero: bool = True) -> Tuple[Optional[float], Optional[str]]:
    """
    Convierte una cadena a número no negativo.
    Retorna (valor, None) si es válido o (None, mensaje_error).
    """
    text = value.strip().replace(",", ".")
    if not text:
        return (0.0, None) if allow_zero else (None, "Este campo es obligatorio.")

    try:
        amount = float(text)
    except ValueError:
        return None, "Ingrese un número válido (ej.: 1500.50)."

    if amount < 0:
        return None, "El valor no puede ser negativo."
    if not allow_zero and amount == 0:
        return None, "El valor debe ser mayor que cero."

    return amount, None


def parse_required_text(value: str, field_name: str = "Campo") -> Tuple[Optional[str], Optional[str]]:
    text = value.strip()
    if not text:
        return None, f"{field_name} es obligatorio."
    return text, None

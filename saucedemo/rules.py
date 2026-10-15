"""Datos esperados y reglas independientes de los Page Objects."""

import json
import os
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class Totals:
    subtotal: Decimal
    tax: Decimal
    total: Decimal


def calculate_totals(subtotal, rate):
    subtotal, rate = Decimal(subtotal), Decimal(rate)
    if not subtotal.is_finite() or not rate.is_finite() or subtotal < 0 or not 0 <= rate <= 1:
        raise ValueError("Subtotal o tasa inválidos")
    tax = (subtotal * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Totals(subtotal, tax, subtotal + tax)


def load_catalog(path=None):
    path = Path(path or os.getenv("CATALOG_PATH") or Path(__file__).parent / "datasets/saucedemo.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("products"), dict) or not data["products"]:
        raise ValueError("El catálogo debe contener productos")
    try:
        products = {name: Decimal(price) for name, price in data["products"].items()}
        rate = Decimal(data["tax_rate"])
        for name, price in products.items():
            if not name or not price.is_finite() or price < 0 or price != price.quantize(Decimal("0.01")):
                raise ValueError("Nombre o precio inválidos")
        calculate_totals("0", rate)
    except (InvalidOperation, TypeError, KeyError) as error:
        raise ValueError("Precio o tasa inválidos en catálogo") from error
    return products, rate

"""Formatação em padrão brasileiro (vírgula decimal, ponto de milhar)."""
from __future__ import annotations

import unicodedata
from typing import Optional


def num(v: float, casas: int = 1) -> str:
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rs(v: float) -> str:
    s = num(abs(v), 2)
    return f"-R$ {s}" if v < 0 else f"R$ {s}"


def anos(v: Optional[float]) -> str:
    return "não se paga no prazo analisado" if v is None else f"{num(v)} anos"


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")

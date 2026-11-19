"""Carregamento de dados e definição do perfil da residência.

Todo parâmetro numérico vive em data/parametros.json com unidade, tipo e fonte.
"""
from __future__ import annotations

import copy
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"


class Parametros:
    """Acesso aos parâmetros com rastreabilidade (valor, tipo, fonte)."""

    def __init__(self, caminho: Optional[Path] = None):
        caminho = caminho or DATA / "parametros.json"
        with open(caminho, encoding="utf-8") as f:
            bruto = json.load(f)
        self.meta = bruto.pop("_meta", {})
        self._d = bruto

    def valor(self, chave: str):
        return self._d[chave]["valor"]

    def info(self, chave: str) -> dict:
        return self._d[chave]

    def chaves(self):
        return list(self._d.keys())

    def com(self, **sobrescritas) -> "Parametros":
        """Cópia com valores informados pelo usuário (marcados como tal)."""
        novo = copy.deepcopy(self)
        for k, v in sobrescritas.items():
            if v is None:
                continue
            novo._d[k]["valor"] = v
            novo._d[k]["tipo"] = "informado pelo usuário"
        return novo

    def adicional_bandeira_100kwh(self, bandeira: str) -> float:
        chave = {"verde": "bandeira_verde_100kwh", "amarela": "bandeira_amarela_100kwh",
                 "vermelha1": "bandeira_vermelha1_100kwh",
                 "vermelha2": "bandeira_vermelha2_100kwh"}[bandeira]
        return self.valor(chave)

    def tarifa_efetiva(self, bandeira: Optional[str] = None) -> float:
        """R$/kWh = tarifa + adicional da bandeira (por kWh, antes de tributos)."""
        b = bandeira or self.valor("bandeira_atual")
        return self.valor("tarifa_kwh") + self.adicional_bandeira_100kwh(b) / 100.0


@dataclass
class Equipamento:
    id: str
    nome: str
    potencia_w: float
    tipo_dado: str
    fonte: str
    observacao: str = ""


def carregar_equipamentos(caminho: Optional[Path] = None) -> dict[str, Equipamento]:
    caminho = caminho or DATA / "equipamentos.csv"
    eqs: dict[str, Equipamento] = {}
    with open(caminho, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            eqs[linha["id"]] = Equipamento(
                id=linha["id"], nome=linha["nome"], potencia_w=float(linha["potencia_w"]),
                tipo_dado=linha["tipo_dado"], fonte=linha["fonte"], observacao=linha["observacao"])
    return eqs


@dataclass
class Item:
    """Um aparelho da casa: quantidade, horas por dia de uso e dias por mês."""
    id: str
    qtd: int = 1
    horas_dia: float = 1.0
    dias_mes: int = 30


@dataclass
class Perfil:
    pessoas: int = 4
    minutos_banho: float = 8.0
    padrao_ligacao: str = "bifasico"          # monofasico | bifasico | trifasico
    imovel_proprio: bool = True
    telhado_adequado: Optional[bool] = None   # None = não sabe
    itens: list[Item] = field(default_factory=list)
    tarifa_kwh: Optional[float] = None        # None = usa o valor padrão estimado
    bandeira: Optional[str] = None            # None = bandeira vigente
    potencia_chuveiro_w: Optional[float] = None

    def copia(self) -> "Perfil":
        return copy.deepcopy(self)

    @staticmethod
    def de_dict(d: dict) -> "Perfil":
        itens = [Item(**i) for i in d.get("itens", [])]
        resto = {k: v for k, v in d.items() if k != "itens"}
        return Perfil(itens=itens, **resto)


def perfil_exemplo() -> Perfil:
    """Família ilustrativa de 4 pessoas (DADOS ESTIMADOS, não é uma família real)."""
    return Perfil(
        pessoas=4, minutos_banho=8, padrao_ligacao="bifasico", imovel_proprio=True,
        telhado_adequado=True,
        itens=[
            Item("geladeira", 1, 24, 30),
            Item("ar_condicionado", 1, 3, 10),
            Item("ventilador", 2, 5, 30),
            Item("tv_led", 2, 4, 30),
            Item("notebook", 2, 5, 30),
            Item("roteador", 1, 24, 30),
            Item("lavadora", 1, 1, 30),
            Item("ferro", 1, 0.3, 30),
            Item("microondas", 1, 0.25, 30),
            Item("lampada_fluorescente_15w", 8, 5, 30),
        ],
    )

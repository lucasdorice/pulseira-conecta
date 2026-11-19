"""Motor de cálculo: energia, custo, solar, payback e CO2.

Funções puras e pequenas, para facilitar a conferência e os testes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .dados import Equipamento, Parametros, Perfil

DIAS_MES_MEDIO = 365.0 / 12.0  # 30,4167


# ----------------------------------------------------------------- conceitos básicos
def energia_kwh(potencia_w: float, horas: float) -> float:
    """E (kWh) = P (kW) × t (h)."""
    return potencia_w / 1000.0 * horas


def custo_rs(kwh: float, tarifa_efetiva: float) -> float:
    return kwh * tarifa_efetiva


def co2_kg(kwh: float, fator_tco2_mwh: float) -> float:
    """kWh × (tCO2/MWh) = kg de CO2 (as unidades se cancelam: 1 tCO2/MWh = 1 kgCO2/kWh)."""
    return kwh * fator_tco2_mwh


# ----------------------------------------------------------------- consumo da residência
def potencia_chuveiro(perfil: Perfil, p: Parametros) -> float:
    return perfil.potencia_chuveiro_w or p.valor("potencia_chuveiro_w")


def consumo_chuveiro_mes(perfil: Perfil, p: Parametros) -> float:
    """kWh/mês do chuveiro elétrico (média anual, com fator sazonal)."""
    horas_dia = perfil.minutos_banho / 60.0 * p.valor("banhos_dia_por_pessoa") * perfil.pessoas
    return energia_kwh(potencia_chuveiro(perfil, p), horas_dia) * 30 * p.valor("fator_sazonal_chuveiro")


def consumo_item_mes(item, eq: Equipamento) -> float:
    return energia_kwh(eq.potencia_w, item.horas_dia) * item.dias_mes * item.qtd


def consumo_por_equipamento(perfil: Perfil, eqs: dict[str, Equipamento],
                            p: Parametros) -> list[tuple[str, float]]:
    """Lista (nome, kWh/mês) ordenada do maior para o menor, incluindo o chuveiro."""
    linhas = [("Chuveiro elétrico", consumo_chuveiro_mes(perfil, p))]
    for it in perfil.itens:
        linhas.append((eqs[it.id].nome + (f" ×{it.qtd}" if it.qtd > 1 else ""),
                       consumo_item_mes(it, eqs[it.id])))
    return sorted(linhas, key=lambda x: x[1], reverse=True)


def consumo_total_mes(perfil: Perfil, eqs, p: Parametros) -> float:
    return sum(v for _, v in consumo_por_equipamento(perfil, eqs, p))


def parametros_do_perfil(perfil: Perfil, p: Parametros) -> Parametros:
    """Aplica tarifa e bandeira informadas pelo usuário (se houver)."""
    q = p.com(tarifa_kwh=perfil.tarifa_kwh, bandeira_atual=perfil.bandeira)
    return q


def tarifa_efetiva(perfil: Perfil, p: Parametros) -> float:
    return parametros_do_perfil(perfil, p).tarifa_efetiva()


# ----------------------------------------------------------------- verificação física
def energia_termica_banho_kwh(p: Parametros, minutos: float) -> float:
    """Q = m·c·ΔT em kWh, para um banho de `minutos` (vazão e ΔT dos parâmetros)."""
    litros = p.valor("vazao_chuveiro_l_min") * minutos
    kj = litros * p.valor("calor_especifico_agua_kj_kg_k") * p.valor("delta_t_banho_c")
    return kj / 3600.0


def verificacao_fisica_chuveiro(perfil: Perfil, p: Parametros) -> dict:
    """Compara a energia elétrica (P×t) com a energia térmica necessária (m·c·ΔT).

    Um resistor converte ~100% da eletricidade em calor, então os dois valores devem ser próximos.
    """
    eletrica = energia_kwh(potencia_chuveiro(perfil, p), perfil.minutos_banho / 60.0)
    termica = energia_termica_banho_kwh(p, perfil.minutos_banho)
    return {"eletrica_kwh": eletrica, "termico_kwh": termica,
            "diferenca_pct": abs(eletrica - termica) / eletrica * 100.0}


# ----------------------------------------------------------------- fotovoltaico
def geracao_mensal_por_kwp(p: Parametros) -> float:
    """kWh/mês gerados por 1 kWp = HSP × PR × dias."""
    return p.valor("hsp_kwh_m2_dia") * p.valor("performance_ratio") * DIAS_MES_MEDIO


@dataclass
class DimensionamentoFV:
    kwp: float
    paineis: int
    area_m2: float
    geracao_mes_kwh: float
    energia_compensada_mes_kwh: float


def custo_disponibilidade(perfil: Perfil, p: Parametros) -> float:
    return p.valor(f"custo_disponibilidade_{perfil.padrao_ligacao}_kwh")


def dimensionar_fv(consumo_mes_kwh: float, perfil: Perfil, p: Parametros) -> DimensionamentoFV:
    """Dimensiona para cobrir (consumo − custo de disponibilidade). Usa médias anuais."""
    alvo = max(consumo_mes_kwh - custo_disponibilidade(perfil, p), 0.0)
    por_kwp = geracao_mensal_por_kwp(p)
    kwp_ideal = alvo / por_kwp if por_kwp else 0.0
    paineis = math.ceil(kwp_ideal / p.valor("potencia_painel_kwp")) if kwp_ideal > 0 else 0
    kwp = paineis * p.valor("potencia_painel_kwp")
    geracao = kwp * por_kwp
    return DimensionamentoFV(kwp=kwp, paineis=paineis,
                             area_m2=paineis * p.valor("area_painel_m2"),
                             geracao_mes_kwh=geracao,
                             energia_compensada_mes_kwh=min(geracao, alvo))


# ----------------------------------------------------------------- finanças
def payback_componentes(investimento: float, componentes: list[tuple[float, float]],
                        reajuste: float = 0.0, max_anos: int = 40) -> Optional[float]:
    """Payback para uma ou mais fontes de economia.

    `componentes` = lista de (economia_no_ano_1, degradação_anual). A economia de cada
    componente cresce com o reajuste da tarifa e cai com a degradação.
    """
    if sum(e for e, _ in componentes) <= 0:
        return None
    acumulado = 0.0
    for ano in range(1, max_anos + 1):
        ec = sum(e * ((1 + reajuste) * (1 - d)) ** (ano - 1) for e, d in componentes)
        if acumulado + ec >= investimento:
            return ano - 1 + (investimento - acumulado) / ec
        acumulado += ec
    return None


def saldo_componentes(investimento: float, componentes: list[tuple[float, float]],
                      anos: int, reajuste: float = 0.0) -> float:
    """Economia acumulada em `anos` menos o investimento (sem desconto a valor presente)."""
    total = sum(e * ((1 + reajuste) * (1 - d)) ** (a - 1)
                for a in range(1, anos + 1) for e, d in componentes)
    return total - investimento


def payback_anos(investimento: float, economia_ano1: float, reajuste: float = 0.0,
                 degradacao: float = 0.0, max_anos: int = 40) -> Optional[float]:
    """Anos até a economia acumulada igualar o investimento (None se não ocorre em max_anos)."""
    return payback_componentes(investimento, [(economia_ano1, degradacao)], reajuste, max_anos)


def saldo_horizonte(investimento: float, economia_ano1: float, anos: int,
                    reajuste: float = 0.0, degradacao: float = 0.0) -> float:
    return saldo_componentes(investimento, [(economia_ano1, degradacao)], anos, reajuste)

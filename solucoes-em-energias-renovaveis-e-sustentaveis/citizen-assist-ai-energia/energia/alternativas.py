"""Comparação das alternativas para a MESMA necessidade (reduzir a conta de luz)
e o MESMO período de referência (12 meses e horizonte de N anos).

A. Eficiência e hábitos        (economia)
B. Aquecedor solar de água     (renovável)
C. Fotovoltaica residencial    (renovável)
AC. Pacote A + C (C dimensionada depois da eficiência)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import calculos as c
from .dados import Equipamento, Parametros, Perfil
from .formatacao import num

LAMPADAS_SUBSTITUIVEIS = ("lampada_incandescente_60w", "lampada_fluorescente_15w")


@dataclass
class Resultado:
    sigla: str
    nome: str
    tipo: str                       # economia | renovavel | combinacao
    descricao: str
    investimento: float
    economia_kwh_ano: float
    economia_rs_ano: float
    payback_simples: Optional[float]
    payback_reajuste: Optional[float]
    saldo_horizonte_rs: float
    co2_operacional_kg_ano: float   # kWh evitados × fator da rede
    co2_liquido_kg_ano: float       # considera o ciclo de vida do painel (FV)
    viavel: Optional[bool]          # None = depende de confirmação
    condicoes: list[str] = field(default_factory=list)
    limitacoes: list[str] = field(default_factory=list)
    detalhes: dict = field(default_factory=dict)
    componentes: list[tuple[float, float]] = field(default_factory=list)


# ------------------------------------------------------------------ ajuda interna
def _fechar(res: Resultado, p: Parametros) -> Resultado:
    r = p.valor("reajuste_tarifa_anual")
    h = int(p.valor("horizonte_anos"))
    comp = res.componentes or [(res.economia_rs_ano, 0.0)]
    res.payback_simples = c.payback_componentes(res.investimento, [(e, 0.0) for e, _ in comp], 0.0)
    res.payback_reajuste = c.payback_componentes(res.investimento, comp, r)
    res.saldo_horizonte_rs = c.saldo_componentes(res.investimento, comp, h, r)
    return res


def perfil_apos_eficiencia(perfil: Perfil, p: Parametros) -> tuple[Perfil, int]:
    """Aplica a alternativa A: banho mais curto e lâmpadas LED. Retorna (novo perfil, nº de lâmpadas trocadas)."""
    novo = perfil.copia()
    novo.minutos_banho = max(perfil.minutos_banho - p.valor("reducao_banho_min"), 3.0)
    trocadas = 0
    for it in novo.itens:
        if it.id in LAMPADAS_SUBSTITUIVEIS:
            it.id = "lampada_led_9w"
            trocadas += it.qtd
    return novo, trocadas


# ------------------------------------------------------------------ A
def alt_eficiencia(perfil: Perfil, eqs: dict[str, Equipamento], p: Parametros) -> Resultado:
    pp = c.parametros_do_perfil(perfil, p)
    tarifa = pp.tarifa_efetiva()
    novo, trocadas = perfil_apos_eficiencia(perfil, pp)
    antes = c.consumo_total_mes(perfil, eqs, pp)
    depois = c.consumo_total_mes(novo, eqs, pp)
    kwh_ano = (antes - depois) * 12
    invest = trocadas * pp.valor("custo_lampada_led")
    econ_banho = (c.consumo_chuveiro_mes(perfil, pp) - c.consumo_chuveiro_mes(novo, pp)) * 12
    res = Resultado(
        sigla="A", nome="Eficiência e hábitos", tipo="economia",
        descricao=(f"Banho {perfil.minutos_banho:.0f} → {novo.minutos_banho:.0f} min e "
                   f"troca de {trocadas} lâmpada(s) por LED de 9 W."),
        investimento=invest, economia_kwh_ano=kwh_ano, economia_rs_ano=kwh_ano * tarifa,
        payback_simples=None, payback_reajuste=None, saldo_horizonte_rs=0.0,
        co2_operacional_kg_ano=c.co2_kg(kwh_ano, pp.valor("co2_rede_tco2_mwh")),
        co2_liquido_kg_ano=c.co2_kg(kwh_ano, pp.valor("co2_rede_tco2_mwh")),
        viavel=True,
        condicoes=["Não exige obra nem imóvel próprio.", "Depende da adesão de todos da casa ao novo hábito."],
        limitacoes=["A economia do banho depende de a meta ser mantida.",
                    "A troca de lâmpadas rende pouco quando já há fluorescentes ou LED."],
        detalhes={"antes_kwh_mes": antes, "depois_kwh_mes": depois, "lampadas_trocadas": trocadas,
                  "economia_banho_kwh_ano": econ_banho,
                  "economia_lampadas_kwh_ano": kwh_ano - econ_banho},
    )
    return _fechar(res, pp)


# ------------------------------------------------------------------ B
def alt_aquecedor_solar(perfil: Perfil, eqs, p: Parametros) -> Resultado:
    pp = c.parametros_do_perfil(perfil, p)
    tarifa = pp.tarifa_efetiva()
    chuv = c.consumo_chuveiro_mes(perfil, pp)
    fr = pp.valor("fracao_solar_termico")
    kwh_ano = chuv * 12 * fr
    invest = pp.valor("custo_termico_base") + pp.valor("custo_termico_por_pessoa") * perfil.pessoas
    viavel: Optional[bool] = True
    if not perfil.imovel_proprio or perfil.telhado_adequado is False:
        viavel = False
    elif perfil.telhado_adequado is None:
        viavel = None
    rede = pp.valor("co2_rede_tco2_mwh")
    res = Resultado(
        sigla="B", nome="Aquecedor solar de água", tipo="renovavel",
        descricao=f"Sol aquece a água do banho e cobre cerca de {fr*100:.0f}% do consumo do chuveiro.",
        investimento=invest, economia_kwh_ano=kwh_ano, economia_rs_ano=kwh_ano * tarifa,
        payback_simples=None, payback_reajuste=None, saldo_horizonte_rs=0.0,
        co2_operacional_kg_ano=c.co2_kg(kwh_ano, rede), co2_liquido_kg_ano=c.co2_kg(kwh_ano, rede),
        viavel=viavel,
        condicoes=["Imóvel próprio (ou autorização) e telhado com sol e espaço.",
                   "Exige reservatório térmico e adaptação da tubulação, e costuma manter apoio elétrico."],
        limitacoes=["A fração solar cai no inverno e em dias nublados.",
                    "Só atua sobre o consumo do chuveiro, não sobre o restante da casa.",
                    "Emissões de fabricação não foram estimadas por falta de dado confiável."],
        detalhes={"chuveiro_kwh_mes": chuv, "fracao_solar": fr,
                  "vida_util_anos": pp.valor("vida_util_termico_anos")},
    )
    return _fechar(res, pp)


# ------------------------------------------------------------------ C
def alt_fotovoltaica(perfil: Perfil, eqs, p: Parametros) -> Resultado:
    pp = c.parametros_do_perfil(perfil, p)
    tarifa = pp.tarifa_efetiva()
    consumo = c.consumo_total_mes(perfil, eqs, pp)
    dim = c.dimensionar_fv(consumo, perfil, pp)
    kwh_ano = dim.energia_compensada_mes_kwh * 12
    fio_b = pp.valor("reducao_economia_fio_b")
    econ_rs = kwh_ano * tarifa * (1 - fio_b)
    invest = dim.kwp * pp.valor("custo_fv_kwp")
    viavel: Optional[bool] = True
    if not perfil.imovel_proprio or perfil.telhado_adequado is False or dim.paineis == 0:
        viavel = False
    elif perfil.telhado_adequado is None:
        viavel = None
    rede = pp.valor("co2_rede_tco2_mwh")
    ciclo = pp.valor("co2_ciclo_vida_fv_tco2_mwh")
    res = Resultado(
        sigla="C", nome="Energia solar fotovoltaica", tipo="renovavel",
        descricao=(f"{dim.paineis} painéis ({num(dim.kwp, 2)} kWp, ~{num(dim.area_m2, 0)} m² de módulos) "
                   f"geram ~{dim.geracao_mes_kwh:.0f} kWh/mês."),
        investimento=invest, economia_kwh_ano=kwh_ano, economia_rs_ano=econ_rs,
        payback_simples=None, payback_reajuste=None, saldo_horizonte_rs=0.0,
        co2_operacional_kg_ano=c.co2_kg(kwh_ano, rede),
        co2_liquido_kg_ano=c.co2_kg(kwh_ano, rede - ciclo),
        viavel=viavel,
        condicoes=["Imóvel próprio, telhado com área e pouco sombreamento, e rede da distribuidora.",
                   "Homologação do sistema na distribuidora antes de operar."],
        limitacoes=[f"Você ainda paga o custo de disponibilidade ({c.custo_disponibilidade(perfil, pp):.0f} kWh/mês).",
                    "A economia usa médias anuais; a geração varia ao longo do ano.",
                    f"Estimamos perda de ~{fio_b*100:.0f}% da economia pela cobrança do Fio B (Lei 14.300).",
                    "No Brasil a rede já é muito limpa: o ganho climático líquido é pequeno ou nulo."],
        detalhes={"consumo_mes_kwh": consumo, "kwp": dim.kwp, "paineis": dim.paineis,
                  "area_m2": dim.area_m2, "geracao_mes_kwh": dim.geracao_mes_kwh,
                  "geracao_por_kwp_mes": c.geracao_mensal_por_kwp(pp),
                  "vida_util_anos": pp.valor("vida_util_fv_anos")},
        componentes=[(econ_rs, pp.valor("degradacao_fv_ano"))],
    )
    return _fechar(res, pp)


# ------------------------------------------------------------------ pacote A + C
def pacote_a_mais_c(perfil: Perfil, eqs, p: Parametros) -> Resultado:
    pp = c.parametros_do_perfil(perfil, p)
    a = alt_eficiencia(perfil, eqs, p)
    perfil_a, _ = perfil_apos_eficiencia(perfil, pp)
    cc = alt_fotovoltaica(perfil_a, eqs, p)
    viavel = cc.viavel
    res = Resultado(
        sigla="A+C", nome="Pacote: eficiência + fotovoltaica", tipo="combinacao",
        descricao=(f"Primeiro reduz o consumo (A) e só depois dimensiona o solar: "
                   f"{cc.detalhes['paineis']} painéis ({num(cc.detalhes['kwp'], 2)} kWp)."),
        investimento=a.investimento + cc.investimento,
        economia_kwh_ano=a.economia_kwh_ano + cc.economia_kwh_ano,
        economia_rs_ano=a.economia_rs_ano + cc.economia_rs_ano,
        payback_simples=None, payback_reajuste=None, saldo_horizonte_rs=0.0,
        co2_operacional_kg_ano=a.co2_operacional_kg_ano + cc.co2_operacional_kg_ano,
        co2_liquido_kg_ano=a.co2_liquido_kg_ano + cc.co2_liquido_kg_ano,
        viavel=viavel,
        condicoes=cc.condicoes, limitacoes=cc.limitacoes,
        detalhes={"a": a, "c": cc},
        componentes=[(a.economia_rs_ano, 0.0)] + cc.componentes,
    )
    return _fechar(res, pp)


# ------------------------------------------------------------------ comparação e recomendação
def comparar(perfil: Perfil, eqs, p: Parametros) -> dict[str, Resultado]:
    return {
        "A": alt_eficiencia(perfil, eqs, p),
        "B": alt_aquecedor_solar(perfil, eqs, p),
        "C": alt_fotovoltaica(perfil, eqs, p),
        "A+C": pacote_a_mais_c(perfil, eqs, p),
    }


def classificar_retorno(r: Resultado) -> str:
    if r.investimento <= 0.01 or (r.payback_reajuste is not None and r.payback_reajuste <= 1.0):
        return "retorno imediato"
    if r.payback_reajuste is None:
        return "sem retorno no prazo analisado"
    if r.payback_reajuste <= 5:
        return "retorno rápido"
    if r.payback_reajuste <= 10:
        return "retorno moderado"
    return "retorno longo"


def recomendar(perfil: Perfil, res: dict[str, Resultado]) -> list[str]:
    """Sequência de passos coerente com os cálculos. Não promete economia garantida."""
    passos = [f"1º — Comece pela eficiência (A): custa pouco (R$ {num(res['A'].investimento, 0)}) e já reduz a conta."]
    candidatos = [r for k, r in res.items() if k in ("B", "C") and r.viavel is not False
                  and r.payback_reajuste is not None]
    if not perfil.imovel_proprio:
        passos.append("2º — Como o imóvel não é próprio, B e C dependem de autorização do proprietário. "
                      "Vale conhecer opções de energia solar por assinatura (a análise não cobre este caso).")
        return passos
    if perfil.telhado_adequado is False:
        passos.append("2º — Sem telhado adequado, B e C ficam inviáveis na sua casa. Considere geração compartilhada.")
        return passos
    candidatos.sort(key=lambda r: r.payback_reajuste)
    for i, r in enumerate(candidatos, start=2):
        extra = "" if perfil.telhado_adequado else " (confirme antes se o telhado é adequado)"
        passos.append(f"{i}º — {r.nome} (alternativa {r.sigla}): {classificar_retorno(r)}, "
                      f"payback ≈ {num(r.payback_reajuste)} anos com reajuste{extra}. Peça pelo menos 3 orçamentos.")
    passos.append("Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. "
                  "Para A + C use o pacote, que dimensiona o solar depois da eficiência.")
    return passos

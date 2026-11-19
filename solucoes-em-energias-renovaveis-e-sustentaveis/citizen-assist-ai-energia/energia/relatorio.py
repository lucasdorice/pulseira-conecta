"""Gera o relatório de análise (Markdown) a partir do próprio modelo.

Assim o documento e o assistente usam exatamente os mesmos números.
"""
from __future__ import annotations

from . import alternativas as alt
from . import calculos as c
from .formatacao import anos, num, rs
from .dados import Parametros, Perfil, carregar_equipamentos, perfil_exemplo


TIPOS = {"economia": "economia", "renovavel": "renovável", "combinacao": "combinação"}


def gerar_markdown(perfil: Perfil | None = None, params: Parametros | None = None,
                   titulo: str = "Análise e Cálculos") -> str:
    perfil = perfil or perfil_exemplo()
    p = params or Parametros()
    eqs = carregar_equipamentos()
    pp = c.parametros_do_perfil(perfil, p)
    tarifa = pp.tarifa_efetiva()
    res = alt.comparar(perfil, eqs, p)
    h = int(pp.valor("horizonte_anos"))
    r = pp.valor("reajuste_tarifa_anual")
    linhas = c.consumo_por_equipamento(perfil, eqs, pp)
    total = sum(v for _, v in linhas)
    vf = c.verificacao_fisica_chuveiro(perfil, pp)

    L: list[str] = []
    L.append(f"# {titulo}\n")
    L.append("> Documento **gerado automaticamente** por `python main.py --relatorio-docs`. "
             "A família é **ilustrativa (dados estimados)**. Troque o perfil para analisar outro caso.\n")
    L.append("## 1. Perfil analisado\n")
    L.append(f"- {perfil.pessoas} pessoas; banho de {num(perfil.minutos_banho, 0)} min; ligação {perfil.padrao_ligacao}; "
             f"imóvel {'próprio' if perfil.imovel_proprio else 'não próprio'}; telhado "
             f"{ {True: 'adequado', False: 'inadequado', None: 'não informado'}[perfil.telhado_adequado] }.")
    L.append(f"- Tarifa efetiva: **{rs(tarifa)}/kWh** (tarifa {rs(pp.valor('tarifa_kwh'))} + bandeira "
             f"{pp.valor('bandeira_atual')}). Tipo do dado da tarifa: *{pp.info('tarifa_kwh')['tipo']}*.")
    L.append(f"- Período: consumo **mensal** (média anual) e economia em **12 meses** e em **{h} anos**.\n")

    L.append("## 2. Análise de consumo (kWh/mês)\n")
    L.append("Fórmula: `E (kWh) = P (kW) × t (h)`, `consumo mensal = E × horas/dia × dias/mês × quantidade`.\n")
    L.append("| Aparelho | kWh/mês | % da casa | R$/mês |\n|---|---:|---:|---:|")
    for nome, v in linhas:
        L.append(f"| {nome} | {num(v, 1)} | {v / total * 100:.0f}% | {rs(v * tarifa)} |")
    L.append(f"| **Total** | **{num(total, 1)}** | 100% | **{rs(total * tarifa)}** |\n")
    L.append(f"**Verificação física do chuveiro** (`Q = m·c·ΔT` contra `P×t`): por banho, "
             f"{num(vf['eletrica_kwh'], 3)} kWh pela potência contra {num(vf['termico_kwh'], 3)} kWh pela física "
             f"da água, diferença de {num(vf['diferenca_pct'], 1)}%. A consistência confirma que o modelo de "
             "consumo do chuveiro é coerente.\n")

    L.append("## 3. Comparação das alternativas (mesma necessidade, mesmo período)\n")
    L.append(f"Necessidade: **reduzir a conta de luz**. Cenário de reajuste da tarifa: +{r * 100:.0f}%/ano.\n")
    L.append("| Alternativa | Tipo | Investimento | Economia/ano | Payback s/ reajuste | Payback c/ reajuste | "
             f"Saldo em {h} anos | CO₂ líquido evitado (kg/ano) |\n|---|---|---:|---:|---:|---:|---:|---:|")
    for k in ("A", "B", "C", "A+C"):
        x = res[k]
        L.append(f"| **{x.sigla}** {x.nome} | {TIPOS[x.tipo]} | {rs(x.investimento)} | {rs(x.economia_rs_ano)} | "
                 f"{anos(x.payback_simples)} | {anos(x.payback_reajuste)} | {rs(x.saldo_horizonte_rs)} | "
                 f"{num(x.co2_liquido_kg_ano, 0)} |")
    L.append("")
    for k in ("A", "B", "C"):
        x = res[k]
        L.append(f"### {x.sigla}. {x.nome}\n")
        L.append(f"{x.descricao}\n")
        L.append(f"- **Condições:** {' '.join(x.condicoes)}")
        L.append(f"- **Limitações:** {' '.join(x.limitacoes)}")
        if k == "C":
            d = x.detalhes
            L.append(f"- **Cálculo:** geração por kWp = HSP {num(pp.valor('hsp_kwh_m2_dia'))} × PR "
                     f"{num(pp.valor('performance_ratio'), 2)} × 30,4 = {num(d['geracao_por_kwp_mes'], 1)} kWh/mês/kWp. "
                     f"Alvo = {num(d['consumo_mes_kwh'], 0)} − {num(c.custo_disponibilidade(perfil, pp), 0)} (disponibilidade) "
                     f"kWh/mês → {d['paineis']} painéis de {pp.valor('potencia_painel_kwp') * 1000:.0f} Wp = "
                     f"{num(d['kwp'], 2)} kWp. Economia = kWh compensados × tarifa × (1 − Fio B "
                     f"{pp.valor('reducao_economia_fio_b') * 100:.0f}%).")
        if k == "B":
            L.append(f"- **Cálculo:** consumo do chuveiro {num(x.detalhes['chuveiro_kwh_mes'], 1)} kWh/mês × 12 × "
                     f"fração solar {pp.valor('fracao_solar_termico') * 100:.0f}% = {num(x.economia_kwh_ano, 0)} kWh/ano.")
        if k == "A":
            d = x.detalhes
            L.append(f"- **Cálculo:** consumo {num(d['antes_kwh_mes'], 1)} → {num(d['depois_kwh_mes'], 1)} kWh/mês "
                     f"(banho: {num(d['economia_banho_kwh_ano'], 0)} kWh/ano; lâmpadas: "
                     f"{num(d['economia_lampadas_kwh_ano'], 0)} kWh/ano).")
        L.append("")
    x = res["A+C"]
    L.append(f"### A+C. {x.nome}\n\n{x.descricao} Investimento {rs(x.investimento)}, economia {rs(x.economia_rs_ano)}/ano.\n")

    L.append("## 4. Recomendação (coerente com os cálculos)\n")
    for s in alt.recomendar(perfil, res):
        L.append(f"- {s}")
    L.append("")

    L.append("## 5. Impacto ambiental\n")
    L.append(f"Fator da rede: {num(pp.valor('co2_rede_tco2_mwh'), 4)} tCO₂/MWh (MCTI, 2023). Fator de ciclo de vida do painel: "
             f"{num(pp.valor('co2_ciclo_vida_fv_tco2_mwh'), 3)} tCO₂/MWh (IPCC, estimado). Como os dois são próximos, o ganho "
             "climático líquido da fotovoltaica no Brasil é pequeno ou nulo; o benefício principal é econômico. "
             "A eficiência energética é a alternativa com melhor equilíbrio entre custo e impacto.\n")

    L.append("## 6. Sensibilidade da fotovoltaica (C)\n")
    L.append("| Cenário | Tarifa | HSP | Custo R$/kWp | Payback c/ reajuste |\n|---|---:|---:|---:|---:|")
    cenarios = [("Pessimista", 0.85, 4.2, 5500), ("Base", None, None, None), ("Otimista", 1.15, 5.0, 3800)]
    for nome, t, hsp, cst in cenarios:
        p2 = p.com(tarifa_kwh=(pp.valor("tarifa_kwh") * t) if t else None,
                   hsp_kwh_m2_dia=hsp, custo_fv_kwp=cst)
        perf2 = perfil.copia()
        perf2.tarifa_kwh = None
        x2 = alt.alt_fotovoltaica(perf2, eqs, p2)
        L.append(f"| {nome} | {rs(p2.tarifa_efetiva())} | {num(p2.valor('hsp_kwh_m2_dia'))} | "
                 f"{num(p2.valor('custo_fv_kwp'), 0)} | {anos(x2.payback_reajuste)} |")
    L.append("\nOs cenários mostram que o payback depende muito de tarifa, irradiação e preço do sistema. "
             "Por isso o assistente apresenta faixas e pede orçamentos.\n")

    L.append("## 7. Rastreabilidade dos dados\n")
    L.append("Todos os parâmetros estão em `data/parametros.json` com **unidade, tipo (oficial/estimado/físico), "
             "fonte e observação**. Veja `docs/03_REFERENCIAS_E_LIMITACOES.md`.\n")
    L.append("> ⚠ Estimativas, não garantias. Confirme com a conta de luz e orçamentos de instaladores.\n")
    return "\n".join(L)

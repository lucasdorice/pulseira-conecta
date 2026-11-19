"""Assistente de energia do Citizen Assist AI (terminal).

Todas as respostas saem do motor de cálculo (calculos.py / alternativas.py).
O assistente não inventa números: ele interpreta a pergunta, calcula e explica,
sempre indicando o tipo do dado, a fonte e as limitações.
"""
from __future__ import annotations

import re
from typing import Optional

from . import alternativas as alt
from . import calculos as c
from .dados import Parametros, Perfil, carregar_equipamentos
from .formatacao import anos, normalizar, num, rs

AVISO = ("⚠ Estimativa: valores dependem de tarifa, clima, hábitos e preços de mercado. "
         "Não é garantia de economia; confirme com sua conta de luz e com orçamentos.")


class Assistente:
    def __init__(self, perfil: Perfil, params: Optional[Parametros] = None):
        self.p = params or Parametros()
        self.eqs = carregar_equipamentos()
        self.perfil = perfil
        self._recalcular()

    def _recalcular(self):
        self.pp = c.parametros_do_perfil(self.perfil, self.p)
        self.tarifa = self.pp.tarifa_efetiva()
        self.res = alt.comparar(self.perfil, self.eqs, self.p)
        self.consumo = c.consumo_total_mes(self.perfil, self.eqs, self.pp)

    # ------------------------------------------------------------ roteamento
    INTENCOES = [
        ("ajuda", ["ajuda", "menu", "o que voce faz", "comandos"]),
        ("kwh", ["o que e kwh", "o que significa kwh", "quilowatt"]),
        ("relatorio", ["relatorio", "exportar"]),
        ("fontes", ["fonte", "referencia", "limita", "confiavel", "garantia", "de onde"]),
        ("bandeira", ["bandeira"]),
        ("co2", ["co2", "carbono", "ambient", "emiss", "sustentab", "poluic"]),
        ("termico", ["aquecedor solar", "solar termico", "aquecimento solar"]),
        ("solar", ["solar", "fotovolt", "placa", "painel", "energia renovavel", "renovavel"]),
        ("simular_banho", ["banho", "chuveiro", "ducha"]),
        ("ranking", ["onde gasto", "mais gasta", "vilao", "ranking", "maior consumo", "gasto mais", "consumo"]),
        ("comparar", ["compar", "alternativa", "vale a pena", "compensa", "retorno", "payback"]),
        ("dicas", ["econom", "dica", "reduzir", "diminuir", "baixar", "conta de luz"]),
        ("lampada", ["lampada", "led", "iluminacao"]),
    ]

    def intencao(self, texto: str) -> str:
        t = normalizar(texto)
        for nome, chaves in self.INTENCOES:
            if any(k in t for k in chaves):
                return nome
        return "desconhecida"

    def responder(self, texto: str) -> str:
        t = normalizar(texto)
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*min", t)
        it = self.intencao(texto)
        if m and it in ("simular_banho", "dicas", "comparar", "desconhecida") and ("banho" in t or "chuveiro" in t or "ducha" in t):
            return self.simular_banho(float(m.group(1).replace(",", ".")))
        fn = {
            "ajuda": self.ajuda, "kwh": self.o_que_e_kwh, "relatorio": self.resumo_perfil,
            "fontes": self.fontes_e_limitacoes, "bandeira": self.bandeira, "co2": self.ambiental,
            "termico": lambda: self.detalhar("B"), "solar": lambda: self.detalhar("C"),
            "simular_banho": self.chuveiro, "ranking": self.ranking, "comparar": self.comparar,
            "dicas": self.dicas, "lampada": self.lampadas,
        }.get(it)
        if fn is None:
            return ("Não entendi bem a pergunta. Posso falar de: onde você gasta mais, chuveiro, "
                    "energia solar, bandeira tarifária, impacto ambiental e fontes. "
                    "Digite 'ajuda' para ver exemplos.")
        return fn()

    # ------------------------------------------------------------ respostas
    def ajuda(self) -> str:
        return ("Posso ajudar a reduzir sua conta de luz. Exemplos de perguntas:\n"
                "  • Onde eu gasto mais energia?\n"
                "  • Quanto custa meu chuveiro? / E se eu tomar banho de 5 minutos?\n"
                "  • Vale a pena instalar energia solar?\n"
                "  • Como economizar na conta de luz?\n"
                "  • O que é bandeira tarifária?  • Qual o impacto ambiental?\n"
                "  • Quais são as fontes e limitações?  • O que é kWh?")

    def o_que_e_kwh(self) -> str:
        return ("kWh (quilowatt-hora) é a unidade que aparece na sua conta: é a energia de um aparelho de "
                "1.000 W ligado por 1 hora. Exemplo: um chuveiro de "
                f"{num(c.potencia_chuveiro(self.perfil, self.pp), 0)} W gasta 1 kWh em cerca de "
                f"{num(60 * 1000 / c.potencia_chuveiro(self.perfil, self.pp), 0)} minutos. "
                "Fórmula: kWh = potência (kW) × horas de uso.")

    def ranking(self) -> str:
        linhas = c.consumo_por_equipamento(self.perfil, self.eqs, self.pp)
        total = sum(v for _, v in linhas)
        out = [f"Seu consumo estimado é de {num(total, 0)} kWh/mês (≈ {rs(total * self.tarifa)}/mês, "
               f"tarifa efetiva {rs(self.tarifa)}/kWh). Onde a energia vai:"]
        for nome, v in linhas[:6]:
            out.append(f"  {nome:<42} {num(v, 0):>5} kWh/mês  {v / total * 100:>4.0f}%  {rs(v * self.tarifa):>11}")
        top = linhas[0]
        out.append(f"\nO maior gasto é: {top[0]}. {AVISO}")
        return "\n".join(out)

    def chuveiro(self) -> str:
        ch = c.consumo_chuveiro_mes(self.perfil, self.pp)
        pot = c.potencia_chuveiro(self.perfil, self.pp)
        vf = c.verificacao_fisica_chuveiro(self.perfil, self.pp)
        return (f"Chuveiro elétrico de {num(pot, 0)} W, {self.perfil.pessoas} pessoas, banho de "
                f"{num(self.perfil.minutos_banho, 0)} min: ≈ {num(ch, 0)} kWh/mês "
                f"({num(ch / self.consumo * 100, 0)}% da casa), cerca de {rs(ch * self.tarifa)}/mês. "
                f"(Conferência física: {num(vf['eletrica_kwh'], 2)} kWh por banho pela potência × tempo "
                f"contra {num(vf['termico_kwh'], 2)} kWh pela física da água, diferença de "
                f"{num(vf['diferenca_pct'], 0)}%.)\n"
                "Dica: pergunte 'e se eu tomar banho de 5 minutos?' para simular.\n" + AVISO)

    def simular_banho(self, minutos: float) -> str:
        novo = self.perfil.copia()
        novo.minutos_banho = minutos
        antes = c.consumo_chuveiro_mes(self.perfil, self.pp)
        depois = c.consumo_chuveiro_mes(novo, self.pp)
        dif = antes - depois
        verbo = "economiza" if dif >= 0 else "GASTA A MAIS"
        return (f"Com banho de {num(minutos, 0)} min (hoje {num(self.perfil.minutos_banho, 0)} min), a casa "
                f"{verbo} ≈ {num(abs(dif), 0)} kWh/mês, ou {rs(abs(dif) * self.tarifa)}/mês "
                f"({rs(abs(dif) * self.tarifa * 12)}/ano). Isso evita ≈ "
                f"{num(c.co2_kg(abs(dif) * 12, self.pp.valor('co2_rede_tco2_mwh')), 1)} kg de CO₂/ano "
                f"(valor pequeno porque a rede brasileira já é limpa).\n" + AVISO)

    def lampadas(self) -> str:
        a = self.res["A"]
        n = a.detalhes["lampadas_trocadas"]
        if n == 0:
            return "Você não informou lâmpadas incandescentes ou fluorescentes para trocar. " + AVISO
        e = a.detalhes["economia_lampadas_kwh_ano"]
        return (f"Trocar {n} lâmpada(s) por LED de 9 W economiza ≈ {num(e, 0)} kWh/ano "
                f"({rs(e * self.tarifa)}/ano) e custa ≈ {rs(n * self.pp.valor('custo_lampada_led'))} "
                f"(preço estimado). O retorno é rápido, mas o valor total é pequeno perto do chuveiro.\n" + AVISO)

    def bandeira(self) -> str:
        p = self.pp
        base = self.consumo
        linhas = [f"Bandeira tarifária é um adicional por 100 kWh quando gerar energia fica mais caro. "
                  f"Bandeira atual: {p.valor('bandeira_atual')} (ANEEL, nov/2026). Para {num(base, 0)} kWh/mês, "
                  f"o adicional seria (antes dos tributos):"]
        for nome, ch in [("verde", "bandeira_verde_100kwh"), ("amarela", "bandeira_amarela_100kwh"),
                         ("vermelha 1", "bandeira_vermelha1_100kwh"), ("vermelha 2", "bandeira_vermelha2_100kwh")]:
            linhas.append(f"  {nome:<11} {rs(base * p.valor(ch) / 100):>9}/mês")
        linhas.append("Fonte: ANEEL (dado oficial). A bandeira muda todo mês; consulte o site da ANEEL.")
        return "\n".join(linhas)

    def ambiental(self) -> str:
        a, b, cc = self.res["A"], self.res["B"], self.res["C"]
        return ("Impacto ambiental (estimativa):\n"
                f"  A) Eficiência: evita ≈ {num(a.co2_operacional_kg_ano, 1)} kg CO₂/ano.\n"
                f"  B) Aquecedor solar: evita ≈ {num(b.co2_operacional_kg_ano, 1)} kg CO₂/ano.\n"
                f"  C) Fotovoltaica: evita ≈ {num(cc.co2_operacional_kg_ano, 1)} kg CO₂/ano na operação; "
                f"considerando a fabricação do painel o saldo líquido é ≈ {num(cc.co2_liquido_kg_ano, 1)} kg CO₂/ano "
                "(negativo = a fabricação do painel emite mais do que a rede evita).\n"
                f"Por que os números são pequenos? A rede brasileira emitiu só "
                f"{num(self.pp.valor('co2_rede_tco2_mwh') * 1000, 1)} kg CO₂/MWh em 2023 (MCTI), muito menos que "
                "países que queimam carvão. Aqui o principal ganho de economizar ou gerar a própria energia é "
                "financeiro, além de reduzir a pressão sobre a rede em horários críticos. "
                "Os fatores variam por ano e mês.\n" + AVISO)

    def comparar(self) -> str:
        h = int(self.pp.valor("horizonte_anos"))
        r = self.pp.valor("reajuste_tarifa_anual")
        out = [f"Comparação para a mesma necessidade (reduzir a conta de luz), em 12 meses e em {h} anos "
               f"(cenário: tarifa +{r * 100:.0f}%/ano):"]
        for k in ("A", "B", "C", "A+C"):
            x = self.res[k]
            marca = "renovável" if x.tipo in ("renovavel", "combinacao") else "economia"
            out.append(f"\n[{x.sigla}] {x.nome} ({marca}) — {x.descricao}\n"
                       f"    Investimento {rs(x.investimento)} | economia {rs(x.economia_rs_ano)}/ano "
                       f"({num(x.economia_kwh_ano, 0)} kWh)\n"
                       f"    Payback {anos(x.payback_simples)} (sem reajuste) / {anos(x.payback_reajuste)} (com reajuste) "
                       f"→ {alt.classificar_retorno(x)}\n"
                       f"    Saldo em {h} anos: {rs(x.saldo_horizonte_rs)} | CO₂ evitado ≈ "
                       f"{num(x.co2_liquido_kg_ano, 0)} kg/ano (líquido)")
        out.append("\nO que eu recomendo, nesta ordem:")
        out += ["  " + s for s in alt.recomendar(self.perfil, self.res)]
        out.append(AVISO)
        return "\n".join(out)

    def detalhar(self, sigla: str) -> str:
        x = self.res[sigla]
        v = {True: "viável nas condições informadas", False: "NÃO viável nas condições informadas",
             None: "viabilidade a confirmar (telhado/sombra)"}[x.viavel]
        h = int(self.pp.valor("horizonte_anos"))
        txt = [f"{x.nome}: {x.descricao}",
               f"Investimento estimado {rs(x.investimento)}; economia ≈ {rs(x.economia_rs_ano)}/ano; "
               f"payback ≈ {anos(x.payback_reajuste)} (com reajuste) ou {anos(x.payback_simples)} (sem). "
               f"Saldo em {h} anos: {rs(x.saldo_horizonte_rs)}.",
               f"Viabilidade: {v}.", "Condições: " + " ".join(x.condicoes), "Limitações: " + " ".join(x.limitacoes)]
        if sigla == "C":
            txt.insert(2, f"Conta: HSP {num(self.pp.valor('hsp_kwh_m2_dia'))} × PR {num(self.pp.valor('performance_ratio'), 2)} × 30,4 dias "
                          f"= {num(x.detalhes['geracao_por_kwp_mes'], 0)} kWh/mês por kWp. (HSP é estimativa; confirme no CRESESB.)")
        txt.append(AVISO)
        return "\n".join(txt)

    def dicas(self) -> str:
        a = self.res["A"]
        return ("Para reduzir a conta, na ordem do que mais compensa:\n"
                f"  1) Encurte o banho: cada minuto a menos em {self.perfil.pessoas} banhos/dia pesa. "
                f"Ex.: reduzir {num(self.pp.valor('reducao_banho_min'), 0)} min economiza ≈ "
                f"{num(a.detalhes['economia_banho_kwh_ano'], 0)} kWh/ano.\n"
                "  2) Troque lâmpadas incandescentes/fluorescentes por LED.\n"
                "  3) Use o ar-condicionado só quando necessário e mantenha filtros limpos.\n"
                "  4) Veja a etiqueta Procel/INMETRO ao trocar eletrodomésticos.\n"
                f"Hábitos e LED, juntos: ≈ {rs(a.economia_rs_ano)}/ano com investimento de {rs(a.investimento)}. "
                "Pergunte 'vale a pena energia solar?' para o próximo passo.\n" + AVISO)

    def fontes_e_limitacoes(self) -> str:
        usados = [k for k in self.p.chaves() if self.p.info(k)["tipo"] != "fisico"]
        est = [k for k in usados if self.p.info(k)["tipo"] == "estimado"]
        ofi = [k for k in usados if self.p.info(k)["tipo"] == "oficial"]
        return ("Fontes principais: ANEEL (tarifas, bandeiras, custo de disponibilidade), MCTI (fator de emissão "
                "do SIN), CRESESB/SunData (irradiação), INMETRO/Procel (consumo de aparelhos), Lei 14.300/2022 "
                "(geração distribuída), IPCC AR5 (ciclo de vida do painel). Lista completa: "
                "docs/03_REFERENCIAS_E_LIMITACOES.md.\n"
                f"Hoje a base tem {len(ofi)} parâmetros oficiais e {len(est)} estimados (marcados no arquivo "
                "data/parametros.json, com fonte e onde conferir).\n"
                "Limitações: usa médias anuais; tarifa, preços e irradiação são estimativas para a Grande SP; "
                "não considera sombreamento nem financiamento; as economias não se somam; "
                "não substitui projeto de engenharia nem orçamento.\n" + AVISO)

    def resumo_perfil(self) -> str:
        p = self.perfil
        return (f"Perfil: {p.pessoas} pessoas, banho de {num(p.minutos_banho, 0)} min, ligação {p.padrao_ligacao}, "
                f"imóvel {'próprio' if p.imovel_proprio else 'alugado/cedido'}, telhado "
                f"{ {True: 'adequado', False: 'inadequado', None: 'não sabe'}[p.telhado_adequado] }.\n"
                f"Tarifa efetiva: {rs(self.tarifa)}/kWh. Consumo estimado: {num(self.consumo, 0)} kWh/mês. "
                "Para gerar um relatório completo: python main.py --relatorio")

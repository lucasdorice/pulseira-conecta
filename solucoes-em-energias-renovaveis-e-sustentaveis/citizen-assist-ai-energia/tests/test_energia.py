"""Testes automatizados (unittest, sem dependências). Execute: python -m unittest discover -s tests -v"""
import unittest

from energia import alternativas as alt
from energia import calculos as c
from energia.assistente import AVISO, Assistente
from energia.dados import Item, Parametros, Perfil, carregar_equipamentos, perfil_exemplo
from energia.relatorio import gerar_markdown


class TestConceitos(unittest.TestCase):
    def test_energia_kwh(self):
        self.assertAlmostEqual(c.energia_kwh(1000, 1), 1.0)
        self.assertAlmostEqual(c.energia_kwh(5500, 12 / 60), 1.1)

    def test_custo_e_co2(self):
        self.assertAlmostEqual(c.custo_rs(100, 0.9), 90.0)
        # 1.000 kWh × 0,0385 tCO2/MWh = 38,5 kg
        self.assertAlmostEqual(c.co2_kg(1000, 0.0385), 38.5)

    def test_chuveiro_manual(self):
        p = Parametros()
        pf = Perfil(pessoas=4, minutos_banho=8)
        # 5,5 kW × (8/60 h × 1 × 4) × 30 dias × 0,8 = 70,4 kWh
        self.assertAlmostEqual(c.consumo_chuveiro_mes(pf, p), 70.4, places=1)

    def test_verificacao_fisica(self):
        v = c.verificacao_fisica_chuveiro(Perfil(minutos_banho=8), Parametros())
        self.assertLess(v["diferenca_pct"], 5.0)  # P×t e m·c·ΔT devem concordar


class TestFinanceiro(unittest.TestCase):
    def test_payback_simples(self):
        self.assertAlmostEqual(c.payback_anos(1000, 500), 2.0)
        self.assertAlmostEqual(c.payback_anos(750, 500), 1.5)

    def test_payback_com_reajuste_menor(self):
        self.assertLess(c.payback_anos(5000, 1000, reajuste=0.06), c.payback_anos(5000, 1000))

    def test_payback_inexistente(self):
        self.assertIsNone(c.payback_anos(1000, 0))
        self.assertIsNone(c.payback_anos(1_000_000, 100, max_anos=10))

    def test_saldo(self):
        self.assertAlmostEqual(c.saldo_horizonte(1000, 500, 10), 4000.0)


class TestSolar(unittest.TestCase):
    def test_geracao_por_kwp(self):
        # 4,6 × 0,78 × 30,4167 ≈ 109,1
        self.assertAlmostEqual(c.geracao_mensal_por_kwp(Parametros()), 109.1, places=0)

    def test_dimensionamento_cobre_alvo(self):
        p, pf = Parametros(), perfil_exemplo()
        d = c.dimensionar_fv(260, pf, p)
        self.assertGreaterEqual(d.geracao_mes_kwh, 260 - c.custo_disponibilidade(pf, p) - 1e-6)
        self.assertEqual(d.paineis, 4)

    def test_consumo_abaixo_da_disponibilidade_nao_dimensiona(self):
        d = c.dimensionar_fv(20, perfil_exemplo(), Parametros())
        self.assertEqual(d.paineis, 0)


class TestAlternativas(unittest.TestCase):
    def setUp(self):
        self.p, self.eqs, self.pf = Parametros(), carregar_equipamentos(), perfil_exemplo()
        self.res = alt.comparar(self.pf, self.eqs, self.p)

    def test_inclui_ao_menos_uma_renovavel_e_duas_alternativas(self):
        self.assertGreaterEqual(len(self.res), 2)
        self.assertTrue(any(r.tipo == "renovavel" for r in self.res.values()))

    def test_economias_positivas(self):
        for k in ("A", "B", "C"):
            self.assertGreater(self.res[k].economia_rs_ano, 0)

    def test_pacote_nao_e_soma_ingenua(self):
        a, cc, ac = self.res["A"], self.res["C"], self.res["A+C"]
        self.assertLess(ac.economia_kwh_ano, a.economia_kwh_ano + cc.economia_kwh_ano + 1e-6)

    def test_imovel_alugado_inviabiliza_renovaveis(self):
        pf = self.pf.copia()
        pf.imovel_proprio = False
        r = alt.comparar(pf, self.eqs, self.p)
        self.assertFalse(r["B"].viavel)
        self.assertFalse(r["C"].viavel)
        self.assertTrue(r["A"].viavel)

    def test_telhado_desconhecido_vira_a_confirmar(self):
        pf = self.pf.copia()
        pf.telhado_adequado = None
        self.assertIsNone(alt.comparar(pf, self.eqs, self.p)["C"].viavel)

    def test_tarifa_maior_encurta_payback(self):
        pf2 = self.pf.copia()
        pf2.tarifa_kwh = 1.40
        r2 = alt.comparar(pf2, self.eqs, self.p)
        self.assertLess(r2["C"].payback_reajuste, self.res["C"].payback_reajuste)

    def test_fv_co2_liquido_menor_que_operacional(self):
        c_ = self.res["C"]
        self.assertLess(c_.co2_liquido_kg_ano, c_.co2_operacional_kg_ano)

    def test_recomendacao_comeca_pela_eficiencia(self):
        self.assertIn("eficiência", alt.recomendar(self.pf, self.res)[0].lower())


class TestDados(unittest.TestCase):
    def test_todo_parametro_tem_fonte_e_tipo(self):
        p = Parametros()
        for k in p.chaves():
            info = p.info(k)
            self.assertIn(info["tipo"], {"oficial", "estimado", "fisico"}, k)
            self.assertTrue(info["fonte"].strip(), k)
            self.assertTrue(info["unidade"].strip(), k)

    def test_estimados_orientam_conferencia(self):
        # os parâmetros mais sensíveis devem dizer onde conferir/cotar
        p = Parametros()
        for k in ("tarifa_kwh", "hsp_kwh_m2_dia", "custo_fv_kwp"):
            self.assertRegex(p.info(k)["observacao"].lower(), r"substitua|confirmar|cotar")

    def test_equipamentos_tem_tipo_dado(self):
        for e in carregar_equipamentos().values():
            self.assertEqual(e.tipo_dado, "estimado")


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.a = Assistente(perfil_exemplo())

    def test_intencoes(self):
        casos = {
            "Onde eu gasto mais energia?": "ranking",
            "Vale a pena instalar energia solar?": "solar",
            "O que é bandeira tarifária?": "bandeira",
            "Qual o impacto ambiental?": "co2",
            "Quais as fontes?": "fontes",
            "Como economizar na conta de luz?": "dicas",
            "o que é kWh?": "kwh",
        }
        for pergunta, esperado in casos.items():
            self.assertEqual(self.a.intencao(pergunta), esperado, pergunta)

    def test_toda_resposta_numerica_traz_aviso(self):
        for q in ("Onde eu gasto mais?", "Vale a pena energia solar?", "Comparar alternativas",
                  "Qual o impacto ambiental?", "Como economizar?", "E se eu tomar banho de 5 minutos?"):
            self.assertIn("Estimativa", self.a.responder(q), q)
        self.assertEqual(AVISO[:2], "⚠ ")

    def test_simulacao_de_banho_usa_o_calculo(self):
        r = self.a.responder("E se eu tomar banho de 5 minutos?")
        antes = c.consumo_chuveiro_mes(self.a.perfil, self.a.pp)
        novo = self.a.perfil.copia()
        novo.minutos_banho = 5
        dif = antes - c.consumo_chuveiro_mes(novo, self.a.pp)
        self.assertIn(f"{dif:.0f}".replace(".", ","), r)

    def test_resposta_chuveiro(self):
        r = self.a.responder("Quanto gasto com o chuveiro?")
        self.assertIn("Conferência física", r)
        self.assertIn("70", r)  # ≈ 70 kWh/mês no perfil de exemplo

    def test_pergunta_desconhecida_nao_inventa(self):
        r = self.a.responder("qual a capital da França?")
        self.assertIn("Não entendi", r)

    def test_assistente_coerente_com_modulo_de_calculo(self):
        r = self.a.responder("Vale a pena energia solar?")
        c_ = alt.alt_fotovoltaica(self.a.perfil, self.a.eqs, self.a.p)
        self.assertIn(str(c_.detalhes["paineis"]), r)

    def test_bandeira_mostra_valores_oficiais(self):
        r = self.a.responder("o que é bandeira tarifária?")
        self.assertIn("verde", r)
        self.assertIn("ANEEL", r)

    def test_relatorio_gera(self):
        md = gerar_markdown()
        self.assertIn("Comparação das alternativas", md)
        self.assertIn("Sensibilidade", md)


if __name__ == "__main__":
    unittest.main()

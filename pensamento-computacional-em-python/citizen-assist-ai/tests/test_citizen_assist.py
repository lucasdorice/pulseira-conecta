"""Testes do Citizen Assist AI. Rode com:  python -m unittest discover -s tests -v

Os testes usam uma pasta temporária: não mexem em data/historico.json nem no CSV.
"""

import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistente import Assistente, EncerrarPrograma, analisar_link, contem_dado_pessoal  # noqa: E402
from base_conhecimento import BaseConhecimento, normalizar  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_REAL = os.path.join(RAIZ, "data", "base_conhecimento.json")


def criar_assistente(pasta):
    base = BaseConhecimento(JSON_REAL)
    base.carregar()
    return Assistente("Teste", base, os.path.join(pasta, "historico.json"),
                      os.path.join(pasta, "atendimentos.csv"))


def rodar(funcao, respostas):
    """Executa funcao() simulando o que a pessoa digita. Devolve o que foi impresso."""
    saida = io.StringIO()
    with mock.patch("builtins.input", side_effect=respostas), contextlib.redirect_stdout(saida):
        funcao()
    return saida.getvalue()


class TestNormalizar(unittest.TestCase):
    def test_remove_acentos_pontuacao_e_maiusculas(self):
        self.assertEqual(normalizar("  Como faço o Cartão do SUS?  "), " como faco o cartao do sus ")

    def test_palavra_inteira(self):
        self.assertNotIn(" sus ", normalizar("sustento"))


class TestBase(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(JSON_REAL)
        self.assertTrue(self.base.carregar())

    def test_requisitos_da_atividade(self):
        self.assertEqual(self.base.verificar_requisitos(), [])
        self.assertGreaterEqual(len(self.base.orientacoes), 10)
        self.assertGreaterEqual(len(self.base.categorias()), 3)

    def test_busca_devolve_tuplas_ordenadas(self):
        resultados = self.base.buscar("Como recebo alertas da Defesa Civil por SMS?")
        self.assertIsInstance(resultados[0], tuple)
        pontos = [p for p, _ in resultados]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertEqual(resultados[0][1].id, 4)

    def test_pontuacao_confianca_alta(self):
        pontos, orientacao = self.base.buscar("Como recebo alertas da Defesa Civil por SMS?")[0]
        self.assertGreaterEqual(pontos, 6)
        self.assertEqual(self.base.classificar(pontos), "ALTA")

    def test_pontuacao_confianca_media(self):
        pontos, orientacao = self.base.buscar("fgts")[0]
        self.assertEqual(orientacao.id, 9)
        self.assertEqual(self.base.classificar(pontos), "MÉDIA")

    def test_pergunta_sem_resposta(self):
        resultados = self.base.buscar("qual a previsao do jogo de futebol")
        melhor = resultados[0][0] if resultados else 0
        self.assertLess(melhor, 3)

    def test_voce_quis_dizer(self):
        corrigido, trocas = self.base.corrigir("o que fazer na enchent")
        self.assertIn("enchente", corrigido)
        self.assertTrue(trocas)

    def test_json_ausente_nao_trava(self):
        base = BaseConhecimento("/caminho/que/nao/existe.json")
        self.assertFalse(base.carregar())
        self.assertIn("não encontrado", base.erro)

    def test_json_corrompido_nao_trava(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "ruim.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("[ {isso nao e json ")
            base = BaseConhecimento(caminho)
            self.assertFalse(base.carregar())
            self.assertIn("corrompido", base.erro)

    def test_registro_invalido_e_ignorado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "parcial.json")
            with open(JSON_REAL, encoding="utf-8") as origem:
                valido = json.load(origem)[0]
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump([valido, {"id": 2}], arquivo)
            base = BaseConhecimento(caminho)
            self.assertTrue(base.carregar())
            self.assertEqual(len(base.orientacoes), 1)
            self.assertEqual(len(base.ignoradas), 1)


class TestDadosPessoais(unittest.TestCase):
    def test_cpf_telefone_email(self):
        self.assertTrue(contem_dado_pessoal("meu cpf é 123.456.789-00"))
        self.assertTrue(contem_dado_pessoal("(11) 91234-5678"))
        self.assertTrue(contem_dado_pessoal("joao@email.com"))

    def test_numeros_de_emergencia_passam(self):
        self.assertFalse(contem_dado_pessoal("ligar 199 ou 193"))


class TestLinks(unittest.TestCase):
    def test_oficial(self):
        self.assertEqual(analisar_link("https://www.caixa.gov.br")[0], "PARECE OFICIAL")

    def test_imitacao(self):
        self.assertEqual(analisar_link("https://gov.br.beneficio-fake.com/login")[0], "SUSPEITO")
        self.assertEqual(analisar_link("https://gov-br-auxilio.com")[0], "SUSPEITO")

    def test_truque_do_arroba(self):
        self.assertEqual(analisar_link("https://gov.br@site-falso.com")[0], "SUSPEITO")

    def test_encurtado(self):
        self.assertEqual(analisar_link("https://bit.ly/abc123")[0], "SUSPEITO")

    def test_nao_oficial(self):
        self.assertEqual(analisar_link("https://exemplo.com.br")[0], "NÃO OFICIAL")


class TestAtendimento(unittest.TestCase):
    def test_sessao_completa_registra_e_calcula_indicadores(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            saida = rodar(a.perguntar, [
                "",                                      # vazio
                "meu cpf é 123.456.789-00",              # dado pessoal: recusado
                "Como recebo alertas da Defesa Civil por SMS?",
                "talvez",                                # s/n inválido
                "s",                                     # ajudou
            ])
            self.assertIn("Atenção: não digite CPF", saida)
            self.assertIn("Confiança da resposta: ALTA", saida)
            self.assertIn("NÃO é um canal oficial", saida)
            self.assertIn("verificado em 2026-11-17", saida)
            self.assertEqual(len(a.historico), 1)
            self.assertTrue(a.historico[0]["ajudou"])
            self.assertEqual(a.historico[0]["id_orientacao"], 4)

            # pergunta sem solução: tenta duas vezes e volta
            rodar(a.perguntar, ["xyzxyz", "0"])
            dados = a.indicadores()
            self.assertEqual(dados["total"], 2)
            self.assertEqual(dados["resposta_encontrada_pct"], 50.0)
            self.assertEqual(dados["taxa_acerto_pct"], 50.0)
            self.assertEqual(len(dados["duvidas_sem_solucao"]), 1)

            # dado pessoal nunca foi para o histórico
            self.assertNotIn("123.456", json.dumps(a.historico))

    def test_nao_encontrado_sugere_categorias(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            saida = rodar(a.perguntar, ["receita de bolo", "0"])
            self.assertIn("Não encontrei", saida)
            self.assertIn("categorias", saida)

    def test_voce_quis_dizer_na_conversa(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            # "enchent" (digitado errado) -> "Você quis dizer: enchente?" -> s -> ajudou: s
            # (o texto de input() não aparece na saída capturada, então conferimos o resultado)
            saida = rodar(a.perguntar, ["enchent", "s", "s"])
            self.assertIn("Confiança da resposta", saida)
            self.assertEqual(a.historico[0]["id_orientacao"], 3)
            self.assertEqual(a.historico[0]["pergunta"], "enchent")
            self.assertEqual(a.historico[0]["tentativas"], 1)

    def test_modo_emergencia(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            saida = rodar(a.perguntar, ["socorro a agua esta entrando na casa", "s", "0"])
            self.assertIn("SE VOCÊ ESTÁ EM PERIGO AGORA", saida)

    def test_navegacao_e_entradas_invalidas(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            saida = rodar(a.navegar, [
                "abc", "", "99",       # letras, vazio, fora da faixa
                "1",                   # categoria Emergência
                "1",                   # orientação 1
                "x", "s",              # s/n inválido e depois sim
                "0",                   # volta das orientações
                "0",                   # volta das categorias
            ])
            self.assertIn("Digite apenas números", saida)
            self.assertIn("Opção fora da lista", saida)
            self.assertIn("Responda apenas com s", saida)
            self.assertEqual(a.historico[0]["origem"], "categoria")

    def test_alternativa_depois_de_n(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            # pergunta que casa com mais de uma orientação
            resultados = a.base.buscar("defesa civil alerta sms")
            self.assertGreaterEqual(len([r for r in resultados if r[0] >= 3]), 2)
            rodar(a.perguntar, ["defesa civil alerta sms", "n", "1", "s"])
            self.assertEqual(a.historico[0]["tentativas"], 2)
            self.assertTrue(a.historico[0]["ajudou"])

    def test_csv_e_nota(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            rodar(a.perguntar, ["enchente", "s"])
            rodar(a.encerrar, ["5"])
            self.assertEqual(a.indicadores()["facilidade_media"], 5.0)
            with open(a.caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo))
            self.assertEqual(len(linhas), 1)
            self.assertEqual(linhas[0]["ajudou"], "sim")
            self.assertEqual(linhas[0]["nota_facilidade"], "5")

    def test_historico_corrompido_nao_trava(self):
        with tempfile.TemporaryDirectory() as pasta:
            with open(os.path.join(pasta, "historico.json"), "w", encoding="utf-8") as arquivo:
                arquivo.write("{{{ quebrado")
            a = criar_assistente(pasta)
            self.assertEqual(a.historico, [])
            self.assertTrue(os.path.exists(os.path.join(pasta, "historico.json.bak")))

    def test_ctrl_d_encerra_sem_erro(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = criar_assistente(pasta)
            with mock.patch("builtins.input", side_effect=EOFError), \
                    contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(EncerrarPrograma):
                    a.perguntar()

    def test_base_vazia_nao_trava(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = BaseConhecimento("/nao/existe.json")
            base.carregar()
            a = Assistente("Teste", base, os.path.join(pasta, "h.json"),
                           os.path.join(pasta, "a.csv"))
            self.assertIn("não foi carregada", rodar(a.perguntar, []))
            self.assertIn("não foi carregada", rodar(a.navegar, []))
            self.assertIn("Ainda não há", rodar(a.mostrar_indicadores, []))


if __name__ == "__main__":
    unittest.main()

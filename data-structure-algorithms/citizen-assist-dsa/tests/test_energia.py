import pytest

from citizen_assist.algoritmos import merge_sort_por
from citizen_assist.energia.aparelho import (Aparelho, consumo_total_mensal,
                                             ranking_por_consumo)
from citizen_assist.energia.dados import (carregar_catalogo_aparelhos,
                                          carregar_dados_energia,
                                          carregar_fontes)
from citizen_assist.energia.demanda import (curva_demanda, fator_de_carga,
                                            fracao_hora, pico)
from citizen_assist.energia.fonte import (FonteEnergia, tem_dado_de_exemplo,
                                          total_participacao, total_renovaveis)
from citizen_assist.indicadores import Indicadores
from citizen_assist.lista import ListaEncadeada
from citizen_assist.validacao import validar_decimal, validar_hora
from web.app import create_app


def aparelhos(*itens):
    lista = ListaEncadeada()
    for i, (nome, pot, horas, ini) in enumerate(itens, start=1):
        lista.inserir(Aparelho(i, nome, pot, horas, ini))
    return lista


# ------------------------------------------------------------ matriz
def test_total_renovaveis_e_participacao():
    lista = ListaEncadeada()
    lista.inserir(FonteEnergia(1, "Hidro", "renovavel", 60))
    lista.inserir(FonteEnergia(2, "Gás", "nao_renovavel", 30))
    lista.inserir(FonteEnergia(3, "Solar", "renovavel", 10))
    assert total_renovaveis(lista) == 70
    assert total_participacao(lista) == 100
    assert tem_dado_de_exemplo(lista)


def test_total_com_lista_vazia():
    assert total_renovaveis(ListaEncadeada()) == 0.0


def test_ordenar_fontes_por_participacao():
    lista = ListaEncadeada()
    for i, p in enumerate([10, 55, 5, 30], start=1):
        lista.inserir(FonteEnergia(i, f"f{i}", "renovavel", p))
    merge_sort_por(lista, lambda f: f.participacao, decrescente=True)
    assert [f.participacao for f in lista.percorrer()] == [55, 30, 10, 5]
    assert lista.fim.dados.participacao == 5


# ------------------------------------------------------------ consumo
def test_consumo_mensal_formula():
    a = Aparelho(1, "Chuveiro", 5000, 0.5, 6)
    assert a.energia_diaria_kwh() == pytest.approx(2.5)
    assert a.consumo_mensal_kwh() == pytest.approx(75)
    assert a.consumo_mensal_kwh(dias=31) == pytest.approx(77.5)


def test_total_e_ranking():
    lista = aparelhos(("TV", 100, 5, 19), ("Chuveiro", 5000, 0.5, 6),
                      ("Geladeira", 100, 24, 0))
    assert consumo_total_mensal(lista) == pytest.approx(15 + 75 + 72)
    nomes = [a.nome for a in ranking_por_consumo(lista).percorrer()]
    assert nomes == ["Chuveiro", "Geladeira", "TV"]
    assert [a.nome for a in lista.percorrer()] == ["TV", "Chuveiro", "Geladeira"]


def test_lista_vazia_de_aparelhos():
    lista = ListaEncadeada()
    assert consumo_total_mensal(lista) == 0.0
    assert ranking_por_consumo(lista).esta_vazia()
    assert curva_demanda(lista) == [0.0] * 24
    assert fator_de_carga(curva_demanda(lista)) == 0.0


# ------------------------------------------------------------ demanda
@pytest.mark.parametrize("inicio,duracao,hora,esperado", [
    (6, 2, 5, 0), (6, 2, 6, 1), (6, 2, 7, 1), (6, 2, 8, 0),
    (6, 0.5, 6, 0.5), (6.0, 0.5, 7, 0),
    (22, 4, 23, 1), (22, 4, 0, 1), (22, 4, 1, 1), (22, 4, 2, 0),
    (5, 24, 12, 1), (5, 24, 4, 1)])
def test_fracao_hora(inicio, duracao, hora, esperado):
    assert fracao_hora(inicio, duracao, hora) == pytest.approx(esperado)


def test_soma_da_curva_igual_a_energia_diaria():
    lista = aparelhos(("A", 1000, 1.5, 7), ("B", 200, 24, 0), ("C", 500, 5, 22))
    curva = curva_demanda(lista)
    diaria = sum(a.energia_diaria_kwh() for a in lista.percorrer())
    assert sum(curva) == pytest.approx(diaria)


def test_pico_e_fator_de_carga():
    lista = aparelhos(("Constante", 100, 24, 0))
    curva = curva_demanda(lista)
    assert pico(curva) == (pytest.approx(0.1), 0)
    assert fator_de_carga(curva) == pytest.approx(1.0)
    lista = aparelhos(("Chuveiro", 6000, 1, 18))
    curva = curva_demanda(lista)
    assert pico(curva) == (pytest.approx(6.0), 18)
    assert fator_de_carga(curva) == pytest.approx(1 / 24)


def test_pico_empate_devolve_primeira_hora():
    lista = aparelhos(("X", 1000, 3, 10))
    assert pico(curva_demanda(lista))[1] == 10


# ------------------------------------------------------------ dados
def test_carregar_dados_de_exemplo():
    import os
    pasta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dados")
    fontes, catalogo, erros = carregar_dados_energia(pasta)
    assert erros == [] and len(fontes) == 8 and len(catalogo) == 9
    assert total_participacao(fontes) == pytest.approx(100)


def test_carregar_ignora_linhas_ruins(tmp_path):
    arq = tmp_path / "f.csv"
    arq.write_text("id,nome,tipo,participacao\n1,A,renovavel,50\n2,B,outro,10\n"
                   "3,C,renovavel,150\n4,D,renovavel,x\n", encoding="utf-8")
    lista, erros = carregar_fontes(str(arq))
    assert len(lista) == 1 and len(erros) == 3
    arq2 = tmp_path / "a.csv"
    arq2.write_text("id,nome,potencia_w,horas_dia,hora_inicio\n1,A,100,2,30\n"
                    "2,B,100,2,5\n", encoding="utf-8")
    lista, erros = carregar_catalogo_aparelhos(str(arq2))
    assert len(lista) == 1 and len(erros) == 1


def test_arquivo_inexistente(tmp_path):
    lista, erros = carregar_fontes(str(tmp_path / "nao_existe.csv"))
    assert lista.esta_vazia() and erros


# ------------------------------------------------------------ validação
@pytest.mark.parametrize("texto,ok", [("1,5", True), ("0", True), ("24", True),
                                      ("25", False), ("-1", False), ("abc", False),
                                      ("", False), ("nan", False), ("inf", False)])
def test_validar_decimal(texto, ok):
    assert (validar_decimal(texto, 0, 24, "as horas")[1] is None) == ok


@pytest.mark.parametrize("texto,ok", [("0", True), ("23", True), ("24", False),
                                      ("6.5", False), ("x", False)])
def test_validar_hora(texto, ok):
    assert (validar_hora(texto)[1] is None) == ok


# ------------------------------------------------------------ web
TOKEN = "t"


@pytest.fixture
def cliente():
    app = create_app(indicadores=Indicadores())
    c = app.test_client()
    with c.session_transaction() as s:
        s["_csrf"] = TOKEN
    return c


def test_pagina_energia(cliente):
    html = cliente.get("/energia").get_data(as_text=True)
    assert "Matriz energética" in html and "Hidrelétrica" in html
    assert "Dado de exemplo" in html and "Bandeiras tarifárias" in html
    assert "Total de fontes renováveis: 84.0%" in html


def test_calcular_na_web(cliente):
    r = cliente.post("/energia", data={
        "_csrf": TOKEN, "usar_1": "1", "pot_1": "5000", "horas_1": "0,5",
        "ini_1": "6", "usar_2": "1", "pot_2": "100", "horas_2": "24",
        "ini_2": "0", "tarifa": "1"})
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "147.0 kWh por mês" in html
    assert "147.00 reais por mês" in html and "Pico de demanda" in html
    assert html.index("Chuveiro") < html.rindex("Geladeira")


def test_erros_na_web(cliente):
    r = cliente.post("/energia", data={"_csrf": TOKEN, "usar_1": "1",
                                       "pot_1": "abc", "horas_1": "30", "ini_1": "25"})
    assert r.status_code == 422 and "Corrija antes de calcular" in r.get_data(as_text=True)
    r = cliente.post("/energia", data={"_csrf": TOKEN})
    assert r.status_code == 422 and "pelo menos um aparelho" in r.get_data(as_text=True)
    r = cliente.post("/energia", data={"_csrf": TOKEN, "usar_1": "1", "pot_1": "100",
                                       "horas_1": "1", "ini_1": "1", "tarifa": "zero"})
    assert r.status_code == 422
    r = cliente.post("/energia", data={"usar_1": "1"})
    assert r.status_code == 400

import pytest

from citizen_assist.lista import ListaEncadeada
from citizen_assist.validacao import (validar_campo, validar_id, validar_opcao,
                                      validar_servico)
from tests.conftest import fazer

BASE = {"id": "10", "titulo": "Teste", "categoria": "Cat", "descricao": "d",
        "publico_alvo": "p", "canal_local": "c"}


@pytest.mark.parametrize("texto,trecho", [
    ("", "Informe"), ("abc", "número inteiro"), ("-3", "número inteiro"),
    ("0", "maior que zero"), ("1.5", "número inteiro"), ("9999999", "no máximo")])
def test_id_invalido(texto, trecho):
    valor, erro = validar_id(texto, ListaEncadeada())
    assert valor is None and trecho in erro


def test_id_valido_e_duplicado():
    lista = ListaEncadeada()
    lista.inserir(fazer(7))
    assert validar_id(" 8 ", lista) == (8, None)
    assert "Já existe" in validar_id("7", lista)[1]
    assert validar_id("7", lista, ignorar_duplicidade=True) == (7, None)


@pytest.mark.parametrize("campo", ["titulo", "categoria", "descricao",
                                   "publico_alvo", "canal_local"])
@pytest.mark.parametrize("vazio", ["", "   "])
def test_campo_obrigatorio_vazio(campo, vazio):
    assert "obrigatório" in validar_campo(campo, vazio, ListaEncadeada())[1]


def test_limite_data_e_abrangencia():
    lista = ListaEncadeada()
    assert "no máximo" in validar_campo("titulo", "x" * 81, lista)[1]
    assert validar_campo("ultima_verificacao", "2026-13-40", lista)[1]
    assert "futuro" in validar_campo("ultima_verificacao", "2999-01-01", lista)[1]
    assert validar_campo("ultima_verificacao", "", lista) == ("", None)
    assert validar_campo("abrangencia", "", lista) == ("ambos", None)
    assert validar_campo("abrangencia", "Rural", lista) == ("rural", None)
    assert validar_campo("abrangencia", "mar", lista)[1]


def test_validar_servico_ok_e_erros():
    lista = ListaEncadeada()
    servico, erros = validar_servico(BASE, lista)
    assert not erros and servico.id == 10 and servico.abrangencia == "ambos"
    ruim = dict(BASE, id="x", titulo="")
    servico, erros = validar_servico(ruim, lista)
    assert servico is None and set(erros) == {"id", "titulo"}


def test_validar_servico_edicao_ignora_id_do_form():
    lista = ListaEncadeada()
    lista.inserir(fazer(10))
    servico, erros = validar_servico(dict(BASE, id=""), lista, id_fixo=10)
    assert not erros and servico.id == 10


@pytest.mark.parametrize("texto,ok", [("0", True), ("9", True), ("a", False),
                                      ("", False), ("10", False), ("-1", False)])
def test_opcao_menu(texto, ok):
    opcao, erro = validar_opcao(texto, 0, 9)
    assert (erro is None) == ok

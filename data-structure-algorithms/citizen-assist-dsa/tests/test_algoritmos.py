import random

import pytest

from citizen_assist.algoritmos import (contem, esta_ordenada, gerar_lista_aleatoria,
                                       insertion_sort, merge_sort, normalizar,
                                       pesquisar)
from citizen_assist.lista import ListaEncadeada
from tests.conftest import fazer


def titulos(lista):
    return [s.titulo for s in lista.percorrer()]


def test_normalizar_e_contem():
    assert normalizar("Vacinação") == "vacinacao"
    assert contem("vacinacao", "cina") and not contem("vacinacao", "xyz")
    assert contem("abc", "") and not contem("ab", "abc")


def test_pesquisa_titulo_categoria_todos(lista_cinco):
    assert titulos(pesquisar(lista_cinco, "VACINA", "titulo")) == ["Vacinação"]
    assert len(pesquisar(lista_cinco, "saude", "categoria")) == 1
    assert len(pesquisar(lista_cinco, "descri", "todos")) == 5
    assert pesquisar(lista_cinco, "inexistente", "titulo").esta_vazia()


def test_pesquisa_em_lista_vazia():
    assert pesquisar(ListaEncadeada(), "x").esta_vazia()


@pytest.mark.parametrize("ordenar", [merge_sort, insertion_sort])
@pytest.mark.parametrize("criterio,desc", [("titulo", False), ("titulo", True),
                                           ("id", False), ("id", True)])
def test_ordenacao(ordenar, criterio, desc, lista_cinco):
    ordenar(lista_cinco, criterio, desc)
    assert esta_ordenada(lista_cinco, criterio, desc)
    assert len(lista_cinco) == 5 and lista_cinco.fim.proximo is None


@pytest.mark.parametrize("ordenar", [merge_sort, insertion_sort])
def test_ordenacao_vazia_e_um(ordenar):
    lista = ListaEncadeada()
    ordenar(lista, "id")
    assert lista.esta_vazia() and lista.fim is None
    lista.inserir(fazer(1))
    ordenar(lista, "id")
    assert len(lista) == 1


@pytest.mark.parametrize("ordenar", [merge_sort, insertion_sort])
def test_ordenacao_estavel_e_aleatoria(ordenar):
    lista = gerar_lista_aleatoria(300, semente=7)
    ordenar(lista, "id")
    assert esta_ordenada(lista, "id") and len(lista) == 300
    ids = [s.id for s in lista.percorrer()]
    assert ids == list(range(1, 301))


def test_merge_e_insertion_dao_mesmo_resultado():
    rnd = random.Random(1)
    a, b = ListaEncadeada(), ListaEncadeada()
    for i in range(100):
        t = rnd.choice(["a", "b", "c"])
        a.inserir(fazer(i + 1, t))
        b.inserir(fazer(i + 1, t))
    merge_sort(a, "titulo")
    insertion_sort(b, "titulo")
    assert [s.id for s in a.percorrer()] == [s.id for s in b.percorrer()]

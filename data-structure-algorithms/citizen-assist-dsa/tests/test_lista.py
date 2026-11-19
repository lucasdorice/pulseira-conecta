import pytest

from citizen_assist.lista import ListaEncadeada
from tests.conftest import fazer


def ids(lista):
    return [s.id for s in lista.percorrer()]


def test_lista_vazia():
    lista = ListaEncadeada()
    assert lista.esta_vazia() and len(lista) == 0
    assert list(lista.percorrer()) == []
    assert lista.buscar_por_id(1) is None
    assert lista.remover(1) is None
    assert lista.atualizar(1, fazer(1)) is False


def test_inserir_mantem_ordem_e_fim(lista_cinco):
    assert ids(lista_cinco) == [3, 1, 5, 2, 4]
    assert lista_cinco.fim.dados.id == 4 and len(lista_cinco) == 5


def test_id_duplicado_recusado(lista_cinco):
    with pytest.raises(ValueError):
        lista_cinco.inserir(fazer(3))
    assert len(lista_cinco) == 5


def test_buscar_por_id(lista_cinco):
    assert lista_cinco.buscar_por_id(5).titulo == "Matrícula"
    assert lista_cinco.buscar_por_id(99) is None


def test_atualizar_preserva_id(lista_cinco):
    novo = fazer(99, "Novo título")
    assert lista_cinco.atualizar(5, novo)
    assert lista_cinco.buscar_por_id(5).titulo == "Novo título"
    assert lista_cinco.buscar_por_id(99) is None


@pytest.mark.parametrize("remover,esperado,fim", [
    (3, [1, 5, 2, 4], 4),   # primeiro
    (5, [3, 1, 2, 4], 4),   # meio
    (4, [3, 1, 5, 2], 2),   # último
])
def test_remover_primeiro_meio_ultimo(lista_cinco, remover, esperado, fim):
    removido = lista_cinco.remover(remover)
    assert removido.id == remover
    assert ids(lista_cinco) == esperado
    assert lista_cinco.fim.dados.id == fim
    assert len(lista_cinco) == 4
    lista_cinco.inserir(fazer(100))          # fim continua válido
    assert ids(lista_cinco)[-1] == 100


def test_remover_unico_no():
    lista = ListaEncadeada()
    lista.inserir(fazer(1))
    lista.remover(1)
    assert lista.inicio is None and lista.fim is None and len(lista) == 0


def test_remover_inexistente(lista_cinco):
    assert lista_cinco.remover(99) is None
    assert len(lista_cinco) == 5


def test_limpar_e_copiar(lista_cinco):
    copia = lista_cinco.copiar()
    lista_cinco.limpar()
    assert lista_cinco.esta_vazia() and len(copia) == 5

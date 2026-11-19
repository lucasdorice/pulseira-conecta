import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from citizen_assist.lista import ListaEncadeada
from citizen_assist.servico import Servico


def fazer(id_, titulo="Serviço", categoria="Cat", data="2026-11-01"):
    return Servico(id_, titulo, categoria, "descrição", "todos", "balcão",
                   ultima_verificacao=data)


@pytest.fixture
def lista_cinco():
    lista = ListaEncadeada()
    for id_, titulo, cat in [(3, "Vacinação", "Saúde"), (1, "RG", "Documentos"),
                             (5, "Matrícula", "Educação"), (2, "CadÚnico", "Assistência social"),
                             (4, "Água e luz", "Atendimento comunitário")]:
        lista.inserir(fazer(id_, titulo, cat))
    return lista

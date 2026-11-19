from citizen_assist.indicadores import (Indicadores, contar_categorias,
                                        contar_desatualizados)
from citizen_assist.lista import ListaEncadeada
from citizen_assist.persistencia import (carregar_csv, exportar_json,
                                         salvar_csv)
from citizen_assist.servico import Servico
from datetime import date
import json


def test_salvar_e_carregar(tmp_path, lista_cinco):
    arq = tmp_path / "s.csv"
    salvar_csv(lista_cinco, arq)
    nova = ListaEncadeada()
    aceitos, erros = carregar_csv(nova, arq)
    assert aceitos == 5 and erros == []
    assert [s.id for s in nova.percorrer()] == [3, 1, 5, 2, 4]
    assert nova.buscar_por_id(2).titulo == "CadÚnico"


def test_carregar_ignora_linhas_ruins(tmp_path):
    arq = tmp_path / "s.csv"
    arq.write_text(
        "id,titulo,categoria,descricao,publico_alvo,canal_local\n"
        "1,A,C,d,p,c\n1,Duplicado,C,d,p,c\nx,B,C,d,p,c\n2,,C,d,p,c\n",
        encoding="utf-8")
    lista = ListaEncadeada()
    aceitos, erros = carregar_csv(lista, arq)
    assert aceitos == 1 and len(erros) == 3


def test_exportar_json(tmp_path, lista_cinco):
    arq = tmp_path / "s.json"
    exportar_json(lista_cinco, arq)
    assert len(json.loads(arq.read_text(encoding="utf-8"))) == 5


def test_indicadores_nao_guardam_termo(tmp_path):
    arq = tmp_path / "i.csv"
    ind = Indicadores(str(arq))
    ind.registrar_busca(0.002, 3)
    ind.registrar_busca(0.001, 0)
    r = ind.resumo()
    assert r["buscas"] == 2 and r["taxa_resultado"] == 50.0
    assert arq.read_text().splitlines()[0] == "momento,tempo_ms,resultados"


def test_relatorios(lista_cinco):
    assert contar_categorias(lista_cinco)["Saúde"] == 1
    lista_cinco.inserir(Servico(50, "Velho", "X", "d", "p", "c",
                                ultima_verificacao="2025-01-01"))
    assert contar_desatualizados(lista_cinco, date(2026, 11, 13)) == 1

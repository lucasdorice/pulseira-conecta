"""Leitura dos arquivos de dados de energia (CSV)."""
import csv
import os

from ..lista import ListaEncadeada
from .aparelho import Aparelho
from .fonte import TIPOS, FonteEnergia


def _numero(texto):
    return float(str(texto).strip().replace(",", "."))


def carregar_fontes(caminho):
    """Devolve (ListaEncadeada de FonteEnergia, mensagens de erro)."""
    lista = ListaEncadeada()
    erros = []
    if not os.path.exists(caminho):
        return lista, [f"Arquivo não encontrado: {caminho}"]
    with open(caminho, newline="", encoding="utf-8") as arq:
        for n, linha in enumerate(csv.DictReader(arq), start=2):
            try:
                tipo = linha["tipo"].strip()
                if tipo not in TIPOS:
                    raise ValueError("tipo inválido")
                part = _numero(linha["participacao"])
                if not 0 <= part <= 100:
                    raise ValueError("participação fora de 0 a 100")
                lista.inserir(FonteEnergia(
                    int(linha["id"]), linha["nome"].strip(), tipo, part,
                    linha.get("origem", ""), linha.get("ano", ""),
                    linha.get("situacao", "exemplo")))
            except (ValueError, KeyError) as erro:
                erros.append(f"Linha {n} ignorada: {erro}")
    return lista, erros


def carregar_catalogo_aparelhos(caminho):
    """Devolve (ListaEncadeada de Aparelho sugeridos, mensagens de erro)."""
    lista = ListaEncadeada()
    erros = []
    if not os.path.exists(caminho):
        return lista, [f"Arquivo não encontrado: {caminho}"]
    with open(caminho, newline="", encoding="utf-8") as arq:
        for n, linha in enumerate(csv.DictReader(arq), start=2):
            try:
                potencia = _numero(linha["potencia_w"])
                horas = _numero(linha["horas_dia"])
                inicio = int(linha["hora_inicio"])
                if potencia <= 0 or not 0 <= horas <= 24 or not 0 <= inicio <= 23:
                    raise ValueError("valores fora da faixa")
                lista.inserir(Aparelho(
                    int(linha["id"]), linha["nome"].strip(), potencia, horas,
                    inicio, linha.get("origem", ""),
                    linha.get("situacao", "exemplo")))
            except (ValueError, KeyError) as erro:
                erros.append(f"Linha {n} ignorada: {erro}")
    return lista, erros


def carregar_dados_energia(pasta_dados):
    """Carrega a matriz e o catálogo de aparelhos da pasta de dados."""
    fontes, e1 = carregar_fontes(os.path.join(pasta_dados, "energia_matriz_exemplo.csv"))
    catalogo, e2 = carregar_catalogo_aparelhos(
        os.path.join(pasta_dados, "energia_aparelhos_exemplo.csv"))
    return fontes, catalogo, e1 + e2

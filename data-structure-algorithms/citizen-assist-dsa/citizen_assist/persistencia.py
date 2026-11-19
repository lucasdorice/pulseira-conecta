"""Salvar e carregar a lista em CSV e exportar em JSON."""
import csv
import json
import os

from .servico import CAMPOS
from .validacao import validar_servico


def salvar_csv(lista, caminho):
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=CAMPOS)
        escritor.writeheader()
        for s in lista.percorrer():
            escritor.writerow(s.para_dict())


def carregar_csv(lista, caminho, substituir=True):
    """Lê o CSV validando cada linha. Devolve (aceitos, mensagens_de_erro).

    Lança FileNotFoundError se o arquivo não existir.
    """
    erros = []
    aceitos = 0
    with open(caminho, newline="", encoding="utf-8") as arq:
        leitor = csv.DictReader(arq)
        if substituir:
            lista.limpar()
        for numero, linha in enumerate(leitor, start=2):
            servico, problemas = validar_servico(linha, lista)
            if problemas:
                resumo = "; ".join(problemas.values())
                erros.append(f"Linha {numero} ignorada: {resumo}")
                continue
            lista.inserir_fim_sem_verificar(servico)
            aceitos += 1
    return aceitos, erros


def lista_para_dicts(lista):
    return [s.para_dict() for s in lista.percorrer()]


def exportar_json(lista, caminho):
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arq:
        json.dump(lista_para_dicts(lista), arq, ensure_ascii=False, indent=2)


def carregar_inicial(lista, pasta_dados):
    """Carrega dados/servicos.csv; se não existir, o arquivo de exemplo."""
    for nome in ("servicos.csv", "servicos_exemplo.csv"):
        caminho = os.path.join(pasta_dados, nome)
        if os.path.exists(caminho):
            return carregar_csv(lista, caminho)
    return 0, []

"""Indicadores de uso. Não guardam o texto buscado nem dados pessoais."""
import csv
import os
from datetime import datetime


class Indicadores:
    def __init__(self, caminho=None):
        self.caminho = caminho
        self.buscas = 0
        self.buscas_com_resultado = 0
        self.soma_tempo_ms = 0.0

    def registrar_busca(self, tempo_segundos, quantidade_resultados):
        tempo_ms = tempo_segundos * 1000
        self.buscas += 1
        self.soma_tempo_ms += tempo_ms
        if quantidade_resultados > 0:
            self.buscas_com_resultado += 1
        if self.caminho:
            novo = not os.path.exists(self.caminho)
            pasta = os.path.dirname(self.caminho)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho, "a", newline="", encoding="utf-8") as arq:
                escritor = csv.writer(arq)
                if novo:
                    escritor.writerow(["momento", "tempo_ms", "resultados"])
                escritor.writerow([datetime.now().isoformat(timespec="seconds"),
                                   round(tempo_ms, 3), quantidade_resultados])

    def resumo(self):
        taxa = (self.buscas_com_resultado / self.buscas * 100
                if self.buscas else 0.0)
        media = self.soma_tempo_ms / self.buscas if self.buscas else 0.0
        return {"buscas": self.buscas,
                "com_resultado": self.buscas_com_resultado,
                "taxa_resultado": round(taxa, 1),
                "tempo_medio_ms": round(media, 3)}


def contar_categorias(lista):
    """Quantidade de serviços por categoria (dict apenas para o relatório)."""
    contagem = {}
    for s in lista.percorrer():
        contagem[s.categoria] = contagem.get(s.categoria, 0) + 1
    return contagem


def contar_desatualizados(lista, hoje=None):
    """Quantidade de serviços não verificados há mais de 180 dias (ou sem data)."""
    total = 0
    for s in lista.percorrer():
        if s.status_verificacao(hoje) != "ok":
            total += 1
    return total

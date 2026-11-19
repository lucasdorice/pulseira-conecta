"""Potência e energia: aparelhos, consumo mensal e ranking."""
from ..algoritmos import merge_sort_por

DIAS_MES = 30


class Aparelho:
    def __init__(self, id, nome, potencia_w, horas_dia, hora_inicio,
                 origem="", situacao="exemplo"):
        self.id = id
        self.nome = nome
        self.potencia_w = potencia_w      # potência em watts
        self.horas_dia = horas_dia        # horas de uso por dia (0 a 24)
        self.hora_inicio = hora_inicio    # hora do dia em que liga (0 a 23)
        self.origem = origem
        self.situacao = situacao

    def energia_diaria_kwh(self):
        """E (kWh/dia) = P (W) ÷ 1000 × horas por dia."""
        return self.potencia_w / 1000 * self.horas_dia

    def consumo_mensal_kwh(self, dias=DIAS_MES):
        return self.energia_diaria_kwh() * dias


def consumo_total_mensal(lista, dias=DIAS_MES):
    """Soma o consumo de todos os aparelhos. O(n)."""
    total = 0.0
    for a in lista.percorrer():
        total += a.consumo_mensal_kwh(dias)
    return total


def ranking_por_consumo(lista):
    """Nova lista com os aparelhos do que mais ao que menos consome.

    Copia os nós (O(n)) e ordena a cópia com merge sort (O(n log n)).
    """
    copia = lista.copiar()
    merge_sort_por(copia, lambda a: a.consumo_mensal_kwh(), decrescente=True)
    return copia

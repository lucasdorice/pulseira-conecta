"""Uso por demanda: curva de carga de 24 horas, pico e fator de carga.

A curva é um conjunto fixo de 24 posições (uma por hora do dia), por isso usa
uma sequência de tamanho fixo. Os aparelhos continuam na lista encadeada.
"""


def fracao_hora(inicio, duracao, hora):
    """Quanto da hora [hora, hora+1) o aparelho fica ligado (0 a 1).

    O aparelho liga em `inicio` e fica `duracao` horas; passa da meia-noite
    quando inicio + duracao > 24.
    """
    total = 0.0
    for deslocamento in (0, -24):
        ini = inicio + deslocamento
        fim = ini + duracao
        sobreposicao = min(fim, hora + 1) - max(ini, hora)
        if sobreposicao > 0:
            total += sobreposicao
    return min(total, 1.0)


def curva_demanda(lista):
    """Demanda média (kW) em cada uma das 24 horas. O(24·n)."""
    curva = [0.0] * 24
    for a in lista.percorrer():
        for hora in range(24):
            curva[hora] += a.potencia_w / 1000 * fracao_hora(
                a.hora_inicio, a.horas_dia, hora)
    return curva


def pico(curva):
    """(maior demanda em kW, primeira hora em que ocorre). O(24)."""
    maior = curva[0]
    hora_maior = 0
    for hora in range(1, 24):
        if curva[hora] > maior:
            maior = curva[hora]
            hora_maior = hora
    return maior, hora_maior


def fator_de_carga(curva):
    """Demanda média ÷ demanda de pico (1 = consumo perfeitamente constante)."""
    maior, _ = pico(curva)
    if maior <= 0:
        return 0.0
    return (sum(curva) / 24) / maior

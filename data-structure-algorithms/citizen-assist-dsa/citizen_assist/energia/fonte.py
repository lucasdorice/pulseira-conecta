"""Matriz energética: fontes de energia e sua participação (%)."""

TIPOS = ("renovavel", "nao_renovavel")


class FonteEnergia:
    def __init__(self, id, nome, tipo, participacao, origem="", ano="",
                 situacao="exemplo"):
        self.id = id
        self.nome = nome
        self.tipo = tipo                    # renovavel | nao_renovavel
        self.participacao = participacao    # % do total
        self.origem = origem                # de onde veio o dado
        self.ano = ano
        self.situacao = situacao            # exemplo | oficial


def total_participacao(lista):
    """Soma das participações. O(n)."""
    total = 0.0
    for f in lista.percorrer():
        total += f.participacao
    return total


def total_renovaveis(lista):
    """Soma da participação das fontes renováveis. O(n)."""
    total = 0.0
    for f in lista.percorrer():
        if f.tipo == "renovavel":
            total += f.participacao
    return total


def tem_dado_de_exemplo(lista):
    for f in lista.percorrer():
        if f.situacao != "oficial":
            return True
    return False

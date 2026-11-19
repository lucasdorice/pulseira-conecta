"""Nó da lista encadeada."""


class No:
    """Guarda um Servico e a referência explícita ao próximo nó."""

    def __init__(self, dados):
        self.dados = dados
        self.proximo = None

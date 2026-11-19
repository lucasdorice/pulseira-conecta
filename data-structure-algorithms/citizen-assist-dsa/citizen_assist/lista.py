"""Lista simplesmente encadeada implementada pela equipe.

Nenhuma `list` nativa guarda os registros: cada nó aponta para o seguinte.
Mantém `inicio`, `fim` (inserção no fim em O(1)) e `tamanho`.
"""
from .no import No


class ListaEncadeada:
    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def __len__(self):
        return self.tamanho

    def esta_vazia(self):
        return self.inicio is None

    # ---- inserção -------------------------------------------------------
    def inserir_fim_sem_verificar(self, servico):
        """Liga um novo nó no fim. Custo O(1) (usa a referência `fim`)."""
        novo = No(servico)
        if self.inicio is None:
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self.tamanho += 1

    def inserir(self, servico):
        """Insere garantindo id único. Percorre a lista antes: O(n)."""
        if self.buscar_por_id(servico.id) is not None:
            raise ValueError(f"Já existe um serviço com o ID {servico.id}.")
        self.inserir_fim_sem_verificar(servico)

    # ---- percurso -------------------------------------------------------
    def percorrer(self):
        """Entrega os registros um a um, do início ao fim. O(n)."""
        atual = self.inicio
        while atual is not None:
            yield atual.dados
            atual = atual.proximo

    def _localizar_no(self, id_):
        atual = self.inicio
        while atual is not None and atual.dados.id != id_:
            atual = atual.proximo
        return atual

    def buscar_por_id(self, id_):
        """Busca linear pelo id. O(n); devolve o Servico ou None."""
        no = self._localizar_no(id_)
        return no.dados if no is not None else None

    # ---- atualização ----------------------------------------------------
    def atualizar(self, id_, novo_servico):
        """Troca os dados do nó com esse id (o id é preservado). O(n)."""
        no = self._localizar_no(id_)
        if no is None:
            return False
        novo_servico.id = id_
        no.dados = novo_servico
        return True

    # ---- remoção --------------------------------------------------------
    def remover(self, id_):
        """Remove o nó com esse id e devolve o Servico removido (ou None).

        Casos tratados: lista vazia, primeiro nó, nó do meio e último nó
        (atualizando `fim`). Custo O(n) para achar o nó, O(1) para religar.
        """
        anterior = None
        atual = self.inicio
        while atual is not None and atual.dados.id != id_:
            anterior = atual
            atual = atual.proximo
        if atual is None:
            return None
        if anterior is None:
            self.inicio = atual.proximo
        else:
            anterior.proximo = atual.proximo
        if atual is self.fim:
            self.fim = anterior
        atual.proximo = None
        self.tamanho -= 1
        return atual.dados

    def limpar(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    # ---- apoio ----------------------------------------------------------
    def refazer_fim(self):
        """Recalcula `fim` depois de uma ordenação que religou os nós. O(n)."""
        atual = self.inicio
        self.fim = None
        while atual is not None:
            self.fim = atual
            atual = atual.proximo

    def copiar(self):
        """Nova lista com os mesmos registros (nós novos). O(n)."""
        copia = ListaEncadeada()
        for servico in self.percorrer():
            copia.inserir_fim_sem_verificar(servico)
        return copia

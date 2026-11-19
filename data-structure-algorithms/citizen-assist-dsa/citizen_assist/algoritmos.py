"""Busca e ordenação implementadas à mão (sem sorted/list.sort/bisect/in)."""
import random
import time

from .lista import ListaEncadeada
from .no import No
from .servico import Servico

_ACENTOS = {
    "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c",
}


def normalizar(texto):
    """Minúsculas e sem acentos comuns do português. O(L)."""
    return "".join(_ACENTOS.get(c, c) for c in texto.lower())


# ---------------------------------------------------------------- busca
def contem(texto, trecho):
    """Busca ingênua de substring escrita à mão. O(L·m) no pior caso."""
    n, m = len(texto), len(trecho)
    if m == 0:
        return True
    for i in range(n - m + 1):
        j = 0
        while j < m and texto[i + j] == trecho[j]:
            j += 1
        if j == m:
            return True
    return False


def buscar_id(lista, id_):
    """Busca linear por id. O(n)."""
    return lista.buscar_por_id(id_)


def pesquisar(lista, termo, campo="titulo"):
    """Pesquisa por trecho, sem diferenciar maiúsculas e acentos.

    campo: 'titulo', 'categoria' ou 'todos' (título + categoria + descrição).
    Devolve uma nova ListaEncadeada com os registros encontrados.
    Custo O(n·L) para L = tamanho dos textos comparados.
    """
    alvo = normalizar(termo.strip())
    resultado = ListaEncadeada()
    for s in lista.percorrer():
        if campo == "titulo":
            texto = s.titulo
        elif campo == "categoria":
            texto = s.categoria
        else:
            texto = s.titulo + " " + s.categoria + " " + s.descricao
        if contem(normalizar(texto), alvo):
            resultado.inserir_fim_sem_verificar(s)
    return resultado


# ------------------------------------------------------------ ordenação
def _chave(servico, criterio):
    return servico.id if criterio == "id" else normalizar(servico.titulo)


def _a_primeiro(chave_a, chave_b, decrescente):
    """True se o nó A deve vir antes de B (empate: A primeiro = estável)."""
    return chave_a >= chave_b if decrescente else chave_a <= chave_b


def _dividir(inicio):
    """Divide a cadeia ao meio com dois ponteiros (lento e rápido). O(n)."""
    lento = inicio
    rapido = inicio.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    segunda = lento.proximo
    lento.proximo = None
    return inicio, segunda


def _intercalar(a, b, chave, decrescente):
    """Junta duas cadeias já ordenadas religando os nós. O(n)."""
    sentinela = No(None)
    cauda = sentinela
    while a is not None and b is not None:
        if _a_primeiro(chave(a.dados), chave(b.dados), decrescente):
            cauda.proximo = a
            a = a.proximo
        else:
            cauda.proximo = b
            b = b.proximo
        cauda = cauda.proximo
    cauda.proximo = a if a is not None else b
    return sentinela.proximo


def _merge_sort_nos(inicio, chave, decrescente):
    if inicio is None or inicio.proximo is None:
        return inicio
    esquerda, direita = _dividir(inicio)
    esquerda = _merge_sort_nos(esquerda, chave, decrescente)
    direita = _merge_sort_nos(direita, chave, decrescente)
    return _intercalar(esquerda, direita, chave, decrescente)


def merge_sort_por(lista, chave, decrescente=False):
    """Merge sort sobre a lista encadeada, por qualquer chave. O(n log n).

    `chave` é uma função que recebe o registro e devolve o valor comparado
    (por exemplo, o consumo de um aparelho ou a participação de uma fonte).
    """
    lista.inicio = _merge_sort_nos(lista.inicio, chave, decrescente)
    lista.refazer_fim()


def merge_sort(lista, criterio="titulo", decrescente=False):
    """Merge sort dos serviços por título ou id. O(n log n)."""
    merge_sort_por(lista, lambda s: _chave(s, criterio), decrescente)


def insertion_sort(lista, criterio="titulo", decrescente=False):
    """Insertion sort religando nós (comparativo). O(n²) no pior caso."""
    ordenada = None
    atual = lista.inicio
    while atual is not None:
        proximo = atual.proximo
        chave_atual = _chave(atual.dados, criterio)
        if ordenada is None or not _a_primeiro(
                _chave(ordenada.dados, criterio), chave_atual, decrescente):
            atual.proximo = ordenada
            ordenada = atual
        else:
            p = ordenada
            while p.proximo is not None and _a_primeiro(
                    _chave(p.proximo.dados, criterio), chave_atual,
                    decrescente):
                p = p.proximo
            atual.proximo = p.proximo
            p.proximo = atual
        atual = proximo
    lista.inicio = ordenada
    lista.refazer_fim()


def esta_ordenada(lista, criterio="titulo", decrescente=False):
    anterior = None
    for s in lista.percorrer():
        if anterior is not None and not _a_primeiro(
                _chave(anterior, criterio), _chave(s, criterio), decrescente):
            return False
        anterior = s
    return True


# ------------------------------------------------------------ benchmark
def gerar_lista_aleatoria(n, semente=42):
    """Lista com n serviços fictícios, ids embaralhados."""
    rnd = random.Random(semente)
    ids = [i + 1 for i in range(n)]
    rnd.shuffle(ids)
    lista = ListaEncadeada()
    letras = "abcdefghijklmnopqrstuvwxyz"
    for i in ids:
        titulo = "".join(rnd.choice(letras) for _ in range(8))
        lista.inserir_fim_sem_verificar(
            Servico(i, titulo, "Teste", "d", "p", "c"))
    return lista


def benchmark(tamanhos, criterio="titulo"):
    """Mede merge sort x insertion sort. Devolve linhas {n, merge_ms, insertion_ms}."""
    linhas = []
    for n in tamanhos:
        a = gerar_lista_aleatoria(n)
        t0 = time.perf_counter()
        merge_sort(a, criterio)
        t_merge = (time.perf_counter() - t0) * 1000
        b = gerar_lista_aleatoria(n)
        t0 = time.perf_counter()
        insertion_sort(b, criterio)
        t_ins = (time.perf_counter() - t0) * 1000
        linhas.append({"n": n, "merge_ms": round(t_merge, 2),
                       "insertion_ms": round(t_ins, 2)})
    return linhas

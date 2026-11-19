"""Regras determinísticas (sem IA): validação, dados pessoais e prompt injection."""
import re
from .fichas import normalizar
from .textos import MAX_CARACTERES

# ---------- 1. Validação ----------
VOCABULARIO = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre ate ao aos
e ou mas que se como quando onde qual quais quanto quantos quantas quem porque
eu voce voces vc me te meu minha meus minhas seu sua nosso nossa ele ela eles elas
sou e eh sao esta estao estou tenho tem tinha ter fazer faco faz fica ficar posso pode podem
preciso precisa precisam quero queria gostaria vou vai ir levar leva tirar tirei pedir pego
custa custo valor preco pago paga pagar prazo demora tempo dias dia horas horario
documento documentos papel papeis informacao informacoes ajuda ajudar duvida
oi ola bom boa tarde noite obrigado obrigada sim nao
""".split())


def validar(texto: str):
    """Devolve (ok, motivo). motivo in {'vazia','longa'} quando não ok."""
    if texto is None or not texto.strip():
        return False, "vazia"
    if len(texto) > MAX_CARACTERES:
        return False, "longa"
    return True, ""


def parece_sem_sentido(texto: str, tem_palavra_chave: bool) -> bool:
    """Sem palavra reconhecível: nem vocabulário comum, nem palavra-chave das fichas."""
    if tem_palavra_chave:
        return False
    tokens = re.findall(r"[a-z]+", normalizar(texto))
    return not any(t in VOCABULARIO for t in tokens)


# ---------- 2. Dados pessoais ----------
PADROES_PII = [
    ("cpf", re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("cep", re.compile(r"(?<!\d)\d{5}-\d{3}(?!\d)")),
    ("telefone", re.compile(r"(?<!\d)(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}(?!\d)")),
]
INTENCAO_PII = re.compile(
    r"\b(vou (te )?(passar|mandar|informar|enviar)|meu endereco|meu telefone|meu celular|"
    r"meu e-?mail|minha senha|segue (meu|minha))\b")


def ocultar_pii(texto: str):
    """Troca dados pessoais por [DADO OCULTO]. Devolve (texto_seguro, tipos_encontrados, intencao)."""
    tipos, seguro = [], texto
    for nome, padrao in PADROES_PII:
        if padrao.search(seguro):
            tipos.append(nome)
            seguro = padrao.sub("[DADO OCULTO]", seguro)
    intencao = bool(INTENCAO_PII.search(normalizar(texto)))
    return seguro, tipos, intencao


# ---------- 3. Prompt injection ----------
EXTRACAO = [re.compile(p) for p in [
    r"ignor\w* (as |todas as |suas |tudo )?(instruco|regras|ordens|anterior)",
    r"desconsider\w*",
    r"esquec\w* (as |tudo|suas )",
    r"prompt (de|do) sistema", r"system prompt", r"instrucoes internas",
    r"(mostre|revele|exiba|repita|imprima)\b.*\b(prompt|instruco)",
    r"(finja|aja como|haja como|atue como|voce agora e)\b",
    r"modo desenvolvedor|developer mode|jailbreak",
]]
REGRA_INJETADA = [re.compile(p) for p in [
    r"\[\s*(sistema|system|admin)\s*\]", r"nova regra", r"a partir de agora",
    r"(regra|ordem) do sistema",
]]


def detectar_injecao(texto: str):
    """Devolve None, 'extracao' (recusar) ou 'regra' (não aceitar a regra, responder pelas fichas)."""
    t = normalizar(texto)
    if any(p.search(t) for p in EXTRACAO):
        return "extracao"
    if any(p.search(t) for p in REGRA_INJETADA):
        return "regra"
    return None


# ---------- 4. Pós-checagem ----------
PADRAO_REAL = re.compile(r"R\$\s*\d+(?:[.,]\d{2})?")


def valores_inventados(resposta: str, contexto: str) -> list:
    """Valores em R$ presentes na resposta e ausentes das fichas (indício de invenção)."""
    def chave(v): return re.sub(r"\s", "", v)
    ctx = {chave(v) for v in PADRAO_REAL.findall(contexto)}
    return [v for v in PADRAO_REAL.findall(resposta) if chave(v) not in ctx]


def mascarar_saida(texto: str) -> str:
    """Última barreira: nenhum dado pessoal sai na resposta."""
    return ocultar_pii(texto)[0]

"""Validações compartilhadas pelo terminal e pela interface web."""
from datetime import date, datetime

from .servico import ABRANGENCIAS, Servico

ID_MAXIMO = 999_999

# nome, rótulo, obrigatório, tamanho máximo
CAMPOS_FORM = (
    ("id", "ID", True, 6),
    ("titulo", "Título", True, 80),
    ("categoria", "Categoria", True, 40),
    ("descricao", "Descrição", True, 300),
    ("publico_alvo", "Público-alvo", True, 80),
    ("canal_local", "Canal ou local de atendimento", True, 100),
    ("referencia", "Referência (fonte da informação)", False, 120),
    ("ultima_verificacao", "Última verificação (AAAA-MM-DD)", False, 10),
    ("aviso", "Aviso de limitação", False, 120),
    ("abrangencia", "Abrangência (urbano, rural ou ambos)", False, 10),
)


def limpar_espacos(texto):
    """Tira espaços das pontas e junta espaços repetidos."""
    return " ".join((texto or "").split())


def validar_id(texto, lista, ignorar_duplicidade=False):
    """Devolve (id_inteiro, None) ou (None, mensagem de erro)."""
    texto = limpar_espacos(texto)
    if texto == "":
        return None, "Informe o ID."
    if not (texto.isascii() and texto.isdigit()):
        return None, "O ID deve ser um número inteiro positivo (ex.: 12)."
    valor = int(texto)
    if valor <= 0:
        return None, "O ID deve ser maior que zero."
    if valor > ID_MAXIMO:
        return None, f"O ID deve ter no máximo {ID_MAXIMO}."
    if not ignorar_duplicidade and lista.buscar_por_id(valor) is not None:
        return None, f"Já existe um serviço com o ID {valor}."
    return valor, None


def validar_campo(nome, texto, lista, ignorar_duplicidade=False):
    """Valida um campo. Devolve (valor_normalizado, None) ou (None, erro)."""
    if nome == "id":
        return validar_id(texto, lista, ignorar_duplicidade)
    rotulo, obrigatorio, limite = next(
        (r, o, l) for n, r, o, l in CAMPOS_FORM if n == nome)
    valor = limpar_espacos(texto)
    if valor == "":
        if obrigatorio:
            return None, f"O campo \"{rotulo}\" é obrigatório."
        if nome == "abrangencia":
            return "ambos", None
        return "", None
    if len(valor) > limite:
        return None, f"\"{rotulo}\" aceita no máximo {limite} caracteres."
    if nome == "ultima_verificacao":
        try:
            data = datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            return None, "Use a data no formato AAAA-MM-DD (ex.: 2026-11-10)."
        if data > date.today():
            return None, "A data de verificação não pode estar no futuro."
    if nome == "abrangencia":
        valor = valor.lower()
        if valor not in ABRANGENCIAS:
            return None, "Abrangência deve ser urbano, rural ou ambos."
    return valor, None


def validar_servico(dados, lista, id_fixo=None):
    """Valida o formulário completo (dict de textos).

    id_fixo: usado na edição; o id não é lido do formulário nem checado
    quanto à duplicidade. Devolve (Servico, {}) ou (None, {campo: erro}).
    """
    erros = {}
    valores = {}
    for nome, _rotulo, _obr, _lim in CAMPOS_FORM:
        if nome == "id" and id_fixo is not None:
            valores["id"] = id_fixo
            continue
        valor, erro = validar_campo(nome, dados.get(nome, ""), lista)
        if erro:
            erros[nome] = erro
        else:
            valores[nome] = valor
    if erros:
        return None, erros
    return Servico(**valores), {}


def validar_opcao(texto, minimo, maximo):
    """Opção numérica de menu. Devolve (opcao, None) ou (None, erro)."""
    texto = limpar_espacos(texto)
    if texto == "":
        return None, "Digite o número de uma opção."
    if not (texto.isascii() and texto.isdigit()):
        return None, f"Opção inválida: use um número de {minimo} a {maximo}."
    valor = int(texto)
    if valor < minimo or valor > maximo:
        return None, f"Opção inexistente: use um número de {minimo} a {maximo}."
    return valor, None


def validar_decimal(texto, minimo, maximo, descricao):
    """Número decimal (aceita vírgula). Devolve (valor, None) ou (None, erro)."""
    texto = limpar_espacos(texto).replace(",", ".")
    if texto == "":
        return None, f"Informe {descricao}."
    try:
        valor = float(texto)
    except ValueError:
        return None, f"Informe {descricao} como número (ex.: 1,5)."
    if valor != valor or valor in (float("inf"), float("-inf")):
        return None, f"Informe {descricao} como um número comum."
    if valor < minimo or valor > maximo:
        return None, f"Informe {descricao} entre {minimo:g} e {maximo:g}."
    return valor, None


def validar_hora(texto):
    """Hora inteira de 0 a 23. Devolve (hora, None) ou (None, erro)."""
    valor, erro = validar_decimal(texto, 0, 23, "a hora de início")
    if erro:
        return None, erro
    if valor != int(valor):
        return None, "Informe a hora de início como número inteiro de 0 a 23."
    return int(valor), None

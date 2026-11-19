"""Roteador por palavras-chave (sem IA): escolhe as fichas relevantes."""
import re
from .fichas import normalizar

# Peso 2 = termo específico do documento; peso 1 = termo genérico (aparece em várias fichas).
TERMOS = {
    "FC-01": {2: ["rg", "identidade", "posto de identificacao"], 1: ["segunda via", "2a via", "perdi", "roubaram", "roubo", "furto", "extravio"]},
    "FC-02": {2: ["cpf", "cadastro de pessoa fisica"], 1: ["inscricao", "inscrever", "regularizar", "correcao de dados", "comprovante"]},
    "FC-03": {2: ["titulo", "eleitor", "votar", "voto", "zona eleitoral", "eleic"], 1: ["transferencia"]},
    "FC-04": {2: ["carteira de trabalho", "ctps", "primeiro emprego"], 1: ["digital", "emprego", "trabalho"]},
    "FC-05": {2: ["certidao", "certidoes", "nascimento", "casamento", "obito", "cartorio"], 1: ["segunda via"]},
    "FC-06": {2: ["cnh", "habilitacao", "carteira de motorista", "dirigir", "renov", "exame medico"], 1: ["vencida", "venceu", "vencimento"]},
    "FC-07": {2: ["atend", "sabado", "domingo", "feriado", "horario", "libras", "interprete", "procuracao",
                  "terceiro", "pix", "pagamento", "prioritario", "gestante", "acessibilidade", "deficiencia", "agend"], 1: ["pagar", "pago", "guia"]},
}
GERAL = "FC-07"
LIMITACAO = re.compile(r"canal oficial|oficial da prefeitura|voce e (a |o )?prefeitura|e oficial")


def _casa(termo: str, texto: str) -> bool:
    return re.search(r"\b" + re.escape(termo) + r"\w*", texto) is not None


def pontuar(texto: str) -> dict:
    t = normalizar(texto)
    return {cod: sum(p for p, termos in pesos.items() for k in termos if _casa(k, t))
            for cod, pesos in TERMOS.items()}


def rotear(texto: str):
    """Devolve ('limitacao'|'fora_escopo'|'ok', [fichas])."""
    if LIMITACAO.search(normalizar(texto)):
        return "limitacao", []
    pontos = pontuar(texto)
    docs = {c: p for c, p in pontos.items() if c != GERAL and p > 0}
    if docs:
        melhor = max(docs.values())
        escolhidas = [c for c, p in sorted(docs.items(), key=lambda x: -x[1])
                      if p >= 0.7 * melhor][:2]
        return "ok", escolhidas + [GERAL]
    if pontos[GERAL] > 0:
        return "ok", [GERAL]
    return "fora_escopo", []


def tem_palavra_chave(texto: str) -> bool:
    return any(p > 0 for p in pontuar(texto).values())

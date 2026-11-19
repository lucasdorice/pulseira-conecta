"""Carregamento e organização das fichas (única fonte de verdade do assistente)."""
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

PASTA_FICHAS = Path(__file__).resolve().parents[2] / "fichas"
CAMPO = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")


def normalizar(texto: str) -> str:
    """minúsculas, sem acentos."""
    t = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


@dataclass
class Ficha:
    codigo: str
    titulo: str
    palavras_chave: list
    campos: dict = field(default_factory=dict)
    texto: str = ""
    versao: str = ""


def carregar_fichas(pasta) -> dict:
    """Lê FC-*.md e devolve {codigo: Ficha}."""
    fichas = {}
    for caminho in sorted(Path(pasta).glob("FC-*.md")):
        texto = caminho.read_text(encoding="utf-8")
        m = re.match(r"#\s*(FC-\d+)\s*—\s*(.+)", texto)
        if not m:
            continue
        campos, atual = {}, None
        for linha in texto.splitlines()[1:]:
            c = CAMPO.match(linha)
            if c:
                atual = c.group(1).strip().lower()
                campos[atual] = c.group(2).strip()
            elif atual and linha.strip():
                campos[atual] += "\n" + linha.strip()
        chaves = [k.strip() for k in campos.get("palavras-chave", "").split(",") if k.strip()]
        v = re.search(r"versão de (\d{2}/\d{2}/\d{4})", texto)
        fichas[m.group(1)] = Ficha(m.group(1), m.group(2).strip(), chaves, campos, texto,
                                   v.group(1) if v else "")
    return fichas


# ---------- Busca por trechos (melhoria v2) ----------
_STOP = set("""de da do das dos a o as os e em no na nos nas um uma para por com que eu meu minha me se ao aos ou
como qual quais quanto quando onde posso preciso pode tem ter fazer faco mais sobre esta esse essa""".split())


def _radicais(texto: str) -> set:
    """Radicais de 4 letras (perdi/perda -> 'perd'), ignorando palavras comuns."""
    toks = re.findall(r"[a-z0-9]+", normalizar(texto))
    return {t[:4] for t in toks if len(t) >= 4 and t not in _STOP}


def trechos_relevantes(pergunta: str, fichas: dict, codigos: list, n: int = 3) -> list:
    """Devolve até n pares (codigo, linha) das fichas escolhidas, mais parecidos com a pergunta."""
    rad, cand, ordem = _radicais(pergunta), [], 0
    for c in codigos:
        for linha in fichas[c].texto.splitlines():
            l = linha.strip()
            baixo = l.lower()
            if not l or l.startswith("#") or baixo.startswith(("**palavras-chave", "**fonte")):
                continue
            pontos = len(rad & _radicais(l))
            if pontos:
                cand.append((-pontos, ordem, c, l))
            ordem += 1
    return [(c, l) for _, _, c, l in sorted(cand)[:n]]

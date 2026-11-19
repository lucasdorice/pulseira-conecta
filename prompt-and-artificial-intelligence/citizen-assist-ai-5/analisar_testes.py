"""Calcula os 3 indicadores dos testes com usuários. Uso: python analisar_testes.py"""
import csv, re, statistics, sys
from pathlib import Path

PASTA = Path("results/usuarios")
ID_OK = re.compile(r"^P\d{2,}$")   # só códigos anônimos: P01, P02...


def ler(nome):
    with open(PASTA / nome, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for l in linhas:
        if not ID_OK.match(l["participante"].strip()):
            sys.exit(f"ERRO: '{l['participante']}' não é um código anônimo (use P01, P02...). Não registre nomes.")
    return linhas


def calcular(tempos, quest):
    for t in tempos:
        if t["tarefa"] not in ("T1", "T2", "T3") or t["acertou"] not in ("0", "1") or t["ajuda"] not in ("0", "1"):
            sys.exit(f"ERRO em tempos.csv (participante {t['participante']}, tarefa {t['tarefa']}): confira tarefa (T1-T3), acertou e ajuda (0/1).")
        t["_ok"] = t["acertou"] == "1" and t["ajuda"] == "0"
        t["_s"] = float(t["tempo_s"])
    for q in quest:
        for k in ("q1", "q2", "q3", "q4", "q5"):
            if q[k] not in ("1", "2", "3", "4", "5"):
                sys.exit(f"ERRO em questionario.csv (participante {q['participante']}, {k}): use notas de 1 a 5.")
    return tempos, quest


def relatorio(tempos, quest):
    pessoas = sorted({t["participante"] for t in tempos})
    out = ["# Indicadores dos testes com usuários", "",
           f"Participantes nos tempos: **{len(pessoas)}** · no questionário: **{len({q['participante'] for q in quest})}**"]
    if len(pessoas) < 5:
        out.append("\n> ATENÇÃO: o enunciado pede pelo menos 5 pessoas de fora do grupo.")
    ok = sum(t["_ok"] for t in tempos)
    segs = [t["_s"] for t in tempos]
    notas = [int(q[k]) for q in quest for k in ("q1", "q2", "q3", "q4", "q5")]
    out += ["", "| Indicador | Resultado |", "|---|---|",
            f"| Acerto das orientações | {100*ok/len(tempos):.0f}% ({ok}/{len(tempos)} tarefas) |",
            f"| Tempo para encontrar a informação | mediana {statistics.median(segs):.0f} s · média {statistics.mean(segs):.0f} s |",
            f"| Facilidade de utilização (1 a 5) | média {statistics.mean(notas):.2f} |",
            "", "## Por tarefa", "", "| Tarefa | Acertos | Tempo mediano (s) | Tempo médio (s) |", "|---|---|---|---|"]
    for tarefa in ("T1", "T2", "T3"):
        sub = [t for t in tempos if t["tarefa"] == tarefa]
        if sub:
            out.append(f"| {tarefa} | {sum(t['_ok'] for t in sub)}/{len(sub)} | {statistics.median(t['_s'] for t in sub):.0f} | {statistics.mean(t['_s'] for t in sub):.0f} |")
    out += ["", "## Caminho usado", ""]
    for c in ("menu", "livre"):
        out.append(f"- {c}: {sum(t['caminho'] == c for t in tempos)} tarefas")
    out += ["", "## Questionário (média por pergunta)", "", "| Pergunta | Média |", "|---|---|"]
    nomes = {"q1": "Fácil encontrar a informação", "q2": "Respostas claras", "q3": "Usou sem ajuda",
             "q4": "Texto fácil de ler", "q5": "Usaria de novo"}
    for k, n in nomes.items():
        out.append(f"| {n} | {statistics.mean(int(q[k]) for q in quest):.2f} |")
    return "\n".join(out)


if __name__ == "__main__":
    t, q = calcular(ler("tempos.csv"), ler("questionario.csv"))
    if not t or not q:
        sys.exit("Os CSV estão vazios. Preencha results/usuarios/tempos.csv e questionario.csv.")
    texto = relatorio(t, q)
    (PASTA / "indicadores.md").write_text(texto, encoding="utf-8")
    print(texto)

"""Roda o agente e o juiz nas 26 mensagens. Uso: python avaliar.py --rotulo antes"""
import argparse, csv, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from citizen_assist import guardrails as g
from citizen_assist import juiz as J


def executar(golden, agente_fn, juiz_fn):
    """agente_fn(mensagem) -> resposta; juiz_fn(sistema, usuario) -> texto."""
    linhas = []
    for item in golden:
        item = {**item, "mensagem_mascarada": g.ocultar_pii(item["mensagem"])[0]}  # o CPF de teste não vai ao juiz nem ao relatório
        t0 = time.time()
        print(f"[{item['id']:>2}/{len(golden)}] agente respondendo...", end=" ", flush=True)
        resposta = agente_fn(item["mensagem"])
        print(f"({time.time()-t0:.0f}s) juiz avaliando...", end=" ", flush=True)
        jz = J.julgar(item, resposta, juiz_fn)
        print(f"{jz['veredito']} (total {time.time()-t0:.0f}s)", flush=True)
        chk = J.checagens(item, resposta)
        linhas.append({
            "id": item["id"], "tipo": item["tipo"], "mensagem": item["mensagem_mascarada"],
            "resposta": resposta, **{c: jz[c] for c in J.CRITERIOS},
            "juiz": jz["veredito"], "justificativa": jz["justificativa"],
            **chk, "final": J.resultado_final(jz, chk),
        })
        ok_det = chk["termos_ok"] and chk["cita_ficha"] and not chk["pii_vazou"]
        linhas[-1]["revisar_manual"] = (linhas[-1]["final"] == "correto") != ok_det   # juiz e regras divergem
    return linhas


def resumo_md(linhas, rotulo):
    total = len(linhas)
    acertos = sum(l["final"] == "correto" for l in linhas)
    out = [f"# Resultado: {rotulo}", "", f"**Acerto final: {acertos}/{total} ({100*acertos/total:.0f}%)**", "",
           "| Tipo | Acertos |", "|---|---|"]
    for tipo in dict.fromkeys(l["tipo"] for l in linhas):
        sub = [l for l in linhas if l["tipo"] == tipo]
        out.append(f"| {tipo} | {sum(l['final']=='correto' for l in sub)}/{len(sub)} |")
    out += ["", "| # | Tipo | Juiz | Cita ficha | Termos | PII vazou | Final | Revisar | Justificativa do juiz |", "|---|---|---|---|---|---|---|---|---|"]
    for l in linhas:
        out.append(f"| {l['id']} | {l['tipo']} | {l['juiz']} | {l['cita_ficha']} | {l['termos_ok']} | {l['pii_vazou']} | **{l['final']}** | {'SIM' if l['revisar_manual'] else ''} | {l['justificativa']} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rotulo", default="antes", help="antes, antes_juiz2 ou depois")
    ap.add_argument("--reaproveitar", help="CSV com respostas já geradas: só roda o juiz (não chama o agente)")
    a = ap.parse_args()
    from citizen_assist.agente import construir_grafo, perguntar
    from citizen_assist.llm import gerar_ollama, MODELO_JUIZ
    golden = json.load(open("data/golden_dataset.json", encoding="utf-8"))
    if a.reaproveitar:
        antigas = {l["mensagem"]: l["resposta"] for l in csv.DictReader(open(a.reaproveitar, encoding="utf-8"))}
        agente = lambda m: antigas[g.ocultar_pii(m)[0]]
    else:
        grafo = construir_grafo()
        agente = lambda m: perguntar(grafo, m)
    linhas = executar(golden, agente,
                      lambda s, u: gerar_ollama(s, u, modelo=MODELO_JUIZ))
    Path("results").mkdir(exist_ok=True)
    with open(f"results/{a.rotulo}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)
    Path(f"results/{a.rotulo}.md").write_text(resumo_md(linhas, a.rotulo), encoding="utf-8")
    print(resumo_md(linhas, a.rotulo))


if __name__ == "__main__":
    main()

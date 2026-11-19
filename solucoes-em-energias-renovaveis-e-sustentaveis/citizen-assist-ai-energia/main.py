#!/usr/bin/env python3
"""Citizen Assist AI — módulo de Energia e Sustentabilidade (terminal).

Uso:
  python main.py                 modo interativo (pergunta o perfil da família)
  python main.py --demo          demonstração com a família de exemplo
  python main.py --perfil f.json usa um perfil salvo em JSON
  python main.py --relatorio     imprime o relatório de análise
  python main.py --relatorio-docs  grava docs/02_ANALISE_E_CALCULOS.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from energia.assistente import Assistente
from energia.dados import Item, Perfil, carregar_equipamentos, perfil_exemplo
from energia.relatorio import gerar_markdown

BANNER = ("=" * 66 + "\n  CITIZEN ASSIST AI · Energia e Sustentabilidade\n"
          "  Orientações com cálculo, fontes e limitações (estimativas)\n" + "=" * 66)

DEMO_PERGUNTAS = [
    "Onde eu gasto mais energia?",
    "E se eu tomar banho de 5 minutos?",
    "Vale a pena instalar energia solar?",
    "Comparar as alternativas",
    "Qual o impacto ambiental?",
    "Quais são as fontes e limitações?",
]


def perguntar(texto: str, padrao):
    r = input(f"{texto} [{padrao}]: ").strip()
    return r if r else str(padrao)


def sim_nao(texto: str, padrao: str = "s"):
    r = perguntar(texto + " (s/n/não sei)", padrao).lower()
    if r.startswith("n") and "sei" not in r:
        return False
    if "sei" in r:
        return None
    return True


def montar_perfil_interativo() -> Perfil:
    eqs = carregar_equipamentos()
    print("\nVamos montar o perfil da sua casa. Tecle ENTER para aceitar o valor entre [colchetes].\n")
    if perguntar("Usar a família de exemplo (4 pessoas)? (s/n)", "s").lower().startswith("s"):
        pf = perfil_exemplo()
    else:
        pf = Perfil(itens=[])
        pf.pessoas = int(perguntar("Quantas pessoas moram na casa?", 4))
        pf.minutos_banho = float(perguntar("Duração média do banho (min)?", 8).replace(",", "."))
        print("\nAparelhos disponíveis:", ", ".join(eqs))
        print("Digite um por linha no formato: id quantidade horas_por_dia dias_por_mes "
              "(ex.: tv_led 2 4 30). Linha vazia termina.")
        while True:
            lin = input("> ").strip()
            if not lin:
                break
            partes = lin.replace(",", ".").split()
            if partes[0] not in eqs or len(partes) < 3:
                print("  Formato ou id inválido.")
                continue
            pf.itens.append(Item(partes[0], int(float(partes[1])), float(partes[2]),
                                 int(float(partes[3])) if len(partes) > 3 else 30))
    t = perguntar("Tarifa da sua conta em R$/kWh (veja na fatura; ENTER usa o valor estimado)", "")
    if t:
        pf.tarifa_kwh = float(t.replace(",", "."))
    pf.padrao_ligacao = perguntar("Ligação (monofasico/bifasico/trifasico)?", pf.padrao_ligacao)
    pf.imovel_proprio = bool(sim_nao("O imóvel é próprio?", "s"))
    pf.telhado_adequado = sim_nao("Tem telhado com sol e espaço?", "s")
    return pf


def carregar_perfil_json(caminho: str) -> Perfil:
    with open(caminho, encoding="utf-8") as f:
        return Perfil.de_dict(json.load(f))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--perfil")
    ap.add_argument("--relatorio", action="store_true")
    ap.add_argument("--relatorio-docs", action="store_true")
    a = ap.parse_args(argv)

    perfil = carregar_perfil_json(a.perfil) if a.perfil else perfil_exemplo()

    if a.relatorio_docs:
        destino = Path(__file__).parent / "docs" / "02_ANALISE_E_CALCULOS.md"
        destino.write_text(gerar_markdown(perfil), encoding="utf-8")
        print(f"Relatório gravado em {destino}")
        return 0
    if a.relatorio:
        print(gerar_markdown(perfil))
        return 0

    print(BANNER)
    if a.demo:
        asst = Assistente(perfil)
        print(asst.resumo_perfil())
        for q in DEMO_PERGUNTAS:
            print(f"\nVocê> {q}\n")
            print(asst.responder(q))
        return 0

    if not a.perfil:
        perfil = montar_perfil_interativo()
    asst = Assistente(perfil)
    print("\n" + asst.resumo_perfil())
    print("\nPergunte o que quiser sobre sua energia. Digite 'ajuda' para exemplos e 'sair' para encerrar.\n")
    while True:
        try:
            q = input("Você> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if normalizar_saida(q):
            print("Até logo! Lembre-se: os valores são estimativas.")
            break
        print("\n" + asst.responder(q) + "\n")
    return 0


def normalizar_saida(q: str) -> bool:
    return q.lower() in {"sair", "exit", "quit", "tchau"}


if __name__ == "__main__":
    sys.exit(main())

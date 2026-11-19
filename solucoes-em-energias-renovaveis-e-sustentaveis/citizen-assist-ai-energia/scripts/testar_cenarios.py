"""Teste de cenários INTERNOS (não são usuários reais).

Roda perfis diferentes pelo assistente e verifica se as respostas são coerentes.
Uso: python scripts/testar_cenarios.py   (grava docs/07_TESTES_DE_CENARIOS.md)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from energia import alternativas as alt
from energia.assistente import Assistente
from energia.formatacao import num, rs
from energia.dados import Item, Perfil, perfil_exemplo

CENARIOS = [
    ("C1 Família de 4, imóvel próprio, telhado ok (perfil de exemplo)", perfil_exemplo()),
    ("C2 Família alugando (imóvel não próprio)",
     Perfil(pessoas=3, minutos_banho=10, imovel_proprio=False, itens=[Item("geladeira", 1, 24), Item("tv_led", 1, 5)])),
    ("C3 Casa pequena, consumo baixo (perto do custo de disponibilidade)",
     Perfil(pessoas=1, minutos_banho=6, padrao_ligacao="monofasico", itens=[Item("geladeira", 1, 24)])),
    ("C4 Telhado desconhecido, tarifa informada R$ 0,95",
     Perfil(pessoas=3, minutos_banho=10, telhado_adequado=None, tarifa_kwh=0.95,
            itens=[Item("geladeira", 1, 24), Item("lampada_incandescente_60w", 6, 4)])),
    ("C5 Casa grande, 6 pessoas, muito ar-condicionado, ligação trifásica",
     Perfil(pessoas=6, minutos_banho=12, padrao_ligacao="trifasico", telhado_adequado=True,
            itens=[Item("geladeira", 2, 24), Item("ar_condicionado", 3, 8, 25), Item("tv_led", 3, 5)])),
]
PERGUNTAS = ["Onde eu gasto mais energia?", "E se eu tomar banho de 5 minutos?",
             "Vale a pena instalar energia solar?", "Comparar as alternativas"]


def checar(perfil, asst):
    r = asst.res
    ok = []
    ok.append(("economias A, B e C não negativas", all(r[k].economia_rs_ano >= 0 for k in "ABC")))
    ok.append(("recomendação começa pela eficiência", "eficiência" in alt.recomendar(perfil, r)[0].lower()))
    if not perfil.imovel_proprio:
        ok.append(("imóvel alugado: B e C marcadas como inviáveis", r["B"].viavel is False and r["C"].viavel is False))
    if perfil.telhado_adequado is None and perfil.imovel_proprio and r["C"].detalhes["paineis"] > 0:
        ok.append(("telhado desconhecido: C marcada 'a confirmar'", r["C"].viavel is None))
    if r["C"].detalhes["paineis"] == 0:
        ok.append(("consumo baixo: não dimensiona solar", r["C"].viavel is False))
    ok.append(("toda resposta traz aviso de estimativa",
               all("Estimativa" in asst.responder(q) for q in PERGUNTAS)))
    return ok


def main():
    L = ["# Teste de Cenários (internos)\n",
         "> **Não são testes com usuários.** São cenários criados pelo grupo para verificar se o assistente "
         "responde de forma coerente em casos diferentes. Gerado por `python scripts/testar_cenarios.py`. "
         "Eles não substituem os testes com usuários (`docs/04_TESTES_COM_USUARIOS.md`).\n"]
    falhas = 0
    for nome, perfil in CENARIOS:
        a = Assistente(perfil)
        L.append(f"## {nome}\n")
        L.append(f"Consumo estimado: {num(a.consumo, 0)} kWh/mês; tarifa efetiva {rs(a.tarifa)}/kWh.\n")
        L.append("| Verificação | Resultado |\n|---|---|")
        for desc, passou in checar(perfil, a):
            falhas += 0 if passou else 1
            L.append(f"| {desc} | {'OK' if passou else 'FALHOU'} |")
        L.append("\n**Recomendação dada:**")
        L += [f"- {s}" for s in alt.recomendar(perfil, a.res)]
        L.append("")
    L.append(f"## Resumo\n\n{len(CENARIOS)} cenários, {falhas} falha(s).\n")
    out = Path(__file__).resolve().parent.parent / "docs" / "07_TESTES_DE_CENARIOS.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Gravado em {out} — {falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())

"""Exporta o diagrama do grafo (entregável: imagem da arquitetura)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from citizen_assist.agente import construir_grafo

g = construir_grafo(llm_fn=lambda s, u: "").get_graph()
Path("docs").mkdir(exist_ok=True)
Path("docs/grafo.mmd").write_text(g.draw_mermaid(), encoding="utf-8")
print("Salvo docs/grafo.mmd (abra em https://mermaid.live se precisar da imagem)")
try:
    Path("docs/grafo.png").write_bytes(g.draw_mermaid_png())   # usa mermaid.ink: precisa de internet
    print("Salvo docs/grafo.png")
except Exception as erro:
    print("PNG não gerado (precisa de internet):", type(erro).__name__)

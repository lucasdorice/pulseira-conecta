"""Interface de terminal: menu por categorias + pergunta livre. Uso só com teclado."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from citizen_assist.agente import construir_grafo, perguntar
from citizen_assist.textos import CATEGORIAS, MAX_CARACTERES


def mostrar(grafo, pergunta: str):
    print("\nPergunta:", pergunta[:MAX_CARACTERES] if len(pergunta) <= MAX_CARACTERES else "(mensagem longa)")
    print("\n" + perguntar(grafo, pergunta) + "\n")
    print("-" * 60)


def menu(grafo):
    print("\n=== Citizen Assist AI (protótipo educacional) ===")
    while True:
        print("\nEscolha um assunto digitando o número:")
        for i, (nome, _) in enumerate(CATEGORIAS, 1):
            print(f"  {i}. {nome}")
        print("  P. Digitar minha própria pergunta")
        print("  0. Sair")
        op = input("\nSua escolha: ").strip().lower()
        if op == "0":
            print("Até logo!")
            return
        if op == "p":
            mostrar(grafo, input("\nDigite sua pergunta: "))
        elif op.isdigit() and 1 <= int(op) <= len(CATEGORIAS):
            nome, perguntas = CATEGORIAS[int(op) - 1]
            print(f"\n{nome}. Perguntas comuns:")
            for j, q in enumerate(perguntas, 1):
                print(f"  {j}. {q}")
            sub = input("Número da pergunta (ou Enter para voltar): ").strip()
            if sub.isdigit() and 1 <= int(sub) <= len(perguntas):
                mostrar(grafo, perguntas[int(sub) - 1])
        else:
            print("\nOpção inválida. Digite um número do menu ou P.")


if __name__ == "__main__":
    menu(construir_grafo())

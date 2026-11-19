"""Citizen Assist AI - assistente de terminal para moradores de áreas de risco.

Como executar:  python main.py
Para conferir os requisitos da base:  python main.py --validar
"""

import os
import sys

from assistente import Assistente, EncerrarPrograma
from base_conhecimento import BaseConhecimento

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")

MENU = """
--- Menu principal ---
  1) Perguntar (texto livre)
  2) Navegar por categorias
  3) Ver indicadores
  4) Exportar atendimentos para CSV
  5) Verificar se um link parece oficial
  6) Modo didático (ver o cálculo da pontuação)
  0) Sair"""


def validar_base(base):
    """Imprime se a base cumpre os requisitos da atividade."""
    problemas = base.verificar_requisitos()
    print(f"Orientações válidas: {len(base.orientacoes)} | Categorias: {len(base.categorias())}")
    if problemas:
        print("Problemas encontrados:")
        for problema in problemas:
            print(f"  - {problema}")
    else:
        print("Base OK: todos os requisitos conferidos.")


def main():
    base = BaseConhecimento(CAMINHO_BASE)           # cria o objeto (ainda sem dados)
    base.carregar()                                  # lê o JSON e cria os objetos Orientacao

    if "--validar" in sys.argv:
        validar_base(base)
        return

    assistente = Assistente("Citizen Assist AI", base, CAMINHO_HISTORICO, CAMINHO_CSV)
    assistente.boas_vindas()

    if base.erro:
        print(f"\nAtenção: {base.erro}")
        print("O assistente abre mesmo assim, mas não vai conseguir responder dúvidas "
              "até a base ser corrigida.")
    elif base.ignoradas:
        print(f"\nAtenção: {len(base.ignoradas)} registro(s) inválido(s) foram ignorados "
              "(use python main.py --validar para ver quais).")

    try:
        while True:
            print(MENU)
            opcao = assistente.ler_numero("Escolha uma opção: ", 0, 6)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.mostrar_indicadores()
            elif opcao == 4:
                assistente.exportar_csv()
            elif opcao == 5:
                assistente.verificar_link()
            elif opcao == 6:
                assistente.modo_didatico()
            else:
                assistente.encerrar()
                assistente.mostrar_indicadores()
                print("\nObrigado por usar o assistente. Cuide-se!")
                return
    except EncerrarPrograma:
        # Ctrl+C ou fim da entrada: salva o que existe e sai sem mostrar erro
        assistente.encerrar(pedir_nota=False)
        print("\nAtendimento encerrado. Cuide-se!")


if __name__ == "__main__":
    main()

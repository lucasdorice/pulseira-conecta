"""Ponto de entrada: python main.py cli | python main.py web"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Citizen Assist AI - catálogo de serviços (DSA)")
    parser.add_argument("modo", choices=["cli", "web"],
                        help="cli = menu no terminal; web = interface no navegador")
    parser.add_argument("--vazio", action="store_true",
                        help="(cli) começar com a lista vazia, sem carregar dados")
    parser.add_argument("--porta", type=int, default=5000, help="(web) porta")
    args = parser.parse_args()

    if args.modo == "cli":
        import cli
        cli.executar(carregar=not args.vazio)
    else:
        from web.app import create_app
        app = create_app(caminho_dados=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "dados", "servicos.csv"))
        if not os.environ.get("CITIZEN_ADMIN_SENHA"):
            print("AVISO: usando a senha de demonstração 'demo123'. "
                  "Defina CITIZEN_ADMIN_SENHA para trocá-la.", file=sys.stderr)
        app.run(host="127.0.0.1", port=args.porta, debug=False)


if __name__ == "__main__":
    main()

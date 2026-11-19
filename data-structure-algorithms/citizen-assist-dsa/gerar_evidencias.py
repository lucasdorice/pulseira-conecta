"""Executa os cenários de teste e gera docs/RELATORIO_TESTES.md.

Cada cenário registra entrada, resultado esperado e resultado observado
(com a saída real do terminal ou da web). Uso: python gerar_evidencias.py
"""
import builtins
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from datetime import datetime

import cli
from citizen_assist.indicadores import Indicadores
from citizen_assist.lista import ListaEncadeada
from citizen_assist.servico import Servico
from web.app import create_app

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "docs", "RELATORIO_TESTES.md")

BASE = [(3, "Vacinação", "Saúde"), (1, "RG", "Documentos"),
        (5, "Matrícula", "Educação"), (2, "CadÚnico", "Assistência social"),
        (4, "Ouvidoria", "Atendimento comunitário")]


def lista_base():
    lista = ListaEncadeada()
    for id_, titulo, cat in BASE:
        lista.inserir(Servico(id_, titulo, cat, f"Descrição de {titulo}",
                              "Qualquer cidadão", "Balcão de atendimento",
                              ultima_verificacao="2026-11-01"))
    return lista


def entradas_servico(id_, titulo, cat):
    """Respostas para os 10 campos do cadastro (4 opcionais em branco)."""
    return [str(id_), titulo, cat, f"Descrição de {titulo}", "Qualquer cidadão",
            "Balcão de atendimento", "", "", "", ""]


def rodar_cli(entradas, lista, indic=None):
    """Roda o menu com entradas simuladas; devolve a saída (com eco das respostas)."""
    respostas = iter(entradas)
    buffer = io.StringIO()

    def entrada_falsa(prompt=""):
        try:
            resposta = next(respostas)
        except StopIteration:
            raise EOFError
        print(prompt + resposta)
        return resposta

    original = builtins.input
    builtins.input = entrada_falsa
    try:
        with contextlib.redirect_stdout(buffer):
            cli.executar(lista=lista, indic=indic or Indicadores(), carregar=False)
    finally:
        builtins.input = original
    texto = buffer.getvalue().replace(cli.MENU, "[... menu principal ...]")
    return texto.replace(cli.AVISO, "[aviso de protótipo não oficial]").strip()


def ids(lista):
    return [s.id for s in lista.percorrer()]


resultados = []


def registrar(codigo, nome, entrada, esperado, ok, saida):
    resultados.append((codigo, nome, entrada, esperado, ok, saida))
    print(("APROVADO " if ok else "REPROVADO"), codigo, nome)


def cenario_cli(codigo, nome, entradas, esperado, lista=None, nao_deve=(),
                verificar=None, descricao_entrada=None):
    lista = lista if lista is not None else ListaEncadeada()
    saida = rodar_cli(entradas, lista)
    ok = all(trecho in saida for trecho in esperado) and \
        not any(trecho in saida for trecho in nao_deve)
    extra = ""
    if verificar:
        ok_v, extra = verificar(lista)
        ok = ok and ok_v
        saida += f"\n\n[verificação no código] {extra}"
    registrar(codigo, nome, descricao_entrada or "\n".join(entradas),
              "\n".join(esperado) + (f"\n{verificar.__doc__}" if verificar else ""),
              ok, saida)


# ------------------------------------------------------------------ CLI
cenario_cli("T1", "Listar com lista vazia", ["3", "0"],
            ["Nenhum serviço cadastrado."])

cenario_cli("T2", "Consultar, atualizar, excluir, pesquisar e ordenar com lista vazia",
            ["2", "4", "5", "6", "7", "0"],
            ["Nenhum serviço cadastrado.",
             "Nenhum serviço cadastrado para atualizar.",
             "Nenhum serviço cadastrado para excluir.",
             "Nenhum serviço cadastrado para pesquisar.",
             "Nenhum serviço cadastrado para ordenar."])

entradas_t3 = ["1"] + entradas_servico(1, "Vacinação", "Saúde") + \
              ["1"] + entradas_servico(2, "RG", "Documentos") + \
              ["1"] + entradas_servico(3, "Matrícula", "Educação") + \
              ["1"] + entradas_servico(4, "CadÚnico", "Assistência social") + \
              ["1"] + entradas_servico(5, "Ouvidoria", "Atendimento comunitário") + \
              ["3", "0", "n"]
cenario_cli("T3", "Cadastrar 5 serviços válidos e listar", entradas_t3,
            ["Serviço 1 cadastrado com sucesso.", "Serviço 5 cadastrado com sucesso.",
             "Serviços cadastrados (5)", "Vacinação", "Ouvidoria"])

lista_t4 = ListaEncadeada()
cenario_cli("T4", "Cadastrar com ID duplicado",
            ["1"] + entradas_servico(1, "Vacinação", "Saúde") +
            ["1", "1", "2"] + entradas_servico(2, "RG", "Documentos")[1:] + ["3", "0", "n"],
            ["Já existe um serviço com o ID 1.", "Serviço 2 cadastrado com sucesso.",
             "Serviços cadastrados (2)"], lista=lista_t4)

cenario_cli("T5", "Cadastrar com campo obrigatório vazio",
            ["1", "1", "", "   ", "Título válido", "Cat", "Desc", "Todos", "Balcão",
             "", "", "", "", "0", "n"],
            ['O campo "Título" é obrigatório.', "Serviço 1 cadastrado com sucesso."])

cenario_cli("T6", "ID com letras, negativo, zero e acima do limite",
            ["1", "abc", "-5", "0", "9999999", "7", "T", "C", "D", "P", "L",
             "", "", "", "", "0", "n"],
            ["O ID deve ser um número inteiro positivo", "O ID deve ser maior que zero.",
             "O ID deve ter no máximo", "Serviço 7 cadastrado com sucesso."])

cenario_cli("T7", "Consultar ID existente e inexistente",
            ["2", "3", "2", "99", "0"],
            ["Título: Vacinação", "Serviço com ID 99 não encontrado."],
            lista=lista_base())

lista_t8 = lista_base()
cenario_cli("T8", "Atualizar o título do serviço 3",
            ["4", "3", "Vacinação infantil"] + [""] * 8 + ["2", "3", "0", "n"],
            ["Serviço 3 atualizado.", "Título: Vacinação infantil"],
            lista=lista_t8)

lista_t9 = lista_base()


def verificar_t9(lista):
    """Lista final contém os IDs [1, 2] e `fim` aponta para o ID 2"""
    ok = ids(lista) == [1, 2] and lista.fim.dados.id == 2 and len(lista) == 2
    return ok, f"IDs = {ids(lista)}, fim = {lista.fim.dados.id}, tamanho = {len(lista)}"


cenario_cli("T9", "Excluir primeiro (3), meio (5) e último (4) nós",
            ["5", "3", "s", "5", "5", "s", "5", "4", "s", "3", "0", "n"],
            ["Serviço 3 excluído.", "Serviço 5 excluído.", "Serviço 4 excluído.",
             "Serviços cadastrados (2)"], lista=lista_t9, verificar=verificar_t9)

cenario_cli("T9b", "Excluir e cancelar a confirmação",
            ["5", "1", "n", "3", "0"],
            ["Exclusão cancelada.", "Serviços cadastrados (5)"], lista=lista_base())

cenario_cli("T10", "Pesquisar com resultado e sem resultado",
            ["6", "1", "VACINA", "6", "3", "balcão", "6", "1", "zzzz", "6", "1", "", "xyz", "0"],
            ["Vacinação", "Nenhum serviço encontrado para essa pesquisa.",
             "Digite pelo menos uma letra para pesquisar."], lista=lista_base())

lista_t11 = lista_base()


def verificar_t11(lista):
    """Ao final a lista está em ordem decrescente de ID: [5, 4, 3, 2, 1]"""
    ok = ids(lista) == [5, 4, 3, 2, 1]
    return ok, f"IDs = {ids(lista)}"


cenario_cli("T11", "Ordenar por título (merge sort) e por ID decrescente (insertion sort)",
            ["7", "1", "1", "1", "7", "2", "2", "2", "0", "n"],
            ["Serviços ordenados por titulo", "Serviços ordenados por id"],
            lista=lista_t11, verificar=verificar_t11)

cenario_cli("T12", "Opções de menu inválidas",
            ["x", "", "99", "-1", "0"],
            ["Opção inválida: use um número de 0 a 10.", "Digite o número de uma opção.",
             "Opção inexistente: use um número de 0 a 10."])

# T13: salvar, sair, reabrir e carregar
tmp = tempfile.mkdtemp()
cli.CAMINHO_CSV = os.path.join(tmp, "servicos.csv")
s1 = rodar_cli(["8", "1", "0"], lista_base())
s2 = rodar_cli(["3", "8", "2", "s", "3", "0"], ListaEncadeada())
s1 = s1.replace(cli.CAMINHO_CSV, os.path.join("dados", "servicos.csv"))
ok13 = ("Dados salvos" in s1 and "5 serviço(s) carregado(s)." in s2
        and "Serviços cadastrados (5)" in s2 and "Nenhum serviço cadastrado." in s2)
registrar("T13", "Salvar, sair, reabrir e carregar",
          "Sessão 1: 8, 1, 0 (salvar e sair)\nSessão 2 (lista vazia): 3, 8, 2, s, 3, 0",
          "Dados salvos; sessão 2 começa vazia e, após carregar, lista 5 serviços",
          ok13, "--- Sessão 1 ---\n" + s1 + "\n\n--- Sessão 2 ---\n" + s2)

# ------------------------------------------------------------ energia (CLI)
from citizen_assist.persistencia import carregar_csv  # noqa: E402


def lista_com_catalogo():
    lista = ListaEncadeada()
    carregar_csv(lista, os.path.join(RAIZ, "dados", "servicos_exemplo.csv"))
    return lista


cenario_cli("T18", "Energia: matriz energética ordenada, com total de renováveis",
            ["10", "1", "0", "0"],
            ["Matriz energética (do maior para o menor)", "Hidrelétrica",
             "Total de fontes renováveis: 84.0%", "valores ilustrativos"])

cenario_cli("T19", "Energia: consumo, ranking e demanda de 2 aparelhos (valores sugeridos)",
            ["10", "2", "1", "", "", "", "2", "", "", "", "", "1", "0", "0"],
            ["Consumo estimado: 171.0 kWh por mês", "1. Chuveiro elétrico: 99.0 kWh/mês (58%)",
             "2. Geladeira (potência média ao longo do dia): 72.0 kWh/mês (42%)",
             "Pico de demanda: 3.40 kW às 06h", "Custo estimado", "Não é garantia"])

cenario_cli("T20", "Energia: entradas inválidas na escolha de aparelhos",
            ["10", "2", "99", "abc", "1", "abc", "5500", "25", "0,5", "30", "6", "", "", "0", "0"],
            ["O aparelho 99 não está na lista.", "O ID deve ser um número inteiro positivo",
             "Informe a potência como número", "Informe as horas de uso entre 0 e 24.",
             "Informe a hora de início entre 0 e 23.", "Consumo estimado: 82.5 kWh por mês"])

cenario_cli("T21", "Energia: nenhum aparelho escolhido",
            ["10", "2", "", "0", "0"], ["Nenhum aparelho escolhido."])

cenario_cli("T22", "Energia: orientações da categoria Energia no catálogo",
            ["10", "3", "0", "0"],
            ["Orientações de energia (5)", "Bandeiras tarifárias", "Energia solar em casa"],
            lista=lista_com_catalogo())

# T14: suíte automatizada
proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header"],
                      cwd=RAIZ, capture_output=True, text=True,
                      encoding="utf-8", errors="replace")
linhas = [l for l in proc.stdout.strip().splitlines() if l.strip()]
registrar("T14", "Suíte automatizada (pytest)", "python -m pytest -q",
          "Todos os testes passam", proc.returncode == 0, "\n".join(linhas[-3:]))

# ------------------------------------------------------------------ Web
TOKEN = "t"
app = create_app(lista=lista_base(), senha="s3nha", indicadores=Indicadores(),
                 carregar=False)
c = app.test_client()
with c.session_transaction() as sess:
    sess["_csrf"] = TOKEN
r_login = c.post("/login", data={"senha": "s3nha", "_csrf": TOKEN})
form = {"id": "10", "titulo": "Assistência técnica rural", "categoria": "Rural",
        "descricao": "Orientação a pequenos produtores", "publico_alvo": "Agricultores",
        "canal_local": "Escritório local", "referencia": "", "ultima_verificacao": "",
        "aviso": "", "abrangencia": "rural", "_csrf": TOKEN}
r_novo = c.post("/admin/novo", data=form)
r_busca = c.get("/?q=rural")
r_ord = c.get("/servicos?ordem=titulo&sentido=asc")
html_ord = r_ord.get_data(as_text=True)
ok15 = (r_login.status_code == 302 and r_novo.status_code == 302
        and "Assistência técnica rural" in r_busca.get_data(as_text=True)
        and html_ord.index("Assistência") < html_ord.index("Vacinação"))
registrar("T15", "Web: entrar, cadastrar, pesquisar e ordenar",
          "POST /login; POST /admin/novo; GET /?q=rural; GET /servicos?ordem=titulo",
          "Login 302, cadastro 302, busca acha o serviço novo, ordenação A-Z correta",
          ok15, f"login={r_login.status_code} cadastro={r_novo.status_code} "
                f"busca={r_busca.status_code} ordenar={r_ord.status_code}\n"
                f"IDs na lista após cadastro: {ids(app.config['LISTA'])}")

r_vazio = c.post("/admin/novo", data=dict(form, titulo=""))
r_dup = c.post("/admin/novo", data=dict(form, id="3"))
r_404 = c.get("/servicos/999")
ok16 = (r_vazio.status_code == 422 and "obrigatório" in r_vazio.get_data(as_text=True)
        and r_dup.status_code == 422 and "Já existe" in r_dup.get_data(as_text=True)
        and r_404.status_code == 404)
registrar("T16", "Web: campo vazio, ID duplicado e ID inexistente",
          "POST /admin/novo (título vazio); POST /admin/novo (id=3); GET /servicos/999",
          "422 com mensagem de campo obrigatório; 422 com mensagem de ID duplicado; 404 amigável",
          ok16, f"título vazio={r_vazio.status_code}; id duplicado={r_dup.status_code}; "
                f"id inexistente={r_404.status_code}")

anonimo = create_app(lista=lista_base(), senha="s3nha", indicadores=Indicadores(),
                     carregar=False).test_client()
rotas_admin = ["/admin/novo", "/admin/3/editar", "/admin/3/excluir", "/indicadores"]
codigos = {rota: anonimo.get(rota) for rota in rotas_admin}
publico = anonimo.get("/").status_code
ok17 = all(r.status_code == 302 and "/login" in r.headers["Location"]
           for r in codigos.values()) and publico == 200
registrar("T17", "Web: acessar páginas de administrador sem entrar",
          "GET " + ", ".join(rotas_admin) + " sem login; GET /",
          "Redireciona para /login (302); páginas públicas continuam abertas (200)",
          ok17, "\n".join(f"{k} -> {v.status_code} {v.headers['Location']}"
                          for k, v in codigos.items()) + f"\n/ -> {publico}")

# ------------------------------------------------------------ energia (web)
app_e = create_app(indicadores=Indicadores())
ce = app_e.test_client()
with ce.session_transaction() as sess:
    sess["_csrf"] = TOKEN
r_get = ce.get("/energia")
h_get = r_get.get_data(as_text=True)
r_calc = ce.post("/energia", data={
    "_csrf": TOKEN, "usar_1": "1", "pot_1": "5000", "horas_1": "0,5", "ini_1": "6",
    "usar_2": "1", "pot_2": "100", "horas_2": "24", "ini_2": "0", "tarifa": "1"})
h_calc = r_calc.get_data(as_text=True)
ok23 = (r_get.status_code == 200 and "Hidrelétrica" in h_get and "Dado de exemplo" in h_get
        and r_calc.status_code == 200 and "147.0 kWh por mês" in h_calc
        and "Pico de demanda" in h_calc and "Quem mais consome" in h_calc)
registrar("T23", "Web: página /energia (matriz) e cálculo de consumo e demanda",
          "GET /energia; POST /energia (chuveiro 5000 W, 0,5 h, 6h; geladeira 100 W, 24 h; tarifa 1)",
          "200 com matriz e aviso de dado de exemplo; 147,0 kWh/mês; pico e ranking exibidos",
          ok23, f"GET={r_get.status_code}; POST={r_calc.status_code}\n"
                f"Consumo na página: {'147.0 kWh por mês' in h_calc}; "
                f"ranking: {'Quem mais consome' in h_calc}; pico: {'Pico de demanda' in h_calc}")
r_e1 = ce.post("/energia", data={"_csrf": TOKEN, "usar_1": "1", "pot_1": "abc",
                                 "horas_1": "30", "ini_1": "25"})
r_e2 = ce.post("/energia", data={"_csrf": TOKEN})
ok24 = (r_e1.status_code == 422 and "Corrija antes de calcular" in r_e1.get_data(as_text=True)
        and r_e2.status_code == 422 and "pelo menos um aparelho" in r_e2.get_data(as_text=True))
registrar("T24", "Web: energia com dados inválidos e sem aparelho marcado",
          "POST /energia (potência 'abc', horas 30, hora 25); POST /energia sem aparelho",
          "422 com mensagens; 422 pedindo ao menos um aparelho",
          ok24, f"dados inválidos={r_e1.status_code}; sem aparelho={r_e2.status_code}")

# ------------------------------------------------------------ relatório
aprovados = sum(1 for r in resultados if r[4])
linhas = [
    "# Relatório de testes e evidências",
    "",
    f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `python gerar_evidencias.py`.",
    f"Resultado: **{aprovados} de {len(resultados)} cenários aprovados**.",
    "",
    "Os cenários de terminal usam a lista de exemplo (5 serviços: IDs 3, 1, 5, 2, 4) "
    "ou lista vazia, conforme indicado. Cada bloco mostra a entrada digitada, o "
    "esperado, o observado e a saída real do programa. Os cenários T1 e T2 cobrem "
    "operações sobre lista vazia.",
    "",
    "| Cenário | Resultado |", "|---|---|",
]
for cod, nome, _e, _x, ok, _s in resultados:
    linhas.append(f"| {cod} · {nome} | {'Aprovado' if ok else 'REPROVADO'} |")
for cod, nome, entrada, esperado, ok, saida in resultados:
    linhas += ["", f"## {cod} · {nome}", "", "**Entrada**", "", "```", entrada, "```", "",
               "**Resultado esperado**", "", "```", esperado, "```", "",
               f"**Resultado observado:** {'Aprovado' if ok else 'REPROVADO'}", "",
               "**Saída**", "", "```", saida, "```"]
with open(SAIDA, "w", encoding="utf-8") as arq:
    arq.write("\n".join(linhas) + "\n")
print(f"\n{aprovados}/{len(resultados)} cenários aprovados. Relatório em {SAIDA}")
sys.exit(0 if aprovados == len(resultados) else 1)

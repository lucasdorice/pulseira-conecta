"""Menu interativo no terminal do Citizen Assist AI."""
import os
import time

from citizen_assist.algoritmos import (benchmark, insertion_sort, merge_sort,
                                       merge_sort_por, pesquisar)
from citizen_assist.energia.aparelho import (Aparelho, consumo_total_mensal,
                                             ranking_por_consumo)
from citizen_assist.energia.dados import carregar_dados_energia
from citizen_assist.energia.demanda import curva_demanda, fator_de_carga, pico
from citizen_assist.energia.fonte import (tem_dado_de_exemplo,
                                          total_renovaveis)
from citizen_assist.indicadores import (Indicadores, contar_categorias,
                                        contar_desatualizados)
from citizen_assist.lista import ListaEncadeada
from citizen_assist.persistencia import (carregar_csv, carregar_inicial,
                                         exportar_json, salvar_csv)
from citizen_assist.servico import Servico
from citizen_assist.validacao import (CAMPOS_FORM, validar_campo,
                                      validar_decimal, validar_hora,
                                      validar_id, validar_opcao,
                                      validar_servico)

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
CAMINHO_CSV = os.path.join(PASTA_DADOS, "servicos.csv")
CAMINHO_JSON = os.path.join(PASTA_DADOS, "servicos.json")

AVISO = ("Protótipo educativo com dados fictícios. Não é canal oficial.\n"
         "Confirme sempre a informação no órgão responsável.")

MENU = """
=== CITIZEN ASSIST AI - Catálogo de Serviços ===
1. Cadastrar serviço
2. Consultar por ID
3. Listar todos
4. Atualizar serviço
5. Excluir serviço
6. Pesquisar (título, categoria ou texto)
7. Ordenar (título ou ID)
8. Salvar, carregar ou exportar dados
9. Relatórios e indicadores
10. Energia (matriz, consumo e demanda)
0. Sair"""


# ------------------------------------------------------------ entrada
def ler(prompt):
    """input() que devolve None se o usuário digitar /cancelar."""
    texto = input(prompt)
    if texto.strip().lower() == "/cancelar":
        return None
    return texto


def perguntar_opcao(titulo, opcoes):
    """Mostra um submenu numerado e devolve a opção (ou None se cancelar)."""
    while True:
        print(titulo)
        for numero, rotulo in opcoes:
            print(f"  {numero}. {rotulo}")
        texto = ler("Escolha (ou /cancelar): ")
        if texto is None:
            return None
        opcao, erro = validar_opcao(texto, opcoes[0][0], opcoes[-1][0])
        if erro:
            print(erro)
            continue
        return opcao


def perguntar_sim_nao(pergunta):
    while True:
        texto = input(f"{pergunta} (s/n): ").strip().lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        print("Resposta inválida: digite s para sim ou n para não.")


def perguntar_id_existente(lista):
    """Pede um id válido que exista na lista. Devolve o Servico ou None."""
    while True:
        texto = ler("ID do serviço (ou /cancelar): ")
        if texto is None:
            return None
        valor, erro = validar_id(texto, lista, ignorar_duplicidade=True)
        if erro:
            print(erro)
            continue
        servico = lista.buscar_por_id(valor)
        if servico is None:
            print(f"Serviço com ID {valor} não encontrado.")
            return None
        return servico


# ------------------------------------------------------------ saída
def mostrar_servico(s):
    print("-" * 60)
    print(f"ID: {s.id}")
    print(f"Título: {s.titulo}")
    print(f"Categoria: {s.categoria}")
    print(f"Descrição: {s.descricao}")
    print(f"Público-alvo: {s.publico_alvo}")
    print(f"Canal/local: {s.canal_local}")
    print(f"Abrangência: {s.abrangencia}")
    print(f"Referência: {s.referencia or '(não informada)'}")
    print(f"Aviso: {s.aviso or '(nenhum)'}")
    status = s.status_verificacao()
    if status == "sem_data":
        print("Verificação: sem data. Confirme a informação no órgão responsável.")
    elif status == "desatualizado":
        print(f"Verificação: ATENÇÃO, última em {s.ultima_verificacao} "
              f"({s.dias_desde_verificacao()} dias). Pode estar desatualizado.")
    else:
        print(f"Verificação: última em {s.ultima_verificacao}")
    print("-" * 60)


def mostrar_lista(lista, titulo):
    if lista.esta_vazia():
        print("Nenhum serviço encontrado.")
        return
    print(f"\n{titulo} ({len(lista)})")
    for s in lista.percorrer():
        marca = "" if s.status_verificacao() == "ok" else "  [verificar atualização]"
        print(f"[{s.id:>3}] {s.titulo} - {s.categoria}{marca}")


# ------------------------------------------------------------ operações
def cadastrar(lista, estado):
    print("\nCadastro de serviço (digite /cancelar para voltar)")
    valores = {}
    for nome, rotulo, obrigatorio, _lim in CAMPOS_FORM:
        while True:
            texto = ler(f"{rotulo}{'' if obrigatorio else ' (opcional)'}: ")
            if texto is None:
                print("Cadastro cancelado.")
                return
            valor, erro = validar_campo(nome, texto, lista)
            if erro:
                print(erro)
                continue
            valores[nome] = valor
            break
    servico = Servico(**valores)
    lista.inserir(servico)
    estado["alterado"] = True
    print(f"Serviço {servico.id} cadastrado com sucesso.")


def consultar(lista):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado.")
        return
    servico = perguntar_id_existente(lista)
    if servico is not None:
        mostrar_servico(servico)


def listar(lista):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado.")
        return
    mostrar_lista(lista, "Serviços cadastrados")


def atualizar(lista, estado):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado para atualizar.")
        return
    atual = perguntar_id_existente(lista)
    if atual is None:
        return
    mostrar_servico(atual)
    print("Pressione Enter para manter o valor atual; use - para limpar um campo opcional.")
    dados = atual.para_dict()
    for nome, rotulo, obrigatorio, _lim in CAMPOS_FORM:
        if nome == "id":
            continue
        while True:
            texto = ler(f"{rotulo} [{dados[nome]}]: ")
            if texto is None:
                print("Atualização cancelada.")
                return
            if texto.strip() == "":
                break
            if texto.strip() == "-" and not obrigatorio:
                dados[nome] = ""
                break
            valor, erro = validar_campo(nome, texto, lista)
            if erro:
                print(erro)
                continue
            dados[nome] = valor
            break
    novo, erros = validar_servico(dados, lista, id_fixo=atual.id)
    if erros:
        print("Não foi possível atualizar: " + "; ".join(erros.values()))
        return
    lista.atualizar(atual.id, novo)
    estado["alterado"] = True
    print(f"Serviço {atual.id} atualizado.")


def excluir(lista, estado):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado para excluir.")
        return
    servico = perguntar_id_existente(lista)
    if servico is None:
        return
    mostrar_servico(servico)
    if perguntar_sim_nao("Excluir este serviço?"):
        lista.remover(servico.id)
        estado["alterado"] = True
        print(f"Serviço {servico.id} excluído.")
    else:
        print("Exclusão cancelada.")


def pesquisar_servicos(lista, indic):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado para pesquisar.")
        return
    campo = perguntar_opcao("Pesquisar em:", [
        (1, "Título"), (2, "Categoria"), (3, "Título, categoria e descrição")])
    if campo is None:
        return
    nome_campo = {1: "titulo", 2: "categoria", 3: "todos"}[campo]
    while True:
        termo = ler("Termo de pesquisa (ou /cancelar): ")
        if termo is None:
            return
        if termo.strip() == "":
            print("Digite pelo menos uma letra para pesquisar.")
            continue
        break
    inicio = time.perf_counter()
    resultado = pesquisar(lista, termo, nome_campo)
    duracao = time.perf_counter() - inicio
    indic.registrar_busca(duracao, len(resultado))
    if resultado.esta_vazia():
        print("Nenhum serviço encontrado para essa pesquisa.")
    else:
        mostrar_lista(resultado, "Resultados da pesquisa")
    print(f"(busca feita em {duracao * 1000:.3f} ms)")


def ordenar(lista, estado):
    if lista.esta_vazia():
        print("Nenhum serviço cadastrado para ordenar.")
        return
    criterio = perguntar_opcao("Ordenar por:", [(1, "Título"), (2, "ID")])
    if criterio is None:
        return
    sentido = perguntar_opcao("Sentido:", [(1, "Crescente"), (2, "Decrescente")])
    if sentido is None:
        return
    algoritmo = perguntar_opcao("Algoritmo:", [
        (1, "Merge sort (O(n log n))"), (2, "Insertion sort (O(n²))")])
    if algoritmo is None:
        return
    nome = "titulo" if criterio == 1 else "id"
    funcao = merge_sort if algoritmo == 1 else insertion_sort
    inicio = time.perf_counter()
    funcao(lista, nome, decrescente=(sentido == 2))
    duracao = time.perf_counter() - inicio
    estado["alterado"] = True
    mostrar_lista(lista, f"Serviços ordenados por {nome}")
    print(f"(ordenação feita em {duracao * 1000:.3f} ms)")


def dados(lista, estado):
    opcao = perguntar_opcao("Dados:", [
        (1, "Salvar em CSV"), (2, "Carregar do CSV (substitui a lista)"),
        (3, "Exportar JSON")])
    if opcao == 1:
        salvar_csv(lista, CAMINHO_CSV)
        estado["alterado"] = False
        print(f"Dados salvos em {CAMINHO_CSV}")
    elif opcao == 2:
        if not os.path.exists(CAMINHO_CSV):
            print("Ainda não existe arquivo salvo. Use a opção 1 antes.")
            return
        if not perguntar_sim_nao("Isso substitui os dados atuais. Continuar?"):
            print("Carregamento cancelado.")
            return
        aceitos, erros = carregar_csv(lista, CAMINHO_CSV)
        estado["alterado"] = False
        print(f"{aceitos} serviço(s) carregado(s).")
        for erro in erros:
            print(erro)
    elif opcao == 3:
        exportar_json(lista, CAMINHO_JSON)
        print(f"JSON exportado em {CAMINHO_JSON}")


def relatorios(lista, indic):
    print("\n--- Relatórios e indicadores ---")
    print(f"Total de serviços: {len(lista)}")
    for categoria, quantidade in contar_categorias(lista).items():
        print(f"  {categoria}: {quantidade}")
    print(f"Serviços para verificar (mais de 180 dias ou sem data): "
          f"{contar_desatualizados(lista)}")
    r = indic.resumo()
    print(f"Buscas nesta sessão: {r['buscas']} "
          f"(com resultado: {r['taxa_resultado']}%, "
          f"tempo médio {r['tempo_medio_ms']} ms)")
    if perguntar_sim_nao("Rodar benchmark de ordenação (n = 500, 1000, 2000)?"):
        print(f"{'n':>6} {'merge (ms)':>12} {'insertion (ms)':>16}")
        for linha in benchmark([500, 1000, 2000]):
            print(f"{linha['n']:>6} {linha['merge_ms']:>12} "
                  f"{linha['insertion_ms']:>16}")


# ------------------------------------------------------------ energia
def perguntar_numero(prompt, padrao, validar):
    """Pergunta um número; Enter mantém o padrão. None = cancelar."""
    while True:
        texto = ler(prompt)
        if texto is None:
            return None
        if texto.strip() == "":
            return padrao
        valor, erro = validar(texto)
        if erro:
            print(erro)
            continue
        return valor


def mostrar_matriz(fontes):
    if fontes.esta_vazia():
        print("Nenhuma fonte de energia carregada.")
        return
    ordenada = fontes.copiar()
    merge_sort_por(ordenada, lambda f: f.participacao, decrescente=True)
    print("\nMatriz energética (do maior para o menor)")
    for f in ordenada.percorrer():
        tipo = "renovável" if f.tipo == "renovavel" else "não renovável"
        print(f"  {f.nome:<24} {f.participacao:>5.1f}%  {tipo}")
    print(f"Total de fontes renováveis: {total_renovaveis(fontes):.1f}%")
    if tem_dado_de_exemplo(fontes):
        print("ATENÇÃO: valores ilustrativos (dado de exemplo). "
              "Substitua pelos dados oficiais da EPE antes de usar.")


def mostrar_catalogo_aparelhos(catalogo):
    print("\nAparelhos disponíveis (valores sugeridos, editáveis)")
    for a in catalogo.percorrer():
        print(f"  {a.id}. {a.nome} - {a.potencia_w:g} W, "
              f"{a.horas_dia:g} h/dia, liga às {a.hora_inicio}h")


def meus_aparelhos(catalogo):
    if catalogo.esta_vazia():
        print("Nenhum aparelho disponível.")
        return
    mostrar_catalogo_aparelhos(catalogo)
    inventario = ListaEncadeada()
    print("\nEscolha os aparelhos da sua casa (Enter sem número para calcular; "
          "/cancelar para voltar).")
    while True:
        texto = ler("Número do aparelho: ")
        if texto is None:
            return
        if texto.strip() == "":
            break
        valor, erro = validar_id(texto, catalogo, ignorar_duplicidade=True)
        if erro:
            print(erro)
            continue
        item = catalogo.buscar_por_id(valor)
        if item is None:
            print(f"O aparelho {valor} não está na lista.")
            continue
        if inventario.buscar_por_id(valor) is not None:
            print("Esse aparelho já foi incluído.")
            continue
        potencia = perguntar_numero(
            f"Potência em watts [{item.potencia_w:g}]: ", item.potencia_w,
            lambda t: validar_decimal(t, 1, 20000, "a potência"))
        if potencia is None:
            return
        horas = perguntar_numero(
            f"Horas de uso por dia [{item.horas_dia:g}]: ", item.horas_dia,
            lambda t: validar_decimal(t, 0, 24, "as horas de uso"))
        if horas is None:
            return
        inicio = perguntar_numero(
            f"Hora em que liga, de 0 a 23 [{item.hora_inicio}]: ",
            item.hora_inicio, validar_hora)
        if inicio is None:
            return
        inventario.inserir_fim_sem_verificar(Aparelho(
            item.id, item.nome, potencia, horas, inicio, item.origem,
            item.situacao))
        print(f"{item.nome} incluído.")
    if inventario.esta_vazia():
        print("Nenhum aparelho escolhido.")
        return
    tarifa = perguntar_numero(
        "Tarifa da sua conta em reais por kWh (Enter para pular): ", None,
        lambda t: validar_decimal(t, 0.01, 10, "a tarifa"))
    mostrar_resultado_energia(inventario, tarifa)


def mostrar_resultado_energia(inventario, tarifa):
    total = consumo_total_mensal(inventario)
    ranking = ranking_por_consumo(inventario)
    curva = curva_demanda(inventario)
    maior, hora_maior = pico(curva)
    print(f"\nConsumo estimado: {total:.1f} kWh por mês")
    if tarifa is not None:
        print(f"Custo estimado (sem impostos e bandeira extras): "
              f"{total * tarifa:.2f} reais por mês")
    print("\nQuem mais consome:")
    for posicao, a in enumerate(ranking.percorrer(), start=1):
        kwh = a.consumo_mensal_kwh()
        parte = kwh / total * 100 if total else 0
        print(f"  {posicao}. {a.nome}: {kwh:.1f} kWh/mês ({parte:.0f}%)")
    print("\nDemanda ao longo do dia (kW):")
    for hora in range(24):
        barras = "#" * int(round(curva[hora] / maior * 30)) if maior else ""
        print(f"  {hora:02d}h {curva[hora]:5.2f} {barras}")
    print(f"Pico de demanda: {maior:.2f} kW às {hora_maior:02d}h")
    print(f"Fator de carga: {fator_de_carga(curva):.2f} "
          "(1 = consumo constante; perto de 0 = consumo concentrado em poucas horas)")
    if any(a.situacao != "oficial" for a in inventario.percorrer()):
        print("ATENÇÃO: potências sugeridas são dados de exemplo; confira no "
              "rótulo do aparelho ou nas tabelas do Procel/INMETRO.")
    print("Estimativa com os dados informados. Não é garantia de consumo "
          "nem de economia.")


def energia(lista, fontes, catalogo):
    while True:
        opcao = perguntar_opcao("\nEnergia:", [
            (0, "Voltar"), (1, "Matriz energética"),
            (2, "Meus aparelhos: consumo e demanda"),
            (3, "Orientações de energia do catálogo")])
        if opcao is None or opcao == 0:
            return
        if opcao == 1:
            mostrar_matriz(fontes)
        elif opcao == 2:
            meus_aparelhos(catalogo)
        elif opcao == 3:
            resultado = pesquisar(lista, "Energia", "categoria")
            mostrar_lista(resultado, "Orientações de energia")


# ------------------------------------------------------------ principal
def executar(lista=None, indic=None, carregar=True):
    lista = lista if lista is not None else ListaEncadeada()
    indic = indic if indic is not None else Indicadores()
    estado = {"alterado": False}
    fontes, catalogo, _erros_energia = carregar_dados_energia(PASTA_DADOS)
    if carregar and lista.esta_vazia():
        aceitos, erros = carregar_inicial(lista, PASTA_DADOS)
        if aceitos:
            print(f"{aceitos} serviço(s) carregado(s) dos dados de exemplo.")
        for erro in erros:
            print(erro)
    print("\n" + AVISO)
    try:
        _laco_principal(lista, indic, estado, fontes, catalogo)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada encerrada. Até logo!")


def _laco_principal(lista, indic, estado, fontes, catalogo):
    while True:
        print(MENU)
        texto = input("Escolha uma opção: ")
        opcao, erro = validar_opcao(texto, 0, 10)
        if erro:
            print(erro)
            continue
        if opcao == 0:
            if estado["alterado"] and perguntar_sim_nao(
                    "Há alterações não salvas. Salvar antes de sair?"):
                salvar_csv(lista, CAMINHO_CSV)
                print("Dados salvos.")
            print("Até logo!")
            break
        if opcao == 1:
            cadastrar(lista, estado)
        elif opcao == 2:
            consultar(lista)
        elif opcao == 3:
            listar(lista)
        elif opcao == 4:
            atualizar(lista, estado)
        elif opcao == 5:
            excluir(lista, estado)
        elif opcao == 6:
            pesquisar_servicos(lista, indic)
        elif opcao == 7:
            ordenar(lista, estado)
        elif opcao == 8:
            dados(lista, estado)
        elif opcao == 9:
            relatorios(lista, indic)
        elif opcao == 10:
            energia(lista, fontes, catalogo)

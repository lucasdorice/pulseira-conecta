"""Interface web (Flask) sobre a mesma ListaEncadeada do terminal."""
import os
import secrets
import threading
import time
from functools import wraps

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)

from citizen_assist.algoritmos import (benchmark, merge_sort, merge_sort_por,
                                       pesquisar)
from citizen_assist.energia.aparelho import (Aparelho, consumo_total_mensal,
                                             ranking_por_consumo)
from citizen_assist.energia.dados import carregar_dados_energia
from citizen_assist.energia.demanda import curva_demanda, fator_de_carga, pico
from citizen_assist.energia.fonte import tem_dado_de_exemplo, total_renovaveis
from citizen_assist.indicadores import (Indicadores, contar_categorias,
                                        contar_desatualizados)
from citizen_assist.lista import ListaEncadeada
from citizen_assist.persistencia import (carregar_inicial, lista_para_dicts,
                                         salvar_csv)
from citizen_assist.validacao import (CAMPOS_FORM, limpar_espacos,
                                      validar_decimal, validar_hora,
                                      validar_servico)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
TAMANHOS_BENCHMARK = (200, 500, 1000, 2000)


def create_app(lista=None, caminho_dados=None, senha=None, indicadores=None,
               carregar=True, fontes=None, catalogo=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("CITIZEN_SECRET_KEY") or secrets.token_hex(32)
    app.json.ensure_ascii = False
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    caminho_css = os.path.join(app.static_folder, "style.css")
    senha = senha or os.environ.get("CITIZEN_ADMIN_SENHA") or "demo123"

    lista = lista if lista is not None else ListaEncadeada()
    if carregar and lista.esta_vazia():
        carregar_inicial(lista, PASTA_DADOS)
    indic = indicadores or Indicadores(
        os.path.join(PASTA_DADOS, "indicadores.csv") if caminho_dados else None)
    trava = threading.Lock()
    if fontes is None or catalogo is None:
        fontes_csv, catalogo_csv, _erros = carregar_dados_energia(PASTA_DADOS)
        fontes = fontes if fontes is not None else fontes_csv
        catalogo = catalogo if catalogo is not None else catalogo_csv

    def persistir():
        if caminho_dados:
            salvar_csv(lista, caminho_dados)

    # ---------------------------------------------------- segurança básica
    def token_csrf():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = token_csrf

    @app.before_request
    def checar_csrf():
        if request.method == "POST":
            enviado = request.form.get("_csrf", "")
            if not secrets.compare_digest(enviado, session.get("_csrf", "")):
                abort(400)

    @app.after_request
    def cabecalhos(resposta):
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; frame-ancestors 'none'")
        return resposta

    def admin_required(funcao):
        @wraps(funcao)
        def envoltorio(*args, **kwargs):
            if not session.get("admin"):
                flash("Entre como administrador para continuar.", "aviso")
                return redirect(url_for("login", proximo=request.path))
            return funcao(*args, **kwargs)
        return envoltorio

    @app.context_processor
    def contexto():
        versao = int(os.path.getmtime(caminho_css)) if os.path.exists(caminho_css) else 0
        return {"admin": bool(session.get("admin")), "total": len(lista),
                "css_versao": versao}

    # ---------------------------------------------------------- cidadão
    @app.route("/")
    def index():
        q = limpar_espacos(request.args.get("q", ""))
        categoria = limpar_espacos(request.args.get("categoria", ""))
        resultados = None
        if q or categoria:
            inicio = time.perf_counter()
            base = lista
            if categoria:
                base = pesquisar(base, categoria, "categoria")
            if q:
                base = pesquisar(base, q, "todos")
            indic.registrar_busca(time.perf_counter() - inicio, len(base))
            resultados = base
        return render_template("index.html", q=q, categoria=categoria,
                               resultados=resultados,
                               categorias=contar_categorias(lista))

    @app.route("/servicos")
    def servicos():
        ordem = request.args.get("ordem", "titulo")
        sentido = request.args.get("sentido", "asc")
        if ordem not in ("titulo", "id"):
            ordem = "titulo"
        copia = lista.copiar()
        merge_sort(copia, ordem, decrescente=(sentido == "desc"))
        return render_template("lista.html", servicos=copia, ordem=ordem,
                               sentido="desc" if sentido == "desc" else "asc")

    @app.route("/servicos/<int:id_>")
    def detalhe(id_):
        servico = lista.buscar_por_id(id_)
        if servico is None:
            abort(404)
        return render_template("detalhe.html", s=servico)

    # ------------------------------------------------------------ energia
    def grafico_demanda(curva):
        """Barras do gráfico em SVG (coordenadas já calculadas)."""
        maior, hora_maior = pico(curva)
        barras = []
        for hora in range(24):
            altura = (curva[hora] / maior * 140) if maior else 0
            barras.append({"hora": hora, "kw": round(curva[hora], 2),
                           "x": 36 + hora * 19, "largura": 15,
                           "y": 160 - altura, "altura": altura,
                           "pico": hora == hora_maior and maior > 0})
        return barras

    @app.route("/energia", methods=["GET", "POST"])
    def energia():
        fontes_ord = fontes.copiar()
        merge_sort_por(fontes_ord, lambda f: f.participacao, decrescente=True)
        orientacoes = pesquisar(lista, "Energia", "categoria")
        valores = {}
        for item in catalogo.percorrer():
            valores[item.id] = {"usar": False, "pot": f"{item.potencia_w:g}",
                                "horas": f"{item.horas_dia:g}",
                                "ini": str(item.hora_inicio)}
        erros, resultado, tarifa_txt = {}, None, ""
        status = 200
        if request.method == "POST":
            inventario = ListaEncadeada()
            tarifa_txt = request.form.get("tarifa", "").strip()
            for item in catalogo.percorrer():
                i = item.id
                valores[i] = {"usar": bool(request.form.get(f"usar_{i}")),
                              "pot": request.form.get(f"pot_{i}", ""),
                              "horas": request.form.get(f"horas_{i}", ""),
                              "ini": request.form.get(f"ini_{i}", "")}
                if not valores[i]["usar"]:
                    continue
                pot, e1 = validar_decimal(valores[i]["pot"], 1, 20000,
                                          "a potência")
                horas, e2 = validar_decimal(valores[i]["horas"], 0, 24,
                                            "as horas de uso")
                ini, e3 = validar_hora(valores[i]["ini"])
                problema = e1 or e2 or e3
                if problema:
                    erros[i] = f"{item.nome}: {problema}"
                else:
                    inventario.inserir_fim_sem_verificar(Aparelho(
                        i, item.nome, pot, horas, ini, item.origem,
                        item.situacao))
            tarifa = None
            if tarifa_txt:
                tarifa, erro_t = validar_decimal(tarifa_txt, 0.01, 10, "a tarifa")
                if erro_t:
                    erros["tarifa"] = erro_t
            if not erros and inventario.esta_vazia():
                erros["geral"] = "Marque pelo menos um aparelho."
            if erros:
                status = 422
            else:
                total = consumo_total_mensal(inventario)
                curva = curva_demanda(inventario)
                maior, hora_maior = pico(curva)
                resultado = {
                    "total": total, "ranking": ranking_por_consumo(inventario),
                    "custo": total * tarifa if tarifa else None,
                    "pico": maior, "hora_pico": hora_maior,
                    "fator": fator_de_carga(curva), "curva": curva,
                    "barras": grafico_demanda(curva),
                    "exemplo": any(a.situacao != "oficial"
                                   for a in inventario.percorrer())}
        return render_template(
            "energia.html", fontes=fontes_ord,
            renovaveis=total_renovaveis(fontes),
            fontes_exemplo=tem_dado_de_exemplo(fontes),
            catalogo=catalogo, valores=valores, erros=erros,
            resultado=resultado, tarifa=tarifa_txt,
            orientacoes=orientacoes), status

    # --------------------------------------------------------- acesso
    @app.route("/login", methods=["GET", "POST"])
    def login():
        proximo = request.values.get("proximo", "")
        if not (proximo.startswith("/") and not proximo.startswith("//")):
            proximo = url_for("admin_inicio")
        if request.method == "POST":
            if secrets.compare_digest(request.form.get("senha", ""), senha):
                session["admin"] = True
                flash("Você entrou como administrador.", "ok")
                return redirect(proximo)
            flash("Senha incorreta. Tente novamente.", "erro")
            return render_template("login.html", proximo=proximo), 401
        return render_template("login.html", proximo=proximo)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("admin", None)
        flash("Você saiu do modo administrador.", "ok")
        return redirect(url_for("index"))

    # ----------------------------------------------------- administrador
    @app.route("/admin")
    @admin_required
    def admin_inicio():
        return redirect(url_for("servicos"))

    @app.route("/admin/novo", methods=["GET", "POST"])
    @admin_required
    def novo():
        if request.method == "POST":
            dados = {n: request.form.get(n, "") for n, *_ in CAMPOS_FORM}
            with trava:
                servico, erros = validar_servico(dados, lista)
                if not erros:
                    lista.inserir(servico)
                    persistir()
            if erros:
                return render_template("form.html", campos=CAMPOS_FORM,
                                       valores=dados, erros=erros,
                                       titulo="Cadastrar serviço",
                                       editando=False), 422
            flash(f"Serviço {servico.id} cadastrado.", "ok")
            return redirect(url_for("detalhe", id_=servico.id))
        return render_template("form.html", campos=CAMPOS_FORM, valores={},
                               erros={}, titulo="Cadastrar serviço",
                               editando=False)

    @app.route("/admin/<int:id_>/editar", methods=["GET", "POST"])
    @admin_required
    def editar(id_):
        atual = lista.buscar_por_id(id_)
        if atual is None:
            abort(404)
        if request.method == "POST":
            dados = {n: request.form.get(n, "") for n, *_ in CAMPOS_FORM}
            dados["id"] = str(id_)
            with trava:
                novo_s, erros = validar_servico(dados, lista, id_fixo=id_)
                if not erros:
                    lista.atualizar(id_, novo_s)
                    persistir()
            if erros:
                return render_template("form.html", campos=CAMPOS_FORM,
                                       valores=dados, erros=erros,
                                       titulo=f"Atualizar serviço {id_}",
                                       editando=True), 422
            flash(f"Serviço {id_} atualizado.", "ok")
            return redirect(url_for("detalhe", id_=id_))
        valores = {k: str(v) for k, v in atual.para_dict().items()}
        return render_template("form.html", campos=CAMPOS_FORM, valores=valores,
                               erros={}, titulo=f"Atualizar serviço {id_}",
                               editando=True)

    @app.route("/admin/<int:id_>/excluir", methods=["GET", "POST"])
    @admin_required
    def excluir(id_):
        servico = lista.buscar_por_id(id_)
        if servico is None:
            abort(404)
        if request.method == "POST":
            with trava:
                lista.remover(id_)
                persistir()
            flash(f"Serviço {id_} excluído.", "ok")
            return redirect(url_for("servicos"))
        return render_template("excluir.html", s=servico)

    @app.route("/indicadores", methods=["GET", "POST"])
    @admin_required
    def indicadores_pagina():
        linhas = None
        if request.method == "POST":
            try:
                n = int(request.form.get("n", ""))
            except ValueError:
                n = 0
            if n not in TAMANHOS_BENCHMARK:
                flash("Escolha um dos tamanhos da lista.", "erro")
            else:
                linhas = benchmark([n])
        return render_template(
            "indicadores.html", resumo=indic.resumo(),
            categorias=contar_categorias(lista),
            desatualizados=contar_desatualizados(lista),
            tamanhos=TAMANHOS_BENCHMARK, linhas=linhas)

    # --------------------------------------------------------------- API
    @app.route("/api/servicos")
    def api_servicos():
        return jsonify(lista_para_dicts(lista))

    @app.route("/api/servicos/<int:id_>")
    def api_servico(id_):
        servico = lista.buscar_por_id(id_)
        if servico is None:
            return jsonify({"erro": f"Serviço {id_} não encontrado."}), 404
        return jsonify(servico.para_dict())

    # ------------------------------------------------------------- erros
    @app.errorhandler(404)
    def nao_encontrado(_e):
        return render_template(
            "erro.html", titulo="Página não encontrada",
            texto="Esse serviço ou página não existe. Volte ao início "
                  "e tente uma nova busca."), 404

    @app.errorhandler(400)
    def requisicao_invalida(_e):
        return render_template(
            "erro.html", titulo="Pedido inválido",
            texto="A sessão expirou ou o formulário é inválido. "
                  "Volte e envie de novo."), 400

    app.config["LISTA"] = lista
    app.config["INDICADORES"] = indic
    return app

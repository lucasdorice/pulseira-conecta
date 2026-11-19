import pytest

from citizen_assist.indicadores import Indicadores
from citizen_assist.lista import ListaEncadeada
from web.app import create_app
from tests.conftest import fazer

TOKEN = "teste"
FORM = {"id": "10", "titulo": "Novo serviço", "categoria": "Teste",
        "descricao": "Descrição", "publico_alvo": "Todos",
        "canal_local": "Balcão", "referencia": "", "ultima_verificacao": "",
        "aviso": "", "abrangencia": "ambos", "_csrf": TOKEN}


@pytest.fixture
def cliente(lista_cinco):
    app = create_app(lista=lista_cinco, senha="s3nha", indicadores=Indicadores(),
                     carregar=False)
    app.config["TESTING"] = True
    c = app.test_client()
    with c.session_transaction() as s:
        s["_csrf"] = TOKEN
    return c


@pytest.fixture
def admin(cliente):
    with cliente.session_transaction() as s:
        s["admin"] = True
    return cliente


def test_paginas_publicas(cliente):
    assert cliente.get("/").status_code == 200
    r = cliente.get("/?q=vacina")
    assert r.status_code == 200 and "Vacinação" in r.get_data(as_text=True)
    assert "Nenhum serviço encontrado" in cliente.get("/?q=zzz").get_data(as_text=True)
    assert cliente.get("/servicos/3").status_code == 200
    assert "Não é canal oficial" in cliente.get("/").get_data(as_text=True)


def test_ordenacao_na_web(cliente):
    html = cliente.get("/servicos?ordem=id&sentido=desc").get_data(as_text=True)
    assert html.index("Matrícula") < html.index("RG")


def test_404_amigavel_e_api(cliente):
    assert cliente.get("/servicos/999").status_code == 404
    r = cliente.get("/api/servicos")
    assert len(r.get_json()) == 5
    assert cliente.get("/api/servicos/999").status_code == 404
    assert cliente.get("/api/servicos/3").get_json()["titulo"] == "Vacinação"


def test_admin_exige_login(cliente):
    for rota in ["/admin/novo", "/admin/3/editar", "/admin/3/excluir", "/indicadores"]:
        r = cliente.get(rota)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    r = cliente.post("/admin/novo", data=FORM)
    assert r.status_code == 302 and len(cliente.application.config["LISTA"]) == 5


def test_login_senha_errada_e_certa(cliente):
    r = cliente.post("/login", data={"senha": "errada", "_csrf": TOKEN})
    assert r.status_code == 401
    r = cliente.post("/login", data={"senha": "s3nha", "_csrf": TOKEN,
                                     "proximo": "/admin/novo"})
    assert r.status_code == 302 and r.headers["Location"].endswith("/admin/novo")


def test_login_nao_redireciona_para_fora(cliente):
    r = cliente.post("/login", data={"senha": "s3nha", "_csrf": TOKEN,
                                     "proximo": "//malicioso.com"})
    assert "malicioso" not in r.headers["Location"]


def test_cadastrar(admin):
    r = admin.post("/admin/novo", data=FORM)
    assert r.status_code == 302
    assert admin.application.config["LISTA"].buscar_por_id(10).titulo == "Novo serviço"


def test_cadastrar_erros(admin):
    r = admin.post("/admin/novo", data=dict(FORM, titulo="", id="3"))
    html = r.get_data(as_text=True)
    assert r.status_code == 422 and "obrigatório" in html and "Já existe" in html
    assert len(admin.application.config["LISTA"]) == 5


def test_editar_e_excluir(admin):
    r = admin.post("/admin/3/editar", data=dict(FORM, titulo="Vacina atualizada"))
    assert r.status_code == 302
    lista = admin.application.config["LISTA"]
    assert lista.buscar_por_id(3).titulo == "Vacina atualizada"
    assert admin.get("/admin/3/excluir").status_code == 200
    assert admin.post("/admin/3/excluir", data={"_csrf": TOKEN}).status_code == 302
    assert lista.buscar_por_id(3) is None and len(lista) == 4
    assert admin.get("/admin/3/editar").status_code == 404


def test_csrf_obrigatorio(admin):
    r = admin.post("/admin/novo", data=dict(FORM, _csrf="falso"))
    assert r.status_code == 400


def test_escapa_html(admin):
    admin.post("/admin/novo", data=dict(FORM, titulo="<script>alert(1)</script>"))
    html = admin.get("/servicos/10").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_indicadores_e_benchmark(admin):
    admin.get("/?q=rg")
    html = admin.get("/indicadores").get_data(as_text=True)
    assert "Buscas feitas" in html
    r = admin.post("/indicadores", data={"n": "200", "_csrf": TOKEN})
    assert "Merge sort (ms)" in r.get_data(as_text=True)
    r = admin.post("/indicadores", data={"n": "99999999", "_csrf": TOKEN})
    assert "Escolha um dos tamanhos" in r.get_data(as_text=True)


def test_lista_vazia_na_web():
    app = create_app(lista=ListaEncadeada(), indicadores=Indicadores(), carregar=False)
    c = app.test_client()
    assert "Nenhum serviço cadastrado" in c.get("/servicos").get_data(as_text=True)
    assert c.get("/api/servicos").get_json() == []

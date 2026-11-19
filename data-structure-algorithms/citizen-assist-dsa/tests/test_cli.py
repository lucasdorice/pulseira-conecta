import builtins

import cli
from citizen_assist.indicadores import Indicadores
from citizen_assist.lista import ListaEncadeada


def rodar(monkeypatch, entradas):
    it = iter(entradas)

    def falsa(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    monkeypatch.setattr(builtins, "input", falsa)
    cli.executar(lista=ListaEncadeada(), indic=Indicadores(), carregar=False)


def test_fim_da_entrada_no_menu(monkeypatch, capsys):
    rodar(monkeypatch, [])
    assert "Até logo" in capsys.readouterr().out


def test_fim_da_entrada_no_meio_do_cadastro(monkeypatch, capsys):
    rodar(monkeypatch, ["1", "5", "Titulo"])
    assert "Até logo" in capsys.readouterr().out


def test_ctrl_c_encerra_sem_erro(monkeypatch, capsys):
    def interrompe(prompt=""):
        raise KeyboardInterrupt
    monkeypatch.setattr(builtins, "input", interrompe)
    cli.executar(lista=ListaEncadeada(), indic=Indicadores(), carregar=False)
    assert "Até logo" in capsys.readouterr().out


def test_sair_normal(monkeypatch, capsys):
    rodar(monkeypatch, ["0"])
    assert "Até logo!" in capsys.readouterr().out

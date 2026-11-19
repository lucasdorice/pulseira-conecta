import json
from pathlib import Path
from citizen_assist import juiz as J

GOLDEN = json.load(open(Path(__file__).resolve().parents[1] / "data" / "golden_dataset.json", encoding="utf-8"))


def item(i):
    it = dict(GOLDEN[i - 1]); it["mensagem_mascarada"] = it["mensagem"]; return it


def test_golden_tem_26_mensagens_exatas():
    assert len(GOLDEN) == 26 and GOLDEN[0]["mensagem"] == "Quanto custa a segunda via do RG?"


def test_extrair_json_com_texto_ao_redor():
    assert J.extrair_json('claro! {"a": true} fim') == {"a": True}
    assert J.extrair_json("sem json") is None


def test_veredito_calculado_pelo_codigo():
    ok = lambda s, u: '{"pontos_esperados":true,"sem_invencao":true,"fonte_citada":true,"seguranca_ok":true,"justificativa":"ok"}'
    ruim = lambda s, u: '{"pontos_esperados":true,"sem_invencao":false,"fonte_citada":true,"seguranca_ok":true,"justificativa":"inventou"}'
    assert J.julgar(item(1), "x", ok)["veredito"] == "correto"
    assert J.julgar(item(1), "x", ruim)["veredito"] == "incorreto"


def test_juiz_invalido_vira_erro_juiz():
    assert J.julgar(item(1), "x", lambda s, u: "lixo")["veredito"] == "erro_juiz"


def test_checagens_e_final():
    c = J.checagens(item(1), "Custa R$ 38,00.\nFonte: FC-01")
    assert c == {"cita_ficha": True, "termos_ok": True, "pii_vazou": False}
    c2 = J.checagens(item(22), "Seu CPF 123.456.789-09 ...")
    assert c2["pii_vazou"]
    juiz_ok = {"veredito": "correto"}
    assert J.resultado_final(juiz_ok, c2) == "incorreto"          # vazar CPF é eliminatório
    assert J.resultado_final(juiz_ok, J.checagens(item(1), "R$ 38,00")) == "incorreto"   # sem citar ficha

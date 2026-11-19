"""
Etapa 5 - Questão 07: geração do relatório estatístico (PDF)
Lê base_dados.csv, resultados/*.json e figuras/*.png produzidos pelos scripts 01 a 04.
Executar na ordem: 00, 01, 02, 03, 04 e, por fim, este arquivo.
Requer: reportlab, pandas, matplotlib, pillow.
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table,
                                TableStyle, Image, KeepTogether)

AZUL, LARANJA, CINZA = colors.HexColor("#1f3b73"), colors.HexColor("#e07a1f"), colors.HexColor("#f2f4f8")
df = pd.read_csv("base_dados.csv")
J = {k: json.load(open(f"resultados/{k}.json", encoding="utf-8")) for k in ["q2_q3", "q4", "q5", "q6"]}
q23, q4, q5, q6 = J["q2_q3"], J["q4"], J["q5"], J["q6"]

def f(x, d=2):
    """Formata número no padrão brasileiro."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
def pv(p): return "< 0,001" if p < 0.001 else f(p, 3)

# ---- Figura descritiva por região ------------------------------------------------
reg = df.groupby("REGIAO")[["RDPC", "ANOSEST", "ESPVIDA", "GINI"]].mean()
reg = reg.loc[["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]]
alta = (df["RDPC"] > df["RDPC"].median()).groupby(df["REGIAO"]).mean().loc[reg.index]
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for a, col, tit, cor in [(ax[0], "RDPC", "Renda per capita média (R$)", "#1f3b73"),
                         (ax[1], "ANOSEST", "Anos de estudo (média)", "#e07a1f"),
                         (ax[2], "ESPVIDA", "Esperança de vida (média, anos)", "#2e8b57")]:
    a.bar(reg.index, reg[col], color=cor)
    a.set_title(tit, fontsize=10); a.tick_params(axis="x", rotation=35, labelsize=8)
    if col != "RDPC": a.set_ylim(reg[col].min() * 0.9, reg[col].max() * 1.03)
fig.suptitle("Médias por região (UFs, 2012-2021)")
fig.tight_layout(); fig.savefig("figuras/descritiva_regiao.png", dpi=150); plt.close(fig)

# ---- Estilos ----------------------------------------------------------------------
ss = getSampleStyleSheet()
corpo = ParagraphStyle("corpo", parent=ss["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15, textColor=AZUL, spaceBefore=10, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, textColor=AZUL, spaceBefore=8, spaceAfter=4)
leg = ParagraphStyle("leg", parent=corpo, fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
cel = ParagraphStyle("cel", parent=corpo, fontSize=8.5, leading=11, alignment=0, spaceAfter=0)
celb = ParagraphStyle("celb", parent=cel, textColor=colors.white, fontName="Helvetica-Bold")
bullet = ParagraphStyle("bullet", parent=corpo, leftIndent=14, bulletIndent=2, spaceAfter=3)
P = lambda t, s=corpo: Paragraph(t, s)
B = lambda t: Paragraph(t, bullet, bulletText="-")

def img(path, largura=15.5 * cm, legenda=None):
    w, h = PILImage.open(path).size
    el = [Image(path, width=largura, height=largura * h / w)]
    if legenda: el.append(P(legenda, leg))
    return KeepTogether(el + [Spacer(1, 6)])

def tabela(dados, larguras=None, cabecalho=True):
    t = [[Paragraph(str(c), celb if (i == 0 and cabecalho) else cel) for c in linha]
         for i, linha in enumerate(dados)]
    tb = Table(t, colWidths=larguras, repeatRows=1 if cabecalho else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c0d0")),
           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA])]
    if cabecalho: est.append(("BACKGROUND", (0, 0), (-1, 0), AZUL))
    tb.setStyle(TableStyle(est))
    return KeepTogether([tb, Spacer(1, 8)])

def rodape(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(2 * cm, 1.2 * cm, "Global Solution FIAP 2026 - CitizenTech | Relatório estatístico")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {d.page}"); c.restoreState()

S = []
# ---- Capa --------------------------------------------------------------------------
S += [Spacer(1, 3.5 * cm),
      Paragraph("Relatório Estatístico", ParagraphStyle("t", parent=ss["Title"], fontSize=28, textColor=AZUL)),
      Paragraph("Educação, saúde e renda nas UFs brasileiras como base para priorizar a implantação da Pulseira NFC Cidadã",
                ParagraphStyle("st", parent=ss["Title"], fontSize=14, leading=19, textColor=LARANJA)),
      Spacer(1, 1.2 * cm),
      P("Global Solution FIAP 2026 - Tema CitizenTech<br/>Ciência da Computação - FIAP", ParagraphStyle("c", parent=corpo, alignment=TA_CENTER, fontSize=11)),
      Spacer(1, 1 * cm),
      tabela([["Integrante", "RM"], ["Arthur Primo Brandão", "573572"],
              ["Leandro Cavaccini Brito", "570556"], ["Lucas Dorice dos Santos", "568692"]],
             [9 * cm, 4 * cm]),
      Spacer(1, 1.5 * cm),
      P("Base de dados: Atlas do Desenvolvimento Humano no Brasil (PNUD, Ipea e Fundação João Pinheiro), 27 UFs, 2012 a 2021 (270 observações). "
        "Análises em Python (pandas, numpy, scipy, matplotlib, seaborn).", ParagraphStyle("c2", parent=leg, fontSize=9)),
      PageBreak()]

# ---- 1. Resumo executivo ---------------------------------------------------------
r = q6["completa"]
S += [P("1. Resumo executivo", h1),
      P("O projeto <b>Pulseira NFC Cidadã</b> propõe uma pulseira de silicone com chip NFC, ligada a um aplicativo, que reúne documentos, "
        "saldo de transporte e rastreio consentido para pessoas com deficiência, idosos e suas redes de apoio. Antes de decidir <i>onde</i> "
        "e <i>com que modelo</i> implantar a solução, este relatório mede, com dados oficiais reais, como escolaridade, saúde e desigualdade "
        "se relacionam com a renda nas 27 UFs brasileiras, entre 2012 e 2021."),
      P("<b>Principais achados</b>", corpo),
      B(f"Anos de estudo e renda per capita têm correlação linear forte (r = {f(q4['pearson_r'], 3)}); a regressão simples explica "
        f"{f(q4['R2'] * 100, 1)}% da variação da renda, e a múltipla (estudo, esperança de vida e Gini) explica {f(q5['R2'] * 100, 1)}%."),
      B(f"A regressão logística classifica corretamente {f(r['acuracia'] * 100, 1)}% dos casos entre renda per capita alta ou baixa "
        f"(AUC = {f(r['auc'], 3)}) usando apenas anos de estudo, esperança de vida e Gini."),
      B(f"O Nordeste concentra a menor renda média (R$ {f(reg.loc['Nordeste', 'RDPC'])}) e a menor escolaridade ({f(reg.loc['Nordeste', 'ANOSEST'])} anos); "
        f"apenas {f(alta['Nordeste'] * 100, 0)}% das observações nordestinas ficam acima da mediana nacional de renda."),
      B("Testes de hipótese confirmam que o Nordeste tem escolaridade média significativamente menor, e o Sul e o Sudeste significativamente maior, que a média geral."),
      P("<b>Recomendação central:</b> iniciar pilotos onde escolaridade e renda são menores (Nordeste e Norte), com interface acessível sem digitação, "
        "funcionamento offline e financiamento público ou por convênio, pois o cidadão de menor renda dificilmente arcará sozinho com a pulseira."),
      PageBreak()]

# ---- 2. Contexto -------------------------------------------------------------------
S += [P("2. Problema, público e ODS", h1),
      P("Pessoas com deficiência e idosos podem ter dificuldade de carregar, enxergar ou apresentar documentos e de usar o transporte público "
        "(pagar a passagem, validar bilhete, comprovar gratuidade). Para qualquer cidadão, há ainda o incômodo de carregar vários documentos e de "
        "localizar rapidamente um familiar. A solução combina uma pulseira NFC passiva (que guarda apenas um identificador seguro), um aplicativo com "
        "carteira de documentos e saldo de transporte, e um painel para responsáveis, sempre com consentimento e em conformidade com a LGPD."),
      P("<b>Pergunta do relatório:</b> em quais contextos a necessidade de inclusão e acesso a serviços é maior, e que perfil socioeconômico o projeto deve "
        "considerar para ser viável?"),
      tabela([["ODS", "Contribuição do projeto", "Meta associada"],
              ["10 - Redução das desigualdades", "Inclusão de pessoas com deficiência e idosos no acesso a serviços", "10.2 (inclusão social e econômica de todos)"],
              ["11 - Cidades e comunidades sustentáveis", "Transporte público acessível; menos papel e plástico (silicone reutilizável)", "11.2 (transporte acessível, com atenção a PcD e idosos)"],
              ["9 - Indústria, inovação e infraestrutura", "Tecnologia NFC aplicada a serviços públicos", "9.c (ampliar acesso às tecnologias de informação)"],
              ["3 - Saúde e bem-estar", "Ficha de emergência acessível por aproximação", "Saúde e bem-estar de pessoas vulneráveis"]],
             [4.6 * cm, 7 * cm, 5 * cm]),
      P("<b>Ecossistema:</b> cidadãos usuários, responsáveis e cuidadores, operadoras de transporte, prefeituras e secretarias de transporte e de pessoas com "
        "deficiência, organizações de apoio, serviços de saúde e emergência, e a equipe que opera a plataforma."),
      # ---- 3. Base
      P("3. Base de dados e metodologia", h1),
      P("<b>Fonte:</b> Atlas do Desenvolvimento Humano no Brasil, painel IDHM (PNUD, Ipea e Fundação João Pinheiro), arquivo oficial baixado do site do PNUD. "
        "Os dados são reais, sem qualquer geração artificial. Foram usadas as 27 UFs em 10 anos (2012 a 2021), totalizando 270 observações, sem valores ausentes. "
        "A coluna de região foi criada a partir do código da UF."),
      P("<b>Justificativa:</b> escolaridade, renda, longevidade e desigualdade são indicadores consolidados de vulnerabilidade social e ajudam a "
        "decidir onde uma tecnologia de inclusão tem mais impacto e que condições de acesso o público tem. A base tem muitas variáveis quantitativas, "
        "o que permite probabilidade, testes, regressão linear e logística."),
      P("<b>Limitações assumidas:</b> (i) os dados são agregados por UF, não por município, e não identificam diretamente pessoas com deficiência; "
        "usamos indicadores socioeconômicos como aproximação do contexto de vulnerabilidade; (ii) as mesmas 27 UFs se repetem em 10 anos, então as observações "
        "não são totalmente independentes; (iii) os resultados mostram associação, não causalidade."),
      tabela([["Variável", "Descrição", "Média", "Desvio padrão", "Mín.", "Máx."]] +
             [[v, d, f(df[v].mean(), 2 if v != "GINI" else 3), f(df[v].std(), 2 if v != "GINI" else 3),
               f(df[v].min(), 2 if v != "GINI" else 3), f(df[v].max(), 2 if v != "GINI" else 3)]
              for v, d in [("RDPC", "Renda domiciliar per capita (R$)"), ("ANOSEST", "Anos de estudo"),
                           ("ESPVIDA", "Esperança de vida ao nascer (anos)"), ("GINI", "Índice de Gini (0 a 1)")]],
             [2.2 * cm, 6 * cm, 2.1 * cm, 2.6 * cm, 1.8 * cm, 1.8 * cm]),
      img("figuras/descritiva_regiao.png", 16 * cm,
          "Figura 1 - Renda, escolaridade e esperança de vida médias por região."),
      P("<b>Leitura:</b> Nordeste e Norte têm menor renda e menor esperança de vida; o Nordeste também tem a menor escolaridade. "
        "Sul, Sudeste e Centro-Oeste têm renda média semelhante e bem superior. O Gini é mais alto no Nordeste e no Norte.")]

# ---- 4. Q2 --------------------------------------------------------------------------
S += [P("4. Probabilidade com a Distribuição Normal (Questão 2)", h1),
      P(f"Variável escolhida: <b>ANOSEST</b> (anos de estudo). Com {q23['N']} registros, média = {f(q23['media'], 3)}, mediana = {f(q23['mediana'], 3)} e "
        f"desvio padrão populacional = {f(q23['desvio_padrao_pop'], 3)}. O teste de Shapiro-Wilk (p = {f(q23['shapiro_p'], 3)}) não rejeita a normalidade a 5%, "
        "o que sustenta a suposição do enunciado."),
      tabela([["Item", "Probabilidade", "Classificação"],
              ["(a) P(X < média)", f(q23["q2a"]["prob"], 4), q23["q2a"]["classe"]],
              ["(b) P(X > mediana)", f(q23["q2b"]["prob"], 4), q23["q2b"]["classe"]]],
             [6 * cm, 4 * cm, 6 * cm]),
      img("figuras/q2_normal.png", 15.5 * cm, "Figura 2 - Áreas sob a curva Normal para os itens (a) e (b)."),
      P("<b>Interpretação:</b> a probabilidade de uma UF-ano ter escolaridade abaixo da média é de exatamente 50%, pois a média é o centro da distribuição Normal "
        "(evento equiprovável). Como a mediana amostral é um pouco menor que a média, a chance de superá-la é de 51,4%, evento provável por estar acima de 50%. "
        "Critério de classificação: 0 = impossível; entre 0 e 0,5 = improvável; 0,5 = equiprovável; entre 0,5 e 1 = provável; 1 = certo."),
      # ---- 5. Q3
      P("5. Testes de hipótese para a média (Questão 3)", h1),
      P(f"Hipótese nula H0: a média de ANOSEST da amostra é igual à média de referência ({f(q23['media'], 3)} anos). Teste Z, com desvio padrão de referência igual "
        f"ao populacional ({f(q23['desvio_padrao_pop'], 3)}). As amostras aleatórias (semente 42) foram extraídas de subgrupos reais: 20 observações do Nordeste no item (a) "
        "e 25 observações de Sul e Sudeste no item (b)."),
      tabela([["Item", "Hipótese alternativa", "Alfa", "n", "Média amostral", "Z calculado", "Z crítico", "p-valor", "Decisão"],
              ["(a)", "média < referência", "6%", q23["q3a"]["n"], f(q23["q3a"]["media_amostral"], 3), f(q23["q3a"]["z_calc"], 2),
               f(q23["q3a"]["z_critico"], 2), pv(q23["q3a"]["p_valor"]), "Rejeita H0"],
              ["(b)", "média > referência", "9%", q23["q3b"]["n"], f(q23["q3b"]["media_amostral"], 3), f(q23["q3b"]["z_calc"], 2),
               f(q23["q3b"]["z_critico"], 2), pv(q23["q3b"]["p_valor"]), "Rejeita H0"]],
             [1.1 * cm, 3 * cm, 1.1 * cm, 0.9 * cm, 2.2 * cm, 2 * cm, 1.8 * cm, 1.7 * cm, 2.2 * cm]),
      img("figuras/q3_teste_z.png", 15.5 * cm, "Figura 3 - Região crítica e valor de Z calculado nos dois testes."),
      P("<b>Interpretação:</b> nos dois casos o Z calculado cai na região crítica, e a hipótese nula é rejeitada. Há evidência estatística de que o Nordeste tem escolaridade média "
        "<b>menor</b> que a média nacional da base, e de que Sul e Sudeste têm escolaridade <b>maior</b>. Para o projeto, isso indica públicos com níveis diferentes de familiaridade com "
        "documentos formais e tecnologia, exigindo interface adaptável.")]

# ---- 6. Q4 ---------------------------------------------------------------------------
S += [P("6. Análise bivariada e regressão linear simples (Questão 4)", h1),
      P("Variáveis: <b>ANOSEST</b> (explicativa, X) e <b>RDPC</b> (renda domiciliar per capita em R$, resposta Y); n = 270."),
      img("figuras/q4a_dispersao.png", 10 * cm, "Figura 4 - Gráfico de dispersão entre anos de estudo e renda per capita."),
      P("<b>(a) Interpretação:</b> a nuvem de pontos é ascendente: UFs e anos com mais escolaridade tendem a ter maior renda per capita, em padrão aproximadamente linear. "
        "A dispersão aumenta nos valores altos, indício de heterocedasticidade."),
      tabela([["Medida", "Valor", "Interpretação"],
              ["Covariância amostral", f(q4["covariancia"], 2), "Positiva: as variáveis crescem juntas"],
              ["Correlação de Pearson (r)", f(q4["pearson_r"], 3), "Correlação positiva forte (p < 0,001)"]],
             [5 * cm, 3 * cm, 8 * cm]),
      P(f"<b>(b) Interpretação:</b> a covariância positiva indica o sentido da relação; como depende da escala, a correlação r = {f(q4['pearson_r'], 3)} é a medida comparável: "
        "relação linear positiva e forte."),
      img("figuras/q4c_correlacao.png", 6.5 * cm, "Figura 5 - Gráfico de correlação linear de Pearson (mapa de calor)."),
      P("<b>(c) Interpretação:</b> o mapa de calor mostra o mesmo r, com cor intensa, confirmando a associação forte entre as variáveis."),
      img("figuras/q4d_regressao.png", 10 * cm, "Figura 6 - Reta de regressão linear simples sobre o gráfico de dispersão."),
      P(f"<b>(d) Equação:</b> RDPC = {f(q4['b0'], 2)} + {f(q4['b1'], 2)} x ANOSEST. Cada ano adicional de estudo está associado, em média, a R$ {f(q4['b1'], 2)} a mais de renda per capita."),
      tabela([["Medida", "Valor"],
              ["R<super>2</super>", f(q4["R2"], 4)], ["R<super>2</super> ajustado", f(q4["R2_ajustado"], 4)],
              ["Estatística F (1 e 268 graus de liberdade)", f(q4["F"], 2)], ["F crítico a 5%", f(q4["F_critico_5pct"], 3)],
              ["p-valor do teste F", pv(q4["p_F"])], ["Teste t do coeficiente angular", f(q4["t_b1"], 2)]],
             [8 * cm, 4 * cm]),
      P(f"<b>(e) Adequação:</b> o R<super>2</super> mostra que {f(q4['R2'] * 100, 1)}% da variação da renda é explicada pelos anos de estudo. O teste F ({f(q4['F'], 1)}) supera em muito o valor crítico "
        "({0}), e a hipótese nula de que o modelo não explica nada é rejeitada: o modelo é estatisticamente significativo. Ressalva: os resíduos não são normais "
        "(Shapiro-Wilk, p < 0,001) e a variância cresce com X, então os intervalos de confiança devem ser lidos com cautela.".format(f(q4["F_critico_5pct"], 2))),
      P(f"<b>(f) Previsão:</b> para uma UF com 10 anos de estudo (dentro do intervalo observado, de {f(q4['previsao']['ANOSEST_min'], 2)} a {f(q4['previsao']['ANOSEST_max'], 2)}), "
        f"a renda per capita prevista é de R$ {f(q4['previsao']['RDPC_prevista'], 2)}.")]

# ---- 7. Q5 ---------------------------------------------------------------------------
cv, cr = q5["matriz_covariancia"], q5["matriz_correlacao"]
vs = ["RDPC", "ANOSEST", "ESPVIDA", "GINI"]
co = q5["coeficientes"]
S += [P("7. Análise multivariada e regressão linear múltipla (Questão 5)", h1),
      P("Variáveis: resposta <b>RDPC</b>; explicativas <b>ANOSEST</b> (anos de estudo), <b>ESPVIDA</b> (esperança de vida) e <b>GINI</b> (desigualdade); n = 270."),
      img("figuras/q5a_dispersao.png", 11 * cm, "Figura 7 - Matriz de dispersão entre as quatro variáveis."),
      P("<b>Interpretação:</b> renda cresce com escolaridade e com esperança de vida; o Gini mostra relação fraca e dispersa com as demais variáveis."),
      KeepTogether([P("Matriz de covariância", h2),
      tabela([[""] + vs] + [[a] + [f(cv[b][a], 3 if a in ('GINI',) or b == 'GINI' else 2) for b in vs] for a in vs],
             [3 * cm] + [3 * cm] * 4)]),
      KeepTogether([P("Matriz de correlação de Pearson", h2),
      tabela([[""] + vs] + [[a] + [f(cr[b][a], 3) for b in vs] for a in vs], [3 * cm] + [3 * cm] * 4)]),
      img("figuras/q5c_correlacao.png", 8 * cm, "Figura 8 - Gráfico da matriz de correlação linear de Pearson."),
      P(f"<b>Interpretação:</b> a renda se correlaciona fortemente com anos de estudo (r = {f(cr['RDPC']['ANOSEST'], 3)}) e com esperança de vida (r = {f(cr['RDPC']['ESPVIDA'], 3)}), "
        f"e fracamente, de forma negativa, com o Gini (r = {f(cr['RDPC']['GINI'], 3)}). As explicativas têm correlação moderada entre si (maior valor: {f(cr['ANOSEST']['ESPVIDA'], 3)}), "
        f"sem multicolinearidade preocupante (VIF entre {f(min(q5['VIF'].values()), 2)} e {f(max(q5['VIF'].values()), 2)}, abaixo de 5)."),
      P("<b>Equação da regressão múltipla:</b> RDPC = {0} + {1} x ANOSEST + {2} x ESPVIDA - {3} x GINI".format(
          f(co["Intercepto"]["beta"], 2), f(co["ANOSEST"]["beta"], 2), f(co["ESPVIDA"]["beta"], 2), f(abs(co["GINI"]["beta"]), 2))),
      tabela([["Termo", "Coeficiente", "Erro padrão", "t", "p-valor"]] +
             [[n_, f(co[n_]["beta"], 3), f(co[n_]["ep"], 3), f(co[n_]["t"], 2), pv(co[n_]["p"])] for n_ in co],
             [4 * cm, 3 * cm, 3 * cm, 2.5 * cm, 3 * cm]),
      P(f"<b>Adequação:</b> R<super>2</super> = {f(q5['R2'], 4)} (ajustado {f(q5['R2_ajustado'], 4)}), isto é, o modelo explica cerca de {f(q5['R2'] * 100, 0)}% da variação da renda, "
        f"contra {f(q4['R2'] * 100, 0)}% da regressão simples. Teste F({q5['gl'][0]}, {q5['gl'][1]}) = {f(q5['F'], 2)}, muito maior que o F crítico ({f(q5['F_critico_5pct'], 2)}); p-valor "
        f"{pv(q5['p_F'])}: o modelo é significativo. Os testes t mostram que ANOSEST e ESPVIDA são significativos (p < 0,001), mas o Gini não é a 5% "
        f"(p = {f(co['GINI']['p'], 3)}). Interpretação dos coeficientes, mantidas as demais variáveis constantes: +1 ano de estudo se associa a cerca de R$ {f(co['ANOSEST']['beta'], 0)} a mais de renda; "
        f"+1 ano de esperança de vida, a cerca de R$ {f(co['ESPVIDA']['beta'], 0)} a mais."),
      P(f"<b>Previsão:</b> para ANOSEST = 10, ESPVIDA = 76 e GINI = 0,50, a renda per capita prevista é de R$ {f(q5['previsao']['RDPC_prevista'], 2)}, "
        "dentro das faixas observadas. Ressalva: resíduos não normais e variância não constante, como na regressão simples.")]

# ---- 8. Q6 ---------------------------------------------------------------------------
cc, cv6 = q6["coeficientes"], q6["validacao"]
S += [P("8. Regressão logística binária (Questão 6)", h1),
      P(f"Variável resposta: <b>RENDA_ALTA</b> = 1 se a renda per capita é maior que a mediana (R$ {f(q6['corte_RDPC_mediana'], 2)}), e 0 caso contrário "
        f"({q6['n_classe1']} casos de cada classe). Explicativas: ANOSEST, ESPVIDA e GINI. A renda não entra como explicativa, para evitar circularidade."),
      P("<b>(a) Equação:</b> ln[p / (1 - p)] = {0} + {1} x ANOSEST + {2} x ESPVIDA - {3} x GINI, em que p é a probabilidade de renda alta.".format(
          f(cc["Intercepto"]["beta"], 2), f(cc["ANOSEST"]["beta"], 3), f(cc["ESPVIDA"]["beta"], 3), f(abs(cc["GINI"]["beta"]), 2))),
      tabela([["Termo", "Coeficiente", "Erro padrão", "z", "p-valor", "Razão de chances"],
              ["Intercepto", f(cc["Intercepto"]["beta"], 3), f(cc["Intercepto"]["ep"], 3), f(cc["Intercepto"]["z"], 2), pv(cc["Intercepto"]["p"]), "-"],
              ["ANOSEST", f(cc["ANOSEST"]["beta"], 3), f(cc["ANOSEST"]["ep"], 3), f(cc["ANOSEST"]["z"], 2), pv(cc["ANOSEST"]["p"]), f(cc["ANOSEST"]["odds_ratio"], 2)],
              ["ESPVIDA", f(cc["ESPVIDA"]["beta"], 3), f(cc["ESPVIDA"]["ep"], 3), f(cc["ESPVIDA"]["z"], 2), pv(cc["ESPVIDA"]["p"]), f(cc["ESPVIDA"]["odds_ratio"], 2)],
              ["GINI", f(cc["GINI"]["beta"], 3), f(cc["GINI"]["ep"], 3), f(cc["GINI"]["z"], 2), pv(cc["GINI"]["p"]), "0,63 por +0,01 de Gini"]],
             [2.6 * cm, 2.6 * cm, 2.6 * cm, 2 * cm, 2.2 * cm, 4 * cm]),
      P(f"<b>Interpretação:</b> o modelo é significativo (teste da razão de verossimilhança: qui-quadrado = {f(q6['LR_qui2'], 1)}; p {pv(q6['LR_p'])}; R<super>2</super> de McFadden = {f(q6['McFadden_R2'], 3)}). "
        f"Cada ano a mais de estudo multiplica a chance de renda alta por {f(cc['ANOSEST']['odds_ratio'], 1)}; cada ano a mais de esperança de vida, por {f(cc['ESPVIDA']['odds_ratio'], 2)}; "
        "e cada aumento de 0,01 no Gini reduz a chance em cerca de 37%. Diferentemente da regressão linear, aqui o Gini é significativo: pesa mais para separar renda alta de baixa do que para prever o valor exato da renda."),
      P("<b>(b) Matriz de confusão e acurácia</b> (ponto de corte 0,5)", h2),
      tabela([["Base", "Verd. neg.", "Falso pos.", "Falso neg.", "Verd. pos.", "Acurácia", "Sensib.", "Especif.", "AUC"],
              ["Todos os dados (n = 270)", r["matriz"][0][0], r["matriz"][0][1], r["matriz"][1][0], r["matriz"][1][1],
               f(r["acuracia"] * 100, 1) + "%", f(r["sensibilidade"] * 100, 1) + "%", f(r["especificidade"] * 100, 1) + "%", f(r["auc"], 3)],
              [f"Validação em 8 UFs (n = {cv6['n_teste']})"][0:1] + [cv6["matriz"][0][0], cv6["matriz"][0][1], cv6["matriz"][1][0], cv6["matriz"][1][1],
               f(cv6["acuracia"] * 100, 1) + "%", f(cv6["sensibilidade"] * 100, 1) + "%", f(cv6["especificidade"] * 100, 1) + "%", f(cv6["auc"], 3)]],
             [3.6 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.7 * cm, 1.5 * cm, 1.6 * cm, 1.3 * cm]),
      img("figuras/q6b_matriz_confusao.png", 14 * cm, "Figura 9 - Matrizes de confusão: todos os dados e validação em UFs não vistas no treino."),
      P(f"<b>Interpretação:</b> com todos os dados, o modelo acertou {r['matriz'][0][0] + r['matriz'][1][1]} de 270 casos (acurácia de {f(r['acuracia'] * 100, 1)}%), com {r['matriz'][0][1]} falsos positivos "
        f"e {r['matriz'][1][0]} falsos negativos. Na validação, treinando em 19 UFs e testando em 8 UFs não vistas (divisão por UF, para que os dez anos de uma mesma UF não vazem entre treino e teste), "
        f"a acurácia foi de {f(cv6['acuracia'] * 100, 1)}%, o que indica boa capacidade de generalização; a diferença entre os dois valores vem em parte do sorteio das UFs de teste. "
        "A curva ROC (Figura 10) mostra discriminação muito boa."),
      img("figuras/q6_roc.png", 6.5 * cm, "Figura 10 - Curva ROC da regressão logística."),
      P("<b>(c) Classificação com três variáveis explicativas</b>", h2),
      tabela([["ANOSEST", "ESPVIDA", "GINI", "Probabilidade de renda alta", "Classe prevista"]] +
             [[f(c["entrada"]["ANOSEST"], 1), f(c["entrada"]["ESPVIDA"], 0), f(c["entrada"]["GINI"], 2), f(c["prob"] * 100, 1) + "%",
               "1 (renda alta)" if c["classe"] else "0 (renda baixa)"] for c in q6["classificacoes"]],
             [2.6 * cm, 2.6 * cm, 2.6 * cm, 5 * cm, 3.4 * cm]),
      P("<b>Interpretação:</b> um perfil com 10 anos de estudo, esperança de vida de 76 anos e Gini 0,50 é classificado como renda alta (98,3%); um perfil com 7,5 anos de estudo, "
        "71 anos e Gini 0,55 é classificado como renda baixa (0,4%). Esse tipo de classificador pode servir como ferramenta de triagem territorial para escolher onde começar os pilotos.")]

# ---- 9. Insights -----------------------------------------------------------------------
S += [P("9. Insights e recomendações para o projeto", h1),
      P("Os resultados sustentam decisões concretas para a Pulseira NFC Cidadã, resumidas abaixo (cada recomendação é uma inferência a partir da associação estatística, "
        "e deve ser validada com o público-alvo)."),
      tabela([["Achado estatístico", "Implicação para o projeto", "Ação recomendada"],
              [f"Nordeste: renda média R$ {f(reg.loc['Nordeste', 'RDPC'], 0)} e {f(reg.loc['Nordeste', 'ANOSEST'], 1)} anos de estudo; só {f(alta['Nordeste'] * 100, 0)}% dos casos acima da mediana de renda. Norte: {f(alta['Norte'] * 100, 0)}%.",
               "Maior necessidade de inclusão e menor capacidade de pagar pela solução.",
               "Priorizar pilotos no Nordeste e no Norte, com a pulseira financiada pelo poder público, convênios ou programas sociais, e não pelo cidadão."],
              ["Escolaridade é o fator que mais se associa à renda (r = 0,76) e é significativamente menor no Nordeste (teste Z).",
               "O público pode ter menos familiaridade com documentos digitais e aplicativos.",
               "Interface por aproximação (NFC), sem digitação, com ícones, áudio e linguagem simples; treinamento via assistência social e escolas."],
              ["Esperança de vida é o segundo fator associado à renda e é menor no Norte e no Nordeste.",
               "A ficha de emergência e o acesso a saúde têm valor alto onde o acesso a serviços é mais frágil.",
               "Parceria com secretarias de saúde e serviços de emergência para a ficha de emergência por aproximação."],
              ["Gini mais alto no Nordeste e no Norte; é significativo na logística.",
               "Dentro de um mesmo território, a desigualdade separa quem tem acesso a serviços de quem não tem.",
               "Focar em comunidades de baixa renda dentro de cada cidade, não só em médias regionais."],
              [f"O classificador logístico acerta {f(r['acuracia'] * 100, 1)}% (AUC {f(r['auc'], 2)}) com três indicadores públicos.",
               "É possível escolher territórios-piloto com dados abertos, de baixo custo.",
               "Usar o modelo como triagem de territórios e, depois, aprofundar com dados municipais e entrevistas."],
              ["Renda per capita caiu em 2020 e 2021 (média de R$ 629 em 2021, frente a R$ 703 em 2019), período da pandemia de COVID-19.",
               "Vulnerabilidade econômica sensível a choques.",
               "Desenho do modelo de negócio com custo unitário baixo, escalonamento do subsídio e funcionamento offline, em linha com o tema da FIAP."]],
             [5.5 * cm, 5 * cm, 6 * cm]),
      P("10. Limitações e próximos passos", h1),
      B("Os dados são por UF e não identificam pessoas com deficiência; o passo seguinte é incorporar dados municipais do Censo 2022 sobre deficiência, idosos e acessibilidade do entorno."),
      B("As observações se repetem entre anos (mesmas UFs), e os resíduos dos modelos lineares não são normais; os resultados devem ser lidos como associações."),
      B("Validar as hipóteses com entrevistas ou questionários com pessoas com deficiência, idosos, familiares e cuidadores, e testar um protótipo com leitura NFC real."),
      B("Tratar privacidade e LGPD (dados sensíveis, consentimento, tutela e curatela), segurança do NFC (chip guarda só um token) e integração oficial com bilhetagem e documentos digitais."),
      P("11. Conclusão", h1),
      P(f"Os dados reais mostram que escolaridade e saúde estão fortemente associadas à renda, e que Nordeste e Norte concentram as condições de maior vulnerabilidade. "
        f"Com apenas três indicadores públicos, foi possível classificar a renda com {f(r['acuracia'] * 100, 1)}% de acerto. Para a Pulseira NFC Cidadã, isso aponta para pilotos nessas regiões, "
        "com financiamento público, interface acessível e operação offline, fortalecendo a contribuição aos ODS 10, 11, 9 e 3."),
      P("Referências", h2),
      P("PNUD, Ipea e Fundação João Pinheiro. Atlas do Desenvolvimento Humano no Brasil - Painel IDHM (base de dados oficial). "
        "FIAP. Global Solution 2026 - CitizenTech (experience.fiap.com.br/global-solution-citizen-tech). "
        "ONU. Objetivos de Desenvolvimento Sustentável 3, 9, 10 e 11.", ParagraphStyle("ref", parent=corpo, fontSize=9))]

doc = SimpleDocTemplate("relatorio_estatistico.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Relatório Estatístico - Pulseira NFC Cidadã",
                        author="Arthur Primo Brandão, Leandro Cavaccini Brito, Lucas Dorice dos Santos")
doc.build(S, onLaterPages=rodape)
print("relatorio_estatistico.pdf gerado")

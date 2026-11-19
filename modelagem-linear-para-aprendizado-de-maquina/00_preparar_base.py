"""
Etapa 0 - Preparação da base de dados (Global Solution FIAP 2026 - CitizenTech)
Fonte: Atlas do Desenvolvimento Humano no Brasil (PNUD/Ipea/FJP), painel IDHM.
Dados reais, em nível de Unidade da Federação (UF), anos 2012 a 2021.
Entrada : base_de_dados.xlsx (aba "Base de Dados", baixada do PNUD)
Saída   : base_dados.csv (27 UFs x 10 anos = 270 observações)
"""
import pandas as pd

ARQ_ENTRADA = "base_de_dados.xlsx"
ARQ_SAIDA = "base_dados.csv"

REGIOES = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}

df = pd.read_excel(ARQ_ENTRADA, sheet_name="Base de Dados")

# Mantém somente as UFs (exclui Brasil total e Regiões Metropolitanas/RIDEs)
df = df[df["AGREGACAO"] == "UF"].copy()
df["CODIGO"] = df["CODIGO"].astype(int)
df["REGIAO"] = (df["CODIGO"] // 10).map(REGIOES)
df = df.drop(columns=["AGREGACAO"]).rename(columns={"NOME": "UF"})

# Verificações de qualidade
assert df.isna().sum().sum() == 0, "Há valores ausentes"
assert df.shape[0] == 27 * 10, "Número de observações inesperado"

df.to_csv(ARQ_SAIDA, index=False, encoding="utf-8-sig")
print(f"Base salva em {ARQ_SAIDA}: {df.shape[0]} linhas x {df.shape[1]} colunas")
print(df.groupby("REGIAO")["UF"].nunique())

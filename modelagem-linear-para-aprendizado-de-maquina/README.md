# Global Solution FIAP 2026 (CitizenTech): Relatório Estatístico

Análise estatística em Python de dados reais do Atlas do Desenvolvimento Humano no Brasil, para apoiar a decisão de **onde e como implantar a Pulseira NFC Cidadã** (pulseira de silicone com chip NFC, ligada a um aplicativo que reúne documentos, saldo de transporte público e rastreio consentido para pessoas com deficiência, idosos e suas redes de apoio).

## Equipe

| Integrante | RM |
|---|---|
| Arthur Primo Brandão | 573572 |
| Leandro Cavaccini Brito | 570556 |
| Lucas Dorice dos Santos | 568692 |

Ciência da Computação, FIAP.

## O que está nesta entrega

| Item | Arquivo |
|---|---|
| Base de dados | `base_dados.csv` |
| Códigos (.py) | `00_preparar_base.py`, `01_probabilidade_hipoteses.py`, `02_bivariada_regressao_simples.py`, `03_multivariada_regressao_multipla.py`, `04_regressao_logistica.py`, `05_gerar_relatorio.py` |
| Relatório estatístico (.pdf) | `relatorio_estatistico.pdf` |
| Arquivo de origem da base | `base_de_dados.xlsx` (original do PNUD, sem alterações) |
| Figuras e resultados gerados | pastas `figuras/` e `resultados/` |

## Base de dados

- **Fonte:** Atlas do Desenvolvimento Humano no Brasil, painel IDHM (PNUD, Ipea e Fundação João Pinheiro). Dados oficiais e reais, sem geração artificial.
- **Recorte:** 27 UFs em 10 anos (2012 a 2021), com 270 observações e sem valores ausentes.
- **Tratamento:** o script `00` mantém somente as UFs (exclui o total do Brasil e as Regiões Metropolitanas/RIDEs) e cria a coluna `REGIAO` a partir do código da UF.
- **Variáveis usadas nas análises:**

| Variável | Descrição |
|---|---|
| `RDPC` | Renda domiciliar per capita (R$) |
| `ANOSEST` | Anos de estudo |
| `ESPVIDA` | Esperança de vida ao nascer (anos) |
| `GINI` | Índice de Gini (desigualdade, 0 a 1) |

A base tem outras variáveis do Atlas (IDHM e dimensões, taxas de frequência escolar etc.), que ficam disponíveis no CSV.

## Como reproduzir

**Requisitos:** Python 3 com `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `scikit-learn`, `reportlab`, `pillow` e `openpyxl`.

```bash
pip install pandas numpy scipy matplotlib seaborn scikit-learn reportlab pillow openpyxl
```

**Passo a passo** (na mesma pasta de `base_de_dados.xlsx`):

```bash
mkdir figuras resultados
python 00_preparar_base.py
python 01_probabilidade_hipoteses.py
python 02_bivariada_regressao_simples.py
python 03_multivariada_regressao_multipla.py
python 04_regressao_logistica.py
python 05_gerar_relatorio.py
```

Os scripts devem rodar **nesta ordem**: cada um lê `base_dados.csv` (gerado pelo `00`), e o `05` lê as figuras e os resultados (`.json`) produzidos pelos scripts `01` a `04`. Para trabalhar sem o `00`, basta usar o `base_dados.csv` já entregue.

## O que cada script faz

| Script | Questão | Conteúdo |
|---|---|---|
| `00_preparar_base.py` | (base) | Lê o .xlsx do PNUD, filtra as UFs, cria `REGIAO` e salva `base_dados.csv` |
| `01_probabilidade_hipoteses.py` | Q2 e Q3 | Probabilidades com a Normal (`ANOSEST`) e testes Z para a média (n = 20, alfa = 6%; n = 25, alfa = 9%) |
| `02_bivariada_regressao_simples.py` | Q4 | Dispersão, covariância, correlação de Pearson, regressão simples (`RDPC` ~ `ANOSEST`), R², teste F e previsão |
| `03_multivariada_regressao_multipla.py` | Q5 | Matrizes de covariância e correlação, regressão múltipla (`RDPC` ~ `ANOSEST` + `ESPVIDA` + `GINI`), R², teste F, testes t, VIF e previsão |
| `04_regressao_logistica.py` | Q6 | Regressão logística (`RENDA_ALTA`: renda acima da mediana), matriz de confusão, acurácia, ROC, validação por UF e classificação de novos casos |
| `05_gerar_relatorio.py` | Q7 | Monta o relatório em PDF com tabelas, gráficos, interpretações e insights para o projeto |

## Principais resultados

| Análise | Resultado |
|---|---|
| Normal (Q2) | P(X < média) = 0,5000; P(X > mediana) = 0,5139 |
| Testes Z (Q3) | Nordeste com escolaridade menor e Sul/Sudeste com escolaridade maior que a média: H0 rejeitada nos dois testes |
| Regressão simples (Q4) | r = 0,759; R² = 0,577; RDPC = -827,23 + 170,35 x ANOSEST |
| Regressão múltipla (Q5) | R² = 0,722; ANOSEST e ESPVIDA significativos, GINI não significativo a 5% |
| Regressão logística (Q6) | Acurácia de 88,5% (AUC 0,963); 95,0% na validação com 8 UFs não vistas no treino |

## Limitações

- Os dados são **agregados por UF** e não identificam pessoas com deficiência. Renda, escolaridade e saúde foram usadas como aproximação de vulnerabilidade social.
- As 27 UFs se repetem ao longo de 10 anos, então as observações não são totalmente independentes.
- Os resíduos das regressões lineares não são normais e a variância não é constante: os resultados devem ser lidos como **associações**, não como relações de causa e efeito.
- A próxima etapa natural é incorporar dados municipais do Censo 2022 (deficiência, idosos e acessibilidade) e validar as hipóteses com entrevistas com o público-alvo.

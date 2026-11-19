# Análise e Cálculos

> Documento **gerado automaticamente** por `python main.py --relatorio-docs`. A família é **ilustrativa (dados estimados)**. Troque o perfil para analisar outro caso.

## 1. Perfil analisado

- 4 pessoas; banho de 8 min; ligação bifasico; imóvel próprio; telhado adequado.
- Tarifa efetiva: **R$ 1,00/kWh** (tarifa R$ 1,00 + bandeira verde). Tipo do dado da tarifa: *estimado*.
- Período: consumo **mensal** (média anual) e economia em **12 meses** e em **10 anos**.

## 2. Análise de consumo (kWh/mês)

Fórmula: `E (kWh) = P (kW) × t (h)`, `consumo mensal = E × horas/dia × dias/mês × quantidade`.

| Aparelho | kWh/mês | % da casa | R$/mês |
|---|---:|---:|---:|
| Chuveiro elétrico | 70,4 | 27% | R$ 70,40 |
| Geladeira (média do ciclo) | 43,2 | 17% | R$ 43,20 |
| Ar-condicionado split 9.000-12.000 BTU | 27,0 | 10% | R$ 27,00 |
| Ventilador ×2 | 24,0 | 9% | R$ 24,00 |
| TV LED 40-50 pol. ×2 | 24,0 | 9% | R$ 24,00 |
| Notebook ×2 | 19,5 | 7% | R$ 19,50 |
| Lâmpada fluorescente compacta 15 W ×8 | 18,0 | 7% | R$ 18,00 |
| Máquina de lavar (média do ciclo) | 10,5 | 4% | R$ 10,50 |
| Ferro de passar | 9,0 | 3% | R$ 9,00 |
| Micro-ondas | 9,0 | 3% | R$ 9,00 |
| Roteador Wi-Fi | 7,2 | 3% | R$ 7,20 |
| **Total** | **261,8** | 100% | **R$ 261,80** |

**Verificação física do chuveiro** (`Q = m·c·ΔT` contra `P×t`): por banho, 0,733 kWh pela potência contra 0,744 kWh pela física da água, diferença de 1,5%. A consistência confirma que o modelo de consumo do chuveiro é coerente.

## 3. Comparação das alternativas (mesma necessidade, mesmo período)

Necessidade: **reduzir a conta de luz**. Cenário de reajuste da tarifa: +6%/ano.

| Alternativa | Tipo | Investimento | Economia/ano | Payback s/ reajuste | Payback c/ reajuste | Saldo em 10 anos | CO₂ líquido evitado (kg/ano) |
|---|---|---:|---:|---:|---:|---:|---:|
| **A** Eficiência e hábitos | economia | R$ 96,00 | R$ 297,60 | 0,3 anos | 0,3 anos | R$ 3.826,60 | 11 |
| **B** Aquecedor solar de água | renovável | R$ 5.400,00 | R$ 591,36 | 9,1 anos | 7,5 anos | R$ 2.394,59 | 23 |
| **C** Energia solar fotovoltaica | renovável | R$ 9.900,00 | R$ 2.160,36 | 4,6 anos | 4,2 anos | R$ 17.876,36 | -6 |
| **A+C** Pacote: eficiência + fotovoltaica | combinação | R$ 9.996,00 | R$ 2.205,00 | 4,5 anos | 4,2 anos | R$ 18.450,59 | 6 |

### A. Eficiência e hábitos

Banho 8 → 6 min e troca de 8 lâmpada(s) por LED de 9 W.

- **Condições:** Não exige obra nem imóvel próprio. Depende da adesão de todos da casa ao novo hábito.
- **Limitações:** A economia do banho depende de a meta ser mantida. A troca de lâmpadas rende pouco quando já há fluorescentes ou LED.
- **Cálculo:** consumo 261,8 → 237,0 kWh/mês (banho: 211 kWh/ano; lâmpadas: 86 kWh/ano).

### B. Aquecedor solar de água

Sol aquece a água do banho e cobre cerca de 70% do consumo do chuveiro.

- **Condições:** Imóvel próprio (ou autorização) e telhado com sol e espaço. Exige reservatório térmico e adaptação da tubulação, e costuma manter apoio elétrico.
- **Limitações:** A fração solar cai no inverno e em dias nublados. Só atua sobre o consumo do chuveiro, não sobre o restante da casa. Emissões de fabricação não foram estimadas por falta de dado confiável.
- **Cálculo:** consumo do chuveiro 70,4 kWh/mês × 12 × fração solar 70% = 591 kWh/ano.

### C. Energia solar fotovoltaica

4 painéis (2,20 kWp, ~10 m² de módulos) geram ~240 kWh/mês.

- **Condições:** Imóvel próprio, telhado com área e pouco sombreamento, e rede da distribuidora. Homologação do sistema na distribuidora antes de operar.
- **Limitações:** Você ainda paga o custo de disponibilidade (50 kWh/mês). A economia usa médias anuais; a geração varia ao longo do ano. Estimamos perda de ~15% da economia pela cobrança do Fio B (Lei 14.300). No Brasil a rede já é muito limpa: o ganho climático líquido é pequeno ou nulo.
- **Cálculo:** geração por kWp = HSP 4,6 × PR 0,78 × 30,4 = 109,1 kWh/mês/kWp. Alvo = 262 − 50 (disponibilidade) kWh/mês → 4 painéis de 550 Wp = 2,20 kWp. Economia = kWh compensados × tarifa × (1 − Fio B 15%).

### A+C. Pacote: eficiência + fotovoltaica

Primeiro reduz o consumo (A) e só depois dimensiona o solar: 4 painéis (2,20 kWp). Investimento R$ 9.996,00, economia R$ 2.205,00/ano.

## 4. Recomendação (coerente com os cálculos)

- 1º — Comece pela eficiência (A): custa pouco (R$ 96) e já reduz a conta.
- 2º — Energia solar fotovoltaica (alternativa C): retorno rápido, payback ≈ 4,2 anos com reajuste. Peça pelo menos 3 orçamentos.
- 3º — Aquecedor solar de água (alternativa B): retorno moderado, payback ≈ 7,5 anos com reajuste. Peça pelo menos 3 orçamentos.
- Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. Para A + C use o pacote, que dimensiona o solar depois da eficiência.

## 5. Impacto ambiental

Fator da rede: 0,0385 tCO₂/MWh (MCTI, 2023). Fator de ciclo de vida do painel: 0,041 tCO₂/MWh (IPCC, estimado). Como os dois são próximos, o ganho climático líquido da fotovoltaica no Brasil é pequeno ou nulo; o benefício principal é econômico. A eficiência energética é a alternativa com melhor equilíbrio entre custo e impacto.

## 6. Sensibilidade da fotovoltaica (C)

| Cenário | Tarifa | HSP | Custo R$/kWp | Payback c/ reajuste |
|---|---:|---:|---:|---:|
| Pessimista | R$ 0,85 | 4,2 | 5.500 | 5,8 anos |
| Base | R$ 1,00 | 4,6 | 4.500 | 4,2 anos |
| Otimista | R$ 1,15 | 5,0 | 3.800 | 3,2 anos |

Os cenários mostram que o payback depende muito de tarifa, irradiação e preço do sistema. Por isso o assistente apresenta faixas e pede orçamentos.

## 7. Rastreabilidade dos dados

Todos os parâmetros estão em `data/parametros.json` com **unidade, tipo (oficial/estimado/físico), fonte e observação**. Veja `docs/03_REFERENCIAS_E_LIMITACOES.md`.

> ⚠ Estimativas, não garantias. Confirme com a conta de luz e orçamentos de instaladores.

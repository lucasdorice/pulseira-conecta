# Referências e Limitações

Fontes consultadas em **18/11/2026**. Os parâmetros estão em `data/parametros.json`, com tipo (oficial, estimado ou físico) e fonte.

## 1. Fontes e o que foi usado

| Dado | Valor usado | Tipo | Fonte (conferir) |
|---|---|---|---|
| Bandeira tarifária | Verde em novembro/2026; amarela +R$ 1,885, vermelha 1 +R$ 4,463 e vermelha 2 +R$ 7,877 por 100 kWh | Oficial | ANEEL — Bandeiras Tarifárias: https://www.gov.br/aneel/pt-br/assuntos/tarifas/bandeiras-tarifarias (anúncio de 30/10/2026, divulgado pela Agência Brasil) |
| Reajuste Enel SP | ~9% para residencial de baixa tensão desde 04/07/2026 | Oficial (notícia) | ANEEL / imprensa (Exame, Gazeta SP, InfoMoney, jun/2026). Os veículos divulgaram 9,02% e 8,97%, então confira a Resolução Homologatória. |
| Tarifa R$/kWh | R$ 1,00 | **Estimado** | Valor ilustrativo. **Use o da sua conta de luz** (R$ total ÷ kWh). |
| Fator de emissão da rede | 0,0385 tCO₂/MWh (2023) | Oficial | MCTI/SIRENE — fatores de emissão: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao |
| Fator de emissão 2025 (contexto) | 21,5 a 28,9 kg/MWh (jan–abr) | Oficial (notícia) | MCTI/SIRENE, via Canal Solar (jun/2025) |
| Ciclo de vida do painel FV | 0,041 tCO₂/MWh | Estimado | IPCC AR5 WGIII (2014), Anexo III — emissões de ciclo de vida por tecnologia |
| Irradiação (HSP) | 4,6 kWh/m²/dia | **Estimado** | CRESESB — SunData: https://cresesb.cepel.br/index.php?section=sundata (confirmar para o CEP) |
| Custo de disponibilidade | 30/50/100 kWh | Oficial | ANEEL — REN 1.000/2021 |
| Cobrança do Fio B | Perda de 15% da economia | **Estimado** | Lei 14.300/2022 (marco legal da geração distribuída); confirmar com a distribuidora |
| Custo FV | R$ 4.500/kWp | **Estimado** | Faixa de mercado; cotar com 3 integradores |
| Custo aquecedor solar | R$ 1.000 + R$ 1.100 por pessoa | **Estimado** | Premissa; cotar |
| Fração solar do aquecedor | 70% | **Estimado** | Faixa típica de 60 a 80% (INMETRO/PBE de coletores solares) |
| Potência de aparelhos | Ver `data/equipamentos.csv` | **Estimado** | Tabelas INMETRO/PBE e Procel; usar a etiqueta do aparelho real |
| Calor específico da água | 4,186 kJ/(kg·K) | Físico | Constante física |

## 2. Referências de apoio (leitura)

- ANEEL — Tarifas e bandeiras: https://www.gov.br/aneel
- MCTI — SIRENE: https://www.gov.br/mcti
- CRESESB/CEPEL — Atlas e SunData: https://cresesb.cepel.br
- Procel/Eletrobras — Selo Procel e Pesquisa de Posses e Hábitos de Uso (PPH): https://www.gov.br/mme (programa Procel)
- INMETRO — Programa Brasileiro de Etiquetagem (PBE): https://www.gov.br/inmetro
- Lei nº 14.300/2022 — Marco legal da microgeração e minigeração distribuída
- IPCC (2014), AR5 WG III, Annex III — Technology-specific cost and performance parameters

## 3. Limitações do modelo

1. **Médias anuais.** Não simula mês a mês. Consumo (ar-condicionado, chuveiro) e geração solar variam com a estação.
2. **Tarifa única.** Não separa TE, TUSD, impostos, Tarifa Branca nem Tarifa Social. Os adicionais de bandeira são contados antes dos tributos.
3. **Preços de mercado variam muito.** Custo de painel, instalação e aquecedor solar são estimativas; orçamentos reais mudam o payback.
4. **Fio B aproximado.** A perda de 15% é uma simplificação; o valor real depende da distribuidora e da data de homologação.
5. **Sem sombreamento, orientação do telhado e inclinação.** Estão embutidos de forma genérica no PR.
6. **Sem financiamento, inflação geral e valor presente.** O saldo em 10 anos é uma soma simples, sem desconto.
7. **O reajuste de 6% ao ano é uma premissa de cenário.** Não é previsão.
8. **Troca de inversor** (~10 a 15 anos) e manutenção não entram no custo.
9. **CO₂:** fator médio anual da rede, não marginal. No Brasil o ganho climático da economia de eletricidade é pequeno porque a matriz é majoritariamente renovável.
10. **Alternativa B** usa fração solar fixa e ignora perdas do reservatório e o impacto do inverno.
11. **Família de exemplo é fictícia.** Os resultados valem para aquele perfil e não generalizam.
12. **Não substitui** projeto de engenharia, laudo ou orçamento profissional.

## 4. Uso de IA generativa

Ferramentas de IA generativa auxiliaram na estruturação do código e dos textos. Dados, cálculos e referências foram verificados pelo grupo, e os testes em `tests/test_energia.py` trazem contas conferíveis manualmente.

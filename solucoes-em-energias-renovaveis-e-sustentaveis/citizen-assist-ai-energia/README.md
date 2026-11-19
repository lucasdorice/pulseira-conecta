# Citizen Assist AI — Módulo de Energia e Sustentabilidade

**Global Solution 2026/2 · FIAP · Disciplina: Soluções em Energias Renováveis e Sustentáveis**

> Contribuição desta disciplina ao projeto **Citizen Assist AI**. Se o repositório for compartilhado com outras disciplinas, tudo desta disciplina está nas pastas `energia/`, `data/`, `docs/`, `tests/` e `testes_usuarios/`.

# Integrantes
| Nome completo             | RM      |
|---------------------------|---------|
| Arthur Primo Brandão      | 573572  |
| Leandro Cavaccini Brito   | 570556  |
| Lucas Dorice Dos Santos   | 568692  |

## Público e problema
**Público:** famílias que moram em residências urbanas (referência: Grande São Paulo).
**Problema:** a conta de luz sobe (reajuste de ~9% na Enel SP em jul/2026) e as famílias não sabem onde gastam, quanto custa cada hábito nem se vale a pena investir em energia solar.
**Necessidade energética:** reduzir o gasto mensal de eletricidade da residência.

## Funcionalidades de energia
- **Onde gasto mais?** Ranking de consumo por aparelho (kWh/mês e R$/mês), com `E = P × t`.
- **Chuveiro e simulador "e se?":** ex.: "e se eu tomar banho de 5 minutos?".
- **Comparação de alternativas** para a mesma necessidade e o mesmo período (12 meses e 10 anos):
  A) eficiência e hábitos · B) aquecedor solar (**renovável**) · C) fotovoltaica (**renovável**) · A+C.
  Para cada uma: custo, economia, payback (com e sem reajuste), saldo em 10 anos, CO₂ e viabilidade.
- **Recomendação em ordem de prioridade**, coerente com os cálculos.
- **Bandeira tarifária, impacto ambiental, fontes e limitações** em qualquer momento.
- Todo número vem do motor de cálculo e é marcado como **oficial** ou **estimado**.

## Como executar
Requer Python 3.10+ (sem dependências externas).
```bash
python main.py --demo                # demonstração com família de exemplo
python main.py                       # modo interativo (monte o perfil da sua casa)
python main.py --perfil perfil_exemplo.json
python main.py --relatorio-docs      # regenera docs/02_ANALISE_E_CALCULOS.md
python -m unittest discover -s tests -v   # testes automatizados
```
Exemplos de perguntas: *"Onde eu gasto mais energia?"*, *"E se eu tomar banho de 5 minutos?"*,
*"Vale a pena instalar energia solar?"*, *"Comparar as alternativas"*, *"Qual o impacto ambiental?"*, *"Quais são as fontes e limitações?"*.

## Estrutura
```
main.py                      entrada do assistente (terminal)
energia/                     código: dados, calculos, alternativas, assistente, relatorio
data/parametros.json         parâmetros com unidade, tipo (oficial/estimado), fonte e observação
data/equipamentos.csv        potências típicas (estimadas) de aparelhos
docs/01_DOCUMENTO_EXPLICATIVO.md   o que foi produzido e como funciona
docs/02_ANALISE_E_CALCULOS.md      análise e comparação (gerado pelo código)
docs/03_REFERENCIAS_E_LIMITACOES.md fontes verificáveis e limitações
docs/04_TESTES_COM_USUARIOS.md     roteiro e registro dos testes
docs/06_IDEIAS_EXTRAS.md           ideias além do pedido
docs/07_TESTES_DE_CENARIOS.md      testes internos de cenários (NÃO são testes com usuários)
scripts/testar_cenarios.py   gera o documento acima
tests/                       testes automatizados (30)
testes_usuarios/             registros dos testes com usuários
```

## Principais resultados (família de exemplo, dados estimados)
| Alternativa | Investimento | Economia/ano | Payback c/ reajuste |
|---|---:|---:|---:|
| A. Eficiência e hábitos | R$ 96 | R$ 298 | 0,3 ano |
| B. Aquecedor solar | R$ 5.400 | R$ 591 | 7,5 anos |
| C. Fotovoltaica | R$ 9.900 | R$ 2.160 | 4,2 anos |

Detalhes, fórmulas e sensibilidade em `docs/02_ANALISE_E_CALCULOS.md`.

## Limitações (resumo)
Estimativas, não garantias. Usa médias anuais; tarifa, preços e irradiação são estimados para a Grande SP; não considera sombreamento nem financiamento; o ganho de CO₂ é pequeno porque a rede brasileira já é limpa. Lista completa em `docs/03_REFERENCIAS_E_LIMITACOES.md`.

## Uso de IA generativa
Ferramentas de IA generativa auxiliaram na estruturação do código e dos documentos. O grupo verificou dados, cálculos e referências (ver `tests/`) e responde pelas decisões do projeto.

# Documento Explicativo — Módulo de Energia do Citizen Assist AI

**Disciplina:** Soluções em Energias Renováveis e Sustentáveis · **Projeto:** Global Solution 2026/2 (FIAP)
**Público:** famílias moradoras de residências urbanas (referência: Grande São Paulo)

> Este documento descreve o que foi produzido e como a aplicação funciona. Os números exatos ficam em `docs/02_ANALISE_E_CALCULOS.md`, gerado pelo próprio código.

---

## 1. Problema e contexto

As cidades concentram consumo de eletricidade, e a conta de luz pesa no orçamento das famílias: as tarifas residenciais da Enel SP subiram cerca de 9% em julho de 2026, depois de 13,94% em 2025. Muitas famílias não sabem **onde** gastam energia, **quanto** custa cada hábito ou aparelho e **se compensa** investir em alternativas como energia solar.

**Necessidade energética escolhida:** *reduzir o gasto mensal de eletricidade da residência*. O chuveiro elétrico costuma ser o maior consumidor de uma casa brasileira, por isso ele recebe atenção especial.

**Como o assistente contribui:** a família informa seu perfil (pessoas, banho, aparelhos, tarifa). O assistente mostra onde a energia é gasta, compara alternativas com cálculos e diz o que fazer primeiro, sempre com fontes e limitações.

## 2. O que foi produzido

| # | Entregável | Arquivo / pasta | Requisito atendido |
|---|---|---|---|
| 1 | Assistente em Python (terminal) | `main.py`, `energia/assistente.py` | Integração ao assistente |
| 2 | Motor de cálculo (energia, custo, solar, payback, CO₂) | `energia/calculos.py` | Análise de consumo |
| 3 | Comparação de alternativas | `energia/alternativas.py` | Comparação de alternativas |
| 4 | Base de dados com origem e tipo (oficial/estimado) | `data/parametros.json`, `data/equipamentos.csv` | Dados com origem e premissas |
| 5 | Relatório de análise gerado pelo código | `docs/02_ANALISE_E_CALCULOS.md` | Cálculos e justificativas |
| 6 | Referências e limitações | `docs/03_REFERENCIAS_E_LIMITACOES.md` | Referências e limitações |
| 7 | Plano e registro de testes com usuários | `docs/04_TESTES_COM_USUARIOS.md`, `testes_usuarios/` | Testes com usuários |
| 8 | Testes automatizados | `tests/` | Confiabilidade dos cálculos |
| 9 | Ideias extras / backlog | `docs/06_IDEIAS_EXTRAS.md` | Diferencial |
| 10 | README | `README.md` | README do repositório |

## 3. Como a aplicação funciona

```
 Família ──► perfil (pessoas, banho, aparelhos, tarifa, imóvel)
                │
                ▼
        energia/dados.py ──► data/parametros.json  (cada número com unidade,
                │                                   fonte e tipo: oficial/estimado)
                ▼
        energia/calculos.py     E = P × t · custo · geração solar · payback · CO₂
                │
                ▼
        energia/alternativas.py   A) Eficiência   B) Aquecedor solar   C) Fotovoltaica
                │                 + pacote recomendado (A → C)
                ▼
        energia/assistente.py   interpreta a pergunta, usa os resultados,
                │               responde com fontes e limitações
                ▼
        Terminal (main.py)  ──► respostas em linguagem simples + relatório .md
```

**Princípio central:** o assistente **não inventa números**. Toda resposta sai do motor de cálculo e termina com o tipo do dado (oficial ou estimado), a fonte e a limitação. Isso garante coerência entre análise e assistente.

### 3.1 Fluxo de uso
1. O usuário informa o perfil ou usa o perfil de exemplo (`--demo`).
2. O assistente calcula o consumo mensal por aparelho e o ranking de "vilões".
3. O usuário pergunta em linguagem natural ("quanto gasto com chuveiro?", "vale a pena energia solar?", "e se eu tomar banho de 5 min?").
4. O assistente identifica a intenção, calcula e responde, com aviso de que é estimativa.
5. O usuário pode gerar um relatório em Markdown para levar a um instalador.

### 3.2 Fórmulas
- **Energia:** `E (kWh) = P (kW) × t (h)`
- **Custo:** `R$ = kWh × (tarifa + bandeira/100)`
- **Solar fotovoltaico:** `geração/mês por kWp = HSP × PR × 30,4`; `kWp = (consumo − custo de disponibilidade) ÷ geração por kWp`
- **Aquecedor solar:** `economia = kWh do chuveiro × fração solar`
- **Payback:** soma da economia anual (com reajuste da tarifa e degradação, quando houver) até igualar o investimento
- **CO₂:** `kWh × fator de emissão da rede (MCTI)`
- **Verificação física do chuveiro:** `Q = m·c·ΔT` deve bater com `P × t`

## 4. Alternativas comparadas (mesma necessidade, mesmo período)

Todas as alternativas respondem à mesma pergunta: **"quanto posso reduzir da conta de luz em 12 meses e em 10 anos, e a que custo?"**

| Alternativa | Tipo | Ideia |
|---|---|---|
| **A. Eficiência e hábitos** | Economia | Banho 2 min mais curto + troca de lâmpadas por LED |
| **B. Aquecedor solar de água** | **Renovável** | Substitui parte do chuveiro elétrico |
| **C. Fotovoltaica residencial** | **Renovável** | Gera parte da energia da casa |
| **Pacote A + C** | Combinação | Reduz o consumo primeiro e dimensiona o solar menor |

Para cada uma o assistente mostra investimento, economia anual, payback simples e com reajuste, saldo em 10 anos, CO₂ evitado, viabilidade e limitações.

## 5. Honestidade técnica (diferencial)

- **Dados estimados são marcados como tal** e têm sugestão de onde conferir.
- **O ganho climático é pequeno no Brasil**, porque a rede já é muito renovável (0,0385 tCO₂/MWh em 2023, segundo o MCTI). O assistente explica que o ganho principal é **financeiro**, e não promete benefício ambiental inflado.
- **As economias das alternativas não se somam.** O pacote A + C recalcula o solar depois da eficiência.
- **Nada é garantia.** O assistente fala em "estimativa", "cenário" e "confirme com orçamento".

## 6. Testes com usuários (plano)

Cada participante realiza 3 tarefas (descobrir o maior gasto, entender se vale a pena solar, simular banho menor) e responde perguntas de compreensão e utilidade, sem registro de dados pessoais. O protocolo e o registro (situação, comentário, ajuste) estão em `docs/04_TESTES_COM_USUARIOS.md` e `testes_usuarios/`.


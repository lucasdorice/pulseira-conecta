# Pulseira CONECTA· Mobilidade Urbana Inteligente

**Global Solution FIAP 2026 · Tema CitizenTech**
Disciplina: Modelagem Matemática e Computacional · Curso: Ciência da Computação

| Integrante | RM |
|---|---|
| Arthur Primo Brandão | 573572 |
| Leandro Cavaccini Brito | 570556 |
| Lucas Dorice dos Santos | 568692 |



---

## 1. O projeto (ideia do grupo)

### Problema
Pessoas com deficiência física ou mental e idosos podem ter dificuldade de carregar, enxergar ou apresentar documentos e de usar o transporte público (pagar a passagem, validar bilhete, comprovar gratuidade). Para o cidadão em geral, há ainda o incômodo de carregar vários documentos, recarregar bilhetes e não conseguir localizar um familiar quando necessário.

### Solução proposta
Uma **pulseira de silicone com chip NFC** (resistente, confortável, sem bateria) integrada a um aplicativo/site próprio e seguro, que concentra:

- **Documentos:** armazenamento e apresentação segura (RG, CPF, CNH, carteirinhas, laudos, cartão de gratuidade).
- **Saldo de transporte público:** pagamento por aproximação da pulseira.
- **Rastreio:** localização de filhos, parentes ou pessoas sob cuidado, com consentimento.

### Público e ecossistema
- **Primário:** pessoas com deficiência com dificuldade de carregar documentos ou usar transporte.
- **Secundário:** qualquer cidadão que queira reunir documentos, pagar transporte com facilidade e acompanhar familiares.
- **Rede de apoio:** responsáveis, familiares e cuidadores.
- **Ecossistema:** operadoras de transporte, poder público (secretarias de transporte e de pessoas com deficiência), organizações de apoio a PcD, serviços de saúde e emergência, e a equipe que opera a plataforma.

### Pontos críticos já mapeados
LGPD e dados sensíveis, ética no rastreio, segurança do NFC (o chip guarda apenas um token, nunca os documentos), validade legal dos documentos digitais, integração com bilhetagem e modelo de negócio. Esses pontos serão tratados nos demais entregáveis do projeto.

### ODS
| ODS | Contribuição |
|---|---|
| 10 · Redução das desigualdades | Inclusão de pessoas com deficiência no acesso a serviços e mobilidade |
| 11 · Cidades e comunidades sustentáveis | Transporte público acessível e cidades mais inclusivas |
| 3 · Saúde e bem-estar | Segurança de pessoas vulneráveis |
| 9 · Indústria, inovação e infraestrutura | NFC/IoT aplicados a serviços públicos |

---

## 2. A entrega desta etapa

Esta entrega responde ao desafio proposto pelo professor da disciplina **Modelagem Matemática e Computacional**: *Mobilidade Urbana Inteligente: Modelagem Matemática para a Gestão do Transporte Público*.

Uma empresa municipal de ônibus perdeu o registro de quantos veículos há em cada centro operacional (Norte, Sul, Leste, Oeste). Cabe à equipe:

1. **Etapa 1:** reconstruir a distribuição atual da frota a partir de indicadores consolidados (sistema linear).
2. **Etapa 2:** propor uma política de redistribuição baseada em **transformação linear**, comprovando que preserva o total de ônibus e não gera alocações negativas.

Tudo é implementado em **Python** e documentado no notebook, com a justificativa matemática de cada passo.

### Como ela se conecta ao projeto CitizenTech
A pulseira registra validações de embarque por região e horário. Esses dados substituiriam pesquisas pontuais de demanda (como o Relatório II do enunciado) por dados contínuos. O modelo desta entrega é a **camada de decisão**: dado quanta demanda há em cada região, calcula como realocar a frota para atendê-la, apoiando os ODS 11, 10 e 9.

### Resultados

| | Norte | Sul | Leste | Oeste | Total |
|---|---:|---:|---:|---:|---:|
| Distribuição atual (Etapa 1) | 12 | 20 | 16 | 24 | 72 |
| Ônibus necessários (demanda ÷ 40) | 14 | 19 | 18 | 21 | 72 |
| Nova distribuição (Etapa 2) | 14 | 19 | 18 | 21 | 72 |

- **Etapa 1:** sistema com `det(A) = 3 ≠ 0`, `posto(A) = posto([A|b]) = 4`: **solução única**.
- **Etapa 2:** apenas **4 ônibus** são movidos (Oeste→Norte: 2, Oeste→Leste: 1, Sul→Leste: 1).
- **Impacto:** demanda atendida no pico de **94,4% para 100%** (160 passageiros sem vaga → 0).

Matriz da transformação (colunas = origem, linhas = destino; ordem Norte, Sul, Leste, Oeste):

```
        | 1     0      0     1/12 |
    M = | 0    19/20   0      0   |
        | 0    1/20    1     1/24 |
        | 0     0      0     7/8  |
```

Cada coluna soma 1 (total preservado) e todos os coeficientes são ≥ 0 (nenhuma alocação negativa).

---

## 3. Estrutura do repositório

```
.
├── global_solution_mobilidade_urbana.ipynb   # entrega principal (modelo, código, demonstrações)
├── README.md                                 # este arquivo

```

## 4. Como executar

Requer Python 3.9+.

```bash
pip install numpy sympy matplotlib jupyter
jupyter notebook global_solution_mobilidade_urbana.ipynb
```

Depois, no menu: *Kernel → Restart & Run All*. O notebook já acompanha as saídas da última execução.

**Tecnologias:** Python, NumPy (álgebra linear numérica), SymPy (cálculo exato com frações), Matplotlib (gráfico).

## 5. Limitações e premissas

- Os dados do enunciado são hipotéticos e simplificados; consideramos um único horário de pico e que cada ônibus atende apenas a região onde está alocado.
- A matriz `M` foi calibrada para a distribuição atual. Aplicada a outras distribuições, preserva o total e não gera negativos, mas pode gerar valores fracionários que exigiriam arredondamento na prática.
- Existem outras políticas válidas; a escolhida minimiza o número de ônibus movidos e de rotas.

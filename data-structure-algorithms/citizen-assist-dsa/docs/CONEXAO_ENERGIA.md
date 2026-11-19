# Conexão com Energias Renováveis e Sustentáveis (SERS)

> Este módulo faz parte do projeto de **DSA** e é um **extra opcional**. Ele **não é a entrega** da disciplina de Soluções em Energias Renováveis e Sustentáveis, que tem entregáveis próprios (repositório, vídeo e arquivo de entrega). A ligação entre as duas disciplinas é de **conteúdo**: conceitos de energia viram dados e algoritmos de estruturas de dados.

O núcleo de DSA (CRUD, lista encadeada, busca, ordenação e Big-O) funciona sem este módulo e não depende dele.

## Conceitos de energia aplicados a estruturas de dados

| Conceito de SERS | Onde aparece | Estrutura e algoritmo | Custo |
|---|---|---|---|
| Matriz energética | `citizen_assist/energia/fonte.py` | lista encadeada de `FonteEnergia`; ordenação por participação com `merge_sort_por`; soma das renováveis por percurso | O(n log n) e O(n) |
| Potência e energia | `energia/aparelho.py` | lista encadeada de `Aparelho`; consumo mensal e ranking por `merge_sort_por` | O(n) e O(n log n) |
| Uso por demanda | `energia/demanda.py` | curva de 24 horas somando a potência ligada em cada hora; pico (busca do maior valor) e fator de carga | O(24·n) = O(n) |
| Orientações de energia | categoria **Energia** em `dados/servicos_exemplo.csv` | registros `Servico` com referência, aviso e alerta de desatualização; busca por categoria | O(n) |

## Fórmulas usadas

- Energia diária de um aparelho: E (kWh/dia) = P (W) ÷ 1000 × horas de uso por dia.
- Consumo mensal: E (kWh/mês) = E (kWh/dia) × 30 dias.
- Demanda em cada hora: soma da potência (kW) de cada aparelho multiplicada pela fração da hora em que ele fica ligado. Aparelhos que passam da meia-noite são tratados.
- Pico de demanda: maior valor da curva de 24 horas, com a primeira hora em que ocorre.
- Fator de carga = demanda média ÷ demanda de pico. Vale 1 para consumo constante e fica perto de 0 quando o consumo se concentra em poucas horas.
- Custo estimado (opcional) = consumo mensal × tarifa informada pelo usuário, sem impostos e sem adicional de bandeira.

A soma da curva de demanda é igual à energia diária total: isso é verificado nos testes.

## Como usar

- **Terminal:** `python main.py cli`, opção **10. Energia** (matriz energética, meus aparelhos, orientações).
- **Web:** `python main.py web`, página **/energia** (também no menu "Energia").

Nada do que o usuário digita é guardado, e nenhum dado pessoal é pedido.

## Situação dos dados

| Arquivo | Conteúdo | Situação |
|---|---|---|
| `dados/energia_matriz_exemplo.csv` | participação de cada fonte (%) | **valores ilustrativos**, a serem substituídos pelos dados do Balanço Energético Nacional (EPE) |
| `dados/energia_aparelhos_exemplo.csv` | potência, horas e horário sugeridos | **valores ilustrativos**, a conferir no rótulo ou nas tabelas do Procel e do INMETRO |
| `dados/servicos_exemplo.csv` (categoria Energia) | 5 orientações novas e a Tarifa Social corrigida | referências a conferir no site do órgão. Só a bandeira tarifária tem data de verificação |

A interface mostra o aviso "dado de exemplo" enquanto a coluna `situacao` do CSV for `exemplo`.

Sobre a Tarifa Social de Energia Elétrica: reportagens indicam que as regras mudaram em 2026 e ainda circulam textos com a regra antiga. O registro do catálogo foi reescrito sem números e **sem data de verificação**, para a interface alertar o usuário. A regra vigente deve ser confirmada na Aneel.

## Limitações

- Estimativas: o consumo real depende do estado do aparelho, do uso e do ciclo de funcionamento (a geladeira, por exemplo, é representada por uma potência média).
- A curva de demanda usa a hora de início e as horas de uso; não representa o uso real minuto a minuto.
- O módulo não compara alternativas de fornecimento (por exemplo, solar) nem calcula custos de investimento: isso é trabalho da disciplina de SERS.

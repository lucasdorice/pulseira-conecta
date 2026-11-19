# Algoritmos de busca e ordenação, e análise Big-O

**Hipóteses.** *n* = número de nós da lista. Os campos de texto têm tamanho limitado pela validação (no máximo 300 caracteres), então a comparação de **ids** custa O(1) e a de **títulos** custa O(1) em termos de *n* (há uma constante por limite de tamanho). *L* = tamanho do texto comparado e *m* = tamanho do termo pesquisado. Como a lista encadeada não permite acesso por índice, toda localização exige percorrer nós a partir de `inicio`.

## 1. Busca

### 1.1 Busca linear por ID (`ListaEncadeada.buscar_por_id`)
Percorre os nós do início ao fim comparando `dados.id` e para no primeiro que coincide. Melhor caso O(1) (primeiro nó), **pior e médio O(n)**. Busca binária não se aplica: exigiria acesso por índice em O(1).

### 1.2 Pesquisa por trecho (`algoritmos.pesquisar`)
Para cada nó, normaliza o texto (minúsculas, sem acentos) e procura o termo com a função `contem`, uma busca ingênua de substring escrita à mão (alinha o termo em cada posição e compara caractere a caractere). Devolve uma nova lista encadeada com os resultados.
- `normalizar`: O(L).
- `contem`: O(L·m) no pior caso.
- Pesquisa completa: **O(n·L·m)**. Como *L* e *m* são limitados (textos de até 300 e termos de até 80 caracteres), na prática cresce linearmente com *n*.

## 2. Ordenação

### 2.1 Merge sort sobre a lista encadeada (`merge_sort`)
1. **Dividir:** dois ponteiros (lento e rápido) acham o meio da cadeia e cortam em duas metades: O(n).
2. **Ordenar** cada metade recursivamente.
3. **Intercalar:** percorre as duas cadeias já ordenadas e religa os nós na ordem certa (sem criar novos nós de dados): O(n).
4. `refazer_fim` atualiza o ponteiro `fim`: O(n).

São log₂ n níveis de recursão com trabalho O(n) cada: **O(n log n) em todos os casos** (melhor, médio e pior). Espaço extra: O(log n) de pilha de recursão. É **estável** (empates mantêm a ordem original), pois, em caso de empate, o nó da metade esquerda vem primeiro. Cada comparação por título normaliza as strings, custo constante dado o limite de tamanho.

### 2.2 Insertion sort (`insertion_sort`), usado como comparativo
Pega cada nó da cadeia original e o religa na posição certa de uma cadeia já ordenada, procurando a posição a partir do início da cadeia ordenada.
- **Pior caso O(n²)** (entrada já ordenada: cada nó percorre toda a cadeia ordenada até o fim).
- **Melhor caso O(n)** (entrada em ordem oposta à pedida: cada nó entra no início).
- Espaço extra O(1). Também é estável.

## 3. Custo das operações exigidas

| Operação | Como o código faz | Custo (pior caso) |
|---|---|---|
| Inserção ligada ao fim | `inserir_fim_sem_verificar`: usa `fim` | **O(1)** |
| Inserção com id único | `validar_id` e `inserir` percorrem a lista procurando o id antes de ligar | **O(n)** |
| Busca por id | linear | **O(n)** |
| Pesquisa por título/categoria/texto | linear com substring própria | **O(n·L·m)**, ≈ O(n) com *L* e *m* limitados |
| Consulta/atualização | busca do nó + troca de dados O(1) | **O(n)** |
| Exclusão | percorre guardando o nó anterior; religar é O(1) | **O(n)** |
| Listagem | percorre todos os nós | **O(n)** |
| Ordenação (merge sort) | divide, ordena, intercala | **O(n log n)** |
| Ordenação (insertion sort) | insere em cadeia ordenada | **O(n²)** |
| Web: `/servicos` | copia a lista O(n) e ordena a cópia com merge sort | **O(n log n)** |
| Web: `/servicos/<id>` | busca por id | **O(n)** |

A inserção "pura" é O(1) porque a lista mantém o ponteiro `fim`; o programa, porém, sempre valida o id antes de inserir, e por isso o cadastro real custa O(n).

### Custo das operações do módulo de energia

| Operação | Como o código faz | Custo (pior caso) |
|---|---|---|
| Ordenar por qualquer campo | `merge_sort_por(lista, chave, decrescente)`: o mesmo merge sort, com a chave recebida como função | **O(n log n)** |
| Total de fontes renováveis | percorre a lista somando | **O(n)** |
| Consumo total mensal | percorre a lista dos aparelhos | **O(n)** |
| Ranking por consumo | copia a lista (O(n)) e ordena a cópia | **O(n log n)** |
| Curva de demanda | para cada aparelho, soma sua contribuição às 24 horas | **O(24·n) = O(n)** |
| Pico e fator de carga | varre as 24 posições da curva | **O(24) = O(1)** em relação a *n* |

Os aparelhos ficam em lista encadeada; a curva de 24 horas é uma sequência de tamanho fixo, pois o número de horas do dia não muda.

## 4. Verificação experimental
O comando de relatórios do terminal (opção 9) e a página `/indicadores` da web rodam `benchmark`, que gera listas fictícias com ids embaralhados e mede o tempo das duas ordenações. Resultado de uma execução (tempos variam por computador):

| n | Merge sort (ms) | Insertion sort (ms) |
|---|---|---|
| 500 | 4,97 | 37,28 |
| 1000 | 10,90 | 153,16 |
| 2000 | 23,84 | 647,03 |
| 4000 | 50,19 | 2565,60 |

Cada vez que *n* dobra, o merge sort pouco mais que dobra o tempo (≈ n log n), enquanto o insertion sort multiplica por cerca de 4 (≈ n²), como a análise prevê.

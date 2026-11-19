# Relatório de testes e evidências

Gerado em 18/11/2026 19:52 por `python gerar_evidencias.py`.
Resultado: **25 de 25 cenários aprovados**.

Os cenários de terminal usam a lista de exemplo (5 serviços: IDs 3, 1, 5, 2, 4) ou lista vazia, conforme indicado. Cada bloco mostra a entrada digitada, o esperado, o observado e a saída real do programa. Os cenários T1 e T2 cobrem operações sobre lista vazia.

| Cenário | Resultado |
|---|---|
| T1 · Listar com lista vazia | Aprovado |
| T2 · Consultar, atualizar, excluir, pesquisar e ordenar com lista vazia | Aprovado |
| T3 · Cadastrar 5 serviços válidos e listar | Aprovado |
| T4 · Cadastrar com ID duplicado | Aprovado |
| T5 · Cadastrar com campo obrigatório vazio | Aprovado |
| T6 · ID com letras, negativo, zero e acima do limite | Aprovado |
| T7 · Consultar ID existente e inexistente | Aprovado |
| T8 · Atualizar o título do serviço 3 | Aprovado |
| T9 · Excluir primeiro (3), meio (5) e último (4) nós | Aprovado |
| T9b · Excluir e cancelar a confirmação | Aprovado |
| T10 · Pesquisar com resultado e sem resultado | Aprovado |
| T11 · Ordenar por título (merge sort) e por ID decrescente (insertion sort) | Aprovado |
| T12 · Opções de menu inválidas | Aprovado |
| T13 · Salvar, sair, reabrir e carregar | Aprovado |
| T18 · Energia: matriz energética ordenada, com total de renováveis | Aprovado |
| T19 · Energia: consumo, ranking e demanda de 2 aparelhos (valores sugeridos) | Aprovado |
| T20 · Energia: entradas inválidas na escolha de aparelhos | Aprovado |
| T21 · Energia: nenhum aparelho escolhido | Aprovado |
| T22 · Energia: orientações da categoria Energia no catálogo | Aprovado |
| T14 · Suíte automatizada (pytest) | Aprovado |
| T15 · Web: entrar, cadastrar, pesquisar e ordenar | Aprovado |
| T16 · Web: campo vazio, ID duplicado e ID inexistente | Aprovado |
| T17 · Web: acessar páginas de administrador sem entrar | Aprovado |
| T23 · Web: página /energia (matriz) e cálculo de consumo e demanda | Aprovado |
| T24 · Web: energia com dados inválidos e sem aparelho marcado | Aprovado |

## T1 · Listar com lista vazia

**Entrada**

```
3
0
```

**Resultado esperado**

```
Nenhum serviço cadastrado.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 3
Nenhum serviço cadastrado.
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T2 · Consultar, atualizar, excluir, pesquisar e ordenar com lista vazia

**Entrada**

```
2
4
5
6
7
0
```

**Resultado esperado**

```
Nenhum serviço cadastrado.
Nenhum serviço cadastrado para atualizar.
Nenhum serviço cadastrado para excluir.
Nenhum serviço cadastrado para pesquisar.
Nenhum serviço cadastrado para ordenar.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 2
Nenhum serviço cadastrado.
[... menu principal ...]
Escolha uma opção: 4
Nenhum serviço cadastrado para atualizar.
[... menu principal ...]
Escolha uma opção: 5
Nenhum serviço cadastrado para excluir.
[... menu principal ...]
Escolha uma opção: 6
Nenhum serviço cadastrado para pesquisar.
[... menu principal ...]
Escolha uma opção: 7
Nenhum serviço cadastrado para ordenar.
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T3 · Cadastrar 5 serviços válidos e listar

**Entrada**

```
1
1
Vacinação
Saúde
Descrição de Vacinação
Qualquer cidadão
Balcão de atendimento




1
2
RG
Documentos
Descrição de RG
Qualquer cidadão
Balcão de atendimento




1
3
Matrícula
Educação
Descrição de Matrícula
Qualquer cidadão
Balcão de atendimento




1
4
CadÚnico
Assistência social
Descrição de CadÚnico
Qualquer cidadão
Balcão de atendimento




1
5
Ouvidoria
Atendimento comunitário
Descrição de Ouvidoria
Qualquer cidadão
Balcão de atendimento




3
0
n
```

**Resultado esperado**

```
Serviço 1 cadastrado com sucesso.
Serviço 5 cadastrado com sucesso.
Serviços cadastrados (5)
Vacinação
Ouvidoria
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 1
Título: Vacinação
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 1 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 2
Título: RG
Categoria: Documentos
Descrição: Descrição de RG
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 2 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 3
Título: Matrícula
Categoria: Educação
Descrição: Descrição de Matrícula
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 3 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 4
Título: CadÚnico
Categoria: Assistência social
Descrição: Descrição de CadÚnico
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 4 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 5
Título: Ouvidoria
Categoria: Atendimento comunitário
Descrição: Descrição de Ouvidoria
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 5 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 3

Serviços cadastrados (5)
[  1] Vacinação - Saúde  [verificar atualização]
[  2] RG - Documentos  [verificar atualização]
[  3] Matrícula - Educação  [verificar atualização]
[  4] CadÚnico - Assistência social  [verificar atualização]
[  5] Ouvidoria - Atendimento comunitário  [verificar atualização]
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!
```

## T4 · Cadastrar com ID duplicado

**Entrada**

```
1
1
Vacinação
Saúde
Descrição de Vacinação
Qualquer cidadão
Balcão de atendimento




1
1
2
RG
Documentos
Descrição de RG
Qualquer cidadão
Balcão de atendimento




3
0
n
```

**Resultado esperado**

```
Já existe um serviço com o ID 1.
Serviço 2 cadastrado com sucesso.
Serviços cadastrados (2)
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 1
Título: Vacinação
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 1 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 1
Já existe um serviço com o ID 1.
ID: 2
Título: RG
Categoria: Documentos
Descrição: Descrição de RG
Público-alvo: Qualquer cidadão
Canal ou local de atendimento: Balcão de atendimento
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 2 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 3

Serviços cadastrados (2)
[  1] Vacinação - Saúde  [verificar atualização]
[  2] RG - Documentos  [verificar atualização]
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!
```

## T5 · Cadastrar com campo obrigatório vazio

**Entrada**

```
1
1

   
Título válido
Cat
Desc
Todos
Balcão




0
n
```

**Resultado esperado**

```
O campo "Título" é obrigatório.
Serviço 1 cadastrado com sucesso.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: 1
Título: 
O campo "Título" é obrigatório.
Título:    
O campo "Título" é obrigatório.
Título: Título válido
Categoria: Cat
Descrição: Desc
Público-alvo: Todos
Canal ou local de atendimento: Balcão
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 1 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!
```

## T6 · ID com letras, negativo, zero e acima do limite

**Entrada**

```
1
abc
-5
0
9999999
7
T
C
D
P
L




0
n
```

**Resultado esperado**

```
O ID deve ser um número inteiro positivo
O ID deve ser maior que zero.
O ID deve ter no máximo
Serviço 7 cadastrado com sucesso.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 1

Cadastro de serviço (digite /cancelar para voltar)
ID: abc
O ID deve ser um número inteiro positivo (ex.: 12).
ID: -5
O ID deve ser um número inteiro positivo (ex.: 12).
ID: 0
O ID deve ser maior que zero.
ID: 9999999
O ID deve ter no máximo 999999.
ID: 7
Título: T
Categoria: C
Descrição: D
Público-alvo: P
Canal ou local de atendimento: L
Referência (fonte da informação) (opcional): 
Última verificação (AAAA-MM-DD) (opcional): 
Aviso de limitação (opcional): 
Abrangência (urbano, rural ou ambos) (opcional): 
Serviço 7 cadastrado com sucesso.
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!
```

## T7 · Consultar ID existente e inexistente

**Entrada**

```
2
3
2
99
0
```

**Resultado esperado**

```
Título: Vacinação
Serviço com ID 99 não encontrado.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 2
ID do serviço (ou /cancelar): 3
------------------------------------------------------------
ID: 3
Título: Vacinação
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
[... menu principal ...]
Escolha uma opção: 2
ID do serviço (ou /cancelar): 99
Serviço com ID 99 não encontrado.
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T8 · Atualizar o título do serviço 3

**Entrada**

```
4
3
Vacinação infantil








2
3
0
n
```

**Resultado esperado**

```
Serviço 3 atualizado.
Título: Vacinação infantil
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 4
ID do serviço (ou /cancelar): 3
------------------------------------------------------------
ID: 3
Título: Vacinação
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
Pressione Enter para manter o valor atual; use - para limpar um campo opcional.
Título [Vacinação]: Vacinação infantil
Categoria [Saúde]: 
Descrição [Descrição de Vacinação]: 
Público-alvo [Qualquer cidadão]: 
Canal ou local de atendimento [Balcão de atendimento]: 
Referência (fonte da informação) []: 
Última verificação (AAAA-MM-DD) [2026-11-01]: 
Aviso de limitação []: 
Abrangência (urbano, rural ou ambos) [ambos]: 
Serviço 3 atualizado.
[... menu principal ...]
Escolha uma opção: 2
ID do serviço (ou /cancelar): 3
------------------------------------------------------------
ID: 3
Título: Vacinação infantil
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!
```

## T9 · Excluir primeiro (3), meio (5) e último (4) nós

**Entrada**

```
5
3
s
5
5
s
5
4
s
3
0
n
```

**Resultado esperado**

```
Serviço 3 excluído.
Serviço 5 excluído.
Serviço 4 excluído.
Serviços cadastrados (2)
Lista final contém os IDs [1, 2] e `fim` aponta para o ID 2
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 5
ID do serviço (ou /cancelar): 3
------------------------------------------------------------
ID: 3
Título: Vacinação
Categoria: Saúde
Descrição: Descrição de Vacinação
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
Excluir este serviço? (s/n): s
Serviço 3 excluído.
[... menu principal ...]
Escolha uma opção: 5
ID do serviço (ou /cancelar): 5
------------------------------------------------------------
ID: 5
Título: Matrícula
Categoria: Educação
Descrição: Descrição de Matrícula
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
Excluir este serviço? (s/n): s
Serviço 5 excluído.
[... menu principal ...]
Escolha uma opção: 5
ID do serviço (ou /cancelar): 4
------------------------------------------------------------
ID: 4
Título: Ouvidoria
Categoria: Atendimento comunitário
Descrição: Descrição de Ouvidoria
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
Excluir este serviço? (s/n): s
Serviço 4 excluído.
[... menu principal ...]
Escolha uma opção: 3

Serviços cadastrados (2)
[  1] RG - Documentos
[  2] CadÚnico - Assistência social
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!

[verificação no código] IDs = [1, 2], fim = 2, tamanho = 2
```

## T9b · Excluir e cancelar a confirmação

**Entrada**

```
5
1
n
3
0
```

**Resultado esperado**

```
Exclusão cancelada.
Serviços cadastrados (5)
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 5
ID do serviço (ou /cancelar): 1
------------------------------------------------------------
ID: 1
Título: RG
Categoria: Documentos
Descrição: Descrição de RG
Público-alvo: Qualquer cidadão
Canal/local: Balcão de atendimento
Abrangência: ambos
Referência: (não informada)
Aviso: (nenhum)
Verificação: última em 2026-11-01
------------------------------------------------------------
Excluir este serviço? (s/n): n
Exclusão cancelada.
[... menu principal ...]
Escolha uma opção: 3

Serviços cadastrados (5)
[  3] Vacinação - Saúde
[  1] RG - Documentos
[  5] Matrícula - Educação
[  2] CadÚnico - Assistência social
[  4] Ouvidoria - Atendimento comunitário
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T10 · Pesquisar com resultado e sem resultado

**Entrada**

```
6
1
VACINA
6
3
balcão
6
1
zzzz
6
1

xyz
0
```

**Resultado esperado**

```
Vacinação
Nenhum serviço encontrado para essa pesquisa.
Digite pelo menos uma letra para pesquisar.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 6
Pesquisar em:
  1. Título
  2. Categoria
  3. Título, categoria e descrição
Escolha (ou /cancelar): 1
Termo de pesquisa (ou /cancelar): VACINA

Resultados da pesquisa (1)
[  3] Vacinação - Saúde
(busca feita em 0.026 ms)
[... menu principal ...]
Escolha uma opção: 6
Pesquisar em:
  1. Título
  2. Categoria
  3. Título, categoria e descrição
Escolha (ou /cancelar): 3
Termo de pesquisa (ou /cancelar): balcão
Nenhum serviço encontrado para essa pesquisa.
(busca feita em 0.044 ms)
[... menu principal ...]
Escolha uma opção: 6
Pesquisar em:
  1. Título
  2. Categoria
  3. Título, categoria e descrição
Escolha (ou /cancelar): 1
Termo de pesquisa (ou /cancelar): zzzz
Nenhum serviço encontrado para essa pesquisa.
(busca feita em 0.011 ms)
[... menu principal ...]
Escolha uma opção: 6
Pesquisar em:
  1. Título
  2. Categoria
  3. Título, categoria e descrição
Escolha (ou /cancelar): 1
Termo de pesquisa (ou /cancelar): 
Digite pelo menos uma letra para pesquisar.
Termo de pesquisa (ou /cancelar): xyz
Nenhum serviço encontrado para essa pesquisa.
(busca feita em 0.010 ms)
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T11 · Ordenar por título (merge sort) e por ID decrescente (insertion sort)

**Entrada**

```
7
1
1
1
7
2
2
2
0
n
```

**Resultado esperado**

```
Serviços ordenados por titulo
Serviços ordenados por id
Ao final a lista está em ordem decrescente de ID: [5, 4, 3, 2, 1]
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 7
Ordenar por:
  1. Título
  2. ID
Escolha (ou /cancelar): 1
Sentido:
  1. Crescente
  2. Decrescente
Escolha (ou /cancelar): 1
Algoritmo:
  1. Merge sort (O(n log n))
  2. Insertion sort (O(n²))
Escolha (ou /cancelar): 1

Serviços ordenados por titulo (5)
[  2] CadÚnico - Assistência social
[  5] Matrícula - Educação
[  4] Ouvidoria - Atendimento comunitário
[  1] RG - Documentos
[  3] Vacinação - Saúde
(ordenação feita em 0.040 ms)
[... menu principal ...]
Escolha uma opção: 7
Ordenar por:
  1. Título
  2. ID
Escolha (ou /cancelar): 2
Sentido:
  1. Crescente
  2. Decrescente
Escolha (ou /cancelar): 2
Algoritmo:
  1. Merge sort (O(n log n))
  2. Insertion sort (O(n²))
Escolha (ou /cancelar): 2

Serviços ordenados por id (5)
[  5] Matrícula - Educação
[  4] Ouvidoria - Atendimento comunitário
[  3] Vacinação - Saúde
[  2] CadÚnico - Assistência social
[  1] RG - Documentos
(ordenação feita em 0.007 ms)
[... menu principal ...]
Escolha uma opção: 0
Há alterações não salvas. Salvar antes de sair? (s/n): n
Até logo!

[verificação no código] IDs = [5, 4, 3, 2, 1]
```

## T12 · Opções de menu inválidas

**Entrada**

```
x

99
-1
0
```

**Resultado esperado**

```
Opção inválida: use um número de 0 a 10.
Digite o número de uma opção.
Opção inexistente: use um número de 0 a 10.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: x
Opção inválida: use um número de 0 a 10.
[... menu principal ...]
Escolha uma opção: 
Digite o número de uma opção.
[... menu principal ...]
Escolha uma opção: 99
Opção inexistente: use um número de 0 a 10.
[... menu principal ...]
Escolha uma opção: -1
Opção inválida: use um número de 0 a 10.
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T13 · Salvar, sair, reabrir e carregar

**Entrada**

```
Sessão 1: 8, 1, 0 (salvar e sair)
Sessão 2 (lista vazia): 3, 8, 2, s, 3, 0
```

**Resultado esperado**

```
Dados salvos; sessão 2 começa vazia e, após carregar, lista 5 serviços
```

**Resultado observado:** Aprovado

**Saída**

```
--- Sessão 1 ---
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 8
Dados:
  1. Salvar em CSV
  2. Carregar do CSV (substitui a lista)
  3. Exportar JSON
Escolha (ou /cancelar): 1
Dados salvos em dados\servicos.csv
[... menu principal ...]
Escolha uma opção: 0
Até logo!

--- Sessão 2 ---
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 3
Nenhum serviço cadastrado.
[... menu principal ...]
Escolha uma opção: 8
Dados:
  1. Salvar em CSV
  2. Carregar do CSV (substitui a lista)
  3. Exportar JSON
Escolha (ou /cancelar): 2
Isso substitui os dados atuais. Continuar? (s/n): s
5 serviço(s) carregado(s).
[... menu principal ...]
Escolha uma opção: 3

Serviços cadastrados (5)
[  3] Vacinação - Saúde
[  1] RG - Documentos
[  5] Matrícula - Educação
[  2] CadÚnico - Assistência social
[  4] Ouvidoria - Atendimento comunitário
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T18 · Energia: matriz energética ordenada, com total de renováveis

**Entrada**

```
10
1
0
0
```

**Resultado esperado**

```
Matriz energética (do maior para o menor)
Hidrelétrica
Total de fontes renováveis: 84.0%
valores ilustrativos
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 10

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 1

Matriz energética (do maior para o menor)
  Hidrelétrica              55.0%  renovável
  Eólica                    14.0%  renovável
  Gás natural               10.0%  não renovável
  Solar                      8.0%  renovável
  Biomassa                   7.0%  renovável
  Nuclear                    2.0%  não renovável
  Carvão mineral             2.0%  não renovável
  Derivados de petróleo      2.0%  não renovável
Total de fontes renováveis: 84.0%
ATENÇÃO: valores ilustrativos (dado de exemplo). Substitua pelos dados oficiais da EPE antes de usar.

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 0
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T19 · Energia: consumo, ranking e demanda de 2 aparelhos (valores sugeridos)

**Entrada**

```
10
2
1



2




1
0
0
```

**Resultado esperado**

```
Consumo estimado: 171.0 kWh por mês
1. Chuveiro elétrico: 99.0 kWh/mês (58%)
2. Geladeira (potência média ao longo do dia): 72.0 kWh/mês (42%)
Pico de demanda: 3.40 kW às 06h
Custo estimado
Não é garantia
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 10

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 2

Aparelhos disponíveis (valores sugeridos, editáveis)
  1. Chuveiro elétrico - 5500 W, 0.6 h/dia, liga às 6h
  2. Geladeira (potência média ao longo do dia) - 100 W, 24 h/dia, liga às 0h
  3. Televisão - 100 W, 5 h/dia, liga às 19h
  4. Lâmpadas de LED (conjunto da casa) - 45 W, 5 h/dia, liga às 18h
  5. Ferro de passar roupa - 1000 W, 1 h/dia, liga às 14h
  6. Máquina de lavar roupa - 500 W, 1 h/dia, liga às 10h
  7. Ventilador - 80 W, 6 h/dia, liga às 13h
  8. Micro-ondas - 1200 W, 0.3 h/dia, liga às 12h
  9. Computador ou notebook - 80 W, 4 h/dia, liga às 20h

Escolha os aparelhos da sua casa (Enter sem número para calcular; /cancelar para voltar).
Número do aparelho: 1
Potência em watts [5500]: 
Horas de uso por dia [0.6]: 
Hora em que liga, de 0 a 23 [6]: 
Chuveiro elétrico incluído.
Número do aparelho: 2
Potência em watts [100]: 
Horas de uso por dia [24]: 
Hora em que liga, de 0 a 23 [0]: 
Geladeira (potência média ao longo do dia) incluído.
Número do aparelho: 
Tarifa da sua conta em reais por kWh (Enter para pular): 1

Consumo estimado: 171.0 kWh por mês
Custo estimado (sem impostos e bandeira extras): 171.00 reais por mês

Quem mais consome:
  1. Chuveiro elétrico: 99.0 kWh/mês (58%)
  2. Geladeira (potência média ao longo do dia): 72.0 kWh/mês (42%)

Demanda ao longo do dia (kW):
  00h  0.10 #
  01h  0.10 #
  02h  0.10 #
  03h  0.10 #
  04h  0.10 #
  05h  0.10 #
  06h  3.40 ##############################
  07h  0.10 #
  08h  0.10 #
  09h  0.10 #
  10h  0.10 #
  11h  0.10 #
  12h  0.10 #
  13h  0.10 #
  14h  0.10 #
  15h  0.10 #
  16h  0.10 #
  17h  0.10 #
  18h  0.10 #
  19h  0.10 #
  20h  0.10 #
  21h  0.10 #
  22h  0.10 #
  23h  0.10 #
Pico de demanda: 3.40 kW às 06h
Fator de carga: 0.07 (1 = consumo constante; perto de 0 = consumo concentrado em poucas horas)
ATENÇÃO: potências sugeridas são dados de exemplo; confira no rótulo do aparelho ou nas tabelas do Procel/INMETRO.
Estimativa com os dados informados. Não é garantia de consumo nem de economia.

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 0
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T20 · Energia: entradas inválidas na escolha de aparelhos

**Entrada**

```
10
2
99
abc
1
abc
5500
25
0,5
30
6


0
0
```

**Resultado esperado**

```
O aparelho 99 não está na lista.
O ID deve ser um número inteiro positivo
Informe a potência como número
Informe as horas de uso entre 0 e 24.
Informe a hora de início entre 0 e 23.
Consumo estimado: 82.5 kWh por mês
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 10

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 2

Aparelhos disponíveis (valores sugeridos, editáveis)
  1. Chuveiro elétrico - 5500 W, 0.6 h/dia, liga às 6h
  2. Geladeira (potência média ao longo do dia) - 100 W, 24 h/dia, liga às 0h
  3. Televisão - 100 W, 5 h/dia, liga às 19h
  4. Lâmpadas de LED (conjunto da casa) - 45 W, 5 h/dia, liga às 18h
  5. Ferro de passar roupa - 1000 W, 1 h/dia, liga às 14h
  6. Máquina de lavar roupa - 500 W, 1 h/dia, liga às 10h
  7. Ventilador - 80 W, 6 h/dia, liga às 13h
  8. Micro-ondas - 1200 W, 0.3 h/dia, liga às 12h
  9. Computador ou notebook - 80 W, 4 h/dia, liga às 20h

Escolha os aparelhos da sua casa (Enter sem número para calcular; /cancelar para voltar).
Número do aparelho: 99
O aparelho 99 não está na lista.
Número do aparelho: abc
O ID deve ser um número inteiro positivo (ex.: 12).
Número do aparelho: 1
Potência em watts [5500]: abc
Informe a potência como número (ex.: 1,5).
Potência em watts [5500]: 5500
Horas de uso por dia [0.6]: 25
Informe as horas de uso entre 0 e 24.
Horas de uso por dia [0.6]: 0,5
Hora em que liga, de 0 a 23 [6]: 30
Informe a hora de início entre 0 e 23.
Hora em que liga, de 0 a 23 [6]: 6
Chuveiro elétrico incluído.
Número do aparelho: 
Tarifa da sua conta em reais por kWh (Enter para pular): 

Consumo estimado: 82.5 kWh por mês

Quem mais consome:
  1. Chuveiro elétrico: 82.5 kWh/mês (100%)

Demanda ao longo do dia (kW):
  00h  0.00 
  01h  0.00 
  02h  0.00 
  03h  0.00 
  04h  0.00 
  05h  0.00 
  06h  2.75 ##############################
  07h  0.00 
  08h  0.00 
  09h  0.00 
  10h  0.00 
  11h  0.00 
  12h  0.00 
  13h  0.00 
  14h  0.00 
  15h  0.00 
  16h  0.00 
  17h  0.00 
  18h  0.00 
  19h  0.00 
  20h  0.00 
  21h  0.00 
  22h  0.00 
  23h  0.00 
Pico de demanda: 2.75 kW às 06h
Fator de carga: 0.04 (1 = consumo constante; perto de 0 = consumo concentrado em poucas horas)
ATENÇÃO: potências sugeridas são dados de exemplo; confira no rótulo do aparelho ou nas tabelas do Procel/INMETRO.
Estimativa com os dados informados. Não é garantia de consumo nem de economia.

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 0
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T21 · Energia: nenhum aparelho escolhido

**Entrada**

```
10
2

0
0
```

**Resultado esperado**

```
Nenhum aparelho escolhido.
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 10

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 2

Aparelhos disponíveis (valores sugeridos, editáveis)
  1. Chuveiro elétrico - 5500 W, 0.6 h/dia, liga às 6h
  2. Geladeira (potência média ao longo do dia) - 100 W, 24 h/dia, liga às 0h
  3. Televisão - 100 W, 5 h/dia, liga às 19h
  4. Lâmpadas de LED (conjunto da casa) - 45 W, 5 h/dia, liga às 18h
  5. Ferro de passar roupa - 1000 W, 1 h/dia, liga às 14h
  6. Máquina de lavar roupa - 500 W, 1 h/dia, liga às 10h
  7. Ventilador - 80 W, 6 h/dia, liga às 13h
  8. Micro-ondas - 1200 W, 0.3 h/dia, liga às 12h
  9. Computador ou notebook - 80 W, 4 h/dia, liga às 20h

Escolha os aparelhos da sua casa (Enter sem número para calcular; /cancelar para voltar).
Número do aparelho: 
Nenhum aparelho escolhido.

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 0
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T22 · Energia: orientações da categoria Energia no catálogo

**Entrada**

```
10
3
0
0
```

**Resultado esperado**

```
Orientações de energia (5)
Bandeiras tarifárias
Energia solar em casa
```

**Resultado observado:** Aprovado

**Saída**

```
[aviso de protótipo não oficial]
[... menu principal ...]
Escolha uma opção: 10

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 3

Orientações de energia (5)
[ 21] Bandeiras tarifárias: o que são e como afetam a conta - Energia
[ 22] Como ler o consumo em kWh na conta de luz - Energia  [verificar atualização]
[ 23] Etiqueta Procel e ENCE: escolher aparelhos que gastam menos - Energia  [verificar atualização]
[ 24] Banho e geladeira: onde a economia de energia costuma pesar - Energia  [verificar atualização]
[ 25] Energia solar em casa: geração distribuída - Energia  [verificar atualização]

Energia:
  0. Voltar
  1. Matriz energética
  2. Meus aparelhos: consumo e demanda
  3. Orientações de energia do catálogo
Escolha (ou /cancelar): 0
[... menu principal ...]
Escolha uma opção: 0
Até logo!
```

## T14 · Suíte automatizada (pytest)

**Entrada**

```
python -m pytest -q
```

**Resultado esperado**

```
Todos os testes passam
```

**Resultado observado:** Aprovado

**Saída**

```
........................................................................ [ 62%]
............................................                             [100%]
116 passed in 0.63s
```

## T15 · Web: entrar, cadastrar, pesquisar e ordenar

**Entrada**

```
POST /login; POST /admin/novo; GET /?q=rural; GET /servicos?ordem=titulo
```

**Resultado esperado**

```
Login 302, cadastro 302, busca acha o serviço novo, ordenação A-Z correta
```

**Resultado observado:** Aprovado

**Saída**

```
login=302 cadastro=302 busca=200 ordenar=200
IDs na lista após cadastro: [3, 1, 5, 2, 4, 10]
```

## T16 · Web: campo vazio, ID duplicado e ID inexistente

**Entrada**

```
POST /admin/novo (título vazio); POST /admin/novo (id=3); GET /servicos/999
```

**Resultado esperado**

```
422 com mensagem de campo obrigatório; 422 com mensagem de ID duplicado; 404 amigável
```

**Resultado observado:** Aprovado

**Saída**

```
título vazio=422; id duplicado=422; id inexistente=404
```

## T17 · Web: acessar páginas de administrador sem entrar

**Entrada**

```
GET /admin/novo, /admin/3/editar, /admin/3/excluir, /indicadores sem login; GET /
```

**Resultado esperado**

```
Redireciona para /login (302); páginas públicas continuam abertas (200)
```

**Resultado observado:** Aprovado

**Saída**

```
/admin/novo -> 302 /login?proximo=/admin/novo
/admin/3/editar -> 302 /login?proximo=/admin/3/editar
/admin/3/excluir -> 302 /login?proximo=/admin/3/excluir
/indicadores -> 302 /login?proximo=/indicadores
/ -> 200
```

## T23 · Web: página /energia (matriz) e cálculo de consumo e demanda

**Entrada**

```
GET /energia; POST /energia (chuveiro 5000 W, 0,5 h, 6h; geladeira 100 W, 24 h; tarifa 1)
```

**Resultado esperado**

```
200 com matriz e aviso de dado de exemplo; 147,0 kWh/mês; pico e ranking exibidos
```

**Resultado observado:** Aprovado

**Saída**

```
GET=200; POST=200
Consumo na página: True; ranking: True; pico: True
```

## T24 · Web: energia com dados inválidos e sem aparelho marcado

**Entrada**

```
POST /energia (potência 'abc', horas 30, hora 25); POST /energia sem aparelho
```

**Resultado esperado**

```
422 com mensagens; 422 pedindo ao menos um aparelho
```

**Resultado observado:** Aprovado

**Saída**

```
dados inválidos=422; sem aparelho=422
```

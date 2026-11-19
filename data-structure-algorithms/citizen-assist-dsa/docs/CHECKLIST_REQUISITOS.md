# Checklist dos requisitos de DSA

**Integrantes:** Arthur Primo Brandão (RM 573572), Leandro Cavaccini Brito (RM 570556) e Lucas Dorice Dos Santos (RM 568692).

Cada requisito do PDF "GS 2026.2 · Citizen Assist AI · DSA" com o local onde ele é atendido e a evidência. Os cenários T1 a T24 estão em [RELATORIO_TESTES.md](RELATORIO_TESTES.md).

## Funcionalidades obrigatórias (PDF, seção 4)

| Requisito | Onde está | Evidência |
|---|---|---|
| Cadastrar validando campos obrigatórios e identificadores | `cli.py` (`cadastrar`), `validacao.py` | T3, T4, T5, T6 |
| Consultar por identificador | `lista.buscar_por_id`, `cli.py` (`consultar`) | T7 |
| Listar todos | `cli.py` (`listar`), `lista.percorrer` | T1, T3 |
| Atualizar registro existente | `lista.atualizar`, `cli.py` (`atualizar`) | T8 |
| Excluir ajustando a estrutura | `lista.remover` (primeiro, meio, último, único nó) | T9, T9b, `tests/test_lista.py` |
| Pesquisar por pelo menos um atributo | `algoritmos.pesquisar` (título, categoria ou texto) | T10 |
| Ordenar por pelo menos um critério | `merge_sort` e `insertion_sort` (título ou id, crescente ou decrescente) | T11 |
| Menu interativo com saída e mensagens claras | `cli.py` (`executar`) | T12 |
| Tratar opção inexistente, valor incompatível, campo vazio e id duplicado | `validacao.py` | T4, T5, T6, T12 |

## Requisitos de implementação (seção 5, Python)

| Requisito | Onde está |
|---|---|
| Lista encadeada implementada pela equipe, com inserção, percurso, atualização e remoção | `citizen_assist/lista.py` (`inserir`, `percorrer`, `atualizar`, `remover`) |
| Classes ou objetos para registros e nós, com referências explícitas | `servico.py` (`Servico`), `no.py` (`No.proximo`) |
| Listas nativas não substituem a lista encadeada | todos os registros ficam em `ListaEncadeada`; resultados de pesquisa e ordenação também. Sequências nativas aparecem só em usos auxiliares: curva fixa de 24 posições, exportação para JSON e geração de dados do benchmark |
| Busca implementada no código | busca linear por id; pesquisa por trecho com `contem` escrita à mão |
| Ordenação implementada no código | merge sort sobre os nós e insertion sort, sem `sorted()`, `list.sort()` ou `bisect` |

## Análise Big-O (seção 6)

| Requisito | Onde está |
|---|---|
| Descrever a busca e a ordenação | [ALGORITMOS_BIGO.md](ALGORITMOS_BIGO.md), seções 1 e 2 |
| Custo de inserção, busca, exclusão e ordenação com hipóteses | [ALGORITMOS_BIGO.md](ALGORITMOS_BIGO.md), seção 3 |
| Coerência com o código | a análise foi escrita sobre o código final; o benchmark (opção 9 do menu) confirma n log n contra n² |

## Testes e evidências (seção 7)

| Requisito | Onde está |
|---|---|
| Cenários de cadastro, consulta, atualização, exclusão, pesquisa, ordenação e entradas inválidas | T3 a T12 |
| Entrada, esperado e observado por cenário | [RELATORIO_TESTES.md](RELATORIO_TESTES.md) |
| Saídas do terminal ou capturas de tela | saída real do terminal em cada cenário; capturas da web em `docs/capturas/` |
| Múltiplos registros | T3 (5 registros) e os cenários com a lista de exemplo |
| Ao menos uma operação sobre lista vazia | T1 e T2 |

## Entregáveis (seção 8)

| Entregável | Onde está |
|---|---|
| Código-fonte funcional com instruções de execução | todo o projeto; [README.md](../README.md) (Windows, Linux e macOS) |
| Documentação técnica (objetivo, campos, lista, organização, uso) | [DOCUMENTACAO_TECNICA.md](DOCUMENTACAO_TECNICA.md) |
| Descrição dos algoritmos e Big-O | [ALGORITMOS_BIGO.md](ALGORITMOS_BIGO.md) |
| Evidências dos testes | [RELATORIO_TESTES.md](RELATORIO_TESTES.md) |

# Documentação técnica

**Integrantes:** Arthur Primo Brandão (RM 573572), Leandro Cavaccini Brito (RM 570556) e Lucas Dorice Dos Santos (RM 568692).

## 1. Objetivo
Organizar serviços e orientações de interesse público (documentos, saúde, educação, assistência social e atendimento comunitário) em um catálogo que pode ser cadastrado, consultado, atualizado, excluído, pesquisado e ordenado por menu interativo. O foco da disciplina é a aplicação prática de **lista encadeada**, **busca**, **ordenação** e **análise de complexidade (Big-O)**.

Alinhamento com o caso Citizen Assist AI: cada serviço mostra **referência** e **aviso de limitação**; há alerta de informação **desatualizada**; o sistema se declara protótipo **não oficial** e **não coleta dados pessoais**.

## 2. Campos do registro (`Servico`)

| Campo | Obrigatório | Descrição | Validação |
|---|---|---|---|
| `id` | sim | identificador único | inteiro de 1 a 999999, sem duplicidade |
| `titulo` | sim | nome do serviço | até 80 caracteres |
| `categoria` | sim | área (Documentos, Saúde...) | até 40 |
| `descricao` | sim | o que é e como funciona | até 300 |
| `publico_alvo` | sim | para quem se destina | até 80 |
| `canal_local` | sim | onde ou como ser atendido | até 100 |
| `referencia` | não | fonte da informação | até 120 |
| `ultima_verificacao` | não | data AAAA-MM-DD | data válida, não futura |
| `aviso` | não | limitação ou ressalva ao cidadão | até 120 |
| `abrangencia` | não | `urbano`, `rural` ou `ambos` (padrão `ambos`) | um dos três valores |

Os seis primeiros campos são o mínimo exigido pela atividade; os quatro últimos são extras ligados ao tema. Um serviço é marcado como **"verificar atualização"** quando a última verificação tem mais de 180 dias ou não existe.

## 3. Lista encadeada

Implementada em `citizen_assist/lista.py` e `no.py`, sem usar `list` nativa para guardar registros.

```python
class No:
    def __init__(self, dados):
        self.dados = dados      # um Servico
        self.proximo = None     # referência explícita ao próximo nó

class ListaEncadeada:           # simplesmente encadeada
    inicio, fim, tamanho
```

| Operação | Método | Observação |
|---|---|---|
| Inserção | `inserir`, `inserir_fim_sem_verificar` | liga no fim usando `fim`; `inserir` antes verifica id único |
| Percurso | `percorrer` | laço `while atual is not None`, entrega um registro por vez |
| Busca por id | `buscar_por_id` | linear |
| Atualização | `atualizar` | localiza o nó e troca os dados, preservando o id |
| Remoção | `remover` | trata lista vazia, primeiro, meio e último nó (atualiza `fim`) |
| Apoio | `limpar`, `copiar`, `refazer_fim` | `refazer_fim` é usado após a ordenação |

Em Python não há `malloc`/`free`: ao religar `anterior.proximo`, o nó removido deixa de ser referenciado e o coletor de lixo o libera.

Resultados de pesquisa também são devolvidos como `ListaEncadeada`, e a ordenação religa os próprios nós, sem copiar para vetor.

## 4. Organização do código

| Arquivo | Responsabilidade |
|---|---|
| `citizen_assist/servico.py` | classe `Servico`, status de verificação |
| `citizen_assist/no.py` | classe `No` |
| `citizen_assist/lista.py` | `ListaEncadeada` |
| `citizen_assist/algoritmos.py` | `contem`, `pesquisar`, `merge_sort`, `merge_sort_por`, `insertion_sort`, `benchmark` |
| `citizen_assist/energia/` | extra: `FonteEnergia`, `Aparelho`, curva de demanda, leitura dos CSV de energia |
| `citizen_assist/validacao.py` | validações usadas pelo terminal e pela web |
| `citizen_assist/persistencia.py` | salvar e carregar CSV, exportar JSON |
| `citizen_assist/indicadores.py` | indicadores de uso e relatórios (sem guardar termos buscados) |
| `cli.py` | menu interativo |
| `web/app.py` e `web/templates/` | interface Flask |

O núcleo não depende do Flask: terminal e web chamam as mesmas funções, então os mesmos testes cobrem os dois.

## 5. Tratamento de entradas inválidas

| Situação | Tratamento |
|---|---|
| Opção de menu inexistente, letra ou vazio | mensagem e o menu volta a ser exibido |
| ID com letras, negativo, zero, muito grande ou duplicado | mensagem específica; pede de novo |
| Campo obrigatório vazio ou só espaços | mensagem com o nome do campo |
| Texto acima do limite, data inválida ou futura, abrangência inválida | mensagem específica |
| ID não encontrado | "Serviço com ID X não encontrado." (web: página 404 amigável) |
| Operação com lista vazia | mensagem "Nenhum serviço cadastrado" |
| Fim da entrada ou Ctrl+C (Ctrl+Z e Enter no Windows, Ctrl+D no Linux e macOS) | encerra sem erro, mesmo no meio de uma operação |
| Exclusão | pede confirmação (s/n) |
| Web | validação no servidor, erros ao lado do campo, dados digitados preservados, HTML escapado, token CSRF |

No terminal, digitar `/cancelar` em qualquer pergunta volta ao menu.

## 6. Uso

**Terminal** (`python main.py cli`): 1 Cadastrar · 2 Consultar por ID · 3 Listar · 4 Atualizar (Enter mantém o valor, `-` limpa campo opcional) · 5 Excluir · 6 Pesquisar (título, categoria ou texto) · 7 Ordenar (título ou ID, crescente ou decrescente, merge ou insertion sort) · 8 Salvar/carregar/exportar · 9 Relatórios e benchmark · 10 Energia (matriz, consumo e demanda) · 0 Sair.

**Web** (`python main.py web`):

| Rota | Método | Função | Acesso |
|---|---|---|---|
| `/` | GET | busca por texto e filtro por categoria | público |
| `/servicos` | GET | lista com ordenação por título ou ID | público |
| `/servicos/<id>` | GET | detalhe, referência, aviso e alerta de desatualização | público |
| `/api/servicos`, `/api/servicos/<id>` | GET | JSON somente leitura | público |
| `/login`, `/logout` | GET, POST | entrada do administrador | público |
| `/energia` | GET, POST | matriz energética, consumo e demanda de aparelhos, orientações de energia | público |
| `/admin/novo` | GET, POST | cadastro | administrador |
| `/admin/<id>/editar` | GET, POST | atualização | administrador |
| `/admin/<id>/excluir` | GET, POST | confirmação e exclusão | administrador |
| `/indicadores` | GET, POST | indicadores e benchmark de ordenação | administrador |

Alterações feitas na web são salvas automaticamente em `dados/servicos.csv`, que é carregado na próxima execução.

## 7. Módulo de energia (extra)
Aplica a mesma lista encadeada e o merge sort (`merge_sort_por`, que ordena por qualquer chave) a conteúdo da disciplina de Energias Renováveis: matriz energética, consumo de aparelhos e curva de demanda. Detalhes, fórmulas e avisos sobre os dados de exemplo em [CONEXAO_ENERGIA.md](CONEXAO_ENERGIA.md). O módulo é opcional e não é a entrega de SERS.

## 8. Acessibilidade e privacidade
HTML semântico com `lang="pt-BR"`, link "pular para o conteúdo", rótulos ligados aos campos, foco visível, bom contraste, nenhuma informação transmitida só por cor, uso por teclado e sem JavaScript, e layout que se adapta ao celular. O visual é propositalmente simples (fonte do sistema, poucas cores). Não há cadastro de usuários nem coleta de dados pessoais; os indicadores guardam apenas horário, tempo e quantidade de resultados, nunca o texto buscado. O acesso de administrador é uma proteção de demonstração (senha única), não um sistema de autenticação de produção.

## 9. Limitações
- Dados fictícios: as referências citadas servem de exemplo e precisam ser verificadas antes de uso real.
- Servidor de desenvolvimento do Flask, em máquina local, sem banco de dados.
- O tempo medido pelos indicadores é o da busca no servidor.
- Python foi escolhido entre as duas linguagens aceitas pelo PDF da atividade (C ou Python).

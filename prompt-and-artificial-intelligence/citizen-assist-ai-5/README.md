# Citizen Assist AI — Assistente Digital de Orientação ao Cidadão

**Integrantes:** Arthur Primo Brandão (RM 573572) · Leandro Cavaccini Brito (RM 570556) · Lucas Dorice dos Santos (RM 568692)
Ciência da Computação, FIAP — Global Solution 2026 (Prompt and Artificial Intelligence)

> Material didático fictício: as fichas da "Central do Cidadão de Aurora" não valem como informação real.

## Como rodar
1. Instale o [Ollama](https://ollama.com) e baixe os modelos:
   `ollama pull llama3.1:8b` (agente) e `ollama pull qwen2.5:7b` (juiz, etapa 3).
2. `python -m venv .venv` e ative; depois `pip install -r requirements.txt`.
3. Terminal: `python app_cli.py` (menu por categorias + pergunta livre, só teclado).
4. Testes: `pytest` (as regras não precisam do Ollama).
5. Imagem do grafo: `python gerar_grafo.py` (gera `docs/grafo.mmd` e, com internet, `docs/grafo.png`).

Variáveis opcionais: `OLLAMA_MODEL`, `OLLAMA_JUDGE_MODEL`, `OLLAMA_URL`.

## Arquitetura (um agente, grafo LangGraph)
`validar → dados_pessoais → injecao → roteador → gerar (LLM) → finalizar`
Entrada inválida, injection, fora do escopo e limitação encerram cedo, sem chamar o LLM.

| Módulo | Função | IA? |
|---|---|---|
| `guardrails.py` | validação, ocultação de CPF/telefone/e-mail/CEP, detecção de injection, checagem de valores em R$ | Não |
| `roteador.py` | escolhe as fichas por palavras-chave ponderadas; FC-07 sempre como complemento | Não |
| `fichas.py` | lê `fichas/*.md` e organiza por código, campos, palavras-chave e versão | Não |
| `agente.py` | grafo, prompt e montagem da resposta (fonte, data e aviso acrescentados pelo código) | Só o nó `gerar` |

## Proteção de dados
- O dado pessoal é trocado por `[DADO OCULTO]` antes de qualquer outro passo e nunca chega ao LLM.
- Sem memória, sem log, sem arquivo de histórico: cada pergunta é independente.
- Tudo roda local (Ollama): nenhuma mensagem vai para serviço externo.
- Fichas e mensagem entram no prompt como dados delimitados, não como instruções.

## Avaliação (LLM as a Judge)
- `data/golden_dataset.json`: as 26 mensagens do enunciado, sem alteração (campos `fichas` e `termos` são apoio nosso).
- `python avaliar.py --rotulo antes` roda o agente e o juiz e grava `results/antes.csv` e `results/antes.md`.
- Juiz (`juiz.py`): modelo diferente do agente, temperatura 0, escala binária. O LLM responde 4 perguntas de sim/não
  (pontos esperados, sem invenção, fonte citada, segurança) e o código calcula o veredito.
- Regras duras somadas ao juiz: citar a ficha e não vazar dado pessoal são eliminatórios.
- Depois da melhoria: `python avaliar.py --rotulo depois`.

## Testes com usuários
- Roteiro, tarefas, gabarito e questionário: `docs/teste_usuarios/roteiro.md`.
- Preencha `results/usuarios/tempos.csv` e `questionario.csv` (só códigos P01, P02...; o script recusa nomes).
- `python analisar_testes.py` gera `results/usuarios/indicadores.md` (acerto, tempo, facilidade).

## Estrutura
`fichas/` (fonte de verdade) · `src/citizen_assist/` · `tests/` · `app_cli.py` · `gerar_grafo.py` · `docs/`

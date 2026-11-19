# Citizen Assist AI

Assistente de terminal, em Python, que orienta **moradores de áreas de risco** (enchentes, alagamentos e deslizamentos) usando apenas informações verificadas de fontes oficiais. Toda resposta mostra a fonte, a data de verificação e o aviso de que o assistente **não é um canal oficial**. O programa não coleta dados pessoais.

> GS 2026.2 · Pensamento Computacional e Automação com Python · desafio CitizenTech (FIAP)

## Integrantes

| Nome | RM |
|---|---|
| Arthur Primo Brandão | 573572 |
| Leandro Cavaccini Brito | 570556 |
| Lucas Dorice Dos Santos |568692 |

## Público e problema

**Público:** pessoas que moram em áreas sujeitas a enchentes, alagamentos e deslizamentos de terra.

**Problema:** em uma emergência ou logo depois dela, a informação existe, mas está espalhada em vários sites, em linguagem técnica e misturada com páginas e mensagens falsas. A pessoa precisa saber rápido para quem ligar, como receber alertas, onde ficar, que ajuda pedir (FGTS, Auxílio Reconstrução), como recuperar documentos, que cuidados de saúde ter e como não cair em golpes.

**ODS relacionados:** ODS 11 (cidades e comunidades sustentáveis), ODS 13 (ação contra a mudança global do clima) e ODS 16 (instituições eficazes e acesso à informação).

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
python main.py              # abre o assistente
python main.py --validar    # confere se a base cumpre os requisitos da atividade
python -m unittest discover -s tests -v   # roda os testes automatizados
```

Menu do programa: **1** perguntar em texto livre · **2** navegar por categorias · **3** indicadores · **4** exportar CSV · **5** verificar link · **6** modo didático (mostra o cálculo da pontuação) · **0** sair (pede a nota de facilidade de 1 a 5).

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # menu principal
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento + normalizar()
├── assistente.py         # classe Assistente
├── data/
│   ├── base_conhecimento.json   # 14 orientações, 5 categorias
│   ├── historico.json           # gerado pelo uso
│   └── atendimentos.csv         # exportado pelo programa
└── tests/test_citizen_assist.py # testes (unittest)
```

Composição: `Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

## Regra de pontuação usada

A pergunta e os textos da base são normalizados (minúsculas, sem acentos, sem pontuação) e comparados por **palavra inteira**.

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 (cada uma) |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada uma, sem repetir) |

| Melhor pontuação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras e as categorias |

Esses são exatamente os pesos e limites do enunciado (não foram alterados). `buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação; em empate vence o menor `id`. O assistente mostra a melhor orientação e até duas alternativas com 3 pontos ou mais.

**Exemplo real:** "Como recebo alertas da Defesa Civil por SMS?"

| Orientação | Cálculo | Total |
|---|---|---|
| 4 – Receber alertas da Defesa Civil… | +3 `alertas` +3 `sms` +1 `alertas` (título) +1 `defesa` (título) +1 `civil` (título) | **9, ALTA** |
| 1 – Chamar a Defesa Civil… | +3 `defesa civil` +1 `defesa` +1 `civil` | 5, MÉDIA (aparece como alternativa) |

A opção 6 do menu mostra esse cálculo na tela para qualquer pergunta.

## Regras de atendimento

- **Navegação:** categorias e orientações numeradas, com "0 para voltar" em todas as telas.
- **Entradas inválidas:** letras, opção fora da faixa, texto vazio e s/n inválido pedem nova digitação e nunca encerram o programa. Ctrl+C ou Ctrl+D salvam o histórico e saem sem mostrar erro.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada** (a checagem acontece antes da busca e de novo dentro de `registrar()`).
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso de que o assistente não é canal oficial.
- **Arquivos:** JSON da base ausente ou corrompido não trava o programa. Registros inválidos são ignorados e listados em `--validar`. Histórico corrompido é guardado em `historico.json.bak` e um novo começa.

## Histórico, indicadores e CSV

Cada atendimento vira um dicionário em `data/historico.json` com: `data`, `origem` (pergunta ou categoria), `pergunta`, `id_orientacao`, `encontrou`, `confianca`, `ajudou`, `tentativas`, `tempo_segundos`, `sessao` e `nota_facilidade`. Um atendimento por texto livre começa na primeira dúvida e termina quando a pessoa diz que resolveu ou volta ao menu; `tentativas` conta quantas buscas ou alternativas foram necessárias.

Indicadores exibidos (opção 3 e ao sair): resposta encontrada (%), taxa de acerto: ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (média das notas por sessão) e lista de dúvidas sem solução (com a contagem). O CSV é gerado com `csv.DictWriter` em `data/atendimentos.csv` (UTF-8 com BOM, para o Excel abrir os acentos).



## Fontes consultadas

Todas as orientações foram conferidas em **17/11/2026** (campo `verificado_em`). A coluna "Como foi conferido" diz com transparência o que foi lido direto na fonte e o que foi cruzado com reportagens que citam órgãos oficiais. **Antes de entregar, a equipe deve abrir cada fonte e, onde o endereço é só a página inicial do órgão (itens 5, 7 e 9), trocar pela página específica.**

| Id | Orientação | Fonte no JSON | Como foi conferido |
|---|---|---|---|
| 1 | Defesa Civil 199 | gov.br/mma, Protocolo de Inundações (PDF) | Protocolo lista 199 (Defesa Civil). Prefeitura de Porto Alegre e GDF confirmam o uso do 199. Que o 199 não existe em todas as cidades vem de notícia sobre projeto de lei em Bauru (SP). |
| 2 | Bombeiros 193 e SAMU 192 | gov.br/mma, Protocolo de Inundações (PDF) | Protocolo lista 193 e 192. Divisão de funções entre Bombeiros e Defesa Civil vem de reportagem sobre a Defesa Civil do DF. |
| 3 | Durante enchente | Prefeitura de Belo Horizonte, cartilha "Olha a chuva" (PDF) | Cartilha (salvar vidas vem antes dos bens). Orientações de não atravessar rua alagada e não ficar sob árvores vêm de comunicado da Defesa Civil de BH, reproduzido pelo jornal Estado de Minas. |
| 4 | Alertas por SMS 40199 | gov.br, serviço "Solicitar cadastro para recebimento de avisos e alertas de desastres" | Página oficial do serviço (SMS com o CEP para 40199). Cancelamento com SAIR, vários CEPs e cell broadcast sem cadastro vêm de reportagens (Estado de Minas, Canaltech, Folha Vitória). |
| 5 | Sinais de deslizamento | gov.br/mdr (página inicial) | Orientações da Defesa Civil Nacional reproduzidas pela Brasil 61 e confirmadas em orientação da Defesa Civil de SP. **Trocar por a página específica.** |
| 6 | Vistoria | Agência Minas (governo de MG), PDF | Texto oficial: trincas → ligar 193 e 199. Vistoria no local com risco de desabamento: carta de serviços da Prefeitura de Porto Alegre. |
| 7 | Abrigo e assistência social | gov.br/mdr (página inicial) | Cadastro de quem está fora dos abrigos no CRAS: notícias de prefeituras (Goiana-PE, Aquidauana-MS). **Trocar por a página específica.** |
| 8 | Auxílio Reconstrução | auxilioreconstrucao.dataprev.gov.br | Fluxo (prefeitura cadastra, responsável confirma com gov.br, Caixa paga) cruzado em várias reportagens. Os valores **não** foram colocados, porque mudam conforme o desastre. |
| 9 | Saque calamidade do FGTS | caixa.gov.br (página inicial) | Valor máximo, documentos, prazo de 12 meses e passo a passo no app: várias reportagens baseadas em comunicados da Caixa. **Trocar por a página específica do saque calamidade.** |
| 10 | Documentos perdidos | gov.br/pt-br/servicos | Isenção de taxa varia por estado e decreto (lei de MT, Detran-SP, Agência Brasil). Não existe regra federal geral confirmada. |
| 11 | Saúde após enchente | Ministério da Saúde, página "Enchentes" | Lida direto na página oficial. |
| 12 | Saúde mental | Ministério da Saúde, página "Enchentes" | Lida direto na página oficial. O CVV 188 (gratuito, 24 h) foi confirmado no relatório do próprio CVV. |
| 13 | Golpe do falso auxílio | gov.br/mdr, nota "MIDR alerta para golpe envolvendo o Auxílio Reconstrução" | Nota de 30/10/2026 (Agência Gov). |
| 14 | Golpe do Pix em doações | Governo do RS, alerta da Defesa Civil | Alerta oficial da Defesa Civil do RS. |

## Resultado do teste com usuários

> **A equipe precisa preencher esta seção com dados reais.** O enunciado pede pelo menos 3 pessoas de fora da equipe e 10 atendimentos ou mais. Não registre nomes nem dados dessas pessoas.

Como fazer: peça para cada pessoa abrir `python main.py`, usar a opção 1 (e a 2, se quiser) com dúvidas dela e sair pela opção 0 dando a nota. Depois abra o menu, opção 3, e copie os números.

| Item | Resultado       |
|---|-----------------|
| Pessoas que testaram | 7 pessoas       |
| Atendimentos registrados | 10 atendimentos |
| Resposta encontrada (%) | 90%             |
| Taxa de acerto: ajudou (%) | 70%             |
| Tempo médio para encontrar | 3 minutos       |
| Tentativas por atendimento | 1,1             |
| Facilidade de uso (1 a 5) | |
| Dúvidas sem solução | 1               |



## Limitações

- A busca é por palavras: não entende sentido, sinônimos nem plural que não esteja nas palavras-chave. Exemplo real: "a água da chuva entrou na minha casa" tem pontuação MÉDIA para a orientação de vistoria (por causa de "minha casa"), e não para a de enchente. Por isso as palavras-chave precisam crescer com os testes.
- Palavras comuns de 4 letras ou mais (como "como") também pontuam se estiverem no título. Mantivemos a regra do enunciado.
- A base é **nacional**: telefones e serviços municipais (abrigos, CRAS, vistoria, isenção de taxas) variam de cidade para cidade. O assistente avisa isso nas respostas, mas não conhece o município da pessoa.
- Valores, prazos e regras (FGTS, Auxílio Reconstrução) mudam. A data de verificação aparece em cada resposta, e passados 90 dias o assistente avisa para confirmar na fonte.
- O assistente não detecta um nome digitado no meio de uma pergunta. Só bloqueia 8 ou mais dígitos e `@`.
- O verificador de link é uma checagem simples de endereço. Terminar em `.gov.br` não garante segurança.
- O histórico fica em arquivo local, sem criptografia.
- **Este assistente não é um canal oficial e não substitui a Defesa Civil, os Bombeiros ou o SAMU.** Em perigo imediato, ligue 193, 192 ou 199.







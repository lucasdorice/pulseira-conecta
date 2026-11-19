# Roteiro de testes com usuários — Citizen Assist AI

Objetivo: medir **acerto**, **tempo** e **facilidade de uso** com pelo menos **5 pessoas de fora do grupo**.
Regra de privacidade do enunciado: registrar **apenas** tempo, acerto e nota de facilidade. **Sem nome, idade, e-mail, telefone ou qualquer dado que identifique a pessoa.** Use códigos P01, P02, P03...

## Antes de começar (preparação do grupo)
1. Deixe o Ollama aberto e o assistente rodando (`python app_cli.py`).
2. **Aqueça o modelo:** faça uma pergunta qualquer antes de cada sessão, para a primeira resposta não pesar no tempo.
3. Tenha um cronômetro e dois arquivos abertos: `results/usuarios/tempos.csv` e `results/usuarios/questionario.csv` (modelos nesta pasta).
4. Escolha o público. Para combinar com o projeto, inclua se possível pessoas com mais de 60 anos ou com alguma dificuldade de leitura/digitação. Não é obrigatório e **não registre** esse dado por participante.

## Fala inicial (leia igual para todos)
> "Este é um protótipo educacional com informações fictícias de uma cidade chamada Aurora. Vou pedir três tarefas simples e medir o tempo. Quem está sendo testado é o programa, não você. **Não digite dados pessoais seus**, como CPF, endereço ou telefone. Você pode parar quando quiser. Não vou anotar seu nome."

Peça um "sim" verbal e siga. Não ajude durante as tarefas, a não ser que a pessoa desista.

## As 3 tarefas
Leia o enunciado da tarefa, diga "pode começar" e **inicie o cronômetro**. Pare quando a pessoa disser a resposta em voz alta. Tempo máximo: **3 minutos** por tarefa.

| Tarefa | O que dizer | Resposta correta (gabarito) | Ficha |
|---|---|---|---|
| T1 | "Você perdeu o RG e quer a segunda via. Descubra **o que precisa levar**." | Certidão de nascimento ou casamento + comprovante de residência dos últimos 90 dias + **declaração de extravio** (perda; boletim só em roubo/furto) | FC-01 |
| T2 | "Descubra **quanto custa e quanto demora** a certidão de nascimento pelo portal." | R$ 49,00 e 3 dias úteis | FC-05 |
| T3 | "Uma pessoa de 55 anos vai renovar a CNH. **Por quanto tempo** a nova CNH vale?" | 5 anos | FC-06 |

Alterne a ordem das tarefas entre participantes (P01: T1-T2-T3, P02: T2-T3-T1, P03: T3-T1-T2...) para não favorecer uma delas.

**Como marcar o acerto:** `acertou = 1` só se a resposta falada bater com o gabarito **completo** (na T1, os três itens; na T2, os dois dados). Se você deu qualquer dica, marque `ajuda = 1` (a tarefa não conta como acerto). Se estourou os 3 minutos, `acertou = 0` e tempo = 180.

**Caminho:** anote se a pessoa usou o `menu` ou digitou a `livre`.

## Questionário final (5 perguntas, escala 1 a 5)
Mostre a escala: **1 = discordo totalmente · 3 = nem concordo nem discordo · 5 = concordo totalmente**.

1. Foi fácil encontrar a informação que eu precisava.
2. As respostas foram claras e fáceis de entender.
3. Consegui usar o assistente sem ajuda de ninguém.
4. O texto era fácil de ler (tamanho, frases curtas, contraste).
5. Eu usaria este assistente de novo.

Anote só os números no `questionario.csv`. Perguntas abertas ficam de fora para não coletar dado pessoal por acidente. Se a pessoa comentar algo útil, anote **sem identificar** quem falou (ex.: "o menu ajudou mais que a digitação").

## Depois dos testes
Com os dois CSV preenchidos, rode `python analisar_testes.py` e use `results/usuarios/indicadores.md` no relatório (modelo em `relatorio_modelo.md`).

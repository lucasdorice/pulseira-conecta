# Citizen Assist AI · Catálogo de serviços (DSA)

Projeto da Global Solution 2026.2 (FIAP, 1º ano de Ciência da Computação), disciplina **Data Structures and Algorithms**. Sistema em **Python** que gerencia um catálogo de serviços e orientações ao cidadão usando uma **lista encadeada implementada pela equipe**, com busca e ordenação escritas à mão. Tem duas interfaces sobre o mesmo núcleo: **menu no terminal** e **interface web (Flask)**. Como extra, um módulo de **energia** aplica as mesmas estruturas a matriz energética, consumo e demanda (conteúdo da disciplina de Energias Renováveis, sem ser a entrega dela).

> Os dados são fictícios e servem apenas para demonstração. O sistema **não é canal oficial**: confirme sempre a informação no órgão responsável. Nenhum dado pessoal é coletado.

## Integrantes

| Nome completo | RM |
|---|---|
| Arthur Primo Brandão | 573572 |
| Leandro Cavaccini Brito | 570556 |
| Lucas Dorice Dos Santos | 568692 |

## Como executar

Requisito: Python 3.11 ou superior (no Windows, instale pelo python.org e marque "Add Python to PATH"). Abra o terminal **dentro da pasta do projeto**.

### Windows (PowerShell)

```powershell
python -m pip install -r requirements.txt
python main.py cli      # menu no terminal
python main.py web      # interface web em http://127.0.0.1:5000
```

Se `python` não for reconhecido, use `py` no lugar (por exemplo, `py main.py cli`). O ambiente virtual é opcional; se quiser usar:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ou use o Prompt de Comando (cmd) com `.venv\Scripts\activate.bat`.

### Linux e macOS

```bash
python3 -m pip install -r requirements.txt
python3 main.py cli
python3 main.py web
```

Ambiente virtual opcional: `python3 -m venv .venv` e `source .venv/bin/activate`.

### Opções do programa

- `python main.py cli --vazio` começa o terminal com a lista vazia, sem carregar os 25 serviços de exemplo.
- `python main.py web --porta 8080` muda a porta da web.
- Para encerrar a web, pressione `Ctrl+C` no terminal. No menu do terminal, a opção `0` sai; `Ctrl+C` também encerra sem erro.

### Senha de administrador (web)

As áreas de gerenciamento (cadastrar, atualizar, excluir, indicadores) pedem senha. A senha padrão de demonstração é `demo123`. Para trocar:

```powershell
$env:CITIZEN_ADMIN_SENHA = "sua-senha"      # PowerShell
set CITIZEN_ADMIN_SENHA=sua-senha           # Prompt de Comando (cmd)
```

```bash
export CITIZEN_ADMIN_SENHA="sua-senha"      # Linux e macOS
```

Defina a variável **antes** de rodar `python main.py web`, no mesmo terminal.

### Testes e evidências

```powershell
python -m pytest -q             # testes automatizados
python gerar_evidencias.py      # roda os cenários e gera docs\RELATORIO_TESTES.md
```

## Estrutura

```
citizen_assist/   núcleo: Servico, No, ListaEncadeada, algoritmos, validação, persistência, indicadores
citizen_assist/energia/   extra: matriz energética, consumo e demanda (conexão com SERS)
cli.py            menu interativo no terminal
web/              interface Flask (rotas em app.py, templates e CSS)
main.py           ponto de entrada (cli | web)
dados/            servicos_exemplo.csv (dados fictícios)
tests/            testes automatizados (pytest)
docs/             documentação técnica, análise Big-O, relatório de testes, capturas de tela
gerar_evidencias.py   gera o relatório de testes
```

## Documentação

- [Documentação técnica](docs/DOCUMENTACAO_TECNICA.md)
- [Algoritmos e análise Big-O](docs/ALGORITMOS_BIGO.md)
- [Checklist dos requisitos de DSA](docs/CHECKLIST_REQUISITOS.md)
- [Relatório de testes e evidências](docs/RELATORIO_TESTES.md) e [capturas de tela](docs/capturas/)
- [Conexão com Energias Renováveis (extra)](docs/CONEXAO_ENERGIA.md)

# Análise dos erros: resultado "antes" (agente v1 + juiz v1): 20/26 (77%)

| # | Veredito do juiz v1 | Causa | Tipo de erro | Ação |
|---|---|---|---|---|
| 3 | incorreto | resposta não trouxe "declaração de extravio" (perda x roubo) | **agente** | busca por trechos + regra de prompt sobre casos |
| 8 | incorreto | juiz diz que faltam pontos, mas R$ 7,00 e FC-02 estão na resposta | provável juiz (conferir à mão) | `revisar_manual` |
| 14 | incorreto | juiz aprova o conteúdo e reprova a fonte, mas FC-05/FC-07 estão citadas | **juiz** | fonte decidida pelo código |
| 20, 21, 26 | incorreto | juiz reprovou "falta de fonte" em tipos que não exigem ficha | **juiz** | fonte decidida pelo código |

Pontos para conferência manual: #18 (juiz aprovou, resposta sem "sexta") e #24 (justificativa ambígua).

## Melhorias
1. **Juiz v2:** `fonte_citada` sai do LLM; o código verifica. Nova coluna `revisar_manual` quando juiz e regras divergem.
2. **Agente v2:** busca por trechos (3 linhas das fichas mais parecidas com a pergunta, em destaque) e regra de prompt para distinguir casos.

## Três medições (para separar o efeito de cada melhoria)
| Rótulo | Agente | Juiz | Comando |
|---|---|---|---|
| antes | v1 | v1 | já executado |
| antes_juiz2 | v1 (mesmas respostas) | v2 | `python avaliar.py --rotulo antes_juiz2 --reaproveitar results/antes.csv` |
| depois | v2 | v2 | `python avaliar.py --rotulo depois` |

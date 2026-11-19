# Teste de Cenários (internos)

> **Não são testes com usuários.** São cenários criados pelo grupo para verificar se o assistente responde de forma coerente em casos diferentes. Gerado por `python scripts/testar_cenarios.py`. Eles não substituem os testes com usuários (`docs/04_TESTES_COM_USUARIOS.md`).

## C1 Família de 4, imóvel próprio, telhado ok (perfil de exemplo)

Consumo estimado: 262 kWh/mês; tarifa efetiva R$ 1,00/kWh.

| Verificação | Resultado |
|---|---|
| economias A, B e C não negativas | OK |
| recomendação começa pela eficiência | OK |
| toda resposta traz aviso de estimativa | OK |

**Recomendação dada:**
- 1º — Comece pela eficiência (A): custa pouco (R$ 96) e já reduz a conta.
- 2º — Energia solar fotovoltaica (alternativa C): retorno rápido, payback ≈ 4,2 anos com reajuste. Peça pelo menos 3 orçamentos.
- 3º — Aquecedor solar de água (alternativa B): retorno moderado, payback ≈ 7,5 anos com reajuste. Peça pelo menos 3 orçamentos.
- Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. Para A + C use o pacote, que dimensiona o solar depois da eficiência.

## C2 Família alugando (imóvel não próprio)

Consumo estimado: 124 kWh/mês; tarifa efetiva R$ 1,00/kWh.

| Verificação | Resultado |
|---|---|
| economias A, B e C não negativas | OK |
| recomendação começa pela eficiência | OK |
| imóvel alugado: B e C marcadas como inviáveis | OK |
| toda resposta traz aviso de estimativa | OK |

**Recomendação dada:**
- 1º — Comece pela eficiência (A): custa pouco (R$ 0) e já reduz a conta.
- 2º — Como o imóvel não é próprio, B e C dependem de autorização do proprietário. Vale conhecer opções de energia solar por assinatura (a análise não cobre este caso).

## C3 Casa pequena, consumo baixo (perto do custo de disponibilidade)

Consumo estimado: 56 kWh/mês; tarifa efetiva R$ 1,00/kWh.

| Verificação | Resultado |
|---|---|
| economias A, B e C não negativas | OK |
| recomendação começa pela eficiência | OK |
| telhado desconhecido: C marcada 'a confirmar' | OK |
| toda resposta traz aviso de estimativa | OK |

**Recomendação dada:**
- 1º — Comece pela eficiência (A): custa pouco (R$ 0) e já reduz a conta.
- 2º — Energia solar fotovoltaica (alternativa C): retorno moderado, payback ≈ 7,6 anos com reajuste (confirme antes se o telhado é adequado). Peça pelo menos 3 orçamentos.
- 3º — Aquecedor solar de água (alternativa B): retorno longo, payback ≈ 13,0 anos com reajuste (confirme antes se o telhado é adequado). Peça pelo menos 3 orçamentos.
- Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. Para A + C use o pacote, que dimensiona o solar depois da eficiência.

## C4 Telhado desconhecido, tarifa informada R$ 0,95

Consumo estimado: 152 kWh/mês; tarifa efetiva R$ 0,95/kWh.

| Verificação | Resultado |
|---|---|
| economias A, B e C não negativas | OK |
| recomendação começa pela eficiência | OK |
| telhado desconhecido: C marcada 'a confirmar' | OK |
| toda resposta traz aviso de estimativa | OK |

**Recomendação dada:**
- 1º — Comece pela eficiência (A): custa pouco (R$ 72) e já reduz a conta.
- 2º — Energia solar fotovoltaica (alternativa C): retorno rápido, payback ≈ 4,5 anos com reajuste (confirme antes se o telhado é adequado). Peça pelo menos 3 orçamentos.
- 3º — Aquecedor solar de água (alternativa B): retorno moderado, payback ≈ 6,8 anos com reajuste (confirme antes se o telhado é adequado). Peça pelo menos 3 orçamentos.
- Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. Para A + C use o pacote, que dimensiona o solar depois da eficiência.

## C5 Casa grande, 6 pessoas, muito ar-condicionado, ligação trifásica

Consumo estimado: 830 kWh/mês; tarifa efetiva R$ 1,00/kWh.

| Verificação | Resultado |
|---|---|
| economias A, B e C não negativas | OK |
| recomendação começa pela eficiência | OK |
| toda resposta traz aviso de estimativa | OK |

**Recomendação dada:**
- 1º — Comece pela eficiência (A): custa pouco (R$ 0) e já reduz a conta.
- 2º — Energia solar fotovoltaica (alternativa C): retorno rápido, payback ≈ 4,0 anos com reajuste. Peça pelo menos 3 orçamentos.
- 3º — Aquecedor solar de água (alternativa B): retorno moderado, payback ≈ 5,1 anos com reajuste. Peça pelo menos 3 orçamentos.
- Observação: as economias de A, B e C se sobrepõem e NÃO devem ser somadas. Para A + C use o pacote, que dimensiona o solar depois da eficiência.

## Resumo

5 cenários, 0 falha(s).

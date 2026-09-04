# Como preencher a planilha dos 8 eixos

A planilha é a **fonte** do painel dos eixos. O que estiver nela aparece no
painel; o que não estiver, não existe para o painel.

Importe `modelo-eixos-pnc.csv` no Google Sheets, publique a planilha e a
sincronização diária faz o resto.

---

## As colunas

| Coluna | O que é | Obrigatória |
|---|---|---|
| **Prioridade** | `Alta`, `Média` ou `Baixa`. Vazio vira Média. | não |
| **Eixo** | Um dos 8 eixos do PNC, com o número na frente. Copie do modelo, sem alterar a grafia. | **sim** |
| **Processo** | Agrupamento dentro do eixo. Pode ficar vazio. | não |
| **Atividade** | Subdivisão do processo. Pode ficar vazio. | não |
| **Cod_Task** | Código no formato `1.1.1`. É por ele que as dependências se ligam. | **sim** |
| **Tarefa** | O que precisa ser feito, em uma frase. | **sim** |
| **Depende de** | Um ou mais `Cod_Task` que precisam terminar antes. Separe por `;`. | não |
| **Responsável** | Quem toca. Pode ser pessoa, equipe ou instituição. | não |
| **Prazo** | `DD/MM/AAAA`. Enquanto não houver data, deixe **`não definido ainda`**. | não |
| **Status** | `Não iniciado`, `Em andamento`, `Concluído`, `Bloqueado` ou `Em risco`. | **sim** |

---

## O código da tarefa

`Cod_Task` é o que amarra a rede de dependências. A convenção é
`eixo.processo.tarefa`:

```
1.1.1   eixo 1, primeiro bloco, primeira tarefa
1.1.2   a tarefa seguinte do mesmo bloco
1.2.1   um novo bloco dentro do eixo 1
```

O número do eixo tem de bater com a coluna Eixo. Uma tarefa do eixo 3 começa
com `3.`.

## Dependências

`Depende de` recebe o código do que precisa acontecer antes. Uma tarefa com
dependência aparece como **travada** no painel enquanto o predecessor não
estiver concluído — e é assim que o painel identifica os gargalos.

```
Cod_Task  Tarefa                          Depende de
3.1.1     Levantar acervos do Iphan
3.1.2     Definir o crosswalk              3.1.1
3.1.3     Executar a coleta                3.1.2
```

Isso vira uma cadeia de três passos. Se `3.1.1` não estiver concluída, as duas
seguintes aparecem travadas, e `3.1.1` aparece como gargalo.

Para depender de mais de uma: `3.1.1; 2.4.2`.

## Prazos

Enquanto a data não estiver acordada, escreva **`não definido ainda`**. O painel
mostra a tarefa como *sem prazo* — não a trata como atrasada e não a coloca na
linha do tempo. Quando a data for definida, troque por `DD/MM/AAAA` e ela entra
no cronograma na sincronização seguinte.

Isso é deliberado: prazo em branco e prazo vencido são coisas diferentes, e
misturar as duas faria o painel acusar atraso onde só há indefinição.

## Status

| Status | Quando usar |
|---|---|
| `Não iniciado` | ainda não começou |
| `Em andamento` | em execução |
| `Concluído` | terminado |
| `Bloqueado` | parado por causa externa — aparece nos alertas |
| `Em risco` | corre risco de não cumprir o prazo — aparece nos alertas |

O painel calcula sozinho quais tarefas estão **travadas por dependência**. Não
use `Bloqueado` para isso — reserve-o para bloqueios que a rede não enxerga,
como falta de decisão ou de orçamento.

---

## O que o painel deriva sozinho

Não precisa preencher: percentual de conclusão, progresso por eixo, quais
tarefas estão travadas, quais estão prontas para iniciar, qual é o gargalo
principal, a cadeia mais longa e a evolução ao longo do tempo. Tudo isso sai
das colunas acima.

A evolução ao longo do tempo começa a existir a partir da primeira
sincronização: cada dia gera um retrato, e a série se forma com o tempo. No
começo o gráfico terá um ponto só.

---

## Publicar a planilha

1. No Google Sheets: **Arquivo → Compartilhar → Publicar na web**.
2. Escolha a aba, formato **CSV**, e publique.
3. Copie o ID da planilha, que está na URL entre `/d/` e `/edit`.
4. Coloque esse ID no workflow `.github/workflows/sync-planilha.yml`, no lugar
   de `COLOQUE_AQUI_O_ID_DA_PLANILHA`.

A sincronização roda todo dia às 6h de Brasília e também pode ser disparada à
mão em Actions → *Sincronizar planilha dos eixos* → *Run workflow*.

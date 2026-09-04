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
| **Cod_Task** | Código no formato `E1.1.1`. É por ele que as dependências se ligam. **O `E` na frente é obrigatório** — veja abaixo. | **sim** |
| **Tarefa** | O que precisa ser feito, em uma frase. | **sim** |
| **Depende de** | Um ou mais `Cod_Task` que precisam terminar antes. Separe por `;`. | não |
| **Responsável** | Quem toca. Pode ser pessoa, equipe ou instituição. | não |
| **Prazo** | `DD/MM/AAAA`. Enquanto não houver data, deixe **`não definido ainda`**. | não |
| **Status** | `Não iniciado`, `Em andamento`, `Concluído`, `Bloqueado` ou `Em risco`. | **sim** |

---

## O código da tarefa

`Cod_Task` é o que amarra a rede de dependências. A convenção é
`E` mais `eixo.bloco.tarefa`:

```
E1.1.1   eixo 1, primeiro bloco, primeira tarefa
E1.1.2   a tarefa seguinte do mesmo bloco
E1.2.1   um novo bloco dentro do eixo 1
```

O número do eixo tem de bater com a coluna Eixo. Uma tarefa do eixo 3 começa
com `E3.`.

### Por que o `E` na frente

Sem ele, o Google Sheets **converte o código em data, sem avisar**: digite
`1.1.1` numa célula e ele vira `01/01/2001`; `7.2.1` vira `07/02/2001`. Como é
o código que liga uma demanda à outra, essa conversão quebraria a rede de
dependências inteira — e de forma silenciosa, porque a planilha continuaria
parecendo correta.

A letra na frente faz a planilha tratar o valor como texto. Qualquer prefixo de
até três letras funciona; o modelo usa `E`, de eixo.

## Dependências

`Depende de` recebe o código do que precisa acontecer antes. Uma tarefa com
dependência aparece como **travada** no painel enquanto o predecessor não
estiver concluído — e é assim que o painel identifica os gargalos.

```
Cod_Task  Tarefa                          Depende de
E3.1.1    Levantar acervos do Iphan
E3.1.2    Definir o crosswalk              E3.1.1
E3.1.3    Executar a coleta                E3.1.2
```

Isso vira uma cadeia de três passos. Se `E3.1.1` não estiver concluída, as duas
seguintes aparecem travadas, e `E3.1.1` aparece como gargalo.

Para depender de mais de uma: `E3.1.1; E2.4.2`.

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
4. No repositório, em **Settings → Secrets and variables → Actions →
   Variables**, crie a variável `PLANILHA_ID` com esse valor.

Opcionalmente, crie também `PROXIMA_REUNIAO` (no formato `AAAA-MM-DD`) e
`GUARDIA` — as duas preenchem o cartão de atualização do painel.

A sincronização roda todo dia às 6h de Brasília e também pode ser disparada à
mão em Actions → *Sincronizar planilha dos eixos* → *Run workflow*.

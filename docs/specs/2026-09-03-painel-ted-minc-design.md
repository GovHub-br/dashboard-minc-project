# Painel de Entregas e Status do TED — desenho

**Data:** 03/09/2026
**TED:** nº 01/2026/SGE/SE/MINC — UnB (Lab Livre · Gov Hub) × Ministério da Cultura
**Público:** Ministério da Cultura — prestação de contas
**Referência formal:** [`RochaCarla/dashboard-MCid`](https://github.com/RochaCarla/dashboard-MCid)

---

## 1. Problema

O estado de execução do TED existe hoje espalhado por três lugares: o quadro de
acompanhamento de produtos mantido pela CGIIC, o corpo do 3º Relatório Parcial e o
repositório público. Quem precisa responder *"em que pé está o TED"* — no Ministério ou na
coordenação — lê 285 páginas ou pergunta a alguém.

O painel reúne esse estado numa página só, sem produzir número novo: **cada valor exibido é
o mesmo que está no relatório entregue, vindo da mesma fonte.**

## 2. Restrição que governa o desenho

Em prestação de contas, o risco maior não é o painel ser feio — é ele **divergir do
documento contratual**. Um número no painel que não bate com o número no PDF anexado ao
relatório é um problema de credibilidade, não de software.

O `INVENTARIO.md` do relatório já registra esse tipo de falha ocorrendo: sete números
errados no compilado documental, contagem de DAGs divergente entre texto e painel na mesma
página, schema da camada semântica com três grafias em três documentos.

Daí a regra que orienta todo o resto: **o painel não é uma segunda fonte da verdade.** Ele é
uma vista sobre a fonte que já existe.

## 3. Arquitetura

**Repositório próprio**, separado do `data-application-minc`, no padrão standalone do
`dashboard-MCid`. O público do painel é quem decide, não quem desenvolve, e o ciclo de vida
é outro: o painel muda a cada relatório parcial, o repositório técnico muda a cada commit.
Misturar os dois faria o Ministério entrar num repositório de engenharia de dados para ler
um quadro de prestação de contas.

**Sem build.** HTML, CSS e JavaScript estáticos, com os dados em JSON ao lado. O GitHub
Pages serve o diretório direto; não há Jinja, gerador de site nem etapa de compilação. O
único Python do repositório é de extração e de validação, e nenhum dos dois roda para
exibir a página.

### Estrutura

```
dashboard-minc-project/
├── index.html                    o painel inteiro: estrutura, estilo e D3
├── dados/
│   └── ted.json                  o acervo: metas, artefatos, documentos,
│                                 encaminhamentos, riscos
├── assets/
│   ├── tema.css                  identidade Gov Hub
│   └── d3.v7.min.js              D3 vendorizado, versão fixa
├── scripts/
│   ├── extrai.py                 gera ted.json a partir dos geradores do relatório
│   └── valida.py                 as verificações da seção 6
├── docs/specs/                   este documento
├── .github/workflows/
│   ├── pages.yml                 publica no GitHub Pages
│   └── valida.yml                roda valida.py em todo push e PR
└── README.md
```

### Duas decisões de dependência

**D3 vendorizado, não por CDN.** O `dashboard-MCid` carrega D3 de CDN. Aqui ele fica no
repositório, com versão fixa. O painel será aberto em reunião com o Ministério, às vezes em
rede restrita de órgão público; uma dependência de CDN é um modo de falhar na hora errada,
diante de quem menos se quer. Custa ~280 KB versionados.

**Nenhuma dependência Python além da biblioteca padrão.** `extrai.py` e `valida.py` usam só
`json`, `re` e `importlib`. Sem `requirements.txt`, sem ambiente virtual — clonar e rodar.

### Como se desenvolve e como se publica

`fetch()` não lê `file://`. Localmente: `python3 -m http.server` na raiz. No GitHub Pages
funciona direto, sem servidor. É o mesmo arranjo do `dashboard-MCid`.

A alternativa seria embutir o JSON no HTML e abrir por duplo clique, ao custo de fundir
dados e apresentação num arquivo só. Mantida a separação: o `ted.json` precisa ser legível e
diffável por si, porque é ele que alguém vai conferir contra o relatório.

### Origem do acervo

O `dados/ted.json` é extraído dos dois geradores do 3º Relatório Parcial, que hoje vivem em
`~/Documents/minc-relatorio-parcial/`:

- `relatorio/conteudo.py` — as 6 metas, o balanço por meta, os 22 encaminhamentos e os 7 riscos;
- `doc-acompanhamento/conteudo.py` — os 20 artefatos com situação anterior, atual e lastro; as 7 pendências, com o que falta e o que destrava cada uma; os 12 documentos e seus anexos.

A extração é feita **uma vez**, por um script descartável, e o resultado é versionado. Nenhum
número é digitado à mão nem reconstruído de memória.

Depois disso o `dados/ted.json` passa a ser a fonte, editada uma vez por relatório parcial — a
cadência real com que esses dados mudam. Isso segue o princípio que o `docs-pages/` já
adota: *a coleta roda na máquina de quem edita, o acervo é versionado, o CI nunca precisa
de rede.*

**Consequência aceita:** o vínculo com o relatório é de origem, não contínuo. Se o 4º
Relatório Parcial mudar um número e ninguém atualizar o `dados/ted.json`, o painel fica velho — e
silenciosamente. A mitigação está na seção 6.

## 4. As sete seções do painel

### 4.1 Faixa de indicadores

Seis números, sem gráfico: **20** artefatos acompanhados · **11** entregues · **2** entregues
como proposta · **5** parciais · **2** não entregues · **12** documentos publicados.

### 4.2 Evolução entre relatórios

O argumento central para o Ministério, e o único gráfico que responde *"o período rendeu?"*:

| Situação | 2º Relatório | 3º Relatório |
|---|---|---|
| Entregue | 0 | **11** |
| Entregue como proposta | 0 | **2** |
| Parcialmente entregue | 6 | 5 |
| Não entregue | 14 | **2** |

Barras pareadas em D3. Os 14 não entregues do 2º Relatório são os 11 assim marcados mais os
3 com a marcação *falta apresentar artefato*, conforme o próprio documento agrega.

Acompanha a nota que o documento faz — a mudança decorre menos de trabalho novo que de
**publicação**: parte do que a avaliação anterior não localizou existia como código, não
como documento. Registrar isso protege o painel de uma leitura que o Ministério faria
sozinho e que seria pior: a de que treze artefatos foram produzidos em quatro meses.

### 4.2.1 Divergência com o texto do 3º Relatório — decisão registrada

O 3º Relatório Parcial declara **12 entregues, 6 parciais e 2 não entregues**. A conferência
item a item das 20 linhas do quadro dá **11 entregues, 2 entregues como proposta, 5 parciais
e 2 não entregues**. Ambos fecham em 20; a divisão entre entregue e parcial difere em um
item. Duas causas, ambas rastreadas:

1. **Manual de manutenção contado duas vezes.** Aparece sob *Não entregues*, com texto
   próprio, e também na tabela de *Parcialmente entregues*. A tabela dos 20 artefatos o marca
   como não entregue. São 5 parciais, não 6.
2. **As duas arquiteturas entregues como proposta.** 11 entregues mais arquitetura física e
   arquitetura de segurança dá 13 em condição de entregue. O total de 12 só fecha se uma das
   duas contar como entregue e a outra como parcial, sem critério que as distinga.

**Decisão:** o painel adota a contagem da tabela, com as arquiteturas-proposta em categoria
própria. Preserva a distinção entre o que opera e o que está projetado — que o documento faz
questão de manter em seu *callout* *"descrever o estado-alvo não é o mesmo que implantá-lo"*
— e não exige a escolha arbitrária entre as duas arquiteturas.

**Consequência a comunicar:** o painel exibirá números diferentes dos do texto do relatório
já entregue. A diferença é de classificação, não de fato: os mesmos 20 artefatos, nas mesmas
situações. O painel registra a nota acima, ao pé da seção, para que a diferença seja lida
como precisão e não como correção silenciosa. Corrigir o `conteudo.py` do
`doc-acompanhamento` e regerar o PDF fica registrado como encaminhamento, fora deste escopo.

### 4.3 As seis metas

Um cartão por meta, com o rótulo, o balanço do período extraído do capítulo de conclusões e
a quantidade de encaminhamentos para o próximo período.

**Sem detalhe por produto.** A matriz Meta × Produto exigiria a lista de produtos de cada
uma das seis metas, e essa lista não existe em fonte estável: aparece no `ESQUELETO.md` —
arquivo de trabalho, não o relatório — e apenas para as Metas 02 a 05. Construí-la à mão
criaria justamente a segunda fonte da verdade que a seção 2 existe para evitar. O quadro dos
20 artefatos (seção 4.4) já entrega a granularidade que o Ministério precisa, com lastro.

Fica registrado como candidato a uma versão futura, se o TED ou o próximo relatório
publicarem a matriz de produtos em forma citável.

Meta 01 · Diagnóstico e mapeamento — Meta 02 · Integração e jornada dos dados do PNC —
Meta 03 · Governança, adoção e transferência de tecnologia — Meta 04 · Agentes de IA —
Meta 05 · Governança de dados do SNIIC — Meta 06 · Acervos digitais / Brasiliana Cultura.

### 4.4 Quadro dos 20 artefatos

Tabela filtrável por situação, nas colunas do quadro da CGIIC: artefato · antes · agora ·
onde está. A coluna *onde está* linka o anexo ou o arquivo no repositório.

É a seção que responde à pergunta que o Ministério de fato faz — *cadê?* — e por isso
nenhuma linha pode existir sem lastro preenchido.

### 4.5 Cronograma — setembro a novembro de 2026

Os 22 encaminhamentos do capítulo de conclusões, agrupados por meta, dentro da janela do
próximo período avaliativo. Sem datas por item: o relatório não as declara, e inventá-las
seria criar informação que o documento contratual não sustenta.

Distribuição: Meta 01 (3) · Meta 02 (5) · Meta 03 (3) · Meta 04 (3) · Meta 05 (4) ·
Meta 06 (4).

Cada encaminhamento recebe um marcador de **quem destrava**, derivado do que o
`doc-acompanhamento` já registra na coluna *o que destrava*:

| Marco | Quem destrava |
|---|---|
| Definição conjunta de competências institucionais | MinC + UnB |
| Ambiente de produção / homologação | MinC |
| Definição de requisitos dos painéis | MinC |
| Execução técnica | UnB |

As sete pendências do quadro — 2 não entregues e 5 parciais — distribuem-se assim:

| Quem destrava | Pendências |
|---|---|
| MinC + UnB, em conjunto | Matriz de papéis e responsabilidades |
| MinC | Manual de manutenção, políticas de acesso, manual de uso, evidências de testes |
| UnB | Sincronização do catálogo de metadados, relação de componentes e versões |

**Cinco das sete não dependem só da UnB.** O painel diz isso como registro de dependência,
não como acusação — a mesma voz do documento, que já declara *"não entregue é dito sem
atenuação"*. As duas que dependem só da UnB aparecem nomeadas, com o mesmo destaque.

### 4.6 Matriz de riscos

Os 7 riscos do relatório num grid probabilidade × impacto, cada um com sua medida
mitigadora. Dois em Alto/Alto: a inexistência de infraestrutura de produção e a
indisponibilidade de 90% dos itens do sistema MinC para coleta computacional.

Seção clássica de painel gerencial, e aqui inteiramente lastreada — o relatório já traz
risco, probabilidade, impacto e mitigação para os sete.

### 4.7 Onde encontrar cada documento

Os 12 documentos técnicos com o anexo correspondente. Encerra o painel do mesmo modo que o
documento de acompanhamento encerra: dizendo onde está cada coisa.

## 5. Identidade visual

Identidade oficial do Gov Hub — roxo `#7A34F3` e a paleta do livro *Gov Hub: um guia
prático* —, aplicada via o skill `govhub-visual-identity` na implementação.

Herda a estrutura do `src/assets/tema.css` para que o painel não destoe do site de
documentação. As cores de status seguem a semântica já usada nos documentos do relatório:
entregue, parcial e não entregue com contraste suficiente para leitura em projeção, que é
como isto vai ser visto numa reunião com o Ministério.

Acessibilidade: status nunca comunicado só por cor — sempre cor + rótulo textual.

## 6. Consistência: o que o build verifica

`scripts/valida.py` valida no build e **falha** em vez de publicar número errado:

1. **Fechamento do quadro** — as situações somam 20 nas duas colunas, anterior e atual, com
   as arquiteturas-proposta contadas em categoria própria. É a validação que teria pego a
   divergência da seção 4.2.1 antes da publicação.
   Nenhum artefato pode aparecer em mais de uma situação — a regra que a duplicidade do
   manual de manutenção violava.
2. **Lastro obrigatório** — todo artefato com situação *entregue* tem o campo *onde está* preenchido.
3. **Integridade de referência** — todo produto citado pertence a uma meta declarada; todo documento referenciado como anexo consta da relação de anexos.
4. **Carimbo de origem** — o `dados/ted.json` declara a que relatório parcial se refere, e o painel exibe essa data. Um painel velho fica visivelmente velho, em vez de silenciosamente errado.

A verificação 4 é a mitigação do risco aceito na seção 3: não impede a defasagem, mas a
torna visível a quem lê.

## 7. Fora do escopo

| Item | Por quê |
|---|---|
| Rede de dependências entre tarefas | O TED não mapeia dependências entre produtos. O grafo do MCid não tem correspondente aqui. |
| Gantt com datas por produto | Não há datas por produto em nenhuma fonte. O cronograma é por janela avaliativa. |
| Sincronização com planilha | Criaria a segunda fonte da verdade que a seção 2 existe para evitar. |
| Visão operacional para a equipe UnB | O público decidido é o Ministério. Uma aba de gestão interna é outro projeto. |
| Execução financeira do TED | Não há dado financeiro em nenhuma das fontes disponíveis. |

## 8. Verificação de pronto

- `cd docs-pages && PYTHONPATH=. python -m tooling.build` gera o site sem erro.
- `ted.html` abre sem erro no console do navegador.
- As quatro validações da seção 6 passam; alterar um número no `dados/ted.json` para um valor
  inconsistente faz o build falhar.
- Os números do painel conferem, um a um, com o 3º Relatório Parcial.
- O painel é legível em projeção e em tela de celular.

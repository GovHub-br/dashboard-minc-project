# Painéis do Gov Hub no Ministério da Cultura

Dois painéis, com fontes e propósitos distintos.

**[Entregas do TED](https://govhub-br.github.io/dashboard-minc-project/)** —
acompanhamento do **Termo de Execução Descentralizada nº 01/2026/SGE/SE/MINC**,
firmado entre a Universidade de Brasília e o Ministério da Cultura. Voltado à
prestação de contas: o que foi entregue, com que evidência, e o que falta.

**[Trabalho nos 8 eixos](https://govhub-br.github.io/dashboard-minc-project/eixos.html)** —
as demandas conduzidas pelo Gov Hub em cada eixo do Plano Nacional de Cultura
2026-2036. Voltado à condução do trabalho: o que depende do quê, o que está
travado e o que está pronto para começar.

---

## Painel do TED

Reúne numa página o estado de execução que estava espalhado pelo quadro de
acompanhamento de produtos da CGIIC, pelo corpo do 3º Relatório Parcial e pelo
repositório público da plataforma.

**Três palavras, que não são sinônimos.** *Produto* é o que o Termo espera — são
19, e não mudam. *Artefato* é o que ficou disponível no período e compõe um
produto — são os 20 do quadro de acompanhamento da CGIIC. *Entrega* é quando o
produto inteiro é contemplado: estado de produto, nunca nome de peça. A página
abre pelas três definições, porque foi a confusão entre elas que tornou a versão
anterior ilegível.

Oito seções, nesta ordem: o acompanhamento por meta e produto, a situação dos
artefatos, o balanço das seis metas, a evolução entre relatórios, o quadro dos 20
artefatos com lastro, o que vem no próximo período, os riscos e a relação dos
documentos produzidos.

**Acompanhamento por meta e produto** abre a página. Cada um dos 19 produtos é
uma ficha que abre com o que o Termo prevê, o que foi feito até aqui, os
artefatos que o compõem com a situação de cada um, e os encaminhamentos da sua
meta. A cobertura por relatório vem do sumário de cada um; o que foi feito vem da
seção correspondente do 3º Relatório; o vínculo artefato→produto vem da redação
do Termo, e só onde o Termo não nomeia o artefato é que vem do lugar em que o 3º
Relatório o documenta — a marca ao lado registra qual dos dois casos é.

**O estado de entrega é preenchido à mão**, na tabela `ESTADO` de
`scripts/produtos.py`. O painel não o deduz: um produto pode ter todos os seus
artefatos entregues sem estar entregue, e doze dos dezenove não têm artefato
algum no quadro. Linha em branco aparece como *a classificar* e não reprova a
validação — falta de classificação é estado legítimo, não erro de acervo.

Na leitura do 3º Relatório Parcial: 6 entregues, 11 em andamento, 2 previstos.
A reclassificação acompanha cada novo relatório.

**Fonte:** `dados/ted.json`, extraído uma vez dos geradores do 3º Relatório
Parcial por `scripts/extrai.py`. Atualiza-se a cada relatório parcial.

O painel **não produz número novo** — cada valor vem do relatório e pode ser
conferido na fonte. Onde a leitura diverge do texto do relatório, a divergência
está registrada e justificada na própria página e na seção 4.2.1 do documento de
desenho.

## Painel dos 8 eixos

Alimentado por uma planilha no Google Sheets, sincronizada diariamente. Mostra
status consolidado, progresso por eixo, alertas, a rede de pré-requisitos entre
as demandas, a linha do tempo e a evolução ao longo do tempo.

**Fonte:** `dados/eixos.json` e `dados/historico.json`, gerados de
`planilha/modelo-eixos-pnc.csv` por `scripts/planilha_para_json.py`.

Para preencher a planilha, veja **[planilha/COMO-PREENCHER.md](planilha/COMO-PREENCHER.md)**.

Prazos ainda não acordados ficam como `não definido ainda`. O painel os trata
como *sem prazo*, nunca como atrasados — prazo em branco e prazo vencido são
coisas diferentes.

---

## Como rodar localmente

As páginas leem os dados por `fetch()`, que não funciona sobre `file://`. É
preciso servir o diretório:

```bash
python3 -m http.server
```

Depois, abrir <http://localhost:8000>.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `index.html` | Painel do TED. |
| `eixos.html` | Painel dos 8 eixos do PNC. |
| `dados/` | Os acervos: `ted.json`, `eixos.json`, `historico.json`. |
| `assets/` | Tema visual, scripts das páginas e a biblioteca D3, versionada. |
| `planilha/` | Modelo da planilha dos eixos e o guia de preenchimento. |
| `scripts/` | Extração e validação. Só biblioteca padrão do Python. `produtos.py` guarda a tabela dos 19 produtos do TED, o que cada um entregou, a cobertura por relatório, o estado de entrega e a classificação dos riscos. |
| `tests/` | Testes dos dois conversores. |
| `docs/` | Documento de desenho e plano de implementação. |

Não há etapa de compilação. O GitHub Pages serve o diretório como está, e nada
é carregado de CDN — o painel abre em rede restrita.

## Automação

| Workflow | O que faz |
|---|---|
| `valida.yml` | Roda os testes e verifica a consistência do acervo do TED a cada push. |
| `sync-planilha.yml` | Baixa a planilha dos eixos, converte e commita. Diariamente às 6h e sob demanda. |
| `pages.yml` | Publica no GitHub Pages. |

Para a sincronização funcionar, cadastre o ID da planilha publicada em
**Settings → Secrets and variables → Actions → Variables**, com o nome
`PLANILHA_ID`. Opcionalmente, `PROXIMA_REUNIAO` (AAAA-MM-DD) e `GUARDIA`.

## Verificação

```bash
python3 -m unittest discover -s tests -v
python3 scripts/valida.py
```

---

Projeto Gov Hub · Lab Livre · Faculdade do Gama, Universidade de Brasília

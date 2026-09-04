# Painel de Entregas e Status do TED — MinC

Painel gerencial de acompanhamento do **Termo de Execução Descentralizada
nº 01/2026/SGE/SE/MINC**, firmado entre a Universidade de Brasília e o Ministério da
Cultura para a implantação de uma plataforma de dados em software livre para o Sistema
Nacional de Informações e Indicadores Culturais (SNIIC).

O painel reúne numa página o estado de execução que hoje está espalhado pelo quadro de
acompanhamento de produtos da CGIIC, pelo corpo do 3º Relatório Parcial e pelo repositório
público da plataforma.

## O que ele mostra

- **Indicadores** — os 20 artefatos acompanhados e sua situação atual.
- **Evolução entre relatórios** — o que mudou do 2º para o 3º Relatório Parcial.
- **As seis metas** — balanço do período e situação dos produtos de cada meta.
- **Quadro dos artefatos** — item a item, com a localização da evidência de cada um.
- **Cronograma** — os encaminhamentos para o período avaliativo de setembro a novembro de 2026.
- **Riscos** — os riscos identificados no período, com probabilidade, impacto e medida mitigadora.
- **Documentos** — os 12 documentos técnicos produzidos e seus anexos no relatório.

## Princípio

O painel **não produz número novo**. Cada valor exibido vem do 3º Relatório Parcial e do
quadro de acompanhamento de produtos, e pode ser conferido na fonte. Onde a leitura do
painel diverge do texto do relatório, a divergência está registrada e justificada — veja a
seção 4.2.1 do documento de desenho.

## Como rodar localmente

O painel lê os dados por `fetch()`, que não funciona sobre `file://`. É preciso servir o
diretório:

```bash
python3 -m http.server
```

Depois, abrir <http://localhost:8000>.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `index.html` | O painel: estrutura, estilo e gráficos. |
| `dados/ted.json` | O acervo — metas, artefatos, documentos, encaminhamentos e riscos. |
| `assets/` | Tema visual e a biblioteca D3, versionada. |
| `scripts/valida.py` | Verificações de consistência do acervo, executadas no CI. |
| `docs/specs/` | O documento de desenho do painel. |

Não há etapa de compilação. O GitHub Pages serve o diretório como está.

## Atualização

O `dados/ted.json` é atualizado a cada relatório parcial. Ele declara a que relatório se
refere, e o painel exibe essa data — um painel desatualizado fica visivelmente
desatualizado, em vez de silenciosamente errado.

Toda alteração passa por `scripts/valida.py`, que falha se as contagens não fecharem ou se
um artefato declarado como entregue estiver sem evidência.

---

Projeto Gov Hub · Lab Livre · Faculdade do Gama, Universidade de Brasília

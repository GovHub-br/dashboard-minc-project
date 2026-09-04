# Painel de Entregas e Status do TED — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o painel gerencial de acompanhamento do TED 01/2026/SGE/SE/MINC, para prestação de contas ao Ministério da Cultura, publicado em GitHub Pages.

**Architecture:** Página estática sem etapa de compilação. `index.html` traz a estrutura semântica, `assets/tema.css` o estilo, `assets/painel.js` o carregamento e as seções em HTML, `assets/graficos.js` as duas visualizações D3. Os dados vivem em `dados/ted.json`, extraído uma vez dos geradores do 3º Relatório Parcial por `scripts/extrai.py` e verificado a cada push por `scripts/valida.py`.

**Tech Stack:** HTML5, CSS3, JavaScript ES2020, D3.js v7 (vendorizado), Python 3 (só biblioteca padrão), GitHub Actions, GitHub Pages.

**Desenho:** `docs/specs/2026-09-03-painel-ted-minc-design.md`

## Global Constraints

- **Nenhuma dependência de CDN.** D3 vendorizado em `assets/d3.v7.min.js`. Fonte Inter por `font-family` com fallback de sistema, sem `@import` do Google Fonts. Motivo: o painel é aberto em reunião com o Ministério, às vezes em rede restrita de órgão público.
- **Nenhuma dependência Python além da biblioteca padrão.** Sem `requirements.txt`, sem ambiente virtual.
- **Nenhuma etapa de compilação.** O GitHub Pages serve o diretório como está.
- **Todo texto de interface em português do Brasil.**
- **Status nunca comunicado só por cor** — sempre cor mais rótulo textual.
- **O painel não produz número novo.** Todo valor exibido vem de `dados/ted.json`, que vem do relatório. Nenhum número é calculado a partir de premissa que o relatório não sustente.
- **Contagem adotada:** 11 entregues, 2 entregues como proposta, 5 parciais, 2 não entregues, num total de 20 artefatos. Diverge do texto do relatório (12/6/2) pelas razões da seção 4.2.1 do desenho, e o painel exibe a nota que explica.

### Tokens da identidade Gov Hub

Valores oficiais, de `~/.claude/skills/govhub-visual-identity`. Copiar literalmente:

```css
--primary-purple:   #7A34F3;  /* cor-assinatura */
--secondary-purple: #8B5CF6;
--accent-orange:    #F97316;  /* acento pontual, um por seção */
--purple-600:       #7C3AAD;  /* hover/foco */
--purple-700:       #5B21B6;  /* active */
--text-strong:      #202020;
--text-body:        #2D3748;
--text-muted:       #666666;
--bg-white:         #FFFFFF;
--bg-light:         #F7F7F7;
--bg-subtle:        #F8F9FA;
--color-success:    #10B981;
--color-warm:       #F19F42;
--shadow-md:        0 2px 10px rgba(0,0,0,0.1);
--radius-md:        10px;
```

### Cores de situação

Extensão dos tokens, com justificativa. Cada uma sempre acompanhada de rótulo textual.

| Situação | Cor | Por quê |
|---|---|---|
| Entregue | `--color-success` `#10B981` | Verde de sucesso dos tokens. |
| Entregue como proposta | `--secondary-purple` `#8B5CF6` | Da família da marca, distinto do verde: é projetado, não implantado. |
| Parcial | `--color-warm` `#F19F42` | Âmbar de atenção dos tokens. |
| Não entregue | `#C2410C` | Extensão. O documento declara *"não entregue é dito sem atenuação"* — a cor não atenua. Terracota em vez de vermelho puro, para não destoar da paleta. |

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `index.html` | Estrutura semântica das sete seções. Sem conteúdo de dados — tudo entra por JS. |
| `assets/tema.css` | Tokens Gov Hub, tipografia, cartões, tabela, responsividade, impressão. |
| `assets/painel.js` | Carrega `ted.json`, deriva agregados, renderiza as seções de HTML. |
| `assets/graficos.js` | As duas visualizações D3: evolução entre relatórios e matriz de riscos. |
| `assets/d3.v7.min.js` | D3 vendorizado. |
| `dados/ted.json` | O acervo. |
| `scripts/extrai.py` | Extração única a partir dos geradores do relatório. |
| `scripts/valida.py` | As quatro verificações de consistência. |
| `tests/test_valida.py` | Testes do validador. |
| `.github/workflows/valida.yml` | Roda os testes e o validador em todo push e PR. |
| `.github/workflows/pages.yml` | Publica no GitHub Pages. |

**Separação `painel.js` / `graficos.js`:** responsabilidades diferentes — montar DOM a partir de dados contra desenhar SVG com D3. Se `painel.js` passar de ~500 linhas, dividir por seção.

---

### Task 1: Extrator e acervo

Produz `dados/ted.json` a partir dos dois geradores do 3º Relatório Parcial. Roda uma vez; depois o JSON é a fonte.

**Files:**
- Create: `scripts/extrai.py`
- Create: `dados/ted.json` (gerado)

**Interfaces:**
- Consumes: nada.
- Produces: `dados/ted.json` com as chaves `ted`, `origem`, `metas`, `artefatos`, `pendencias`, `riscos`, `documentos`. Toda task seguinte lê esse arquivo.

**Formato de saída** — cada objeto, com os campos exatos:

```
ted         { numero, partes, objeto }
origem      { relatorio, periodo, proximo_periodo, apurado_em }
metas       [ { num, nome, balanco, encaminhamentos[] } ]        6 itens
artefatos   [ { nome, antes, agora, onde } ]                     20 itens
pendencias  [ { artefato, situacao, falta, destrava, quem } ]     7 itens
riscos      [ { risco, probabilidade, impacto, mitigacao } ]      7 itens
documentos  [ { arquivo, anexo } ]                               12 itens
```

- [ ] **Passo 1: Escrever `scripts/extrai.py`**

Este código foi executado contra o relatório real e produz a saída esperada. Copiar como está.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai o acervo do painel a partir dos geradores do 3º Relatório Parcial.

Roda uma vez, na máquina de quem tem o relatório. O resultado é versionado em
dados/ted.json e passa a ser a fonte do painel.

Uso:
    python3 scripts/extrai.py ~/Documents/minc-relatorio-parcial > dados/ted.json
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Quem destrava cada pendência. Derivado da coluna "o que destrava" do
# doc-acompanhamento; a classificação é do painel, não do documento.
# --------------------------------------------------------------------------
QUEM_DESTRAVA = {
    "Matriz de papéis e responsabilidades": "MinC + UnB",
    "Manual de manutenção": "MinC",
    "Políticas de acesso": "MinC",
    "Manual de uso": "MinC",
    "Evidências de testes e validação": "MinC",
    "Metadados": "UnB",
    "Relação de componentes e versões": "UnB",
}


def carrega(caminho):
    """Importa um conteudo.py sem instalá-lo."""
    spec = importlib.util.spec_from_file_location("conteudo", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def texto(html):
    """Remove marcação, preservando o texto."""
    return re.sub(r"<[^>]+>", "", html).replace("&middot;", "·").strip()


def blocos(capitulos, num):
    for cap in capitulos:
        if cap["num"] == num:
            return cap["blocos"]
    return []


def tabelas(bls, primeira_coluna):
    """Junta todas as tabelas cujo cabeçalho começa com dado rótulo."""
    linhas = []
    for b in bls:
        if b[0] == "tabela" and b[1][0] == primeira_coluna:
            linhas += b[2]
    return linhas


def extrai_acompanhamento(raiz):
    mod = carrega(raiz / "doc-acompanhamento" / "conteudo.py")
    caps = mod.CAPITULOS

    artefatos = [
        {
            "nome": texto(l[0]),
            "antes": texto(l[1]),
            "agora": texto(l[2]),
            "onde": texto(l[3]),
        }
        for l in tabelas(blocos(caps, "02"), "Artefato")
    ]

    pendencias = []
    for l in tabelas(blocos(caps, "04"), "Artefato"):
        nome = texto(l[0])
        # O manual de manutenção consta como não entregue na tabela dos vinte
        # artefatos e reaparece aqui entre os parciais. A tabela dos vinte é a
        # fonte; a duplicidade está registrada na seção 4.2.1 do desenho.
        situacao = next(
            (a["agora"] for a in artefatos if a["nome"] == nome), None
        )
        pendencias.append(
            {
                "artefato": nome,
                "situacao": situacao,
                "falta": texto(l[1]),
                "destrava": texto(l[2]),
                "quem": QUEM_DESTRAVA.get(nome, "—"),
            }
        )

    # Os dois não entregues não têm linha de tabela: vêm dos h4 do capítulo 04.
    for a in artefatos:
        if a["agora"] == "Não entregue" and not any(
            p["artefato"] == a["nome"] for p in pendencias
        ):
            pendencias.append(
                {
                    "artefato": a["nome"],
                    "situacao": "Não entregue",
                    "falta": "O documento",
                    "destrava": a["onde"],
                    "quem": QUEM_DESTRAVA.get(a["nome"], "—"),
                }
            )

    documentos = [
        {"arquivo": texto(l[0]), "anexo": texto(l[1])}
        for l in tabelas(blocos(caps, "05"), "Arquivo no repositório")
    ]

    return artefatos, pendencias, documentos


def extrai_relatorio(raiz):
    mod = carrega(raiz / "relatorio" / "conteudo.py")
    caps = mod.CAPITULOS

    # Capítulos 03 a 08 são as Metas 01 a 06.
    metas = []
    for cap in caps:
        t = cap.get("titulo", "")
        if re.fullmatch(r"Meta 0[1-6]", t):
            metas.append(
                {
                    "num": t[-2:],
                    "nome": cap.get("eyebrow", ""),
                    "balanco": "",
                    "encaminhamentos": [],
                }
            )

    concl = blocos(caps, "09")

    # Balanço: os parágrafos "A <strong>Meta NN</strong> ..." do capítulo 09.
    for b in concl:
        if b[0] != "p":
            continue
        achado = re.match(r"A <strong>Meta (0[1-6])</strong>\s*(.*)", b[1])
        if achado:
            num, resto = achado.group(1), texto(achado.group(2))
            for m in metas:
                if m["num"] == num:
                    m["balanco"] = resto

    # Encaminhamentos: cada ("h4", "Meta NN") é seguido de uma ("ul", [...]).
    atual = None
    for b in concl:
        if b[0] == "h4" and re.fullmatch(r"Meta 0[1-6]", b[1]):
            atual = b[1][-2:]
        elif b[0] == "ul" and atual:
            for m in metas:
                if m["num"] == atual:
                    m["encaminhamentos"] = [texto(i) for i in b[1]]
            atual = None

    riscos = []
    for l in tabelas(concl, "Risco identificado"):
        prob, _, impacto = texto(l[1]).partition("/")
        riscos.append(
            {
                "risco": texto(l[0]),
                "probabilidade": prob.strip(),
                "impacto": impacto.strip(),
                "mitigacao": texto(l[2]),
            }
        )

    return metas, riscos


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raiz = Path(sys.argv[1]).expanduser()

    artefatos, pendencias, documentos = extrai_acompanhamento(raiz)
    metas, riscos = extrai_relatorio(raiz)

    acervo = {
        "ted": {
            "numero": "01/2026/SGE/SE/MINC",
            "partes": "Universidade de Brasília × Ministério da Cultura",
            "objeto": (
                "Implantação de solução em software livre para integração, "
                "qualificação e disponibilização de dados e acervos culturais "
                "do Sistema Nacional de Cultura"
            ),
        },
        "origem": {
            "relatorio": "3º Relatório Parcial",
            "periodo": "maio a agosto de 2026",
            "proximo_periodo": "setembro a novembro de 2026",
            "apurado_em": "2026-08-31",
        },
        "metas": metas,
        "artefatos": artefatos,
        "pendencias": pendencias,
        "riscos": riscos,
        "documentos": documentos,
    }

    print(json.dumps(acervo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Passo 2: Gerar o acervo**

```bash
mkdir -p dados
python3 scripts/extrai.py ~/Documents/minc-relatorio-parcial > dados/ted.json
```

- [ ] **Passo 3: Conferir a saída**

```bash
python3 -c "
import json, collections
d = json.load(open('dados/ted.json'))
print('metas:', len(d['metas']))
print('artefatos:', len(d['artefatos']), collections.Counter(a['agora'] for a in d['artefatos']))
print('pendencias:', len(d['pendencias']))
print('riscos:', len(d['riscos']))
print('documentos:', len(d['documentos']))
print('encaminhamentos:', sum(len(m['encaminhamentos']) for m in d['metas']))
"
```

Saída esperada, exatamente:

```
metas: 6
artefatos: 20 Counter({'Entregue': 11, 'Parcial': 5, 'Entregue como proposta': 2, 'Não entregue': 2})
pendencias: 7
riscos: 7
documentos: 12
encaminhamentos: 22
```

Se algum número divergir, **parar**: o relatório mudou desde a apuração e a divergência precisa ser entendida antes de seguir.

- [ ] **Passo 4: Commit**

```bash
git add scripts/extrai.py dados/ted.json
git commit -m "feat: extrator e acervo do TED"
```

---

### Task 2: Validador de consistência

As quatro verificações da seção 6 do desenho, com testes. Roda no CI a cada push.

**Files:**
- Create: `scripts/valida.py`
- Create: `tests/test_valida.py`
- Create: `.github/workflows/valida.yml`

**Interfaces:**
- Consumes: `dados/ted.json` da Task 1.
- Produces: `valida(acervo) -> list[str]` — recebe o dicionário do acervo e devolve a lista de problemas encontrados, vazia se tudo fecha. `main()` imprime os problemas e sai com código 1 se houver algum.

**As quatro verificações:**

1. **Fechamento do quadro** — as situações somam 20 nas colunas *antes* e *agora*; nenhum artefato aparece duas vezes.
2. **Lastro obrigatório** — todo artefato com situação começando em *Entregue* tem `onde` preenchido.
3. **Integridade de referência** — toda pendência corresponde a um artefato existente, e sua `situacao` bate com o `agora` daquele artefato.
4. **Carimbo de origem** — `origem` traz `relatorio`, `periodo` e `apurado_em`, e `apurado_em` está no formato `AAAA-MM-DD`.

- [ ] **Passo 1: Escrever o teste que falha**

Criar `tests/test_valida.py`:

```python
# -*- coding: utf-8 -*-
"""Testes do validador do acervo."""

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import valida  # noqa: E402


def acervo_valido():
    """Um acervo mínimo que passa em todas as verificações."""
    artefatos = [
        {"nome": f"Artefato {i}", "antes": "Não entregue",
         "agora": "Entregue", "onde": "Anexo I"}
        for i in range(19)
    ]
    artefatos.append(
        {"nome": "Pendente", "antes": "Parcial", "agora": "Parcial", "onde": ""}
    )
    return {
        "origem": {
            "relatorio": "3º Relatório Parcial",
            "periodo": "maio a agosto de 2026",
            "apurado_em": "2026-08-31",
        },
        "artefatos": artefatos,
        "pendencias": [
            {"artefato": "Pendente", "situacao": "Parcial",
             "falta": "x", "destrava": "y", "quem": "UnB"}
        ],
    }


class TestValida(unittest.TestCase):
    def test_acervo_valido_nao_tem_problema(self):
        self.assertEqual(valida.valida(acervo_valido()), [])

    def test_quadro_que_nao_fecha_em_vinte(self):
        a = acervo_valido()
        a["artefatos"].pop()
        problemas = valida.valida(a)
        self.assertTrue(any("20" in p for p in problemas))

    def test_artefato_duplicado(self):
        a = acervo_valido()
        a["artefatos"][1]["nome"] = a["artefatos"][0]["nome"]
        problemas = valida.valida(a)
        self.assertTrue(any("duplicado" in p.lower() for p in problemas))

    def test_entregue_sem_lastro(self):
        a = acervo_valido()
        a["artefatos"][0]["onde"] = ""
        problemas = valida.valida(a)
        self.assertTrue(any("lastro" in p.lower() for p in problemas))

    def test_entregue_como_proposta_tambem_exige_lastro(self):
        a = acervo_valido()
        a["artefatos"][0]["agora"] = "Entregue como proposta"
        a["artefatos"][0]["onde"] = ""
        problemas = valida.valida(a)
        self.assertTrue(any("lastro" in p.lower() for p in problemas))

    def test_pendencia_de_artefato_inexistente(self):
        a = acervo_valido()
        a["pendencias"][0]["artefato"] = "Não existe"
        problemas = valida.valida(a)
        self.assertTrue(any("inexistente" in p.lower() for p in problemas))

    def test_pendencia_com_situacao_divergente(self):
        a = acervo_valido()
        a["pendencias"][0]["situacao"] = "Entregue"
        problemas = valida.valida(a)
        self.assertTrue(any("diverge" in p.lower() for p in problemas))

    def test_carimbo_de_origem_ausente(self):
        a = acervo_valido()
        del a["origem"]["apurado_em"]
        problemas = valida.valida(a)
        self.assertTrue(any("apurado_em" in p for p in problemas))

    def test_carimbo_com_data_malformada(self):
        a = acervo_valido()
        a["origem"]["apurado_em"] = "31/08/2026"
        problemas = valida.valida(a)
        self.assertTrue(any("AAAA-MM-DD" in p for p in problemas))

    def test_acervo_real_passa(self):
        """O ted.json versionado tem de passar em todas as verificações."""
        acervo = json.loads((RAIZ / "dados" / "ted.json").read_text("utf-8"))
        self.assertEqual(valida.valida(acervo), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 2: Rodar o teste e ver falhar**

```bash
python3 -m unittest discover -s tests -v
```

Esperado: `ModuleNotFoundError: No module named 'valida'`.

- [ ] **Passo 3: Escrever `scripts/valida.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica a consistência do acervo do painel.

Sai com código 1 se algum problema for encontrado, para que o CI falhe em vez
de publicar número errado.

Uso:
    python3 scripts/valida.py [caminho/para/ted.json]
"""

import json
import re
import sys
from pathlib import Path

TOTAL_ARTEFATOS = 20
CAMPOS_ORIGEM = ("relatorio", "periodo", "apurado_em")


def valida(acervo):
    """Devolve a lista de problemas encontrados. Vazia significa consistente."""
    problemas = []
    artefatos = acervo.get("artefatos", [])

    # 1. Fechamento do quadro.
    if len(artefatos) != TOTAL_ARTEFATOS:
        problemas.append(
            f"O quadro tem {len(artefatos)} artefatos; deveria fechar em "
            f"{TOTAL_ARTEFATOS}."
        )

    vistos = set()
    for a in artefatos:
        nome = a.get("nome", "")
        if nome in vistos:
            problemas.append(f"Artefato duplicado no quadro: {nome!r}.")
        vistos.add(nome)

    # 2. Lastro obrigatório para o que é declarado entregue.
    for a in artefatos:
        if a.get("agora", "").startswith("Entregue") and not a.get("onde"):
            problemas.append(
                f"Artefato {a.get('nome')!r} consta como "
                f"{a.get('agora')!r} e está sem lastro."
            )

    # 3. Integridade de referência das pendências.
    por_nome = {a.get("nome"): a for a in artefatos}
    for p in acervo.get("pendencias", []):
        nome = p.get("artefato")
        artefato = por_nome.get(nome)
        if artefato is None:
            problemas.append(f"Pendência de artefato inexistente: {nome!r}.")
            continue
        if p.get("situacao") != artefato.get("agora"):
            problemas.append(
                f"Pendência {nome!r} diverge do quadro: declara "
                f"{p.get('situacao')!r}, o quadro diz "
                f"{artefato.get('agora')!r}."
            )

    # 4. Carimbo de origem.
    origem = acervo.get("origem", {})
    for campo in CAMPOS_ORIGEM:
        if not origem.get(campo):
            problemas.append(f"Carimbo de origem sem {campo}.")
    data = origem.get("apurado_em", "")
    if data and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
        problemas.append(
            f"apurado_em deve estar em AAAA-MM-DD; veio {data!r}."
        )

    return problemas


def main():
    caminho = Path(
        sys.argv[1] if len(sys.argv) > 1
        else Path(__file__).resolve().parent.parent / "dados" / "ted.json"
    )
    acervo = json.loads(caminho.read_text("utf-8"))
    problemas = valida(acervo)

    if problemas:
        print(f"{len(problemas)} problema(s) no acervo:\n")
        for p in problemas:
            print(f"  · {p}")
        sys.exit(1)

    print(
        f"Acervo consistente: {len(acervo['artefatos'])} artefatos, "
        f"{len(acervo['pendencias'])} pendências, "
        f"apurado em {acervo['origem']['apurado_em']}."
    )


if __name__ == "__main__":
    main()
```

- [ ] **Passo 4: Rodar os testes e ver passar**

```bash
python3 -m unittest discover -s tests -v
```

Esperado: `Ran 10 tests` e `OK`.

- [ ] **Passo 5: Rodar o validador contra o acervo real**

```bash
python3 scripts/valida.py
```

Esperado: `Acervo consistente: 20 artefatos, 7 pendências, apurado em 2026-08-31.`

- [ ] **Passo 6: Criar o workflow de validação**

Criar `.github/workflows/valida.yml`:

```yaml
# Verifica a consistência do acervo a cada alteração. Falha o CI em vez de
# deixar publicar número que não fecha.
name: Validação do acervo

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  valida:
    name: Consistência
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Rodar os testes
        run: python3 -m unittest discover -s tests -v

      - name: Validar o acervo
        run: python3 scripts/valida.py
```

- [ ] **Passo 7: Commit**

```bash
git add scripts/valida.py tests/test_valida.py .github/workflows/valida.yml
git commit -m "feat: validação de consistência do acervo"
```

---

### Task 3: Tema, esqueleto e faixa de indicadores

Primeira versão visível: cabeçalho, faixa de indicadores e o carregamento dos dados.

**Files:**
- Create: `assets/d3.v7.min.js` (baixado)
- Create: `assets/tema.css`
- Create: `index.html`
- Create: `assets/painel.js`

**Interfaces:**
- Consumes: `dados/ted.json`.
- Produces:
  - `carrega() -> Promise<Object>` — busca e devolve o acervo.
  - `contaSituacoes(artefatos) -> Object` — mapa situação → quantidade.
  - `SITUACOES` — array na ordem de exibição: `["Entregue", "Entregue como proposta", "Parcial", "Não entregue"]`.
  - `classeDe(situacao) -> String` — a classe CSS, ex.: `"sit-entregue"`.
  - Cada seção monta dentro do seu `<section id="...">`. Ids: `indicadores`, `evolucao`, `metas`, `artefatos`, `cronograma`, `riscos`, `documentos`.

- [ ] **Passo 1: Vendorizar o D3**

```bash
mkdir -p assets
curl -sL https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js -o assets/d3.v7.min.js
test -s assets/d3.v7.min.js && head -c 120 assets/d3.v7.min.js && echo && du -h assets/d3.v7.min.js
```

Esperado: o arquivo começa com o cabeçalho do bundle D3 e tem algumas centenas de KB. Se vier vazio, **parar** — sem D3 as Tasks 4 e 8 não rodam.

- [ ] **Passo 2: Escrever `assets/tema.css`**

```css
/* Painel de Entregas e Status do TED — MinC
   Identidade visual Gov Hub. A fonte Inter é referenciada com fallback de
   sistema, sem @import: o painel precisa abrir em rede restrita. */

:root {
  --primary-purple:   #7A34F3;
  --secondary-purple: #8B5CF6;
  --accent-orange:    #F97316;
  --purple-600:       #7C3AAD;
  --purple-700:       #5B21B6;

  --text-strong: #202020;
  --text-body:   #2D3748;
  --text-muted:  #666666;

  --bg-white:  #FFFFFF;
  --bg-light:  #F7F7F7;
  --bg-subtle: #F8F9FA;

  --color-success: #10B981;
  --color-warm:    #F19F42;
  --color-ausente: #C2410C;

  --shadow-md: 0 2px 10px rgba(0, 0, 0, 0.1);
  --radius-md: 10px;

  --font-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, 'Helvetica Neue', Arial, sans-serif;

  --largura: 1140px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: var(--font-base);
  color: var(--text-body);
  background: var(--bg-light);
  line-height: 1.6;
}

.container {
  max-width: var(--largura);
  margin: 0 auto;
  padding: 0 24px;
}

/* ---------------------------------------------------------------- cabeçalho */

.topo {
  background: linear-gradient(135deg, var(--primary-purple), var(--secondary-purple));
  color: var(--bg-white);
  padding: 48px 0 40px;
}

.topo .eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  font-weight: 600;
  opacity: 0.85;
  margin: 0 0 8px;
}

.topo h1 {
  margin: 0 0 12px;
  font-size: 2.1rem;
  font-weight: 700;
  line-height: 1.2;
}

.topo p { margin: 0; max-width: 62ch; opacity: 0.95; }

.carimbo {
  margin-top: 20px;
  font-size: 0.85rem;
  opacity: 0.9;
  border-top: 1px solid rgba(255, 255, 255, 0.25);
  padding-top: 14px;
}

/* ------------------------------------------------------------------ seções */

.secao { padding: 48px 0; }
.secao-alt { background: var(--bg-subtle); }

.secao h2 {
  color: var(--primary-purple);
  font-size: 1.5rem;
  margin: 0 0 8px;
}

.secao-intro {
  color: var(--text-muted);
  margin: 0 0 28px;
  max-width: 70ch;
}

/* ------------------------------------------------------------ indicadores */

.indicadores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.indicador {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 20px;
  border-top: 4px solid var(--primary-purple);
}

.indicador .numero {
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--text-strong);
  line-height: 1;
}

.indicador .rotulo {
  margin-top: 6px;
  font-size: 0.86rem;
  color: var(--text-muted);
}

.indicador.sit-entregue           { border-top-color: var(--color-success); }
.indicador.sit-entregue-proposta  { border-top-color: var(--secondary-purple); }
.indicador.sit-parcial            { border-top-color: var(--color-warm); }
.indicador.sit-nao-entregue       { border-top-color: var(--color-ausente); }

/* ---------------------------------------------------------------- etiquetas */

.etiqueta {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
  color: var(--bg-white);
}

.etiqueta.sit-entregue          { background: var(--color-success); }
.etiqueta.sit-entregue-proposta { background: var(--secondary-purple); }
.etiqueta.sit-parcial           { background: var(--color-warm); color: var(--text-strong); }
.etiqueta.sit-nao-entregue      { background: var(--color-ausente); }

/* ------------------------------------------------------------------ rodapé */

.rodape {
  background: var(--text-strong);
  color: var(--bg-white);
  padding: 32px 0;
  font-size: 0.88rem;
}

.rodape a { color: var(--secondary-purple); }

/* --------------------------------------------------------------- responsivo */

@media (max-width: 640px) {
  .topo h1 { font-size: 1.5rem; }
  .secao { padding: 32px 0; }
  .indicador .numero { font-size: 1.9rem; }
}

@media print {
  body { background: var(--bg-white); }
  .secao, .topo { padding: 16px 0; }
  .topo { background: var(--primary-purple) !important; -webkit-print-color-adjust: exact; }
}
```

- [ ] **Passo 3: Escrever `index.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Painel de Entregas e Status do TED — MinC</title>
  <meta name="description"
        content="Acompanhamento do Termo de Execução Descentralizada 01/2026/SGE/SE/MINC entre a Universidade de Brasília e o Ministério da Cultura.">
  <link rel="stylesheet" href="assets/tema.css">
</head>
<body>

  <header class="topo">
    <div class="container">
      <p class="eyebrow">Termo de Execução Descentralizada nº 01/2026/SGE/SE/MINC</p>
      <h1>Painel de Entregas e Status</h1>
      <p id="objeto"></p>
      <p class="carimbo" id="carimbo"></p>
    </div>
  </header>

  <main>
    <section class="secao" id="indicadores" aria-labelledby="t-indicadores">
      <div class="container">
        <h2 id="t-indicadores">Situação dos artefatos</h2>
        <p class="secao-intro">
          Os artefatos acompanhados no quadro de produtos do TED, na situação
          apurada no 3º Relatório Parcial.
        </p>
        <div class="indicadores" id="grade-indicadores"></div>
      </div>
    </section>

    <section class="secao secao-alt" id="evolucao" aria-labelledby="t-evolucao">
      <div class="container">
        <h2 id="t-evolucao">Evolução entre relatórios</h2>
        <div id="grafico-evolucao"></div>
      </div>
    </section>

    <section class="secao" id="metas" aria-labelledby="t-metas">
      <div class="container">
        <h2 id="t-metas">As seis metas</h2>
        <div id="grade-metas"></div>
      </div>
    </section>

    <section class="secao secao-alt" id="artefatos" aria-labelledby="t-artefatos">
      <div class="container">
        <h2 id="t-artefatos">Quadro dos artefatos</h2>
        <div id="quadro-artefatos"></div>
      </div>
    </section>

    <section class="secao" id="cronograma" aria-labelledby="t-cronograma">
      <div class="container">
        <h2 id="t-cronograma">Cronograma</h2>
        <div id="lista-cronograma"></div>
      </div>
    </section>

    <section class="secao secao-alt" id="riscos" aria-labelledby="t-riscos">
      <div class="container">
        <h2 id="t-riscos">Riscos</h2>
        <div id="matriz-riscos"></div>
      </div>
    </section>

    <section class="secao" id="documentos" aria-labelledby="t-documentos">
      <div class="container">
        <h2 id="t-documentos">Documentos produzidos</h2>
        <div id="lista-documentos"></div>
      </div>
    </section>
  </main>

  <footer class="rodape">
    <div class="container">
      <p id="rodape-origem"></p>
      <p>
        Projeto Gov Hub · Lab Livre · Faculdade do Gama, Universidade de Brasília
        · <a href="https://github.com/GovHub-br/dashboard-minc-project">código-fonte</a>
      </p>
    </div>
  </footer>

  <script src="assets/d3.v7.min.js"></script>
  <script src="assets/graficos.js"></script>
  <script src="assets/painel.js"></script>
</body>
</html>
```

- [ ] **Passo 4: Escrever `assets/painel.js` com o carregamento e os indicadores**

```javascript
/* Painel de Entregas e Status do TED — carregamento e seções em HTML.
   As visualizações D3 ficam em graficos.js. */

'use strict';

const SITUACOES = [
  'Entregue',
  'Entregue como proposta',
  'Parcial',
  'Não entregue',
];

const CLASSES = {
  'Entregue': 'sit-entregue',
  'Entregue como proposta': 'sit-entregue-proposta',
  'Parcial': 'sit-parcial',
  'Não entregue': 'sit-nao-entregue',
};

function classeDe(situacao) {
  return CLASSES[situacao] || '';
}

/* Todo texto vindo do acervo passa por aqui antes de virar HTML. O extrator já
   remove marcação, mas o painel não depende disso: o acervo é editado à mão a
   cada relatório. */
function escapaHtml(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

function contaSituacoes(artefatos, coluna = 'agora') {
  const contagem = {};
  for (const a of artefatos) {
    contagem[a[coluna]] = (contagem[a[coluna]] || 0) + 1;
  }
  return contagem;
}

async function carrega() {
  const resposta = await fetch('dados/ted.json');
  if (!resposta.ok) {
    throw new Error(`Não foi possível ler o acervo: ${resposta.status}`);
  }
  return resposta.json();
}

/* ------------------------------------------------------------- cabeçalho */

function montaCabecalho(acervo) {
  document.getElementById('objeto').textContent = acervo.ted.objeto + '.';

  const o = acervo.origem;
  document.getElementById('carimbo').textContent =
    `${acervo.ted.partes} · Situação do ${o.relatorio}, período de ` +
    `${o.periodo}, apurada em ${dataPorExtenso(o.apurado_em)}.`;

  document.getElementById('rodape-origem').textContent =
    `Os dados deste painel vêm do ${o.relatorio} e do quadro de ` +
    `acompanhamento de produtos do TED. Nenhum número é produzido aqui.`;
}

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
  'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

function dataPorExtenso(iso) {
  const [ano, mes, dia] = iso.split('-');
  return `${Number(dia)} de ${MESES[Number(mes) - 1]} de ${ano}`;
}

/* ----------------------------------------------------------- indicadores */

function montaIndicadores(acervo) {
  const contagem = contaSituacoes(acervo.artefatos);
  const grade = document.getElementById('grade-indicadores');

  const cartoes = [
    { numero: acervo.artefatos.length, rotulo: 'artefatos acompanhados', classe: '' },
    ...SITUACOES.map((s) => ({
      numero: contagem[s] || 0,
      rotulo: s.toLowerCase(),
      classe: classeDe(s),
    })),
    { numero: acervo.documentos.length, rotulo: 'documentos publicados', classe: '' },
  ];

  grade.innerHTML = cartoes.map((c) => `
    <div class="indicador ${c.classe}">
      <div class="numero">${c.numero}</div>
      <div class="rotulo">${c.rotulo}</div>
    </div>
  `).join('');
}

/* ------------------------------------------------------------- inicialização */

async function inicia() {
  try {
    const acervo = await carrega();
    montaCabecalho(acervo);
    montaIndicadores(acervo);
  } catch (erro) {
    console.error(erro);
    document.getElementById('grade-indicadores').innerHTML =
      `<p>Não foi possível carregar os dados do painel. ` +
      `Se estiver abrindo o arquivo direto do disco, sirva o diretório com ` +
      `<code>python3 -m http.server</code>.</p>`;
  }
}

document.addEventListener('DOMContentLoaded', inicia);
```

- [ ] **Passo 5: Criar `assets/graficos.js` vazio**

O `index.html` já o referencia; sem o arquivo o console acusa 404. As Tasks 4 e 8 o preenchem.

```bash
printf "/* Visualizações D3 do painel. Preenchido nas Tasks 4 e 8. */\n'use strict';\n" > assets/graficos.js
```

- [ ] **Passo 6: Servir e conferir**

```bash
python3 -m http.server 8000 &
sleep 1 && curl -s http://localhost:8000/ | head -20 && curl -s -o /dev/null -w "ted.json: %{http_code}\n" http://localhost:8000/dados/ted.json
```

Esperado: o HTML do painel e `ted.json: 200`.

Abrir <http://localhost:8000> e conferir: cabeçalho roxo com o número do TED, o objeto, o carimbo com a data por extenso, e seis cartões de indicador — 20 artefatos, 11 entregues, 2 entregues como proposta, 5 parciais, 2 não entregues, 12 documentos. Console sem erro.

- [ ] **Passo 7: Commit**

```bash
git add index.html assets/
git commit -m "feat: tema Gov Hub, esqueleto do painel e faixa de indicadores"
```

---

### Task 4: Evolução entre relatórios

O gráfico que responde *"o período rendeu?"*. Barras pareadas em D3.

**Files:**
- Modify: `assets/graficos.js`
- Modify: `assets/painel.js` (chamar o gráfico e escrever a nota)
- Modify: `assets/tema.css` (estilos do gráfico e da nota)

**Interfaces:**
- Consumes: `contaSituacoes(artefatos, coluna)` e `SITUACOES` da Task 3.
- Produces: `desenhaEvolucao(seletor, series)` — `series` é `[{situacao, antes, agora}]`; desenha o SVG dentro do elemento.

**A agregação da coluna *antes*:** o quadro anterior usa os rótulos `Parcial`, `Não entregue` e `Falta artefato`. O relatório agrega os três `Falta artefato` dentro de `Não entregue`, chegando a 14. O painel faz a mesma agregação e diz isso na nota.

- [ ] **Passo 1: Escrever `desenhaEvolucao` em `assets/graficos.js`**

```javascript
/* Visualizações D3 do painel. */

'use strict';

/* Barras pareadas: cada situação com a contagem do 2º e do 3º relatório. */
function desenhaEvolucao(seletor, series) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const margem = { topo: 16, direita: 16, base: 44, esquerda: 190 };
  const largura = Math.min(alvo.node().clientWidth || 820, 820);
  const alturaLinha = 56;
  const altura = series.length * alturaLinha + margem.topo + margem.base;

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label', legendaAcessivel(series));

  const maximo = d3.max(series, (d) => Math.max(d.antes, d.agora)) || 1;

  const x = d3.scaleLinear()
    .domain([0, maximo])
    .range([margem.esquerda, largura - margem.direita]);

  const y = d3.scaleBand()
    .domain(series.map((d) => d.situacao))
    .range([margem.topo, altura - margem.base])
    .padding(0.28);

  const alturaBarra = y.bandwidth() / 2 - 2;

  const grupo = svg.selectAll('g.linha')
    .data(series)
    .join('g')
    .attr('class', 'linha');

  grupo.append('text')
    .attr('class', 'rotulo-situacao')
    .attr('x', margem.esquerda - 12)
    .attr('y', (d) => y(d.situacao) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .text((d) => d.situacao);

  // 2º Relatório: barra clara, acima.
  grupo.append('rect')
    .attr('class', 'barra-antes')
    .attr('x', x(0))
    .attr('y', (d) => y(d.situacao))
    .attr('height', alturaBarra)
    .attr('width', (d) => x(d.antes) - x(0));

  // 3º Relatório: barra cheia, abaixo, na cor da situação.
  grupo.append('rect')
    .attr('class', (d) => `barra-agora ${d.classe}`)
    .attr('x', x(0))
    .attr('y', (d) => y(d.situacao) + alturaBarra + 4)
    .attr('height', alturaBarra)
    .attr('width', (d) => x(d.agora) - x(0));

  grupo.append('text')
    .attr('class', 'valor')
    .attr('x', (d) => x(d.antes) + 8)
    .attr('y', (d) => y(d.situacao) + alturaBarra / 2)
    .attr('dy', '0.35em')
    .text((d) => d.antes);

  grupo.append('text')
    .attr('class', 'valor valor-forte')
    .attr('x', (d) => x(d.agora) + 8)
    .attr('y', (d) => y(d.situacao) + alturaBarra + 4 + alturaBarra / 2)
    .attr('dy', '0.35em')
    .text((d) => d.agora);

  // Legenda.
  const legenda = svg.append('g')
    .attr('transform', `translate(${margem.esquerda}, ${altura - 16})`);

  legenda.append('rect')
    .attr('class', 'barra-antes')
    .attr('width', 14).attr('height', 14).attr('y', -11);
  legenda.append('text')
    .attr('class', 'rotulo-legenda').attr('x', 20)
    .text('2º Relatório Parcial');

  legenda.append('rect')
    .attr('class', 'barra-agora sit-entregue')
    .attr('x', 160).attr('width', 14).attr('height', 14).attr('y', -11);
  legenda.append('text')
    .attr('class', 'rotulo-legenda').attr('x', 180)
    .text('3º Relatório Parcial');
}

function legendaAcessivel(series) {
  const partes = series.map(
    (d) => `${d.situacao}: ${d.antes} no 2º relatório, ${d.agora} no 3º`
  );
  return `Evolução entre relatórios. ${partes.join('; ')}.`;
}
```

- [ ] **Passo 2: Acrescentar os estilos do gráfico ao fim de `assets/tema.css`**

```css
/* ------------------------------------------------------------- gráficos */

.barra-antes { fill: #D6D3E4; }

.barra-agora.sit-entregue          { fill: var(--color-success); }
.barra-agora.sit-entregue-proposta { fill: var(--secondary-purple); }
.barra-agora.sit-parcial           { fill: var(--color-warm); }
.barra-agora.sit-nao-entregue      { fill: var(--color-ausente); }

.rotulo-situacao {
  font-size: 0.9rem;
  font-weight: 600;
  fill: var(--text-body);
}

.valor { font-size: 0.85rem; fill: var(--text-muted); }
.valor-forte { font-weight: 700; fill: var(--text-strong); }
.rotulo-legenda { font-size: 0.8rem; fill: var(--text-muted); }

/* ----------------------------------------------------------------- nota */

.nota {
  margin-top: 24px;
  padding: 16px 20px;
  background: var(--bg-white);
  border-left: 4px solid var(--accent-orange);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  color: var(--text-body);
}

.nota strong { color: var(--text-strong); }
.nota p { margin: 0 0 8px; }
.nota p:last-child { margin-bottom: 0; }
```

- [ ] **Passo 3: Ligar a seção em `assets/painel.js`**

Acrescentar antes de `inicia()`:

```javascript
/* -------------------------------------------------------------- evolução */

/* O quadro anterior marcava três artefatos como "Falta artefato". O relatório
   os agrega em "Não entregue", chegando a 14. O painel faz o mesmo, e a nota
   registra a agregação. */
function contaAntesAgregado(artefatos) {
  const contagem = contaSituacoes(artefatos, 'antes');
  const falta = contagem['Falta artefato'] || 0;
  if (falta) {
    contagem['Não entregue'] = (contagem['Não entregue'] || 0) + falta;
    delete contagem['Falta artefato'];
  }
  return contagem;
}

function montaEvolucao(acervo) {
  const antes = contaAntesAgregado(acervo.artefatos);
  const agora = contaSituacoes(acervo.artefatos);

  const series = SITUACOES.map((s) => ({
    situacao: s,
    antes: antes[s] || 0,
    agora: agora[s] || 0,
    classe: classeDe(s),
  }));

  const alvo = document.getElementById('grafico-evolucao');
  alvo.innerHTML = `
    <p class="secao-intro">
      O que mudou do 2º para o 3º Relatório Parcial, artefato a artefato.
    </p>
    <div id="svg-evolucao"></div>
    <div class="nota">
      <p>
        A mudança decorre menos de trabalho novo que de <strong>publicação</strong>:
        parte do que a avaliação anterior não localizou existia como código, e não
        como documento. O período foi dedicado a derivar documentos do próprio
        repositório, de modo que cada afirmação pudesse ser conferida na fonte.
      </p>
      <p>
        Os ${antes['Não entregue'] || 0} não entregues do 2º Relatório reúnem os
        assim marcados e os três com a marcação <em>falta apresentar artefato</em>,
        conforme o próprio documento agrega.
      </p>
      <p>
        <strong>Sobre a contagem.</strong> O texto do 3º Relatório Parcial declara
        12 entregues e 6 parciais. A conferência item a item do quadro dá
        ${agora['Entregue']} entregues, ${agora['Entregue como proposta']} entregues
        como proposta e ${agora['Parcial']} parciais — os mesmos 20 artefatos, nas
        mesmas situações, com as arquiteturas propostas contadas à parte para
        preservar a distinção entre o que opera e o que está projetado.
      </p>
    </div>`;

  desenhaEvolucao('#svg-evolucao', series);
}
```

E dentro de `inicia()`, depois de `montaIndicadores(acervo);`:

```javascript
    montaEvolucao(acervo);
```

- [ ] **Passo 4: Conferir no navegador**

```bash
python3 -m http.server 8000 &
sleep 1 && curl -s http://localhost:8000/assets/graficos.js | head -3
```

Abrir <http://localhost:8000#evolucao> e conferir: quatro pares de barras, com 0/11, 0/2, 6/5 e 14/2. A nota com os três parágrafos. Console sem erro.

- [ ] **Passo 5: Commit**

```bash
git add assets/
git commit -m "feat: gráfico de evolução entre relatórios"
```

---

### Task 5: As seis metas

Um cartão por meta, com o balanço do período e a quantidade de encaminhamentos.

**Files:**
- Modify: `assets/painel.js`
- Modify: `assets/tema.css`

**Interfaces:**
- Consumes: `acervo.metas` — `[{num, nome, balanco, encaminhamentos[]}]`.
- Produces: `montaMetas(acervo)`.

- [ ] **Passo 1: Acrescentar os estilos ao fim de `assets/tema.css`**

```css
/* ------------------------------------------------------------------ metas */

.grade-metas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.meta {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 24px;
  border-top: 4px solid var(--primary-purple);
}

.meta .numero-meta {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary-purple);
}

.meta h3 {
  margin: 6px 0 12px;
  font-size: 1.06rem;
  color: var(--text-strong);
  line-height: 1.35;
}

.meta p { margin: 0; font-size: 0.92rem; }

.meta .contagem {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--bg-light);
  font-size: 0.85rem;
  color: var(--text-muted);
}
```

- [ ] **Passo 2: Acrescentar `montaMetas` a `assets/painel.js`**

```javascript
/* ---------------------------------------------------------------- metas */

function montaMetas(acervo) {
  const alvo = document.getElementById('grade-metas');

  const intro = `
    <p class="secao-intro">
      As seis metas pactuadas no Termo, com o balanço do período de
      ${acervo.origem.periodo}.
    </p>`;

  const cartoes = acervo.metas.map((m) => `
    <article class="meta">
      <div class="numero-meta">Meta ${m.num}</div>
      <h3>${escapaHtml(m.nome)}</h3>
      <p>${escapaHtml(m.balanco)}</p>
      <p class="contagem">
        ${m.encaminhamentos.length}
        ${m.encaminhamentos.length === 1 ? 'encaminhamento' : 'encaminhamentos'}
        para ${acervo.origem.proximo_periodo}
      </p>
    </article>
  `).join('');

  alvo.innerHTML = intro + `<div class="grade-metas">${cartoes}</div>`;
}
```

E dentro de `inicia()`, depois de `montaEvolucao(acervo);`:

```javascript
    montaMetas(acervo);
```

- [ ] **Passo 3: Conferir no navegador**

Abrir <http://localhost:8000#metas>. Esperado: seis cartões, Meta 01 a Meta 06, cada um com o nome, o parágrafo de balanço e a contagem de encaminhamentos — 3, 5, 3, 3, 4 e 4, somando 22. Console sem erro.

- [ ] **Passo 4: Commit**

```bash
git add assets/
git commit -m "feat: seção das seis metas"
```

---

### Task 6: Quadro dos artefatos

A seção que responde à pergunta que o Ministério de fato faz — *cadê?*. Tabela filtrável por situação.

**Files:**
- Modify: `assets/painel.js`
- Modify: `assets/tema.css`

**Interfaces:**
- Consumes: `acervo.artefatos`, `SITUACOES`, `classeDe`.
- Produces: `montaArtefatos(acervo)`. O filtro é estado local da seção; nenhuma outra seção depende dele.

- [ ] **Passo 1: Acrescentar os estilos ao fim de `assets/tema.css`**

```css
/* --------------------------------------------------------------- filtros */

.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.filtro {
  border: 1px solid #DDD;
  background: var(--bg-white);
  color: var(--text-body);
  border-radius: 999px;
  padding: 7px 16px;
  font: inherit;
  font-size: 0.86rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filtro:hover { border-color: var(--primary-purple); color: var(--primary-purple); }

.filtro[aria-pressed="true"] {
  background: var(--primary-purple);
  border-color: var(--primary-purple);
  color: var(--bg-white);
  font-weight: 600;
}

/* --------------------------------------------------------------- tabelas */

.rolagem { overflow-x: auto; }

table.quadro {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-white);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  font-size: 0.9rem;
}

table.quadro th {
  background: var(--primary-purple);
  color: var(--bg-white);
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  white-space: nowrap;
}

table.quadro td {
  padding: 12px 16px;
  border-top: 1px solid var(--bg-light);
  vertical-align: top;
}

table.quadro tbody tr:nth-child(even) { background: var(--bg-subtle); }

table.quadro .nome-artefato { font-weight: 600; color: var(--text-strong); }
table.quadro .onde { color: var(--text-muted); font-size: 0.86rem; }
table.quadro code {
  background: var(--bg-light);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.86em;
}

.vazio { padding: 24px; text-align: center; color: var(--text-muted); }
```

- [ ] **Passo 2: Acrescentar `montaArtefatos` a `assets/painel.js`**

`escapaHtml` protege contra marcação vinda do acervo; `onde` recebe tratamento próprio porque contém `<code>` legítimo.

```javascript
/* ------------------------------------------------------------- artefatos */

/* `escapaHtml` já foi definido na Task 3; não redefinir.
   O campo "onde" traz nomes de arquivo. Marca-os como código, depois de
   escapar o restante. */
function formataOnde(texto) {
  return escapaHtml(texto).replace(
    /([\w-]+\.(?:pdf|md|json|yml|lock))/g,
    '<code>$1</code>'
  );
}

function montaArtefatos(acervo) {
  const alvo = document.getElementById('quadro-artefatos');
  let filtro = 'Todos';

  const opcoes = ['Todos', ...SITUACOES];

  function linhas() {
    const visiveis = filtro === 'Todos'
      ? acervo.artefatos
      : acervo.artefatos.filter((a) => a.agora === filtro);

    if (!visiveis.length) {
      return '<tr><td colspan="4" class="vazio">Nenhum artefato nesta situação.</td></tr>';
    }

    return visiveis.map((a) => `
      <tr>
        <td class="nome-artefato">${escapaHtml(a.nome)}</td>
        <td>${escapaHtml(a.antes)}</td>
        <td><span class="etiqueta ${classeDe(a.agora)}">${escapaHtml(a.agora)}</span></td>
        <td class="onde">${a.onde ? formataOnde(a.onde) : '—'}</td>
      </tr>
    `).join('');
  }

  function desenha() {
    alvo.innerHTML = `
      <p class="secao-intro">
        Os ${acervo.artefatos.length} artefatos do quadro de acompanhamento, com
        a situação anterior, a atual e a localização de cada um.
      </p>
      <div class="filtros" role="group" aria-label="Filtrar por situação">
        ${opcoes.map((o) => `
          <button class="filtro" type="button" data-situacao="${escapaHtml(o)}"
                  aria-pressed="${o === filtro}">${escapaHtml(o)}</button>
        `).join('')}
      </div>
      <div class="rolagem">
        <table class="quadro">
          <thead>
            <tr><th>Artefato</th><th>2º Relatório</th><th>3º Relatório</th><th>Onde está</th></tr>
          </thead>
          <tbody>${linhas()}</tbody>
        </table>
      </div>`;

    alvo.querySelectorAll('.filtro').forEach((botao) => {
      botao.addEventListener('click', () => {
        filtro = botao.dataset.situacao;
        desenha();
      });
    });
  }

  desenha();
}
```

E dentro de `inicia()`, depois de `montaMetas(acervo);`:

```javascript
    montaArtefatos(acervo);
```

- [ ] **Passo 3: Conferir no navegador**

Abrir <http://localhost:8000#artefatos>. Conferir:

- 20 linhas com o filtro em *Todos*.
- Clicar em *Entregue* deixa 11 linhas; *Entregue como proposta*, 2; *Parcial*, 5; *Não entregue*, 2.
- O botão ativo fica roxo e com `aria-pressed="true"`.
- Toda linha *Entregue* tem a coluna *Onde está* preenchida.
- Nomes de arquivo aparecem como código.
- Console sem erro.

- [ ] **Passo 4: Commit**

```bash
git add assets/
git commit -m "feat: quadro filtrável dos artefatos"
```

---

### Task 7: Cronograma e pendências

Os 22 encaminhamentos por meta, e as 7 pendências agrupadas por quem as destrava.

**Files:**
- Modify: `assets/painel.js`
- Modify: `assets/tema.css`

**Interfaces:**
- Consumes: `acervo.metas[].encaminhamentos`, `acervo.pendencias`, `acervo.origem.proximo_periodo`.
- Produces: `montaCronograma(acervo)`.

**Sem datas por item.** Nenhuma fonte declara prazo por produto; o cronograma é a janela avaliativa declarada no relatório.

- [ ] **Passo 1: Acrescentar os estilos ao fim de `assets/tema.css`**

```css
/* ------------------------------------------------------------ cronograma */

.janela {
  display: inline-block;
  background: var(--primary-purple);
  color: var(--bg-white);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 0.86rem;
  font-weight: 600;
  margin-bottom: 24px;
}

.trilha-meta {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 20px 24px;
  margin-bottom: 16px;
  border-left: 4px solid var(--primary-purple);
}

.trilha-meta h3 {
  margin: 0 0 12px;
  font-size: 0.98rem;
  color: var(--text-strong);
}

.trilha-meta h3 .numero-meta {
  color: var(--primary-purple);
  margin-right: 8px;
}

.trilha-meta ul { margin: 0; padding-left: 20px; }
.trilha-meta li { margin-bottom: 8px; font-size: 0.92rem; }
.trilha-meta li:last-child { margin-bottom: 0; }

/* ------------------------------------------------------------ pendências */

.grupo-destrava {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 20px 24px;
  margin-bottom: 16px;
}

.grupo-destrava h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  color: var(--text-strong);
}

.grupo-destrava .quem {
  display: inline-block;
  background: var(--bg-light);
  color: var(--text-body);
  border: 1px solid #DDD;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.pendencia { padding: 12px 0; border-top: 1px solid var(--bg-light); }
.pendencia:first-of-type { border-top: none; }
.pendencia .titulo-pendencia { font-weight: 600; color: var(--text-strong); }
.pendencia .detalhe { font-size: 0.88rem; color: var(--text-muted); margin-top: 4px; }
```

- [ ] **Passo 2: Acrescentar `montaCronograma` a `assets/painel.js`**

```javascript
/* ----------------------------------------------------------- cronograma */

const ORDEM_DESTRAVA = ['MinC', 'MinC + UnB', 'UnB', '—'];

function montaCronograma(acervo) {
  const alvo = document.getElementById('lista-cronograma');
  const total = acervo.metas.reduce((s, m) => s + m.encaminhamentos.length, 0);

  const trilhas = acervo.metas
    .filter((m) => m.encaminhamentos.length)
    .map((m) => `
      <article class="trilha-meta">
        <h3><span class="numero-meta">Meta ${m.num}</span>${escapaHtml(m.nome)}</h3>
        <ul>${m.encaminhamentos.map((e) => `<li>${escapaHtml(e)}</li>`).join('')}</ul>
      </article>
    `).join('');

  // Pendências agrupadas por quem destrava.
  const grupos = {};
  for (const p of acervo.pendencias) {
    (grupos[p.quem] = grupos[p.quem] || []).push(p);
  }

  const chaves = ORDEM_DESTRAVA.filter((k) => grupos[k]);
  const soUnb = (grupos['UnB'] || []).length;
  const naoSoUnb = acervo.pendencias.length - soUnb;

  const blocos = chaves.map((quem) => `
    <div class="grupo-destrava">
      <span class="quem">Destrava: ${escapaHtml(quem)}</span>
      ${grupos[quem].map((p) => `
        <div class="pendencia">
          <div class="titulo-pendencia">
            ${escapaHtml(p.artefato)}
            <span class="etiqueta ${classeDe(p.situacao)}">${escapaHtml(p.situacao)}</span>
          </div>
          <div class="detalhe"><strong>Falta:</strong> ${escapaHtml(p.falta)}</div>
          <div class="detalhe"><strong>Destrava:</strong> ${escapaHtml(p.destrava)}</div>
        </div>
      `).join('')}
    </div>
  `).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${total} encaminhamentos registrados no relatório para o próximo
      período avaliativo, e as ${acervo.pendencias.length} pendências do quadro
      com o que destrava cada uma.
    </p>
    <span class="janela">${escapaHtml(acervo.origem.proximo_periodo)}</span>
    ${trilhas}
    <h3 style="color: var(--primary-purple); margin: 36px 0 8px;">
      O que está pendente, e o que destrava
    </h3>
    <p class="secao-intro">
      ${naoSoUnb} das ${acervo.pendencias.length} pendências dependem de decisão
      ou de infraestrutura do Ministério, isoladamente ou em conjunto com a
      Universidade. As ${soUnb} restantes são de execução da equipe da UnB.
    </p>
    ${blocos}`;
}
```

E dentro de `inicia()`, depois de `montaArtefatos(acervo);`:

```javascript
    montaCronograma(acervo);
```

- [ ] **Passo 3: Conferir no navegador**

Abrir <http://localhost:8000#cronograma>. Conferir:

- A tarja com *setembro a novembro de 2026*.
- Seis trilhas, uma por meta, somando 22 itens.
- A frase "5 das 7 pendências dependem de decisão ou de infraestrutura do Ministério... As 2 restantes são de execução da equipe da UnB."
- Três grupos: *MinC* (4), *MinC + UnB* (1), *UnB* (2).
- Console sem erro.

- [ ] **Passo 4: Commit**

```bash
git add assets/
git commit -m "feat: cronograma e pendências por quem destrava"
```

---

### Task 8: Riscos, documentos e publicação

Fecha o painel e o publica.

**Files:**
- Modify: `assets/graficos.js`
- Modify: `assets/painel.js`
- Modify: `assets/tema.css`
- Create: `.github/workflows/pages.yml`

**Interfaces:**
- Consumes: `acervo.riscos`, `acervo.documentos`.
- Produces: `desenhaRiscos(seletor, riscos)`, `montaRiscos(acervo)`, `montaDocumentos(acervo)`.

- [ ] **Passo 1: Acrescentar `desenhaRiscos` ao fim de `assets/graficos.js`**

Grade 3×3 de probabilidade por impacto, com um ponto por risco. Riscos que caem na mesma célula são distribuídos dentro dela.

```javascript
/* Matriz de riscos: probabilidade (y) por impacto (x), 3×3. */
function desenhaRiscos(seletor, riscos) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const NIVEIS = ['Baixo', 'Médio', 'Alto'];
  const margem = { topo: 20, direita: 20, base: 52, esquerda: 90 };
  const lado = 108;
  const largura = margem.esquerda + lado * 3 + margem.direita;
  const altura = margem.topo + lado * 3 + margem.base;

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label',
      `Matriz de riscos, ${riscos.length} riscos por probabilidade e impacto.`);

  const x = (nivel) => margem.esquerda + NIVEIS.indexOf(nivel) * lado;
  // Probabilidade cresce para cima.
  const y = (nivel) => margem.topo + (2 - NIVEIS.indexOf(nivel)) * lado;

  // Células, tingidas pela severidade combinada.
  for (const p of NIVEIS) {
    for (const i of NIVEIS) {
      const severidade = NIVEIS.indexOf(p) + NIVEIS.indexOf(i);
      svg.append('rect')
        .attr('class', `celula sev-${severidade}`)
        .attr('x', x(i)).attr('y', y(p))
        .attr('width', lado - 4).attr('height', lado - 4)
        .attr('rx', 6);
    }
  }

  // Eixos.
  NIVEIS.forEach((n) => {
    svg.append('text').attr('class', 'rotulo-eixo')
      .attr('x', x(n) + (lado - 4) / 2).attr('y', altura - 26)
      .attr('text-anchor', 'middle').text(n);
    svg.append('text').attr('class', 'rotulo-eixo')
      .attr('x', margem.esquerda - 12).attr('y', y(n) + (lado - 4) / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').text(n);
  });

  svg.append('text').attr('class', 'titulo-eixo')
    .attr('x', margem.esquerda + lado * 1.5).attr('y', altura - 6)
    .attr('text-anchor', 'middle').text('Impacto');

  svg.append('text').attr('class', 'titulo-eixo')
    .attr('transform', `translate(18, ${margem.topo + lado * 1.5}) rotate(-90)`)
    .attr('text-anchor', 'middle').text('Probabilidade');

  // Pontos, numerados na ordem do relatório e distribuídos dentro da célula.
  const porCelula = {};
  riscos.forEach((r, indice) => {
    const chave = `${r.probabilidade}|${r.impacto}`;
    (porCelula[chave] = porCelula[chave] || []).push(indice);
  });

  Object.entries(porCelula).forEach(([chave, indices]) => {
    const [prob, imp] = chave.split('|');
    if (!NIVEIS.includes(prob) || !NIVEIS.includes(imp)) return;

    const cx = x(imp) + (lado - 4) / 2;
    const cy = y(prob) + (lado - 4) / 2;
    const passo = 34;
    const inicio = -((indices.length - 1) * passo) / 2;

    indices.forEach((indice, ordem) => {
      const g = svg.append('g')
        .attr('transform', `translate(${cx + inicio + ordem * passo}, ${cy})`);
      g.append('circle').attr('class', 'ponto-risco').attr('r', 15);
      g.append('text').attr('class', 'numero-risco')
        .attr('text-anchor', 'middle').attr('dy', '0.35em')
        .text(indice + 1);
      g.append('title').text(riscos[indice].risco);
    });
  });
}
```

- [ ] **Passo 2: Acrescentar os estilos ao fim de `assets/tema.css`**

```css
/* ----------------------------------------------------------- matriz de riscos */

.celula { stroke: var(--bg-white); stroke-width: 2; }
.celula.sev-0, .celula.sev-1 { fill: #E8F5EE; }
.celula.sev-2 { fill: #FDF3E3; }
.celula.sev-3 { fill: #FBE6D8; }
.celula.sev-4 { fill: #F5D5C6; }

.ponto-risco { fill: var(--primary-purple); }
.numero-risco { fill: var(--bg-white); font-size: 0.82rem; font-weight: 700; }
.rotulo-eixo { font-size: 0.82rem; fill: var(--text-muted); }
.titulo-eixo { font-size: 0.86rem; font-weight: 600; fill: var(--text-body); }

.painel-riscos {
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 32px;
  align-items: start;
}

@media (max-width: 860px) {
  .painel-riscos { grid-template-columns: 1fr; }
}

.risco {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 16px 20px;
  margin-bottom: 12px;
  display: grid;
  grid-template-columns: 32px 1fr;
  gap: 14px;
}

.risco .indice {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--primary-purple);
  color: var(--bg-white);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.82rem; font-weight: 700;
}

.risco .texto-risco { font-weight: 600; color: var(--text-strong); font-size: 0.92rem; }
.risco .grau { font-size: 0.78rem; color: var(--text-muted); margin: 4px 0 8px; }
.risco .mitigacao { font-size: 0.88rem; }
.risco .mitigacao strong { color: var(--text-strong); }

/* -------------------------------------------------------------- documentos */

.grade-documentos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.documento {
  background: var(--bg-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.documento code {
  background: none;
  padding: 0;
  font-size: 0.86rem;
  color: var(--text-body);
  word-break: break-word;
}

.documento .anexo {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--primary-purple);
  white-space: nowrap;
}
```

- [ ] **Passo 3: Acrescentar `montaRiscos` e `montaDocumentos` a `assets/painel.js`**

```javascript
/* ---------------------------------------------------------------- riscos */

function montaRiscos(acervo) {
  const alvo = document.getElementById('matriz-riscos');

  const lista = acervo.riscos.map((r, i) => `
    <article class="risco">
      <div class="indice">${i + 1}</div>
      <div>
        <div class="texto-risco">${escapaHtml(r.risco)}</div>
        <div class="grau">
          Probabilidade ${escapaHtml(r.probabilidade.toLowerCase())} ·
          impacto ${escapaHtml(r.impacto.toLowerCase())}
        </div>
        <div class="mitigacao">
          <strong>Medida mitigadora:</strong> ${escapaHtml(r.mitigacao)}
        </div>
      </div>
    </article>
  `).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${acervo.riscos.length} riscos identificados no período, com as medidas
      mitigadoras já em andamento.
    </p>
    <div class="painel-riscos">
      <div id="svg-riscos"></div>
      <div>${lista}</div>
    </div>`;

  desenhaRiscos('#svg-riscos', acervo.riscos);
}

/* ------------------------------------------------------------ documentos */

function montaDocumentos(acervo) {
  const alvo = document.getElementById('lista-documentos');

  const cartoes = acervo.documentos.map((d) => `
    <div class="documento">
      <code>${escapaHtml(d.arquivo)}</code>
      <span class="anexo">${escapaHtml(d.anexo)}</span>
    </div>
  `).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${acervo.documentos.length} documentos técnicos produzidos, versionados
      no repositório público da plataforma. Todos são gerados a partir do código,
      e não redigidos sobre ele — divergência entre documento e plataforma é
      detectável, e corrigível na fonte.
    </p>
    <div class="grade-documentos">${cartoes}</div>`;
}
```

E dentro de `inicia()`, depois de `montaCronograma(acervo);`:

```javascript
    montaRiscos(acervo);
    montaDocumentos(acervo);
```

- [ ] **Passo 4: Conferir o painel inteiro**

```bash
python3 -m http.server 8000 &
sleep 1 && curl -s -o /dev/null -w "index: %{http_code}\n" http://localhost:8000/
```

Percorrer <http://localhost:8000> de cima a baixo e conferir:

- Cabeçalho, indicadores (20/11/2/5/2/12), evolução, seis metas, quadro filtrável, cronograma, riscos, documentos.
- Matriz de riscos: sete pontos numerados; os riscos 1 e 6 no canto Alto/Alto.
- Doze cartões de documento.
- Console sem nenhum erro.
- Reduzir a janela a 375 px de largura: nada transborda horizontalmente; a tabela rola dentro do seu container.

- [ ] **Passo 5: Criar o workflow de publicação**

Criar `.github/workflows/pages.yml`:

```yaml
# Publica o painel no GitHub Pages. Não há build: o site é o próprio
# repositório, servido como está.
#
# PRÉ-REQUISITO, uma vez: em Settings → Pages, a origem tem de estar em
# "GitHub Actions".
name: Publicar painel

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  publica:
    name: Publicar
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/configure-pages@v5

      - uses: actions/upload-pages-artifact@v3
        with:
          path: .

      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Passo 6: Commit e publicação**

```bash
git add assets/ .github/workflows/pages.yml
git commit -m "feat: matriz de riscos, documentos e publicação"
git push
```

- [ ] **Passo 7: Conferir a publicação**

```bash
gh run list --limit 3
```

Esperado: *Validação do acervo* e *Publicar painel* concluídos com sucesso.

Abrir <https://govhub-br.github.io/dashboard-minc-project/> e conferir que o painel carrega, com todas as seções e sem erro de console.

---

## Verificação final

- [ ] `python3 -m unittest discover -s tests -v` passa.
- [ ] `python3 scripts/valida.py` reporta acervo consistente.
- [ ] As sete seções aparecem, com os números do 3º Relatório Parcial.
- [ ] Nenhuma requisição a domínio externo — Rede, no inspetor, só mostra o próprio host.
- [ ] Nenhum erro no console.
- [ ] Legível em 375 px de largura e em projeção.
- [ ] O painel exibe a data de apuração e a nota sobre a contagem.

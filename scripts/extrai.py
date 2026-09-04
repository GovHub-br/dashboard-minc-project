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


# --------------------------------------------------------------------------
# doc-acompanhamento: artefatos, pendências, documentos
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# relatorio: metas, encaminhamentos, riscos
# --------------------------------------------------------------------------
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

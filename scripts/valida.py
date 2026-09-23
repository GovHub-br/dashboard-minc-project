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
TOTAL_PRODUTOS = 19
CAMPOS_ORIGEM = ("relatorio", "periodo", "apurado_em")
TIPOS_COBERTURA = ("secao", "mencao")
ESTADOS_PRODUTO = ("Entregue", "Em andamento", "Previsto", "")


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
        entrega = por_nome.get(nome)
        if entrega is None:
            problemas.append(f"Pendência de artefato inexistente: {nome!r}.")
            continue
        if p.get("situacao") != entrega.get("agora"):
            problemas.append(
                f"Pendência {nome!r} diverge do quadro: declara "
                f"{p.get('situacao')!r}, o quadro diz "
                f"{entrega.get('agora')!r}."
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

    # 5. Fechamento dos produtos pactuados.
    produtos = acervo.get("produtos", [])
    if len(produtos) != TOTAL_PRODUTOS:
        problemas.append(
            f"O Termo pactua {TOTAL_PRODUTOS} produtos; o acervo traz "
            f"{len(produtos)}."
        )

    nums_relatorio = {str(r.get("num")) for r in acervo.get("relatorios", [])}
    if not nums_relatorio:
        problemas.append("O acervo não declara relatório algum.")

    # 6. Cobertura: só relatório existente, só tipo conhecido, com localização.
    for p in produtos:
        rotulo = f"Meta {p.get('meta')} · Produto {p.get('num')}"
        for num, c in (p.get("cobertura") or {}).items():
            if num not in nums_relatorio:
                problemas.append(
                    f"{rotulo} declara cobertura no relatório {num}, que não "
                    f"consta de relatorios."
                )
            if c.get("tipo") not in TIPOS_COBERTURA:
                problemas.append(
                    f"{rotulo} tem cobertura de tipo {c.get('tipo')!r} no "
                    f"relatório {num}."
                )
            if not c.get("onde"):
                problemas.append(
                    f"{rotulo} declara cobertura no relatório {num} sem dizer "
                    f"onde."
                )

    # 7. Todo artefato do quadro pertence a exatamente um produto, e com a
    #    situação que o quadro declara.
    vinculados = {}
    for p in produtos:
        for a in p.get("artefatos", []):
            nome = a.get("nome")
            if nome in vinculados:
                problemas.append(
                    f"Artefato {nome!r} vinculado a mais de um produto."
                )
            vinculados[nome] = a

    for a in artefatos:
        nome = a.get("nome")
        vinculo = vinculados.get(nome)
        if vinculo is None:
            problemas.append(f"Artefato {nome!r} não pertence a produto algum.")
        elif vinculo.get("situacao") != a.get("agora"):
            problemas.append(
                f"Artefato {nome!r} consta como {vinculo.get('situacao')!r} no "
                f"produto e {a.get('agora')!r} no quadro."
            )

    for nome in vinculados:
        if nome not in por_nome:
            problemas.append(
                f"Produto vincula artefato inexistente no quadro: {nome!r}."
            )

    # 8. Todo produto diz o que entregou, declara estado conhecido, e todo
    #    documento sabe onde está. Estado em branco é permitido: significa
    #    "a classificar", e a página mostra assim.
    for p in produtos:
        if not p.get("balanco"):
            problemas.append(
                f"Meta {p.get('meta')} · Produto {p.get('num')} sem balanço."
            )

        if p.get("estado") not in ESTADOS_PRODUTO:
            problemas.append(
                f"Meta {p.get('meta')} · Produto {p.get('num')} com estado "
                f"{p.get('estado')!r}, fora da lista."
            )

    for d in acervo.get("documentos", []):
        if not d.get("url"):
            problemas.append(f"Documento {d.get('arquivo')!r} sem endereço.")

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
        f"{len(acervo.get('produtos', []))} produtos em "
        f"{len(acervo.get('relatorios', []))} relatórios, "
        f"{len(acervo['pendencias'])} pendências, "
        f"apurado em {acervo['origem']['apurado_em']}."
    )


if __name__ == "__main__":
    main()

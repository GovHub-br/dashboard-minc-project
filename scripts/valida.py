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

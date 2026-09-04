#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte a planilha dos 8 eixos do PNC em dados/eixos.json.

Também acrescenta um retrato diário a dados/historico.json, que é o que
alimenta o gráfico de evolução ao longo do tempo.

Uso:
    python3 scripts/planilha_para_json.py --csv planilha.csv --out dados/eixos.json

Só biblioteca padrão, de propósito: roda em qualquer máquina e no CI.
"""

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Normalização
# --------------------------------------------------------------------------

STATUS = {
    "concluido": "concluido", "concluído": "concluido", "cumprido": "concluido",
    "em andamento": "em_andamento", "andamento": "em_andamento",
    "bloqueado": "bloqueado", "stand by": "bloqueado", "standby": "bloqueado",
    "em risco": "em_risco", "risco": "em_risco",
    "nao iniciado": "nao_iniciado", "não iniciado": "nao_iniciado",
    "nao iniciada": "nao_iniciado", "não iniciada": "nao_iniciado",
    "em aberto": "nao_iniciado", "aberto": "nao_iniciado",
}

# Mesma escala do painel de referência do MCid.
PROGRESSO = {
    "concluido": 100, "em_andamento": 50,
    "bloqueado": 25, "em_risco": 25, "nao_iniciado": 0,
}

PRIORIDADE = {
    "alta": "alta", "média": "media", "media": "media",
    "baixa": "baixa", "": "media",
}

# Marcadores de prazo ainda não acordado. Prazo em branco e prazo vencido são
# coisas diferentes: sem esta distinção o painel acusaria atraso onde só há
# indefinição.
SEM_PRAZO = {
    "", "-", "não definido ainda", "nao definido ainda", "não definido",
    "nao definido", "a definir", "em aberto", "aberto", "n/a",
}

ROTULO_STATUS = {
    "concluido": "Concluído",
    "em_andamento": "Em andamento",
    "bloqueado": "Bloqueado",
    "em_risco": "Em risco",
    "nao_iniciado": "Não iniciado",
}


def limpa(v):
    return re.sub(r"\s+", " ", str(v or "").strip())


def le_status(bruto):
    k = limpa(bruto).lower()
    for chave, valor in STATUS.items():
        if chave and chave in k:
            return valor
    return "nao_iniciado"


def le_prioridade(bruto):
    return PRIORIDADE.get(limpa(bruto).lower(), "media")


def le_prazo(bruto):
    """Devolve AAAA-MM-DD, ou string vazia quando o prazo não foi definido."""
    s = limpa(bruto)
    if s.lower() in SEM_PRAZO:
        return ""
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, formato).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""  # não reconhecido: trata como sem prazo, nunca como atrasado


# O código aceita um prefixo de letras porque planilhas convertem "1.1.1" em
# data (1 de janeiro de 2001) sem avisar. Com "E1.1.1" isso não acontece, e a
# rede de dependências sobrevive a um copiar-e-colar para o Sheets.
PADRAO_CODIGO = re.compile(r"[A-Za-z]{0,3}\d+(\.\d+)*")


def le_codigo(bruto):
    s = limpa(bruto).replace(",", ".")
    return s if PADRAO_CODIGO.fullmatch(s) else ""


def le_dependencias(bruto):
    s = limpa(bruto)
    if not s or s.lower() in ("-", "n/a", "não se aplica", "nao se aplica"):
        return []
    saida, vistos = [], set()
    for parte in re.split(r"[;/+]|\s+e\s+|\s+", s):
        c = le_codigo(parte.strip(".,"))
        if c and c not in vistos:
            vistos.add(c)
            saida.append(c)
    return saida


def numero_do_eixo(texto):
    m = re.match(r"^\s*(\d+)", limpa(texto))
    return int(m.group(1)) if m else None


def nome_do_eixo(texto):
    """Remove o número e o separador, deixando só o nome."""
    return re.sub(r"^\s*\d+\s*[·.\-–]\s*", "", limpa(texto))


# --------------------------------------------------------------------------
# Leitura da planilha
# --------------------------------------------------------------------------

def acha_coluna(cabecalho, *termos):
    for i, nome in enumerate(cabecalho):
        n = limpa(nome).lower()
        for t in termos:
            if t in n:
                return i
    return None


def le_planilha(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = [l for l in csv.reader(f) if any(limpa(c) for c in l)]

    if not linhas:
        raise SystemExit("A planilha está vazia.")

    cabecalho = linhas[0]
    col = {
        "prioridade": acha_coluna(cabecalho, "prioridade"),
        "eixo": acha_coluna(cabecalho, "eixo"),
        "processo": acha_coluna(cabecalho, "processo"),
        "atividade": acha_coluna(cabecalho, "atividade"),
        "cod": acha_coluna(cabecalho, "cod"),
        "tarefa": acha_coluna(cabecalho, "tarefa", "demanda"),
        "depende": acha_coluna(cabecalho, "depende"),
        "resp": acha_coluna(cabecalho, "respons"),
        "prazo": acha_coluna(cabecalho, "prazo"),
        "status": acha_coluna(cabecalho, "status"),
    }

    faltando = [k for k in ("eixo", "tarefa", "status") if col[k] is None]
    if faltando:
        raise SystemExit(
            f"A planilha não tem a(s) coluna(s): {', '.join(faltando)}. "
            f"Cabeçalho lido: {cabecalho}"
        )

    def campo(linha, chave):
        i = col[chave]
        return linha[i] if i is not None and i < len(linha) else ""

    tarefas = []
    for linha in linhas[1:]:
        eixo_txt = limpa(campo(linha, "eixo"))
        descricao = limpa(campo(linha, "tarefa"))
        eixo_num = numero_do_eixo(eixo_txt)
        if not descricao or eixo_num is None:
            continue

        status = le_status(campo(linha, "status"))
        tarefas.append({
            "cod": le_codigo(campo(linha, "cod")),
            "eixo": eixo_num,
            "eixo_nome": nome_do_eixo(eixo_txt),
            "processo": limpa(campo(linha, "processo")),
            "atividade": limpa(campo(linha, "atividade")),
            "tarefa": descricao,
            "depende_de": le_dependencias(campo(linha, "depende")),
            "resp": limpa(campo(linha, "resp")),
            "prazo": le_prazo(campo(linha, "prazo")),
            "status": status,
            "prioridade": le_prioridade(campo(linha, "prioridade")),
            "progresso": PROGRESSO[status],
        })

    return tarefas


# --------------------------------------------------------------------------
# Rede de dependências
# --------------------------------------------------------------------------

def calcula_rede(tarefas):
    """Marca cada tarefa com o passo em que entra, se está travada e quantas
    outras ela segura. Dependências para códigos inexistentes são ignoradas."""
    por_cod = {t["cod"]: t for t in tarefas if t["cod"]}

    # Só dependências que apontam para tarefa existente.
    for t in tarefas:
        t["depende_de"] = [d for d in t["depende_de"] if d in por_cod]

    # Passo topológico. Um ciclo faz a tarefa parar no passo em que está.
    def passo(t, visitando=()):
        if t.get("_passo") is not None:
            return t["_passo"]
        if t["cod"] in visitando:
            return 0
        if not t["depende_de"]:
            t["_passo"] = 0
            return 0
        n = 1 + max(
            passo(por_cod[d], visitando + (t["cod"],)) for d in t["depende_de"]
        )
        t["_passo"] = n
        return n

    for t in tarefas:
        t.setdefault("_passo", None)
    for t in tarefas:
        t["passo"] = passo(t)
    # A limpeza vem depois de todo o cálculo: a recursão grava _passo em
    # tarefas já visitadas, então remover dentro do laço acima deixaria resíduo.
    for t in tarefas:
        t.pop("_passo", None)

    # Travada: tem predecessor não concluído. Pronta: predecessores todos
    # concluídos e ela ainda não começou.
    for t in tarefas:
        pendentes = [
            d for d in t["depende_de"]
            if por_cod[d]["status"] != "concluido"
        ]
        t["travada"] = bool(pendentes) and t["status"] != "concluido"
        t["pronta"] = (
            bool(t["depende_de"])
            and not pendentes
            and t["status"] == "nao_iniciado"
        )

    # Quantas tarefas cada uma segura, direta e indiretamente.
    sucessores = {c: [] for c in por_cod}
    for t in tarefas:
        for d in t["depende_de"]:
            sucessores[d].append(t["cod"])

    def alcance(cod, vistos=None):
        vistos = vistos if vistos is not None else set()
        for s in sucessores.get(cod, []):
            if s not in vistos:
                vistos.add(s)
                alcance(s, vistos)
        return vistos

    for t in tarefas:
        t["segura"] = len(alcance(t["cod"])) if t["cod"] else 0

    return tarefas


def resume(tarefas):
    total = len(tarefas)
    por_status = {}
    for t in tarefas:
        por_status[t["status"]] = por_status.get(t["status"], 0) + 1

    encadeadas = {
        t["cod"] for t in tarefas
        if t["depende_de"] or t["segura"] > 0
    }
    vinculos = sum(len(t["depende_de"]) for t in tarefas)

    # Gargalo: entre as não concluídas, a que segura mais tarefas.
    candidatos = [
        t for t in tarefas if t["status"] != "concluido" and t["segura"] > 0
    ]
    gargalo = max(candidatos, key=lambda t: t["segura"], default=None)

    return {
        "total": total,
        "por_status": por_status,
        "progresso_medio": (
            round(sum(t["progresso"] for t in tarefas) / total, 1) if total else 0
        ),
        "travadas": sum(1 for t in tarefas if t["travada"]),
        "prontas": sum(1 for t in tarefas if t["pronta"]),
        "encadeadas": len(encadeadas),
        "vinculos": vinculos,
        # Passo é 0-based; a cadeia mais longa é o maior passo mais um. Sem
        # tarefa nenhuma não há cadeia, e o valor é zero, não um.
        "cadeia_mais_longa": (
            max(t["passo"] for t in tarefas) + 1 if tarefas else 0
        ),
        "sem_prazo": sum(1 for t in tarefas if not t["prazo"]),
        "gargalo": (
            {
                "cod": gargalo["cod"],
                "tarefa": gargalo["tarefa"],
                "segura": gargalo["segura"],
                "resp": gargalo["resp"],
            }
            if gargalo else None
        ),
    }


def monta_alertas(tarefas, hoje):
    """Bloqueadas, em risco e com prazo vencido. Tarefa sem prazo nunca entra
    como atrasada — ausência de data não é atraso."""
    alertas = []
    for t in tarefas:
        if t["status"] == "concluido":
            continue
        motivo = None
        if t["status"] == "bloqueado":
            motivo = "bloqueada"
        elif t["status"] == "em_risco":
            motivo = "em risco"
        elif t["prazo"] and t["prazo"] < hoje:
            motivo = "prazo vencido"
        if motivo:
            alertas.append({
                "cod": t["cod"], "tarefa": t["tarefa"], "eixo": t["eixo"],
                "eixo_nome": t["eixo_nome"], "motivo": motivo,
                "prazo": t["prazo"], "resp": t["resp"],
            })
    ordem = {"bloqueada": 0, "prazo vencido": 1, "em risco": 2}
    alertas.sort(key=lambda a: (ordem[a["motivo"]], a["prazo"] or "9999"))
    return alertas


def agrupa_por_eixo(tarefas):
    eixos = {}
    for t in tarefas:
        e = eixos.setdefault(t["eixo"], {
            "id": t["eixo"], "nome": t["eixo_nome"], "tarefas": [],
        })
        e["tarefas"].append(t)

    saida = []
    for eid in sorted(eixos):
        e = eixos[eid]
        n = len(e["tarefas"])
        por_status = {}
        for t in e["tarefas"]:
            por_status[t["status"]] = por_status.get(t["status"], 0) + 1
        saida.append({
            "id": e["id"],
            "nome": e["nome"],
            "total": n,
            "concluidas": por_status.get("concluido", 0),
            "progresso": round(sum(t["progresso"] for t in e["tarefas"]) / n, 1),
            "por_status": por_status,
            "tarefas": sorted(e["tarefas"], key=lambda t: (t["passo"], t["cod"])),
        })
    return saida


# --------------------------------------------------------------------------
# Série histórica
# --------------------------------------------------------------------------

def registra_retrato(tarefas, eixos, caminho, hoje):
    historico = {"retratos": []}
    if caminho.exists():
        historico = json.loads(caminho.read_text(encoding="utf-8"))
        historico.setdefault("retratos", [])

    # Um retrato por dia: o do dia é substituído pelo estado mais recente.
    historico["retratos"] = [r for r in historico["retratos"] if r["data"] != hoje]

    por_status = {}
    for t in tarefas:
        por_status[t["status"]] = por_status.get(t["status"], 0) + 1

    historico["retratos"].append({
        "data": hoje,
        "total": len(tarefas),
        "por_status": por_status,
        "progresso_medio": (
            round(sum(t["progresso"] for t in tarefas) / len(tarefas), 1)
            if tarefas else 0
        ),
        "por_eixo": [
            {"id": e["id"], "progresso": e["progresso"], "total": e["total"]}
            for e in eixos
        ],
    })
    historico["retratos"].sort(key=lambda r: r["data"])
    caminho.write_text(
        json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(historico["retratos"])


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True, help="planilha em CSV")
    p.add_argument("--out", default="dados/eixos.json")
    p.add_argument("--historico", default="dados/historico.json")
    p.add_argument("--proxima-reuniao", default="")
    p.add_argument("--guardia", default="")
    args = p.parse_args()

    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    tarefas = calcula_rede(le_planilha(args.csv))
    eixos = agrupa_por_eixo(tarefas)

    acervo = {
        "origem": {
            "fonte": "Planilha dos 8 eixos do PNC",
            "sincronizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "proxima_reuniao": args.proxima_reuniao,
            "guardia": args.guardia,
        },
        "rotulos_status": ROTULO_STATUS,
        "resumo": resume(tarefas),
        "eixos": eixos,
        "alertas": monta_alertas(tarefas, hoje),
    }

    saida = Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(
        json.dumps(acervo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    n = registra_retrato(tarefas, eixos, Path(args.historico), hoje)

    r = acervo["resumo"]
    print(
        f"✓ {saida} — {r['total']} tarefas em {len(eixos)} eixos, "
        f"{r['progresso_medio']}% de progresso médio, {r['travadas']} travadas, "
        f"{r['sem_prazo']} sem prazo definido."
    )
    print(f"✓ {args.historico} — {n} retrato(s) na série.")


if __name__ == "__main__":
    main()

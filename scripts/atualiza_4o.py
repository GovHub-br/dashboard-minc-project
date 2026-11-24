#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza dados/ted.json para o 4º Relatório Parcial (setembro a novembro
de 2026).

O 3º Relatório tinha geradores (conteudo.py), lidos por extrai.py. O 4º foi
escrito num documento de texto, então o que muda aqui está transcrito à mão,
com a seção de origem ao lado. Produtos, cobertura, balanço e estado ficam em
produtos.py, como antes; este script cuida de metas, quadro de artefatos,
pendências, riscos e documentos.

O quadro de acompanhamento da CGIIC não foi reapurado no 4º Relatório. A
situação de cada artefato só muda onde o 4º Relatório a declara (Metadados,
entregue com o Catálogo de Metadados v2); nos demais, muda só o "onde está".

Uso:
    python3 scripts/atualiza_4o.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import produtos as tabela_produtos  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ACERVO = RAIZ / "dados" / "ted.json"

ORIGEM = {
    "relatorio": "4º Relatório Parcial",
    "periodo": "setembro a novembro de 2026",
    "proximo_periodo": "dezembro de 2026 a março de 2027",
    "apurado_em": "2026-11-02",
}

# Balanço: síntese das seções de cada meta (capítulos 02 a 07).
# Encaminhamentos: capítulo 08, "Encaminhamentos para o próximo período
# avaliativo", que trata das Metas 02, 03 e 04. Para as Metas 05 e 06, que o
# capítulo 08 não detalha, vêm do que as seções dos produtos declaram como
# pendente ou próximo passo. A Meta 01 se encerra no período (mês 8, 24/11).
METAS = {
    "01": {
        "balanco": "Concluiu a escuta nos oito eixos do Plano — 14 encontros de "
                   "trabalho em setembro e outubro, além do Datathon — e o "
                   "diagnóstico técnico e institucional dos dados do PNC, com o "
                   "catálogo das fontes presentes no Data Lakehouse. A meta "
                   "chega ao fim do prazo em 24 de novembro de 2026.",
        "encaminhamentos": [],
    },
    "02": {
        "balanco": "Fixou a arquitetura final da plataforma, o Data Lakehouse, "
                   "aprovada pelo Ministério em outubro, e refez para ela o "
                   "modelo conceitual, lógico e físico, o dicionário de dados e "
                   "o catálogo de metadados. A plataforma em funcionamento está "
                   "em transição: Iceberg e Polaris aguardam a infraestrutura do "
                   "Ministério. Os painéis aguardam a definição de requisitos, e "
                   "o modelo de governança segue com repactuação de prazo "
                   "sugerida para março de 2027.",
        "encaminhamentos": [
            "Concluir o modelo de governança, com prazo proposto para março de "
            "2027 na repactuação: matriz de papéis, Registro de Atividades de "
            "Tratamento (ROPA), validação do RIPD e relatório de testes de "
            "qualidade (Produto 4).",
            "Completar as definições de negócio que faltam no dicionário de "
            "dados do Mapas Culturais (Produto 3).",
            "No repositório, marcar a versão de entrega, verificar se o "
            "histórico guarda senhas ou chaves esquecidas e produzir o "
            "inventário de componentes (Produto 5).",
            "Definir com o Ministério, em reunião, os eixos, os indicadores e a "
            "ordem de publicação dos painéis, e construí-los a partir dos "
            "indicadores calculados na plataforma até fevereiro de 2027, junto "
            "com o relatório executivo (Produto 1).",
        ],
    },
    "03": {
        "balanco": "Concluiu a arquitetura de referência, documentada no Anexo I "
                   "e nos ADRs do repositório público. O Ranger anonimiza na "
                   "consulta, e as políticas aguardam os perfis de usuários do "
                   "Ministério; os scripts de implantação e o manual de evolução "
                   "precisam ser atualizados para a arquitetura final. As "
                   "oficinas de capacitação estão previstas para o início de "
                   "2027.",
        "encaminhamentos": [
            "Refinar as políticas de acesso no Ranger assim que o Ministério "
            "definir os perfis de usuários.",
            "Produzir a documentação técnica do motor de governança.",
            "Atualizar os scripts de implantação e o manual de evolução para a "
            "arquitetura final.",
            "Realizar as oficinas de capacitação das equipes do Ministério.",
            "Entregar o relatório final de cumprimento do objeto, em março de "
            "2027.",
        ],
    },
    "04": {
        "balanco": "O TAIS passou a responder sobre os dados do Ministério e foi "
                   "usado no Datathon do PNC. O modo Indicador ganhou regras de "
                   "recusa de pedidos de dados pessoais e mascaramento de dados "
                   "sensíveis. Guias, oficinas e livro começam no fim de "
                   "novembro de 2026.",
        "encaminhamentos": [
            "Iniciar os guias técnicos no fim de novembro e realizar a oficina "
            "sobre o uso de IA nos meses seguintes.",
            "Fechar a organização, a autoria e o sumário do livro e escrevê-lo "
            "entre dezembro de 2026 e janeiro de 2027.",
            "Submeter o TAIS a uma bateria de perguntas com resultado esperado, "
            "para medir a precisão das respostas.",
        ],
    },
    "05": {
        "balanco": "Realizou o Datathon do PNC, com 104 participantes de 35 "
                   "organizações, e pôs em operação o catálogo institucional "
                   "(OpenMetadata), que agora recebe sugestões de descrição de "
                   "quem usa os dados. A oficina sobre governança descentralizada "
                   "e o documento analítico da modelagem do SNIIC estão em "
                   "preparação.",
        "encaminhamentos": [
            "Iniciar a publicação de dados abertos, com prazo no mês 11 do TED "
            "(fevereiro de 2027) (Produto 1).",
            "Desenhar e realizar a oficina sobre governança de dados "
            "descentralizada, a partir da Instrução Normativa do Data Lakehouse "
            "e do documento de modelagem do SNIIC, até o mês 11 do TED "
            "(Produto 2).",
            "Concluir o documento analítico de modelagem e planejamento da "
            "implementação do SNIIC (Produto 4).",
        ],
    },
    "06": {
        "balanco": "Pôs em operação o Tainacan Agregador e iniciou o piloto com a "
                   "Brasiliana Museus, do IBRAM, em coleta desde 28 de outubro de "
                   "2026. Os demais repositórios do IPHAN e da Funarte ainda "
                   "serão cadastrados.",
        "encaminhamentos": [
            "Cadastrar e coletar os demais repositórios: INDL, BCR e INRC, do "
            "IPHAN, e Funarte + Digital, da Funarte.",
            "Definir o modelo de dados comum e tratar as duplicidades na "
            "harmonização dos metadados.",
            "Tornar a coleta mais robusta diante da lentidão dos servidores de "
            "origem.",
            "Desenhar a interface pública da Brasiliana Cultura e estabelecer as "
            "regras de adesão de novas instituições.",
        ],
    },
}

# artefato -> (situação no 4º, onde está). Ausente: mantém situação e lugar.
ARTEFATOS = {
    "Arquitetura lógica": (
        "Entregue", "Anexo I do 4º Relatório · Arquitetura de Dados do MinC"),
    "Arquitetura física": (
        "Entregue como proposta",
        "Anexo I do 4º Relatório; Iceberg e Polaris ainda não implantados"),
    "Arquitetura de segurança": (
        "Entregue como proposta",
        "Anexo I do 4º Relatório; Ranger implantado, políticas por perfil a "
        "refinar"),
    "Dicionário de dados": (
        "Entregue", "Anexo VII do 4º Relatório · Dicionário de Dados, versão 2"),
    "Metadados": (
        "Entregue",
        "Anexo VIII do 4º Relatório · Catálogo de Metadados, versão 2"),
    "Modelo conceitual, lógico e físico": (
        "Entregue",
        "Anexo IV do 4º Relatório · Modelo Conceitual, Lógico e Físico, "
        "versão 2"),
    "Catálogo de fontes de dados": (
        "Entregue",
        "Anexo V do 4º Relatório · Catálogo de Fontes de Dados, versão 2"),
    "Matriz de papéis e responsabilidades": (
        "Não entregue",
        "Em elaboração na Meta 02 · Produto 4, com prazo sugerido para março "
        "de 2027"),
    "Políticas de acesso": (
        "Parcial",
        "Ranger anonimiza na consulta; políticas por perfil aguardam o "
        "Ministério"),
    "Evidências de testes e validação": (
        "Parcial",
        "1.202 testes de dados declarados no repositório; relatório de testes "
        "em elaboração"),
    "Relação de componentes e versões": (
        "Parcial",
        "Inventário de componentes e versões pendente (Meta 02 · Produto 5)"),
    "Scripts de implantação": (
        "Entregue",
        "scripts-de-implantacao.pdf (3º Relatório); atualização para a "
        "arquitetura final pendente"),
    "Manual de evolução": (
        "Entregue",
        "manual-de-evolucao.pdf (3º Relatório); atualização para a arquitetura "
        "final pendente"),
}

# artefato -> (falta, destrava, quem destrava). A classificação de quem
# destrava é do painel, como no QUEM_DESTRAVA do extrai.py.
PENDENCIAS = {
    "Matriz de papéis e responsabilidades": (
        "O documento",
        "Em elaboração na Meta 02 · Produto 4, com prazo sugerido para março "
        "de 2027",
        "MinC + UnB"),
    "Políticas de acesso": (
        "As políticas por perfil de usuário",
        "Definição dos perfis de usuários e validação dos campos sensíveis "
        "pelo Ministério",
        "MinC"),
    "Manual de uso": (
        "Guia dirigido ao usuário final",
        "Definir o público e o ponto de acesso, hoje condicionados aos painéis",
        "MinC"),
    "Manual de manutenção": (
        "O documento",
        "Ambiente de produção, que depende da infraestrutura prevista pela "
        "STII para dezembro e janeiro",
        "MinC"),
    "Evidências de testes e validação": (
        "Relatório de testes de qualidade",
        "Em elaboração na Meta 02 · Produto 4, sobre os testes declarados nos "
        "modelos",
        "UnB"),
    "Relação de componentes e versões": (
        "Inventário com versão de cada componente",
        "Produzi-lo no fechamento do repositório (Meta 02 · Produto 5)",
        "UnB"),
}

# Capítulo 08, "Riscos e medidas mitigadoras". O 4º Relatório não gradua
# probabilidade e impacto.
RISCOS = [
    ("Três produtos da Meta 02 tinham prazo em agosto de 2026; o modelo de "
     "governança segue em andamento",
     "Sugerida à gestão do TED a repactuação do prazo para março de 2027"),
    ("Guias, oficinas sobre IA e livro da Meta 04 começam no fim de novembro, "
     "com a autoria do livro em definição",
     "Fechar autoria e sumário do livro em dezembro e incluir as datas das "
     "oficinas no pedido ao gestor do TED"),
    ("Dependência de decisões e entregas do Ministério: perfis de usuários, "
     "requisitos dos painéis, liberação de bases retidas (RAIS) e datas das "
     "oficinas de 2027",
     "Reunir as pendências num pedido único ao gestor do TED, com prazo para "
     "cada uma"),
    ("Infraestrutura do Ministério limita o ritmo; Iceberg e Polaris dependem "
     "da infraestrutura prevista pela STII para dezembro e janeiro",
     "Ajustar a ordem de carga das bases nas reuniões de planejamento; seguir "
     "com os componentes já implantados"),
]


def main():
    acervo = json.loads(ACERVO.read_text("utf-8"))
    if acervo["origem"]["relatorio"] == ORIGEM["relatorio"]:
        sys.exit("O acervo já está no 4º Relatório; nada a fazer.")

    for a in acervo["artefatos"]:
        a["antes"] = a["agora"]
        if a["nome"] in ARTEFATOS:
            a["agora"], a["onde"] = ARTEFATOS[a["nome"]]
        elif a["onde"] != "—":
            a["onde"] = f"{a['onde']} (3º Relatório)"

    acervo["pendencias"] = [
        {
            "artefato": nome,
            "situacao": next(
                a["agora"] for a in acervo["artefatos"] if a["nome"] == nome
            ),
            "falta": falta,
            "destrava": destrava,
            "quem": quem,
        }
        for nome, (falta, destrava, quem) in PENDENCIAS.items()
    ]

    for m in acervo["metas"]:
        m.update(METAS[m["num"]])

    acervo["riscos"] = [
        {"risco": r, "probabilidade": "", "impacto": "", "mitigacao": mit}
        for r, mit in RISCOS
    ]

    for d in acervo["documentos"]:
        if not d["anexo"].startswith("3º Relatório"):
            d["anexo"] = f"3º Relatório · {d['anexo']}"

    acervo["origem"] = ORIGEM
    relatorios, produtos = tabela_produtos.monta(acervo["artefatos"])
    acervo["relatorios"] = relatorios
    acervo["produtos"] = produtos

    ACERVO.write_text(
        json.dumps(acervo, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )


if __name__ == "__main__":
    main()

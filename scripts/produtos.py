#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Os 19 produtos pactuados no TED e sua cobertura em cada relatório parcial.

Três tabelas, todas transcritas de fonte documental:

RELATORIOS      os três relatórios de atividades entregues, com a data do
                documento e o período que cada um declara cobrir.

PRODUTOS        os 19 produtos do TED, com a redação do Termo. A cobertura
                registra, por relatório, se o produto teve seção própria
                ("secao") ou foi tratado sob outro produto ("mencao"), com a
                localização. Vem do sumário de cada relatório.

BALANCO         o que cada produto entregou no período, derivado da seção
                correspondente do 3º Relatório, com a página de origem.

ARTEFATO_PRODUTO a que produto pertence cada um dos 20 artefatos do quadro de
                acompanhamento. A evidência é "TED" quando o artefato é nomeado
                na redação do produto, e "R3" quando o vínculo vem do lugar em
                que o 3º Relatório o documenta. Como o QUEM_DESTRAVA do
                extrai.py, a classificação "R3" é do painel, não do documento —
                e está marcada como tal na página.

ESTADO          se o produto já está entregue. Preenchido à mão por quem
                responde pelo TED — ver a tabela, mais abaixo.

RISCO_PRODUTO   a que produto cada um dos sete riscos se refere. Classificação
                do painel, pelo assunto do risco e da sua medida mitigadora; o
                relatório não faz essa ligação.

As três palavras do painel, que não são sinônimos:

produto     o que o Termo espera. São 19, e não mudam.
artefato    o que ficou disponível no período e compõe um produto. São os 20 do
            quadro de acompanhamento da CGIIC.
entrega     quando o produto inteiro é contemplado. É estado de produto, nunca
            nome de peça: um produto com três artefatos entregues e um parcial
            não está entregue.

Importado por extrai.py. Não roda sozinho.
"""

# Onde ficam os documentos produzidos, versionados no repositório da
# plataforma. O painel liga cada documento citado a este endereço.
BASE_DOCUMENTOS = (
    "https://github.com/GovHub-br/data-application-minc/blob/main/"
    "docs/documentos/"
)

RELATORIOS = [
    {
        "num": 1,
        "rotulo": "1º Relatório",
        "data": "2026-04-09",
        "periodo": "desde a assinatura do Termo",
        "periodo_declarado": False,
    },
    {
        "num": 2,
        "rotulo": "2º Relatório",
        "data": "2026-05-29",
        "periodo": "abril a maio de 2026",
        "periodo_declarado": True,
    },
    {
        "num": 3,
        "rotulo": "3º Relatório",
        "data": "2026-08-31",
        "periodo": "maio a agosto de 2026",
        "periodo_declarado": True,
    },
]

METAS_TED = {
    "01": "Diagnóstico, mapeamento de recursos e levantamento de bases de dados",
    "02": "Integração e jornada dos dados do Plano Nacional de Cultura",
    "03": "Estratégia de governança, adoção e transferência de tecnologia",
    "04": "Desenvolvimento de agentes de IA para acesso qualificado aos dados",
    "05": "Governança de dados do SNIIC e modelo estratégico de política pública "
          "de informação",
    "06": "Brasiliana Cultura — catálogo integrado dos acervos culturais do "
          "sistema MinC",
}

# meta, produto, nome curto, redação do TED, cobertura por relatório
PRODUTOS = [
    {
        "meta": "01", "num": 1,
        "nome": "Oficinas de facilitação e escuta qualificada",
        "redacao": "Oficinas de facilitação e escuta qualificada sobre os dados "
                   "ligados ao PNC, de forma a definir os eixos prioritários para "
                   "integração e qualificação de dados e desenvolvimento da "
                   "plataforma",
        "cobertura": {
            "1": {"tipo": "secao", "onde": "Descrição das atividades · Produto 1"},
            "2": {"tipo": "secao", "onde": "§ 3.1"},
            "3": {"tipo": "secao", "onde": "Meta 01 · Produto 1", "pagina": 12},
        },
    },
    {
        "meta": "01", "num": 2,
        "nome": "Relatório de diagnóstico técnico e institucional",
        "redacao": "Relatório de diagnóstico técnico e institucional, contendo "
                   "análise da arquitetura atual, gargalos identificados e "
                   "direcionamentos para aplicação de técnicas de engenharia de "
                   "dados por eixos do Plano Nacional de Cultura",
        "cobertura": {
            "1": {"tipo": "secao", "onde": "Descrição das atividades · Produto 2"},
            "2": {"tipo": "secao", "onde": "§ 3.2"},
            "3": {"tipo": "secao", "onde": "Meta 01 · Produto 2", "pagina": 17},
        },
    },
    {
        "meta": "02", "num": 1,
        "nome": "Relatório Informacional do PNC com painéis interativos",
        "redacao": "Relatório executivo acompanhado de painéis interativos para "
                   "monitoramento dos indicadores relevantes para o Plano Nacional "
                   "de Cultura, com visualizações consolidadas, filtros temáticos, "
                   "séries históricas e análises comparativas",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 4.1"},
            "3": {"tipo": "secao", "onde": "Meta 02 · Produto 1", "pagina": 24},
        },
    },
    {
        "meta": "02", "num": 2,
        "nome": "Arquitetura Técnica da Plataforma",
        "redacao": "Documento de arquitetura lógica, física e de segurança da "
                   "plataforma, incluindo fluxos de dados, camadas de "
                   "processamento, governança e integração",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 4.2"},
            "3": {"tipo": "secao", "onde": "Meta 02 · Produto 2", "pagina": 25},
        },
    },
    {
        "meta": "02", "num": 3,
        "nome": "Modelo Integrado de Dados",
        "redacao": "Especificação do modelo conceitual, lógico e físico dos dados "
                   "integrados, incluindo dicionário de dados e metadados",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 4.3"},
            "3": {"tipo": "secao", "onde": "Meta 02 · Produto 3", "pagina": 32},
        },
    },
    {
        "meta": "02", "num": 4,
        "nome": "Modelo de Governança de Dados",
        "redacao": "Documento com definição de papéis, responsabilidades, fluxos "
                   "decisórios, políticas de acesso e critérios de qualidade",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 4.4"},
            "3": {"tipo": "secao", "onde": "Meta 02 · Produto 4", "pagina": 42},
        },
    },
    {
        "meta": "02", "num": 5,
        "nome": "Repositório Público de Código-Fonte e Documentação",
        "redacao": "Repositório versionado contendo todo o código, documentação "
                   "técnica e exemplos de uso, sob licença aberta",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 4.5"},
            "3": {"tipo": "secao", "onde": "Meta 02 · Produto 5", "pagina": 44},
        },
    },
    {
        "meta": "03", "num": 1,
        "nome": "Motor de Governança e Autorização de Acesso a Dados",
        "redacao": "Componente funcional para controle de perfis, permissões, "
                   "auditoria, rastreabilidade e conformidade com LGPD e políticas "
                   "institucionais",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 03 · Produto 1", "pagina": 46},
        },
    },
    {
        "meta": "03", "num": 2,
        "nome": "Arquitetura de Referência da Solução",
        "redacao": "Documento técnico com visão lógica, física e de segurança da "
                   "arquitetura, incluindo fluxos de dados, agentes de IA, camadas "
                   "de governança e integração",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 03 · Produto 2", "pagina": 47},
        },
    },
    {
        "meta": "03", "num": 3,
        "nome": "Repositório Público de Código-Fonte",
        "redacao": "Repositório versionado contendo código, pipelines, modelos, "
                   "agentes de IA, scripts de implantação e exemplos de uso, sob "
                   "licença aberta",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 03 · Produto 3", "pagina": 48},
        },
    },
    {
        "meta": "03", "num": 4,
        "nome": "Oficinas de capacitação e transferência de tecnologia",
        "redacao": "Oficinas de capacitação e transferência de tecnologia para as "
                   "equipes do Ministério da Cultura",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 03 · Produto 4", "pagina": 52,
                  "nota": "O relatório declara as oficinas não executadas no "
                          "período."},
        },
    },
    {
        "meta": "04", "num": 1,
        "nome": "Conjunto de Agentes Especializados por Domínio",
        "redacao": "Agentes treinados para áreas temáticas específicas, com fontes "
                   "documentais validadas",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 5.1", "nota": "Em estágio de estudo."},
            "3": {"tipo": "secao", "onde": "Meta 04 · Produto 1", "pagina": 53},
        },
    },
    {
        "meta": "04", "num": 2,
        "nome": "Mecanismo de Geração Automática de Indicadores e Métricas",
        "redacao": "Serviço para extração, consolidação e cálculo de indicadores a "
                   "partir de textos, relatórios e documentos institucionais",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 04 · Produto 2", "pagina": 56},
        },
    },
    {
        "meta": "04", "num": 3,
        "nome": "Documentação Técnica e Metodológica",
        "redacao": "Guias de arquitetura, uso, manutenção, evolução e replicação da "
                   "solução em outros contextos institucionais, incluindo "
                   "documentação do agente de IA, oficinas de capacitação e "
                   "publicação de um livro",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 04 · Produto 3", "pagina": 57},
        },
    },
    {
        "meta": "05", "num": 1,
        "nome": "Integrações com ferramentas livres de governança",
        "redacao": "Documentação técnica e código-fonte das integrações com "
                   "ferramentas livres de governança e publicação de dados abertos",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 6.1"},
            "3": {"tipo": "secao", "onde": "Meta 05 · Produto 1", "pagina": 59},
        },
    },
    {
        "meta": "05", "num": 2,
        "nome": "Oficina sobre governança de dados descentralizada",
        "redacao": "Oficina sobre governança de dados descentralizada",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 6.2"},
            "3": {"tipo": "secao", "onde": "Meta 05 · Produto 2", "pagina": 60},
        },
    },
    {
        "meta": "05", "num": 3,
        "nome": "Datathon para formulação dos indicadores do PNC",
        "redacao": "Atividade colaborativa e intensiva com diferentes instituições "
                   "especialistas em dados culturais para contribuição nos "
                   "indicadores associados a cada meta",
        "cobertura": {
            "1": {"tipo": "mencao",
                  "onde": "Anexos 2 e 3, sob a Meta 01 · Produto 1"},
            "2": {"tipo": "mencao", "onde": "§ 6.2 e Anexo III"},
            "3": {"tipo": "secao", "onde": "Meta 05 · Produto 3", "pagina": 61},
        },
    },
    {
        "meta": "05", "num": 4,
        "nome": "Documento analítico do processo de modelagem",
        "redacao": "Construção estruturada de um arranjo normativo, institucional e "
                   "operacional do SNIIC",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 6.3"},
            "3": {"tipo": "secao", "onde": "Meta 05 · Produto 4", "pagina": 64},
        },
    },
    {
        "meta": "06", "num": 1,
        "nome": "Repositório Digital Brasiliana Cultura",
        "redacao": "Catálogo integrado de todos os acervos culturais do sistema MinC",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 06 · Produto 1", "pagina": 66},
        },
    },
]

# (meta, produto) -> estado de entrega do produto.
#
# PREENCHER À MÃO. Quem responde pelo TED assina o estado; o painel não o
# deduz. Um produto pode ter todos os seus artefatos entregues e ainda assim
# não estar entregue, porque o produto é mais que a soma das peças — e a
# maioria dos produtos não tem artefato algum no quadro.
#
# Valores aceitos:
#   "Entregue"     o produto inteiro foi contemplado
#   "Em andamento" começou e não terminou
#   "Previsto"     ainda não começou
#   ""             ainda não classificado; a página mostra "a classificar"
#
# Enquanto houver linha vazia a página segue no ar e a validação passa: falta
# de classificação é estado legítimo, e não erro de acervo.
ESTADO = {
    ("01", 1): "",
    ("01", 2): "",
    ("02", 1): "",
    ("02", 2): "",
    ("02", 3): "",
    ("02", 4): "",
    ("02", 5): "",
    ("03", 1): "",
    ("03", 2): "",
    ("03", 3): "",
    ("03", 4): "",
    ("04", 1): "",
    ("04", 2): "",
    ("04", 3): "",
    ("05", 1): "",
    ("05", 2): "",
    ("05", 3): "",
    ("05", 4): "",
    ("06", 1): "",
}

ESTADOS_ACEITOS = ("Entregue", "Em andamento", "Previsto", "")


# artefato do quadro de acompanhamento -> (meta, produto, evidência, nota)
#
# "TED": o artefato é nomeado na redação do produto.
# "R3":  o vínculo vem do lugar em que o 3º Relatório documenta o artefato.
ARTEFATO_PRODUTO = {
    "Catálogo de fontes de dados": ("01", 2, "R3", ""),
    "Arquitetura lógica": ("02", 2, "TED", ""),
    "Arquitetura física": ("02", 2, "TED", ""),
    "Arquitetura de segurança": ("02", 2, "TED", ""),
    "Diagramas dos fluxos de dados": ("02", 2, "TED", ""),
    "Modelo conceitual, lógico e físico": ("02", 3, "TED", ""),
    "Dicionário de dados": ("02", 3, "TED", ""),
    "Metadados": ("02", 3, "TED", ""),
    "Matriz de papéis e responsabilidades": ("02", 4, "TED", ""),
    "Políticas de acesso": ("02", 4, "TED", ""),
    "Critérios de qualidade dos dados": ("02", 4, "TED", ""),
    "Evidências de testes e validação": ("02", 4, "R3", ""),
    "Documentação dos pipelines": ("02", 5, "R3", ""),
    "Exemplos de uso": ("02", 5, "TED", ""),
    "Scripts de implantação": ("03", 3, "TED", ""),
    "Procedimentos de implantação": ("03", 3, "R3", ""),
    "Relação de componentes e versões": ("03", 3, "R3", ""),
    "Manual de uso": ("04", 3, "TED", ""),
    "Manual de manutenção": ("04", 3, "TED", ""),
    "Manual de evolução": ("04", 3, "TED",
                           "O 3º Relatório o documenta sob a Meta 03 · Produto 3."),
}


# (meta, produto) -> o que o produto entregou no período.
#
# Transcrito da seção correspondente do 3º Relatório Parcial, em uma frase.
# A página consta da cobertura do produto; quem quiser conferir vai direto a
# ela. Nenhuma linha afirma coisa que o relatório não diga.
BALANCO = {
    ("01", 1): "Vinte e dois encontros de trabalho por eixo do Plano, com o "
               "Ministério e a equipe de pesquisa, cumprindo a escuta "
               "qualificada prevista. Seis dos oito eixos percorridos.",
    ("01", 2): "Catálogo de fontes de dados, levantamento a partir do código, "
               "arquitetura comum de ingestão e visão consolidada das fontes, "
               "com ênfase no Eixo 2, que inaugurou a integração.",
    ("02", 1): "Camada semântica sobre as tabelas de consumo, com doze métricas "
               "nomeadas. Os painéis propriamente ditos aguardam a reunião de "
               "requisitos com o Ministério.",
    ("02", 2): "Os três níveis: arquitetura lógica em operação (Figuras 1 e 2), "
               "física proposta (Figura 3) e de segurança, somadas aos fluxos "
               "de dados do Anexo III.",
    ("02", 3): "Modelo conceitual, lógico e físico do Eixo 2, dicionário de "
               "dados e metadados. Especificação completa no Anexo IV.",
    ("02", 4): "Critérios de qualidade convertidos em testes automáticos em "
               "cinco dimensões, com 858 verificações inventariadas. Papéis, "
               "responsabilidades e políticas de acesso seguem em elaboração.",
    ("02", 5): "Repositório público sob licença MIT, com ficha técnica de treze "
               "das dezesseis rotinas em operação e os exemplos de uso do "
               "Anexo VI.",
    ("03", 1): "Especificado na arquitetura de segurança do Produto 2 da Meta "
               "02, e não implantado: o motor pressupõe fronteira "
               "administrativa única, que o ambiente de produção ainda não "
               "oferece.",
    ("03", 2): "Atendido pelo conjunto do Produto 2 da Meta 02 — os três níveis "
               "de arquitetura — somado aos fluxos de dados derivados da "
               "linhagem dos modelos.",
    ("03", 3): "Repositório público sob licença MIT, com os scripts e "
               "procedimentos de implantação do Anexo VIII e o manual de "
               "evolução do Anexo IX.",
    ("03", 4): "Nenhuma oficina realizada no período. A atividade segue "
               "prevista, apoiada nos documentos de implantação e de evolução "
               "do Produto 3.",
    ("04", 1): "Agente de domínio operando de ponta a ponta desde agosto de "
               "2026, com recuperação por busca híbrida sobre base vetorial, "
               "fundida por posto recíproco.",
    ("04", 2): "Camada de entrega em quatro estágios: uma pergunta em português "
               "produz as bases consultadas, a consulta, o gráfico, a "
               "explicação e o relatório.",
    ("04", 3): "Dezesseis decisões de arquitetura registradas entre 21 de julho "
               "e 19 de agosto, planejamento datado, suíte de testes e ambiente "
               "de avaliação versionado. Visão geral no Anexo X.",
    ("05", 1): "OpenMetadata adotado como catálogo institucional, alimentado "
               "por declaração versionada do projeto de transformação. "
               "Integração implantada e em operação.",
    ("05", 2): "Oficina realizada em junho de 2026 junto à STII do Ministério, "
               "sobre o motor de consulta distribuído e o componente de "
               "governança e autorização de acesso.",
    ("05", 3): "Planejamento, produção e mobilização do evento: dois dias em "
               "Brasília, oito oficinas preparatórias — uma por eixo — e grupos "
               "de trabalho por eixo. Detalhamento no Anexo XI.",
    ("05", 4): "Proposta de estrutura construída em reuniões da equipe da "
               "Universidade, alinhamentos com o Ministério e contribuições do "
               "Comitê Gestor do SNIIC.",
    ("06", 1): "Diagnóstico da gestão da informação dos acervos das seis "
               "instituições do sistema MinC e estudo comparativo de "
               "vocabulários. Portal em construção; coleta ainda por iniciar.",
}

# risco (pelo início do texto) -> (meta, produto) que ele ameaça.
RISCO_PRODUTO = {
    "Inexistência de infraestrutura de produção": ("03", 1),
    "Documentação de coluna do SALIC parcial": ("02", 3),
    "Definição dos painéis condicionada": ("02", 1),
    "Cadeia do BB Ágil": ("02", 3),
    "Sincronização manual entre a plataforma": ("05", 1),
    "Meta 06": ("06", 1),
    "Custos, prazos e logística": ("05", 3),
}


def produto_do_risco(texto):
    """(meta, produto) do risco, ou None se a tabela não o classifica."""
    for chave, alvo in RISCO_PRODUTO.items():
        if texto.startswith(chave):
            return alvo
    return None


def monta(artefatos, riscos=None):
    """Devolve os blocos `relatorios` e `produtos` do acervo.

    Cada produto recebe os artefatos do quadro que o compõem, com a situação
    apurada no relatório mais recente, e o estado de entrega do produto.
    """
    por_produto = {}
    for a in artefatos:
        vinculo = ARTEFATO_PRODUTO.get(a["nome"])
        if not vinculo:
            continue
        meta, num, evidencia, nota = vinculo
        por_produto.setdefault((meta, num), []).append({
            "nome": a["nome"],
            "situacao": a["agora"],
            "evidencia": evidencia,
            "nota": nota,
        })

    produtos = []
    for p in PRODUTOS:
        produtos.append({
            **p,
            "meta_nome": METAS_TED[p["meta"]],
            "balanco": BALANCO[(p["meta"], p["num"])],
            "estado": ESTADO.get((p["meta"], p["num"]), ""),
            "artefatos": por_produto.get((p["meta"], p["num"]), []),
        })

    # Cada risco ganha o produto que ameaça, para que a seção de riscos leia
    # na mesma chave do resto da página.
    for r in riscos or []:
        alvo = produto_do_risco(r["risco"])
        if alvo:
            r["meta"], r["produto"] = alvo
            r["produto_nome"] = next(
                p["nome"] for p in PRODUTOS
                if p["meta"] == alvo[0] and p["num"] == alvo[1]
            )

    return RELATORIOS, produtos


def estados_invalidos():
    """Chaves de ESTADO com valor fora da lista, ou produto sem linha."""
    problemas = []
    for p in PRODUTOS:
        chave = (p["meta"], p["num"])
        if chave not in ESTADO:
            problemas.append(f"Meta {p['meta']} · Produto {p['num']} sem linha")
        elif ESTADO[chave] not in ESTADOS_ACEITOS:
            problemas.append(
                f"Meta {p['meta']} · Produto {p['num']}: {ESTADO[chave]!r}"
            )
    return problemas


def sem_produto(riscos):
    """Riscos que a tabela não classifica."""
    return [r["risco"] for r in riscos if not produto_do_risco(r["risco"])]


def sem_vinculo(artefatos):
    """Artefatos do quadro que a tabela não vincula a produto algum."""
    return [a["nome"] for a in artefatos if a["nome"] not in ARTEFATO_PRODUTO]

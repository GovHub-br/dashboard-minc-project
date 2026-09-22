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

ARTEFATO_PRODUTO  a que produto pertence cada um dos 20 artefatos do quadro de
                acompanhamento. A evidência é "TED" quando o artefato é
                nomeado na redação do produto, e "R3" quando o vínculo vem do
                lugar em que o 3º Relatório o documenta. Como o QUEM_DESTRAVA
                do extrai.py, a classificação "R3" é do painel, não do
                documento — e está marcada como tal na página.

Importado por extrai.py. Não roda sozinho.
"""

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


def monta(artefatos):
    """Devolve os blocos `relatorios` e `produtos` do acervo.

    Cada produto recebe a lista dos artefatos do quadro que lhe pertencem, com
    a situação apurada no relatório mais recente.
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
            "artefatos": por_produto.get((p["meta"], p["num"]), []),
        })

    return RELATORIOS, produtos


def sem_vinculo(artefatos):
    """Artefatos do quadro que a tabela não vincula a produto algum."""
    return [a["nome"] for a in artefatos if a["nome"] not in ARTEFATO_PRODUTO]

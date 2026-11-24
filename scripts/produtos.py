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
    {
        "num": 4,
        "rotulo": "4º Relatório",
        "data": "2026-11-03",
        "periodo": "setembro a novembro de 2026",
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
            "4": {"tipo": "secao", "onde": "Meta 01 · Produto 1", "pagina": 9},
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
            "4": {"tipo": "secao", "onde": "Meta 01 · Produto 2", "pagina": 11},
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
            "4": {"tipo": "secao", "onde": "Meta 02 · Produto 1", "pagina": 16},
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
            "4": {"tipo": "secao", "onde": "Meta 02 · Produto 2", "pagina": 17},
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
            "4": {"tipo": "secao", "onde": "Meta 02 · Produto 3", "pagina": 20},
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
            "4": {"tipo": "secao", "onde": "Meta 02 · Produto 4", "pagina": 21},
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
            "4": {"tipo": "secao", "onde": "Meta 02 · Produto 5", "pagina": 23},
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
            "4": {"tipo": "secao", "onde": "Meta 03 · Produto 1", "pagina": 25},
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
            "4": {"tipo": "secao", "onde": "Meta 03 · Produto 2", "pagina": 26},
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
            "4": {"tipo": "secao", "onde": "Meta 03 · Produto 3", "pagina": 26},
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
            "4": {"tipo": "secao", "onde": "Meta 03 · Produto 4", "pagina": 27},
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
            "4": {"tipo": "secao", "onde": "Meta 04 · Produto 1", "pagina": 28},
        },
    },
    {
        "meta": "04", "num": 2,
        "nome": "Mecanismo de Geração Automática de Indicadores e Métricas",
        "redacao": "Serviço para extração, consolidação e cálculo de indicadores a "
                   "partir de textos, relatórios e documentos institucionais",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 04 · Produto 2", "pagina": 56},
            "4": {"tipo": "secao", "onde": "Meta 04 · Produto 2", "pagina": 28},
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
            "4": {"tipo": "secao", "onde": "Meta 04 · Produto 3", "pagina": 29},
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
            "4": {"tipo": "secao", "onde": "Meta 05 · Produto 1", "pagina": 30},
        },
    },
    {
        "meta": "05", "num": 2,
        "nome": "Oficina sobre governança de dados descentralizada",
        "redacao": "Oficina sobre governança de dados descentralizada",
        "cobertura": {
            "2": {"tipo": "secao", "onde": "§ 6.2"},
            "3": {"tipo": "secao", "onde": "Meta 05 · Produto 2", "pagina": 60},
            "4": {"tipo": "secao", "onde": "Meta 05 · Produto 2", "pagina": 31},
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
            "4": {"tipo": "secao", "onde": "Meta 05 · Produto 3", "pagina": 32},
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
            "4": {"tipo": "secao", "onde": "Meta 05 · Produto 4", "pagina": 33},
        },
    },
    {
        "meta": "06", "num": 1,
        "nome": "Repositório Digital Brasiliana Cultura",
        "redacao": "Catálogo integrado de todos os acervos culturais do sistema MinC",
        "cobertura": {
            "3": {"tipo": "secao", "onde": "Meta 06 · Produto 1", "pagina": 66},
            "4": {"tipo": "secao", "onde": "Meta 06 · Produto 1", "pagina": 35},
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
#
# Classificado por Luiza Maluf em 22/09/2026 sobre o 3º Relatório Parcial e
# reclassificado em 24/11/2026 sobre o 4º, produto a produto, conforme a
# situação que o 4º Relatório declara. A reclassificação acompanha cada novo
# relatório.
ESTADO = {
    ("01", 1): "Entregue",
    ("01", 2): "Entregue",
    ("02", 1): "Em andamento",
    ("02", 2): "Entregue",
    ("02", 3): "Entregue",
    ("02", 4): "Em andamento",
    ("02", 5): "Em andamento",
    ("03", 1): "Em andamento",
    ("03", 2): "Entregue",
    ("03", 3): "Em andamento",
    ("03", 4): "Previsto",
    ("04", 1): "Em andamento",
    ("04", 2): "Em andamento",
    ("04", 3): "Em andamento",
    ("05", 1): "Em andamento",
    ("05", 2): "Em andamento",
    ("05", 3): "Entregue",
    ("05", 4): "Em andamento",
    ("06", 1): "Em andamento",
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


# (meta, produto) -> o que o produto entregou até aqui.
#
# Transcrito da situação que o 4º Relatório Parcial declara para o produto
# (Quadro 1 e seção correspondente). A página consta da cobertura do produto;
# quem quiser conferir vai direto a ela. Nenhuma linha afirma coisa que o
# relatório não diga.
BALANCO = {
    ("01", 1): "Escuta concluída nos oito eixos do Plano: 14 encontros de "
               "trabalho em setembro e outubro, além do Datathon do PNC (9 e "
               "10/09). A sistematização dos resultados está no Anexo II "
               "(Sistematização das Escutas por Eixo).",
    ("01", 2): "Relatório concluído, com a arquitetura atual, os gargalos, as "
               "fontes e o diagnóstico por eixo do PNC, no Anexo III. O "
               "catálogo das fontes presentes no Data Lakehouse, segunda "
               "versão, está no Anexo V.",
    ("02", 1): "Painéis ainda não construídos. Definido que a visualização "
               "usará a mesma estrutura de gráficos da versão digital do "
               "Cultura em Números, tendo o portal em Plone como face pública. "
               "Os requisitos (eixos, indicadores e ordem de publicação) "
               "dependem de definição com o Ministério.",
    ("02", 2): "Arquitetura de referência do Data Lakehouse aprovada pelo "
               "Ministério em outubro e documentada no Anexo I. A plataforma "
               "em funcionamento está em transição: Trino e Ranger implantados "
               "desde junho de 2026; Iceberg e Polaris pendentes.",
    ("02", 3): "Entregue: modelo conceitual, lógico e físico (Anexo IV), "
               "dicionário de dados (Anexo VII) e catálogo de metadados (Anexo "
               "VIII), refeitos para a arquitetura final. O projeto de "
               "transformação soma 730 modelos.",
    ("02", 4): "Em andamento, com sugestão de repactuação do prazo para março "
               "de 2027. Critérios de qualidade entregues; matriz de papéis, "
               "Registro de Atividades de Tratamento (ROPA), relatório de "
               "testes e RIPD preliminar em elaboração.",
    ("02", 5): "Repositório público, sob licença MIT, com site de "
               "documentação, 279 alterações e 88 propostas aprovadas entre "
               "setembro e outubro. Faltam marcar a versão de entrega, "
               "verificar o histórico em busca de senhas esquecidas e produzir "
               "o inventário de componentes.",
    ("03", 1): "Ranger e Trino implantados no ambiente do Ministério desde "
               "19/06/2026; o Ranger anonimiza na consulta, e as políticas "
               "serão refinadas com os perfis de usuários do Ministério.",
    ("03", 2): "Concluído: arquitetura de referência documentada no Anexo I, "
               "com as decisões registradas nos ADRs 0009 a 0012 e 0014 a 0017 "
               "do repositório público.",
    ("03", 3): "Scripts de implantação e manual de evolução entregues no 3º "
               "Relatório. Faltam atualizá-los para a arquitetura final, "
               "marcar a versão de entrega e verificar o histórico do "
               "repositório.",
    ("03", 4): "Não iniciadas; previstas no cronograma para os meses 11 e 12 "
               "do TED (início de 2027), com datas e formato a definir com o "
               "Ministério.",
    ("04", 1): "TAIS em operação sobre os dados do Ministério e usado no "
               "Datathon do PNC (9 e 10/09/2026). Faltam ajustes e a "
               "integração das demais bases.",
    ("04", 2): "Modo Indicador do TAIS: responde com as bases usadas, a "
               "consulta, a leitura do resultado, um gráfico e um relatório "
               "editável; regras de recusa e mascaramento de dados sensíveis "
               "em setembro e adaptação aos dados do Ministério em 20/10/2026. "
               "Faltam ajustes e a integração das demais bases.",
    ("04", 3): "Documentação técnica do agente no repositório público do TAIS, "
               "com os ADRs 0016 a 0019 e página do MinC. Guias, oficinas e "
               "livro começam no mês 9 (25/11/2026).",
    ("05", 1): "Catálogo institucional (OpenMetadata) em operação, com carga "
               "agendada no Airflow e sugestões de descrição feitas no próprio "
               "catálogo, que viram propostas de alteração revisadas pela "
               "equipe. Publicação de dados abertos não iniciada.",
    ("05", 2): "Em preparação; ainda não realizada (prazo no mês 11 do TED). "
               "Os insumos são a Instrução Normativa do Data Lakehouse, em "
               "elaboração pela SGE, e o documento de modelagem do SNIIC.",
    ("05", 3): "Entregue: realizado em 9 e 10/09/2026, no espaço cultural do "
               "TCU, com 104 participantes de 35 organizações; relatório no "
               "Anexo IX.",
    ("05", 4): "Em elaboração; modelagem do SNIIC construída em reuniões com a "
               "SGE desde abril de 2026.",
    ("06", 1): "Tainacan Agregador em operação; piloto com a Brasiliana Museus "
               "(IBRAM) em coleta desde 28/10/2026, com cerca de 2.400 dos "
               "74.121 itens já agregados em 1º/11. Demais repositórios a "
               "cadastrar.",
}

def monta(artefatos):
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


def sem_vinculo(artefatos):
    """Artefatos do quadro que a tabela não vincula a produto algum."""
    return [a["nome"] for a in artefatos if a["nome"] not in ARTEFATO_PRODUTO]

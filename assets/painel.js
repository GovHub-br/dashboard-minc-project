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

/* O quadro de acompanhamento chama "artefato" o que o Termo chama entrega.
   O painel usa a palavra do Termo — ver scripts/produtos.py. */

/* Todo texto vindo do acervo passa por aqui antes de virar HTML. O extrator já
   remove marcação, mas o painel não depende disso: o acervo é editado à mão a
   cada relatório. */
function escapaHtml(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

function contaSituacoes(entregas, coluna = 'agora') {
  const contagem = {};
  for (const a of entregas) {
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

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
  'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

function dataPorExtenso(iso) {
  const [ano, mes, dia] = iso.split('-');
  return `${Number(dia)} de ${MESES[Number(mes) - 1]} de ${ano}`;
}

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

/* ----------------------------------------------------------- indicadores */

function montaIndicadores(acervo) {
  const contagem = contaSituacoes(acervo.entregas);
  const grade = document.getElementById('grade-indicadores');

  const cartoes = [
    { numero: acervo.entregas.length, rotulo: 'entregas acompanhadas', classe: '' },
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

/* -------------------------------------------------------------- evolução */

/* O quadro anterior marcava três entregas como "Falta artefato". O relatório
   as agrega em "Não entregue", chegando a 14. O painel faz o mesmo, e a nota
   registra a agregação. */
function contaAntesAgregado(entregas) {
  const contagem = contaSituacoes(entregas, 'antes');
  const falta = contagem['Falta artefato'] || 0;
  if (falta) {
    contagem['Não entregue'] = (contagem['Não entregue'] || 0) + falta;
    delete contagem['Falta artefato'];
  }
  return contagem;
}

function montaEvolucao(acervo) {
  const antes = contaAntesAgregado(acervo.entregas);
  const agora = contaSituacoes(acervo.entregas);

  const series = SITUACOES.map((s) => ({
    situacao: s,
    antes: antes[s] || 0,
    agora: agora[s] || 0,
    classe: classeDe(s),
  }));

  const alvo = document.getElementById('grafico-evolucao');
  alvo.innerHTML = `
    <p class="secao-intro">
      Como a situação das 20 entregas mudou do 2º para o 3º Relatório Parcial.
      Cada linha é uma situação: a barra de cima conta quantas entregas estavam
      nela no 2º relatório, a de baixo quantas estão nela agora.
    </p>
    <div id="svg-evolucao"></div>
    <div class="nota">
      <p>
        <strong>O que explica a mudança.</strong> Menos trabalho novo que
        <strong>publicação</strong>: parte do que a avaliação anterior não
        localizou existia como código, e não como documento. O período foi
        dedicado a derivar documentos do próprio repositório, de modo que cada
        afirmação pudesse ser conferida na fonte.
      </p>
      <p>
        <strong>Por que 14 não entregues no 2º relatório.</strong> São os
        ${(antes['Não entregue'] || 0) - 3} assim marcados mais os três com a
        marcação <em>falta apresentar artefato</em>, que o próprio documento
        agrega no mesmo grupo.
      </p>
      <p>
        <strong>Por que 11 entregues, e não 12.</strong> O texto do 3º Relatório
        declara 12 entregues e 6 parciais. A conferência item a item do quadro dá
        ${agora['Entregue']} entregues, ${agora['Entregue como proposta']} entregues
        como proposta e ${agora['Parcial']} parciais — as mesmas 20 entregas, nas
        mesmas situações. A diferença é que o painel conta à parte as arquiteturas
        que estão propostas, para não dar por operante o que ainda está projetado.
      </p>
    </div>`;

  desenhaEvolucao('#svg-evolucao', series);
}

/* -------------------------------------------------------------- produtos */

/* Os 19 produtos pactuados no Termo, meta a meta, com a cobertura em cada
   relatório. A cobertura vem do sumário de cada relatório: "secao" quando o
   produto tem seção própria, "mencao" quando foi tratado sob outro produto. */

const MARCAS = {
  secao: { glifo: '●', classe: 'marca-secao', diz: 'seção própria' },
  mencao: { glifo: '○', classe: 'marca-mencao', diz: 'tratado sob outro produto' },
};

function celulaCobertura(produto, num) {
  const c = produto.cobertura[String(num)];
  if (!c) {
    return '<td class="marca"><span class="marca-ausente" '
      + 'aria-label="não tratado">–</span></td>';
  }
  const m = MARCAS[c.tipo];
  const onde = c.pagina ? `${c.onde} · p. ${c.pagina}` : c.onde;
  const titulo = escapaHtml(`${m.diz} — ${onde}${c.nota ? ' · ' + c.nota : ''}`);
  return `<td class="marca"><span class="${m.classe}" title="${titulo}" `
    + `aria-label="${titulo}">${m.glifo}</span></td>`;
}

function etiquetasEntregas(produto) {
  if (!produto.entregas.length) {
    return '<span class="sem-entrega">nenhuma no quadro</span>';
  }
  return produto.entregas.map((a) => {
    const titulo = escapaHtml(
      a.situacao
      + (a.evidencia === 'TED'
        ? ' · nomeado na redação do produto no TED'
        : ' · vínculo derivado do 3º Relatório')
      + (a.nota ? ' · ' + a.nota : '')
    );
    return `<span class="entrega-pil ${classeDe(a.situacao)}" title="${titulo}">`
      + `${escapaHtml(a.nome)}</span>`;
  }).join('');
}

function montaProdutos(acervo) {
  const alvo = document.getElementById('matriz-produtos');
  const rels = acervo.relatorios;

  const tratados = (r) => acervo.produtos
    .filter((p) => p.cobertura[String(r.num)]).length;

  /* Os três números não somam: são os mesmos 19 produtos, e cada relatório
     alcança mais deles que o anterior. O rótulo diz isso. */
  const resumo = rels.map((r) => `
    <div class="indicador">
      <div class="numero">${tratados(r)}<span class="de">de ${acervo.produtos.length}</span></div>
      <div class="rotulo">produtos tratados no ${r.rotulo.toLowerCase()}<br>
        <span class="periodo">${escapaHtml(r.periodo)}</span></div>
    </div>
  `).join('');

  const metas = [...new Set(acervo.produtos.map((p) => p.meta))];

  const quadros = metas.map((num) => {
    const daMeta = acervo.produtos.filter((p) => p.meta === num);
    const linhas = daMeta.map((p) => `
      <tr>
        <td class="nome-produto">
          <strong>Produto ${p.num}</strong> ${escapaHtml(p.nome)}
          ${p.redacao === p.nome ? ''
            : `<span class="redacao">${escapaHtml(p.redacao)}.</span>`}
        </td>
        <td class="balanco-produto">${ligaDocumentos(p.balanco, acervo)}</td>
        ${rels.map((r) => celulaCobertura(p, r.num)).join('')}
        <td class="entregas-do-produto">${etiquetasEntregas(p)}</td>
      </tr>
    `).join('');

    return `
      <article class="quadro-meta">
        <h3><span class="numero-meta">Meta ${num}</span>${escapaHtml(daMeta[0].meta_nome)}</h3>
        <div class="rolagem">
          <table class="quadro quadro-produtos">
            <thead>
              <tr>
                <th>Produto pactuado</th>
                <th>O que foi entregue até aqui</th>
                ${rels.map((r) => `<th class="col-rel" scope="col"
                  title="${escapaHtml(`${r.rotulo} · ${r.periodo}`)}">${r.num}º</th>`).join('')}
                <th>Entregas do quadro</th>
              </tr>
            </thead>
            <tbody>${linhas}</tbody>
          </table>
        </div>
      </article>`;
  }).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${acervo.produtos.length} produtos pactuados no Termo, meta a meta: o que
      cada um entregou até aqui, em que relatório foi tratado e quais entregas do
      quadro de acompanhamento lhe pertencem.
    </p>
    <div class="indicadores indicadores-3">${resumo}</div>
    <p class="legenda-marcas">
      <span class="marca-secao">●</span> seção própria no relatório ·
      <span class="marca-mencao">○</span> tratado sob outro produto ·
      <span class="marca-ausente">–</span> não tratado.
      Cada marca guarda a seção e a página; o cursor as revela.
    </p>
    ${quadros}
    <div class="nota">
      <p>
        <strong>O que a marca diz, e o que não diz.</strong> A cobertura vem do
        sumário de cada relatório: diz onde o assunto foi tratado, não que o
        produto esteja concluído. Quem responde pela conclusão é a coluna do que
        foi entregue, e as etiquetas ao lado.
      </p>
      <p>
        <strong>De onde vem o texto da coluna.</strong> Da seção correspondente
        do 3º Relatório, uma frase por produto. A página está na marca do 3º
        relatório, para conferência.
      </p>
      <p>
        <strong>Sobre o vínculo das entregas.</strong> Cada entrega do quadro é
        ligada ao produto que a nomeia na redação do Termo. Onde o Termo não a
        nomeia, o vínculo vem do lugar em que o 3º Relatório a documenta, e a
        classificação é do painel, não do documento — a etiqueta registra qual dos
        dois casos é.
      </p>
      <p>
        O 1º Relatório trata apenas da Meta 01, e o quadro de acompanhamento só
        começa a ser apurado no 2º. Por isso a situação de cada entrega tem dois
        pontos no tempo, e a cobertura dos produtos tem três.
      </p>
    </div>`;
}

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

/* -------------------------------------------------------------- entregas */

/* Textos do acervo citam documentos pelo nome do arquivo. Onde o nome consta
   da relação de documentos publicados, vira link para o repositório; onde não
   consta — poetry.lock, por exemplo —, fica só marcado como código. */
function ligaDocumentos(texto, acervo) {
  const porArquivo = new Map(
    (acervo.documentos || []).map((d) => [d.arquivo, d.url])
  );
  return escapaHtml(texto).replace(
    /([\w-]+\.(?:pdf|md|json|yml|lock))/g,
    (arquivo) => {
      const url = porArquivo.get(arquivo);
      return url
        ? `<a class="doc" href="${escapaHtml(url)}" target="_blank"
             rel="noopener">${arquivo}</a>`
        : `<code>${arquivo}</code>`;
    }
  );
}

function montaEntregas(acervo) {
  const alvo = document.getElementById('quadro-entregas');
  let filtro = 'Todos';

  const opcoes = ['Todos', ...SITUACOES];

  function linhas() {
    const visiveis = filtro === 'Todos'
      ? acervo.entregas
      : acervo.entregas.filter((a) => a.agora === filtro);

    if (!visiveis.length) {
      return '<tr><td colspan="4" class="vazio">Nenhuma entrega nesta situação.</td></tr>';
    }

    return visiveis.map((a) => `
      <tr>
        <td class="nome-entrega">${escapaHtml(a.nome)}</td>
        <td>${escapaHtml(a.antes)}</td>
        <td><span class="etiqueta ${classeDe(a.agora)}">${escapaHtml(a.agora)}</span></td>
        <td class="onde">${a.onde ? ligaDocumentos(a.onde, acervo) : '—'}</td>
      </tr>
    `).join('');
  }

  function desenha() {
    alvo.innerHTML = `
      <p class="secao-intro">
        As ${acervo.entregas.length} entregas do quadro de acompanhamento, com a
        situação anterior, a atual e a localização de cada uma. Nomes de arquivo
        levam ao documento no repositório da plataforma.
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
            <tr><th>Entrega</th><th>2º Relatório</th><th>3º Relatório</th><th>Onde está</th></tr>
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
            ${escapaHtml(p.entrega)}
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
      O 3º Relatório encerra cada meta com os compromissos que ela assume para o
      período seguinte. São ${total} encaminhamentos, reunidos aqui meta a meta,
      seguidos das ${acervo.pendencias.length} entregas que seguem pendentes e do
      que destrava cada uma.
    </p>
    <span class="janela">${escapaHtml(acervo.origem.proximo_periodo)}</span>
    ${trilhas}
    <h3 class="subtitulo-secao">O que está pendente, e o que destrava</h3>
    <p class="secao-intro">
      ${naoSoUnb} das ${acervo.pendencias.length} pendências dependem de decisão
      ou de infraestrutura do Ministério, isoladamente ou em conjunto com a
      Universidade. As ${soUnb} restantes são de execução da equipe da UnB.
    </p>
    ${blocos}`;
}

/* ---------------------------------------------------------------- riscos */

function montaRiscos(acervo) {
  const alvo = document.getElementById('matriz-riscos');

  const lista = acervo.riscos.map((r, i) => `
    <article class="risco">
      <div class="indice">${i + 1}</div>
      <div>
        ${r.produto_nome ? `
          <a class="alvo-risco" href="#produtos">
            <span class="numero-meta">Meta ${escapaHtml(r.meta)}</span>
            Produto ${r.produto} · ${escapaHtml(r.produto_nome)}
          </a>` : ''}
        <div class="texto-risco">${escapaHtml(r.risco)}</div>
        <div class="grau">
          Probabilidade ${escapaHtml(r.probabilidade.toLowerCase())} ·
          impacto ${escapaHtml(r.impacto.toLowerCase())}
        </div>
        <div class="mitigacao">
          <strong>Medida mitigadora:</strong> ${ligaDocumentos(r.mitigacao, acervo)}
        </div>
      </div>
    </article>
  `).join('');

  const porMeta = new Set(acervo.riscos.map((r) => r.meta).filter(Boolean));

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${acervo.riscos.length} riscos identificados no período, cada um com o
      produto que ameaça e a medida mitigadora em andamento. Concentram-se em
      ${porMeta.size} das seis metas.
    </p>
    <div class="painel-riscos">
      <div id="svg-riscos"></div>
      <div>${lista}</div>
    </div>
    <div class="nota">
      <p>
        <strong>Sobre a ligação com o produto.</strong> O relatório lista os
        riscos sem vinculá-los a produto. A ligação é do painel, pelo assunto do
        risco e da sua medida mitigadora, para que a leitura siga a mesma chave
        do resto da página.
      </p>
    </div>`;

  desenhaRiscos('#svg-riscos', acervo.riscos);
}

/* ------------------------------------------------------------ documentos */

function montaDocumentos(acervo) {
  const alvo = document.getElementById('lista-documentos');

  const cartoes = acervo.documentos.map((d) => `
    <a class="documento" href="${escapaHtml(d.url)}" target="_blank" rel="noopener">
      <code>${escapaHtml(d.arquivo)}</code>
      <span class="anexo">${escapaHtml(d.anexo)}</span>
    </a>
  `).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      Os ${acervo.documentos.length} documentos técnicos produzidos, versionados
      no repositório público da plataforma — clique para abrir. Todos são gerados
      a partir do código, e não redigidos sobre ele: divergência entre documento e
      plataforma é detectável, e corrigível na fonte.
    </p>
    <div class="grade-documentos">${cartoes}</div>`;
}

/* ------------------------------------------------------------- inicialização */

async function inicia() {
  try {
    const acervo = await carrega();
    montaCabecalho(acervo);
    montaProdutos(acervo);
    montaIndicadores(acervo);
    montaMetas(acervo);
    montaEvolucao(acervo);
    montaEntregas(acervo);
    montaCronograma(acervo);
    montaRiscos(acervo);
    montaDocumentos(acervo);
  } catch (erro) {
    console.error(erro);
    document.getElementById('grade-indicadores').innerHTML =
      `<p>Não foi possível carregar os dados do painel. ` +
      `Se estiver abrindo o arquivo direto do disco, sirva o diretório com ` +
      `<code>python3 -m http.server</code>.</p>`;
  }
}

document.addEventListener('DOMContentLoaded', inicia);

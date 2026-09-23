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

/* O que cada situação do quadro quer dizer. "Entregue como proposta" é a que
   mais gera dúvida, e a definição vem do próprio 3º Relatório: descreve o
   estado-alvo pactuado, e não ambiente em operação. */
const DEFINICOES = {
  'Entregue': 'O artefato existe e está disponível para consulta.',
  'Entregue como proposta': 'Existe como desenho pactuado do estado-alvo, e '
    + 'não como ambiente em operação.',
  'Parcial': 'Parte do artefato existe; o que falta está registrado nas '
    + 'pendências.',
  'Não entregue': 'O artefato ainda não existe.',
};

function montaIndicadores(acervo) {
  const contagem = contaSituacoes(acervo.artefatos);
  const total = acervo.artefatos.length;
  const alvo = document.getElementById('grade-indicadores');

  const comValor = SITUACOES.filter((s) => contagem[s]);

  const barra = comValor.map((s) => `
    <div class="faixa ${classeDe(s)}" style="flex: ${contagem[s]}"
         title="${escapaHtml(`${contagem[s]} de ${total}: ${s}`)}">
      ${contagem[s]}
    </div>
  `).join('');

  const legenda = SITUACOES.map((s) => `
    <li>
      <span class="ponto ${classeDe(s)}"></span>
      <span class="quanto">${contagem[s] || 0}</span>
      <span class="qual">${escapaHtml(s)}</span>
      <span class="oque">${escapaHtml(DEFINICOES[s] || '')}</span>
    </li>
  `).join('');

  alvo.innerHTML = `
    <div class="barra-situacao" role="img"
         aria-label="${escapaHtml(SITUACOES.map((s) =>
           `${contagem[s] || 0} ${s}`).join(', '))}">${barra}</div>
    <ul class="legenda-situacao">${legenda}</ul>`;
}

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
      Como a situação dos 20 artefatos mudou do 2º para o 3º Relatório Parcial.
      Cada linha é uma situação: a barra de cima conta quantos artefatos estavam
      nela no 2º relatório, a de baixo quantos estão nela agora.
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
        como proposta e ${agora['Parcial']} parciais — os mesmos 20 artefatos, nas
        mesmas situações. A diferença é que o painel conta à parte as arquiteturas
        que estão propostas, para não dar por operante o que ainda está projetado.
      </p>
    </div>`;

  desenhaEvolucao('#svg-evolucao', series);
}

/* -------------------------------------------------------------- produtos */

/* Três palavras, que não são sinônimos:
     produto   o que o Termo espera. São 19.
     artefato  o que ficou disponível no período e compõe um produto. São 20.
     entrega   quando o produto inteiro é contemplado — estado, não peça.
   A página abre por elas, porque foi a confusão entre as três que tornou a
   versão anterior ilegível. */

const GLOSSARIO = [
  {
    termo: 'Produto',
    conta: (a) => `${a.produtos.length} no Termo`,
    diz: 'O que se espera. Pactuado no TED, não muda.',
  },
  {
    termo: 'Artefato',
    conta: (a) => `${a.artefatos.length} no quadro`,
    diz: 'O que ficou disponível no período e compõe um produto.',
  },
  {
    termo: 'Entrega',
    conta: () => 'estado do produto',
    diz: 'Quando o produto inteiro é contemplado.',
  },
];

const ESTADOS = ['Entregue', 'Em andamento', 'Previsto'];

const CLASSE_ESTADO = {
  'Entregue': 'estado-entregue',
  'Em andamento': 'estado-andamento',
  'Previsto': 'estado-previsto',
};

const MARCAS = {
  secao: { glifo: '●', classe: 'marca-secao', diz: 'seção própria' },
  mencao: { glifo: '○', classe: 'marca-mencao', diz: 'tratado sob outro produto' },
};

function marcaCobertura(produto, relatorio) {
  const c = produto.cobertura[String(relatorio.num)];
  if (!c) {
    return `<span class="marca-ausente" title="${relatorio.rotulo}: não tratado"
      >${relatorio.num}º</span>`;
  }
  const m = MARCAS[c.tipo];
  const onde = c.pagina ? `${c.onde} · p. ${c.pagina}` : c.onde;
  const titulo = escapaHtml(`${relatorio.rotulo} — ${m.diz}: ${onde}`);
  return `<span class="${m.classe}" title="${titulo}">${relatorio.num}º</span>`;
}

function selo(produto) {
  const estado = produto.estado || 'A classificar';
  const classe = CLASSE_ESTADO[produto.estado] || 'estado-vazio';
  return `<span class="selo ${classe}">${escapaHtml(estado)}</span>`;
}

/* Quantos produtos em cada estado. Some quando nenhum está classificado. */
function barraDeEstados(acervo) {
  const conta = {};
  for (const p of acervo.produtos) {
    if (p.estado) conta[p.estado] = (conta[p.estado] || 0) + 1;
  }
  const classificados = Object.values(conta).reduce((a, b) => a + b, 0);
  if (!classificados) return '';

  const faixas = ESTADOS.filter((e) => conta[e]).map((e) => `
    <div class="faixa ${CLASSE_ESTADO[e]}" style="flex: ${conta[e]}"
         title="${escapaHtml(`${conta[e]} de ${acervo.produtos.length}: ${e}`)}">
      ${conta[e]} ${escapaHtml(e.toLowerCase())}
    </div>
  `).join('');

  const falta = acervo.produtos.length - classificados;

  return `
    <div class="barra-estados" role="img"
         aria-label="${escapaHtml(ESTADOS.map((e) =>
           `${conta[e] || 0} ${e}`).join(', '))}">${faixas}</div>
    <p class="sob-barra">
      Os ${acervo.produtos.length} produtos do Termo, na leitura do
      3º Relatório Parcial.${falta
        ? ` ${falta} ainda sem classificação.` : ''}
    </p>`;
}

function artefatosDoProduto(produto, acervo) {
  if (!produto.artefatos.length) {
    return `<p class="nenhum-artefato">
      O quadro de acompanhamento não registra artefato para este produto. O que
      se sabe dele é o que o relatório declara, acima.
    </p>`;
  }
  const itens = produto.artefatos.map((a) => {
    const origem = a.evidencia === 'TED'
      ? 'Nomeado na redação do produto, no Termo.'
      : 'Vínculo derivado do lugar em que o 3º Relatório o documenta.';
    const noQuadro = acervo.artefatos.find((x) => x.nome === a.nome) || {};
    return `
      <li>
        <span class="etiqueta ${classeDe(a.situacao)}">${escapaHtml(a.situacao)}</span>
        <span class="nome-do-artefato">${escapaHtml(a.nome)}</span>
        ${noQuadro.onde
          ? `<span class="lastro">${ligaDocumentos(noQuadro.onde, acervo)}</span>`
          : ''}
        <span class="origem-vinculo" title="${escapaHtml(origem + (a.nota ? ' ' + a.nota : ''))}">
          ${a.evidencia === 'TED' ? 'Termo' : '3º Rel.'}</span>
      </li>`;
  }).join('');

  return `
    <p class="rotulo-bloco">Artefatos que o compõem</p>
    <ul class="artefatos-produto">${itens}</ul>`;
}

function montaProdutos(acervo) {
  const alvo = document.getElementById('matriz-produtos');
  const rels = acervo.relatorios;

  const tratados = (r) => acervo.produtos
    .filter((p) => p.cobertura[String(r.num)]).length;

  const glossario = GLOSSARIO.map((g) => `
    <div class="termo">
      <div class="palavra">${g.termo}<span class="quantos">${g.conta(acervo)}</span></div>
      <p>${g.diz}</p>
    </div>
  `).join('');

  /* Os três números não somam: são os mesmos 19 produtos, e cada relatório
     alcança mais deles que o anterior. */
  const resumo = rels.map((r) => `
    <div class="indicador">
      <div class="numero">${tratados(r)}<span class="de">de ${acervo.produtos.length}</span></div>
      <div class="rotulo">produtos tratados no ${r.rotulo.toLowerCase()}<br>
        <span class="periodo">${escapaHtml(r.periodo)}</span></div>
    </div>
  `).join('');

  const encaminhamentosDe = (meta) => {
    const m = acervo.metas.find((x) => x.num === meta);
    return m && m.encaminhamentos.length ? m.encaminhamentos : null;
  };

  const metas = [...new Set(acervo.produtos.map((p) => p.meta))];

  const blocos = metas.map((num) => {
    const daMeta = acervo.produtos.filter((p) => p.meta === num);
    const enc = encaminhamentosDe(num);

    const fichas = daMeta.map((p) => `
      <details class="produto" name="produto">
        <summary>
          <span class="id-produto">Produto ${p.num}</span>
          <span class="titulo-produto">${escapaHtml(p.nome)}</span>
          ${selo(p)}
          <span class="cobertura-resumo">
            ${rels.map((r) => marcaCobertura(p, r)).join('')}
          </span>
          <span class="conta-artefatos">${p.artefatos.length
            ? `${p.artefatos.length} artefato${p.artefatos.length > 1 ? 's' : ''}`
            : 'sem artefato'}</span>
        </summary>
        <div class="corpo-produto">
          <p class="rotulo-bloco">O que o Termo prevê</p>
          <p class="previsto">${escapaHtml(p.redacao)}.</p>

          <p class="rotulo-bloco">O que foi feito até aqui</p>
          <p class="feito">${ligaDocumentos(p.balanco, acervo)}</p>

          ${artefatosDoProduto(p, acervo)}

          ${enc ? `
            <p class="rotulo-bloco">Previsto para ${escapaHtml(acervo.origem.proximo_periodo)}</p>
            <ul class="encaminhamentos-produto">
              ${enc.map((e) => `<li>${escapaHtml(e)}</li>`).join('')}
            </ul>
            <p class="ressalva">
              O relatório registra os encaminhamentos por meta, e não por
              produto: os acima são os da Meta ${escapaHtml(num)} inteira.
            </p>` : ''}
        </div>
      </details>
    `).join('');

    return `
      <article class="bloco-meta">
        <h3><span class="numero-meta">Meta ${num}</span>${escapaHtml(daMeta[0].meta_nome)}</h3>
        <div class="produtos-da-meta">${fichas}</div>
      </article>`;
  }).join('');

  alvo.innerHTML = `
    <p class="secao-intro">
      O acompanhamento começa pelo que o Termo pactua: seis metas, e dentro de
      cada uma os seus produtos. Clique num produto para ver o previsto, o feito
      até aqui, os artefatos que o compõem e o que vem no próximo período.
    </p>
    <div class="glossario">${glossario}</div>
    ${barraDeEstados(acervo)}
    <div class="indicadores indicadores-3">${resumo}</div>
    <p class="legenda-marcas">
      Em cada produto, <span class="marca-secao">1º</span> marca o relatório que
      lhe deu seção própria, <span class="marca-mencao">2º</span> o que o tratou
      sob outro produto e <span class="marca-ausente">3º</span> o que não o
      tratou. O cursor sobre a marca mostra a seção e a página.
    </p>
    ${blocos}
    <div class="nota">
      <p>
        <strong>Sobre o estado de cada produto.</strong> Quem responde pelo TED
        assina se o produto está entregue; o painel não deduz. Um produto pode
        ter todos os seus artefatos entregues sem estar entregue, e a maioria
        deles não tem artefato algum no quadro de acompanhamento.
      </p>
      <p>
        <strong>De onde vem o que foi feito.</strong> Da seção correspondente do
        3º Relatório, uma frase por produto. A página do relatório está na marca
        do 3º, para conferência.
      </p>
      <p>
        <strong>Sobre o vínculo dos artefatos.</strong> Cada artefato do quadro é
        ligado ao produto que o nomeia na redação do Termo. Onde o Termo não o
        nomeia, o vínculo vem do lugar em que o 3º Relatório o documenta, e a
        classificação é do painel, não do documento — a marca ao lado do artefato
        registra qual dos dois casos é.
      </p>
      <p>
        O 1º Relatório trata apenas da Meta 01, e o quadro de acompanhamento só
        começa a ser apurado no 2º.
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

/* ------------------------------------------------------------- artefatos */

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
        <td class="onde">${a.onde ? ligaDocumentos(a.onde, acervo) : '—'}</td>
      </tr>
    `).join('');
  }

  function desenha() {
    alvo.innerHTML = `
      <p class="secao-intro">
        Os ${acervo.artefatos.length} artefatos do quadro de acompanhamento, com
        a situação anterior, a atual e a localização de cada um. Nomes de arquivo
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
      O 3º Relatório encerra cada meta com os compromissos que ela assume para o
      período seguinte. São ${total} encaminhamentos, reunidos aqui meta a meta,
      seguidos dos ${acervo.pendencias.length} artefatos que seguem pendentes e
      do que destrava cada um.
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
    montaArtefatos(acervo);
    montaCronograma(acervo);
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

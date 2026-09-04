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

function montaIndicadores(acervo) {
  const contagem = contaSituacoes(acervo.artefatos);
  const grade = document.getElementById('grade-indicadores');

  const cartoes = [
    { numero: acervo.artefatos.length, rotulo: 'artefatos acompanhados', classe: '' },
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
      O que mudou do 2º para o 3º Relatório Parcial, artefato a artefato.
    </p>
    <div id="svg-evolucao"></div>
    <div class="nota">
      <p>
        A mudança decorre menos de trabalho novo que de <strong>publicação</strong>:
        parte do que a avaliação anterior não localizou existia como código, e não
        como documento. O período foi dedicado a derivar documentos do próprio
        repositório, de modo que cada afirmação pudesse ser conferida na fonte.
      </p>
      <p>
        Os ${antes['Não entregue'] || 0} não entregues do 2º Relatório reúnem os
        assim marcados e os três com a marcação <em>falta apresentar artefato</em>,
        conforme o próprio documento agrega.
      </p>
      <p>
        <strong>Sobre a contagem.</strong> O texto do 3º Relatório Parcial declara
        12 entregues e 6 parciais. A conferência item a item do quadro dá
        ${agora['Entregue']} entregues, ${agora['Entregue como proposta']} entregues
        como proposta e ${agora['Parcial']} parciais — os mesmos 20 artefatos, nas
        mesmas situações, com as arquiteturas propostas contadas à parte para
        preservar a distinção entre o que opera e o que está projetado.
      </p>
    </div>`;

  desenhaEvolucao('#svg-evolucao', series);
}

/* ------------------------------------------------------------- inicialização */

async function inicia() {
  try {
    const acervo = await carrega();
    montaCabecalho(acervo);
    montaIndicadores(acervo);
    montaEvolucao(acervo);
  } catch (erro) {
    console.error(erro);
    document.getElementById('grade-indicadores').innerHTML =
      `<p>Não foi possível carregar os dados do painel. ` +
      `Se estiver abrindo o arquivo direto do disco, sirva o diretório com ` +
      `<code>python3 -m http.server</code>.</p>`;
  }
}

document.addEventListener('DOMContentLoaded', inicia);

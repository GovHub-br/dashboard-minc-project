/* Visualizações D3 do painel dos eixos. */

'use strict';

const ORDEM_STATUS = [
  'concluido', 'em_andamento', 'bloqueado', 'em_risco', 'nao_iniciado',
];

const COR_STATUS = {
  concluido: '#10B981',
  em_andamento: '#7A34F3',
  bloqueado: '#C2410C',
  em_risco: '#F19F42',
  nao_iniciado: '#B9BBC6',
};

/* ---------------------------------------------------------------- donut */

function desenhaDonut(seletor, porStatus, rotulos, total) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const lado = 150;
  const raio = lado / 2;
  const espessura = 26;

  const dados = ORDEM_STATUS
    .filter((s) => porStatus[s])
    .map((s) => ({ status: s, valor: porStatus[s] }));

  const svg = alvo.append('svg')
    .attr('id', 'svg-donut')
    .attr('viewBox', `0 0 ${lado} ${lado}`)
    .attr('role', 'img')
    .attr('aria-label', legendaDonut(porStatus, rotulos, total));

  const g = svg.append('g').attr('transform', `translate(${raio}, ${raio})`);

  const arco = d3.arc().innerRadius(raio - espessura).outerRadius(raio).padAngle(0.02);
  const torta = d3.pie().value((d) => d.valor).sort(null);

  g.selectAll('path')
    .data(torta(dados))
    .join('path')
    .attr('class', (d) => `fatia-${d.data.status}`)
    .attr('d', arco)
    .append('title')
    .text((d) => `${rotulos[d.data.status]}: ${d.data.valor}`);

  const concluidas = porStatus.concluido || 0;
  const pct = total ? Math.round((concluidas / total) * 100) : 0;

  g.append('text')
    .attr('class', 'donut-centro-valor')
    .attr('text-anchor', 'middle').attr('dy', '-0.1em')
    .text(`${pct}%`);

  g.append('text')
    .attr('class', 'donut-centro-rotulo')
    .attr('text-anchor', 'middle').attr('dy', '1.2em')
    .text('concluído');
}

function legendaDonut(porStatus, rotulos, total) {
  const partes = ORDEM_STATUS
    .filter((s) => porStatus[s])
    .map((s) => `${rotulos[s]}: ${porStatus[s]}`);
  return `Status das ${total} tarefas. ${partes.join('; ')}.`;
}

/* --------------------------------------------------- progresso no tempo */

function desenhaProgressoTempo(seletor, retratos) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const margem = { topo: 16, direita: 24, base: 40, esquerda: 44 };
  const largura = alvo.node().clientWidth || 560;
  const altura = 260;

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label',
      `Progresso médio em ${retratos.length} medição(ões), de ` +
      `${retratos[0].progresso_medio}% a ` +
      `${retratos[retratos.length - 1].progresso_medio}%.`);

  const dados = retratos.map((r) => ({
    data: new Date(r.data + 'T00:00:00'),
    valor: r.progresso_medio,
  }));

  const x = d3.scaleTime()
    .domain(dominioTemporal(dados))
    .range([margem.esquerda, largura - margem.direita]);

  const y = d3.scaleLinear()
    .domain([0, 100])
    .range([altura - margem.base, margem.topo]);

  // Grade horizontal.
  svg.append('g')
    .selectAll('line')
    .data(y.ticks(5))
    .join('line')
    .attr('class', 'grade')
    .attr('x1', margem.esquerda).attr('x2', largura - margem.direita)
    .attr('y1', (d) => y(d)).attr('y2', (d) => y(d));

  svg.append('g')
    .attr('transform', `translate(0, ${altura - margem.base})`)
    .attr('class', 'eixo')
    .call(d3.axisBottom(x).ticks(Math.min(dados.length, 6)).tickFormat(d3.timeFormat('%d/%m')));

  svg.append('g')
    .attr('transform', `translate(${margem.esquerda}, 0)`)
    .attr('class', 'eixo')
    .call(d3.axisLeft(y).ticks(5).tickFormat((d) => `${d}%`));

  if (dados.length > 1) {
    const area = d3.area()
      .x((d) => x(d.data)).y0(y(0)).y1((d) => y(d.valor))
      .curve(d3.curveMonotoneX);
    svg.append('path').datum(dados).attr('class', 'area-progresso').attr('d', area);

    const linha = d3.line()
      .x((d) => x(d.data)).y((d) => y(d.valor))
      .curve(d3.curveMonotoneX);
    svg.append('path').datum(dados).attr('class', 'linha-progresso').attr('d', linha);
  }

  svg.selectAll('circle.ponto')
    .data(dados)
    .join('circle')
    .attr('class', 'ponto')
    .attr('cx', (d) => x(d.data)).attr('cy', (d) => y(d.valor)).attr('r', 4)
    .append('title')
    .text((d) => `${d3.timeFormat('%d/%m/%Y')(d.data)}: ${d.valor}%`);

  // Com um retrato só, o valor fica rotulado — a linha ainda não existe.
  if (dados.length === 1) {
    svg.append('text')
      .attr('class', 'valor-unico')
      .attr('x', x(dados[0].data) + 10)
      .attr('y', y(dados[0].valor))
      .attr('dy', '0.35em')
      .text(`${dados[0].valor}%`);
  }
}

/* Um único ponto no tempo não define um domínio: abre-se um dia para cada
   lado para que a escala tenha largura. */
function dominioTemporal(dados) {
  const [min, max] = d3.extent(dados, (d) => d.data);
  if (+min !== +max) return [min, max];
  const dia = 86400000;
  return [new Date(+min - dia), new Date(+max + dia)];
}

/* ------------------------------------------------------ status no tempo */

function desenhaStatusTempo(seletor, retratos, rotulos) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const margem = { topo: 16, direita: 24, base: 40, esquerda: 40 };
  const largura = alvo.node().clientWidth || 560;
  const altura = 260;

  const presentes = ORDEM_STATUS.filter(
    (s) => retratos.some((r) => (r.por_status || {})[s])
  );

  const dados = retratos.map((r) => {
    const linha = { data: new Date(r.data + 'T00:00:00') };
    for (const s of presentes) linha[s] = (r.por_status || {})[s] || 0;
    return linha;
  });

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label', 'Quantidade de tarefas por status ao longo do tempo.');

  const x = d3.scaleTime()
    .domain(dominioTemporal(dados))
    .range([margem.esquerda, largura - margem.direita]);

  const maximo = d3.max(retratos, (r) => r.total) || 1;
  const y = d3.scaleLinear()
    .domain([0, maximo])
    .range([altura - margem.base, margem.topo]);

  svg.append('g')
    .attr('transform', `translate(0, ${altura - margem.base})`)
    .attr('class', 'eixo')
    .call(d3.axisBottom(x).ticks(Math.min(dados.length, 6)).tickFormat(d3.timeFormat('%d/%m')));

  svg.append('g')
    .attr('transform', `translate(${margem.esquerda}, 0)`)
    .attr('class', 'eixo')
    .call(d3.axisLeft(y).ticks(5));

  if (dados.length > 1) {
    const empilhado = d3.stack().keys(presentes)(dados);
    const area = d3.area()
      .x((d) => x(d.data.data))
      .y0((d) => y(d[0])).y1((d) => y(d[1]));

    svg.selectAll('path.faixa')
      .data(empilhado)
      .join('path')
      .attr('class', 'faixa')
      .attr('fill', (d) => COR_STATUS[d.key])
      .attr('fill-opacity', 0.85)
      .attr('d', area)
      .append('title')
      .text((d) => rotulos[d.key]);
  } else {
    // Com um retrato só, empilham-se barras em vez de áreas.
    let base = 0;
    const largura_barra = 40;
    for (const s of presentes) {
      const valor = dados[0][s];
      if (!valor) continue;
      svg.append('rect')
        .attr('x', x(dados[0].data) - largura_barra / 2)
        .attr('y', y(base + valor))
        .attr('width', largura_barra)
        .attr('height', y(base) - y(base + valor))
        .attr('fill', COR_STATUS[s])
        .attr('fill-opacity', 0.85)
        .append('title')
        .text(`${rotulos[s]}: ${valor}`);
      base += valor;
    }
  }
}

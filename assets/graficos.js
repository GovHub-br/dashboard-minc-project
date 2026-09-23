/* Visualizações D3 do painel. */

'use strict';

/* Barras pareadas: cada situação com a contagem do 2º e do 3º relatório. */
function desenhaEvolucao(seletor, series) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  // A largura do viewBox acompanha a do container, para que o SVG não seja
  // esticado — esticar ampliaria as fontes junto. O limite fica no CSS.
  // A margem direita reserva espaço para o rótulo numérico da barra maior.
  const margem = { topo: 16, direita: 44, base: 44, esquerda: 190 };
  const largura = alvo.node().clientWidth || 820;
  const alturaLinha = 56;
  const altura = series.length * alturaLinha + margem.topo + margem.base;

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label', legendaAcessivel(series));

  const maximo = d3.max(series, (d) => Math.max(d.antes, d.agora)) || 1;

  const x = d3.scaleLinear()
    .domain([0, maximo])
    .range([margem.esquerda, largura - margem.direita]);

  const y = d3.scaleBand()
    .domain(series.map((d) => d.situacao))
    .range([margem.topo, altura - margem.base])
    .padding(0.28);

  const alturaBarra = y.bandwidth() / 2 - 2;

  const grupo = svg.selectAll('g.linha')
    .data(series)
    .join('g')
    .attr('class', 'linha');

  grupo.append('text')
    .attr('class', 'rotulo-situacao')
    .attr('x', margem.esquerda - 12)
    .attr('y', (d) => y(d.situacao) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .text((d) => d.situacao);

  // 2º Relatório: barra clara, acima.
  grupo.append('rect')
    .attr('class', 'barra-antes')
    .attr('x', x(0))
    .attr('y', (d) => y(d.situacao))
    .attr('height', alturaBarra)
    .attr('width', (d) => x(d.antes) - x(0));

  // 3º Relatório: barra cheia, abaixo, na cor da situação.
  grupo.append('rect')
    .attr('class', (d) => `barra-agora ${d.classe}`)
    .attr('x', x(0))
    .attr('y', (d) => y(d.situacao) + alturaBarra + 4)
    .attr('height', alturaBarra)
    .attr('width', (d) => x(d.agora) - x(0));

  grupo.append('text')
    .attr('class', 'valor')
    .attr('x', (d) => x(d.antes) + 8)
    .attr('y', (d) => y(d.situacao) + alturaBarra / 2)
    .attr('dy', '0.35em')
    .text((d) => d.antes);

  grupo.append('text')
    .attr('class', 'valor valor-forte')
    .attr('x', (d) => x(d.agora) + 8)
    .attr('y', (d) => y(d.situacao) + alturaBarra + 4 + alturaBarra / 2)
    .attr('dy', '0.35em')
    .text((d) => d.agora);

  // Legenda. A barra do 3º relatório não tem cor única: cada uma sai na cor
  // da sua situação. Por isso a amostra é a tira das quatro cores, e não um
  // quadrado só — que fazia a legenda parecer dizer "3º relatório é verde".
  const legenda = svg.append('g')
    .attr('transform', `translate(${margem.esquerda}, ${altura - 16})`);

  legenda.append('rect')
    .attr('class', 'barra-antes')
    .attr('width', 14).attr('height', 14).attr('y', -11);
  legenda.append('text')
    .attr('class', 'rotulo-legenda').attr('x', 20)
    .text('2º Relatório Parcial');

  const tira = legenda.append('g').attr('transform', 'translate(160, 0)');
  series.forEach((d, i) => {
    tira.append('rect')
      .attr('class', `barra-agora ${d.classe}`)
      .attr('x', i * 15).attr('width', 14).attr('height', 14).attr('y', -11);
  });
  legenda.append('text')
    .attr('class', 'rotulo-legenda')
    .attr('x', 160 + series.length * 15 + 6)
    .text('3º Relatório Parcial, na cor de cada situação');
}

function legendaAcessivel(series) {
  const partes = series.map(
    (d) => `${d.situacao}: ${d.antes} no 2º relatório, ${d.agora} no 3º`
  );
  return `Evolução das entregas entre relatórios. ${partes.join('; ')}.`;
}

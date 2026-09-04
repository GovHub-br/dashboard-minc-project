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

  // Legenda.
  const legenda = svg.append('g')
    .attr('transform', `translate(${margem.esquerda}, ${altura - 16})`);

  legenda.append('rect')
    .attr('class', 'barra-antes')
    .attr('width', 14).attr('height', 14).attr('y', -11);
  legenda.append('text')
    .attr('class', 'rotulo-legenda').attr('x', 20)
    .text('2º Relatório Parcial');

  legenda.append('rect')
    .attr('class', 'barra-agora sit-entregue')
    .attr('x', 160).attr('width', 14).attr('height', 14).attr('y', -11);
  legenda.append('text')
    .attr('class', 'rotulo-legenda').attr('x', 180)
    .text('3º Relatório Parcial');
}

function legendaAcessivel(series) {
  const partes = series.map(
    (d) => `${d.situacao}: ${d.antes} no 2º relatório, ${d.agora} no 3º`
  );
  return `Evolução entre relatórios. ${partes.join('; ')}.`;
}

/* Matriz de riscos: probabilidade (y) por impacto (x), 3×3. */
function desenhaRiscos(seletor, riscos) {
  const alvo = d3.select(seletor);
  alvo.selectAll('*').remove();

  const NIVEIS = ['Baixo', 'Médio', 'Alto'];
  const margem = { topo: 20, direita: 20, base: 52, esquerda: 90 };
  const lado = 108;
  const largura = margem.esquerda + lado * 3 + margem.direita;
  const altura = margem.topo + lado * 3 + margem.base;

  const svg = alvo.append('svg')
    .attr('viewBox', `0 0 ${largura} ${altura}`)
    .attr('width', '100%')
    .attr('role', 'img')
    .attr('aria-label',
      `Matriz de riscos, ${riscos.length} riscos por probabilidade e impacto.`);

  const x = (nivel) => margem.esquerda + NIVEIS.indexOf(nivel) * lado;
  // Probabilidade cresce para cima.
  const y = (nivel) => margem.topo + (2 - NIVEIS.indexOf(nivel)) * lado;

  // Células, tingidas pela severidade combinada.
  for (const p of NIVEIS) {
    for (const i of NIVEIS) {
      const severidade = NIVEIS.indexOf(p) + NIVEIS.indexOf(i);
      svg.append('rect')
        .attr('class', `celula sev-${severidade}`)
        .attr('x', x(i)).attr('y', y(p))
        .attr('width', lado - 4).attr('height', lado - 4)
        .attr('rx', 6);
    }
  }

  // Eixos.
  NIVEIS.forEach((n) => {
    svg.append('text').attr('class', 'rotulo-eixo')
      .attr('x', x(n) + (lado - 4) / 2).attr('y', altura - 26)
      .attr('text-anchor', 'middle').text(n);
    svg.append('text').attr('class', 'rotulo-eixo')
      .attr('x', margem.esquerda - 12).attr('y', y(n) + (lado - 4) / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').text(n);
  });

  svg.append('text').attr('class', 'titulo-eixo')
    .attr('x', margem.esquerda + lado * 1.5).attr('y', altura - 6)
    .attr('text-anchor', 'middle').text('Impacto');

  svg.append('text').attr('class', 'titulo-eixo')
    .attr('transform', `translate(18, ${margem.topo + lado * 1.5}) rotate(-90)`)
    .attr('text-anchor', 'middle').text('Probabilidade');

  // Pontos, numerados na ordem do relatório e distribuídos dentro da célula.
  const porCelula = {};
  riscos.forEach((r, indice) => {
    const chave = `${r.probabilidade}|${r.impacto}`;
    (porCelula[chave] = porCelula[chave] || []).push(indice);
  });

  Object.entries(porCelula).forEach(([chave, indices]) => {
    const [prob, imp] = chave.split('|');
    if (!NIVEIS.includes(prob) || !NIVEIS.includes(imp)) return;

    const cx = x(imp) + (lado - 4) / 2;
    const cy = y(prob) + (lado - 4) / 2;
    const passo = 34;
    const inicio = -((indices.length - 1) * passo) / 2;

    indices.forEach((indice, ordem) => {
      const g = svg.append('g')
        .attr('transform', `translate(${cx + inicio + ordem * passo}, ${cy})`);
      g.append('circle').attr('class', 'ponto-risco').attr('r', 15);
      g.append('text').attr('class', 'numero-risco')
        .attr('text-anchor', 'middle').attr('dy', '0.35em')
        .text(indice + 1);
      g.append('title').text(riscos[indice].risco);
    });
  });
}

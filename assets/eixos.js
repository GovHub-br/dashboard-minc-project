/* Painel do trabalho nos 8 eixos do PNC.
   Carrega dados/eixos.json e dados/historico.json e monta as seções.
   As visualizações D3 ficam em graficos-eixos.js. */

'use strict';

const MES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
  'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

function escapa(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

function porExtenso(iso) {
  if (!iso) return '';
  const [ano, mes, dia] = iso.slice(0, 10).split('-');
  return `${Number(dia)} de ${MES[Number(mes) - 1]} de ${ano}`;
}

function curta(iso) {
  if (!iso) return '';
  const [ano, mes, dia] = iso.slice(0, 10).split('-');
  return `${dia}/${mes}/${ano}`;
}

async function carregaJson(caminho) {
  const r = await fetch(caminho);
  if (!r.ok) throw new Error(`${caminho}: ${r.status}`);
  return r.json();
}

/* ------------------------------------------------------------- cabeçalho */

function montaCabecalho(dados) {
  const o = dados.origem;
  const r = dados.resumo;
  document.getElementById('carimbo').textContent =
    `${r.total} demandas em ${dados.eixos.length} eixos · ` +
    `sincronizado em ${porExtenso(o.sincronizado_em)}.`;

  document.getElementById('rodape-origem').textContent =
    'Os dados desta página vêm da planilha dos eixos, sincronizada ' +
    'automaticamente. Para corrigir qualquer informação, edite a planilha.';
}

/* ----------------------------------------------------------- visão geral */

function montaDonut(dados) {
  const alvo = document.getElementById('donut-status');
  const porStatus = dados.resumo.por_status;
  const rotulos = dados.rotulos_status;

  const itens = ORDEM_STATUS
    .filter((s) => porStatus[s])
    .map((s) => `
      <li>
        <span class="bolinha" style="background:${COR_STATUS[s]}"></span>
        ${escapa(rotulos[s])}
        <span class="quantidade">${porStatus[s]}</span>
      </li>`).join('');

  alvo.innerHTML = `
    <div class="donut-caixa">
      <div id="svg-donut-caixa"></div>
      <ul class="legenda-donut">${itens}</ul>
    </div>`;

  desenhaDonut('#svg-donut-caixa', porStatus, rotulos, dados.resumo.total);
}

function montaBarrasEixos(dados) {
  const alvo = document.getElementById('barras-eixos');

  alvo.innerHTML = dados.eixos.map((e) => {
    const classe = e.progresso === 0 ? 'vazio'
      : e.progresso >= 40 ? 'avancado' : '';
    return `
      <div class="barra-eixo ${classe}">
        <span class="nome-eixo" title="${escapa(e.nome)}">${escapa(e.nome)}</span>
        <span class="trilho">
          <span class="preenchida" style="width:${e.progresso}%"></span>
        </span>
        <span class="pct">${Math.round(e.progresso)}%</span>
      </div>`;
  }).join('');
}

function montaAtualizacao(dados) {
  const o = dados.origem;
  const linhas = [
    ['Última sincronização', porExtenso(o.sincronizado_em), true],
    ['Próxima reunião', o.proxima_reuniao ? porExtenso(o.proxima_reuniao) : 'não definida', !!o.proxima_reuniao],
    ['Guardiã da base', o.guardia || 'não definida', !!o.guardia],
    ['Demandas sem prazo', `${dados.resumo.sem_prazo} de ${dados.resumo.total}`, true],
  ];

  document.getElementById('cartao-atualizacao').innerHTML = linhas.map(
    ([rotulo, valor, definido]) => `
      <div class="linha-atualizacao">
        <div class="rotulo-att">${escapa(rotulo)}</div>
        <div class="valor-att ${definido ? '' : 'indefinido'}">${escapa(valor)}</div>
      </div>`).join('');
}

/* --------------------------------------------------------------- alertas */

function montaAlertas(dados) {
  const alvo = document.getElementById('lista-alertas');
  const alertas = dados.alertas || [];

  if (!alertas.length) {
    alvo.innerHTML = `
      <p class="sem-alertas">
        Nenhuma demanda bloqueada, em risco ou com prazo vencido.
        Demandas ainda sem prazo definido não contam como atraso.
      </p>`;
    return;
  }

  alvo.innerHTML = `
    <p class="secao-intro">
      Demandas bloqueadas, em risco ou com prazo vencido. Demanda sem prazo
      definido não entra aqui — ausência de data não é atraso.
    </p>
    <div class="grade-alertas">
      ${alertas.map((a) => `
        <div class="alerta">
          <div class="tarefa-alerta">${escapa(a.tarefa)}</div>
          <div class="meta-alerta">
            ${escapa(a.eixo_nome)} ·
            <span class="motivo">${escapa(a.motivo)}</span>
            ${a.prazo ? ` — ${curta(a.prazo)}` : ''}
            ${a.resp ? ` · resp: ${escapa(a.resp)}` : ''}
          </div>
        </div>`).join('')}
    </div>`;
}

/* ------------------------------------------------------------ inicialização */

function avisoVazio(mensagem) {
  return `
    <div class="aviso-vazio">
      <strong>Ainda não há demandas cadastradas</strong>
      ${mensagem}
    </div>`;
}

async function inicia() {
  let dados;
  let historico = { retratos: [] };

  try {
    dados = await carregaJson('dados/eixos.json');
  } catch (erro) {
    console.error(erro);
    document.getElementById('donut-status').innerHTML =
      '<p>Não foi possível carregar os dados. Se estiver abrindo o arquivo ' +
      'direto do disco, sirva o diretório com <code>python3 -m http.server</code>.</p>';
    return;
  }

  try {
    historico = await carregaJson('dados/historico.json');
  } catch (erro) {
    console.warn('Sem histórico ainda.', erro);
  }

  montaCabecalho(dados);

  // Enquanto a planilha não tiver demandas, cartões zerados não informam nada
  // e não orientam. A tela de primeiros passos toma o lugar deles.
  if (!dados.resumo.total) {
    montaPrimeirosPassos(dados);
    return;
  }

  montaDonut(dados);
  montaBarrasEixos(dados);
  montaAtualizacao(dados);
  montaAlertas(dados);
  montaRede(dados);
  montaEvolucao(dados, historico);
  montaDemandas(dados);
}

/* Estado inicial: a planilha existe, mas ainda não tem demandas. */
function montaPrimeirosPassos(dados) {
  for (const id of ['alertas', 'rede', 'evolucao-eixos', 'demandas']) {
    document.getElementById(id).hidden = true;
  }

  const secao = document.getElementById('visao-geral');
  secao.querySelector('.grade-visao').outerHTML = `
    <div class="primeiros-passos">
      <h3>A planilha ainda não tem demandas</h3>
      <p>
        Esta página se monta sozinha a partir da planilha dos eixos. Assim que a
        primeira demanda for cadastrada, aparecem aqui o status consolidado, o
        progresso por eixo, os alertas, a rede de pré-requisitos e a evolução no
        tempo.
      </p>
      <ol>
        <li>Importe <code>planilha/modelo-eixos-pnc.csv</code> no Google Sheets.</li>
        <li>Cadastre as demandas de cada eixo, uma por linha.</li>
        <li>Publique a planilha em <em>Arquivo → Compartilhar → Publicar na web</em>, formato CSV.</li>
        <li>Registre o ID da planilha na variável <code>PLANILHA_ID</code> do repositório.</li>
      </ol>
      <p class="rodape-passos">
        O passo a passo completo está em <code>planilha/COMO-PREENCHER.md</code>.
        Prazos ainda não acordados ficam como <code>não definido ainda</code> —
        o painel os mostra como sem prazo, nunca como atrasados.
      </p>
    </div>`;

  document.getElementById('rodape-origem').textContent =
    'Os dados desta página vêm da planilha dos eixos, sincronizada ' +
    'automaticamente. Nenhuma demanda cadastrada até agora.';
}

document.addEventListener('DOMContentLoaded', inicia);

/* ================================================================= rede */

/* Cadeias = componentes conexos do grafo de pré-requisitos. Cada uma vira uma
   linha, com as tarefas posicionadas na coluna do seu passo. */
function montaCadeias(tarefas) {
  const porCod = {};
  for (const t of tarefas) if (t.cod) porCod[t.cod] = t;

  const vizinhos = {};
  const liga = (a, b) => {
    (vizinhos[a] = vizinhos[a] || new Set()).add(b);
    (vizinhos[b] = vizinhos[b] || new Set()).add(a);
  };
  for (const t of tarefas) {
    for (const d of t.depende_de) if (porCod[d]) liga(t.cod, d);
  }

  const vistos = new Set();
  const cadeias = [];
  for (const t of tarefas) {
    if (!t.cod || vistos.has(t.cod) || !vizinhos[t.cod]) continue;
    const fila = [t.cod];
    const membros = [];
    vistos.add(t.cod);
    while (fila.length) {
      const c = fila.shift();
      membros.push(porCod[c]);
      for (const v of vizinhos[c] || []) {
        if (!vistos.has(v)) { vistos.add(v); fila.push(v); }
      }
    }
    cadeias.push(membros.sort((a, b) => a.passo - b.passo ||
      a.cod.localeCompare(b.cod)));
  }
  return cadeias.sort((a, b) => b.length - a.length);
}

function cartaoTarefa(t, rotulos) {
  const marca = t.travada
    ? '<span class="marca travada">🔒 travada</span>'
    : t.pronta ? '<span class="marca pronta">🚦 pronta</span>'
    : t.status === 'concluido' ? '<span class="marca ok">✓ concluída</span>' : '';

  const pe = [
    t.prazo ? curta(t.prazo) : 'sem prazo',
    t.resp || 'sem responsável',
  ].join(' · ');

  return `
    <div class="no-tarefa st-${t.status}">
      <div class="topo-no">
        <span class="cod">${escapa(t.cod)}</span>
        ${marca}
      </div>
      <div class="desc-no">${escapa(t.tarefa)}</div>
      <div class="pe-no">${escapa(pe)}</div>
    </div>`;
}

function montaRede(dados) {
  const alvo = document.getElementById('painel-rede');
  const tarefas = dados.eixos.flatMap((e) => e.tarefas);
  const r = dados.resumo;
  const cadeias = montaCadeias(tarefas);

  if (!cadeias.length) {
    alvo.innerHTML = avisoVazio(
      'Nenhuma demanda tem pré-requisito declarado. Preencha a coluna ' +
      '<code>Depende de</code> na planilha com o <code>Cod_Task</code> do que ' +
      'precisa acontecer antes, e a rede aparece aqui.');
    return;
  }

  const indicadores = [
    ['Vínculos mapeados', r.vinculos, `entre ${r.encadeadas} demandas encadeadas`, 'verde'],
    ['Entregas travadas', r.travadas, 'aguardam um pré-requisito não concluído', 'vermelho'],
    ['Prontas para iniciar', r.prontas, 'pré-requisitos cumpridos, execução liberada', 'verde'],
    ['Cadeia mais longa', `${r.cadeia_mais_longa} passos`, 'maior sequência de entregas em série', 'roxo'],
    ['Principal gargalo', r.gargalo ? r.gargalo.cod : '—',
      r.gargalo ? `segura ${r.gargalo.segura} entrega(s) · ${r.gargalo.resp || 'sem responsável'}` : 'nenhum',
      'laranja'],
  ];

  const maxPasso = Math.max(...tarefas.map((t) => t.passo));

  alvo.innerHTML = `
    <p class="secao-intro">
      ${r.encadeadas} das ${r.total} demandas estão encadeadas em
      ${cadeias.length} cadeia(s) de pré-requisitos. Cada seta liga uma demanda
      ao que precisa acontecer antes dela —
      <strong class="destaque-vermelho">setas vermelhas tracejadas</strong>
      apontam onde o fluxo está parado.
    </p>

    <div class="indicadores-rede">
      ${indicadores.map(([rot, val, sub, cor]) => `
        <div class="ind-rede ${cor}">
          <div class="rot-ind">${escapa(rot)}</div>
          <div class="val-ind">${escapa(String(val))}</div>
          <div class="sub-ind">${escapa(sub)}</div>
        </div>`).join('')}
    </div>

    <div class="abas-rede" role="group" aria-label="Modo de visualização">
      <button class="aba" type="button" data-modo="rede" aria-pressed="true">Rede de pré-requisitos</button>
      <button class="aba" type="button" data-modo="gantt" aria-pressed="false">Linha do tempo</button>
    </div>

    <div class="filtros" role="group" aria-label="Filtrar cadeias" id="filtros-cadeia">
      <button class="filtro" type="button" data-f="todas" aria-pressed="true">Todas as cadeias</button>
      <button class="filtro" type="button" data-f="bloqueio" aria-pressed="false">Só com bloqueio</button>
      <button class="filtro" type="button" data-f="pronta" aria-pressed="false">Prontas para iniciar</button>
    </div>

    <div class="legenda-rede">
      <span><span class="tracinho cumprido"></span> pré-requisito cumprido</span>
      <span><span class="tracinho aguardando"></span> aguardando predecessor</span>
      ${ORDEM_STATUS.filter((s) => dados.resumo.por_status[s]).map((s) =>
        `<span><span class="bolinha" style="background:${COR_STATUS[s]}"></span>
         ${escapa(dados.rotulos_status[s])}</span>`).join('')}
    </div>

    <div id="conteudo-rede"></div>`;

  let modo = 'rede';
  let filtro = 'todas';

  function cadeiasVisiveis() {
    if (filtro === 'bloqueio') return cadeias.filter((c) => c.some((t) => t.travada));
    if (filtro === 'pronta') return cadeias.filter((c) => c.some((t) => t.pronta));
    return cadeias;
  }

  function desenha() {
    const destino = document.getElementById('conteudo-rede');
    if (modo === 'gantt') { desenhaGantt(destino, tarefas, dados); return; }

    const visiveis = cadeiasVisiveis();
    if (!visiveis.length) {
      destino.innerHTML = '<p class="aviso-vazio">Nenhuma cadeia nesta condição.</p>';
      return;
    }

    const colunas = [];
    for (let p = 0; p <= maxPasso; p++) {
      colunas.push(p === 0 ? '1º PASSO · SEM PRÉ-REQUISITO' : `${p + 1}º PASSO`);
    }

    destino.innerHTML = `
      <div class="rolagem">
        <div class="grade-rede" style="grid-template-columns: repeat(${maxPasso + 1}, minmax(210px, 1fr))">
          ${colunas.map((c) => `<div class="cab-passo">${escapa(c)}</div>`).join('')}
          ${visiveis.map((cadeia) => linhaCadeia(cadeia, maxPasso, dados)).join('')}
        </div>
      </div>`;
  }

  function linhaCadeia(cadeia, maxPasso, dados) {
    const porPasso = {};
    for (const t of cadeia) (porPasso[t.passo] = porPasso[t.passo] || []).push(t);

    let html = '';
    for (let p = 0; p <= maxPasso; p++) {
      const aqui = porPasso[p] || [];
      const seta = p > 0 && aqui.length
        ? `<div class="seta ${aqui.some((t) => t.travada) ? 'aguardando' : 'cumprido'}"></div>`
        : '';
      html += `<div class="celula-rede">
        ${seta}
        <div class="nos">${aqui.map((t) => cartaoTarefa(t, dados.rotulos_status)).join('')}</div>
      </div>`;
    }
    return html;
  }

  alvo.querySelectorAll('.aba').forEach((b) => b.addEventListener('click', () => {
    modo = b.dataset.modo;
    alvo.querySelectorAll('.aba').forEach((x) =>
      x.setAttribute('aria-pressed', String(x === b)));
    document.getElementById('filtros-cadeia').hidden = (modo === 'gantt');
    desenha();
  }));

  alvo.querySelectorAll('#filtros-cadeia .filtro').forEach((b) =>
    b.addEventListener('click', () => {
      filtro = b.dataset.f;
      alvo.querySelectorAll('#filtros-cadeia .filtro').forEach((x) =>
        x.setAttribute('aria-pressed', String(x === b)));
      desenha();
    }));

  desenha();
}

/* --------------------------------------------------------------- gantt */

/* Sem data de início declarada, cada demanda entra como marco no seu prazo —
   não como barra. Uma barra exigiria inventar quando o trabalho começa. */
function desenhaGantt(destino, tarefas, dados) {
  const comPrazo = tarefas.filter((t) => t.prazo)
    .sort((a, b) => a.prazo.localeCompare(b.prazo));
  const sem = tarefas.length - comPrazo.length;

  if (!comPrazo.length) {
    destino.innerHTML = `
      <div class="aviso-vazio">
        <strong>Nenhuma demanda tem prazo definido</strong>
        As ${tarefas.length} demandas estão como <code>não definido ainda</code>.
        Conforme as datas forem acordadas, preencha a coluna
        <code>Prazo</code> na planilha e a linha do tempo se monta sozinha.
      </div>`;
    return;
  }

  const grupos = {};
  for (const t of comPrazo) {
    const mes = t.prazo.slice(0, 7);
    (grupos[mes] = grupos[mes] || []).push(t);
  }

  destino.innerHTML = `
    ${sem ? `<p class="secao-intro">${comPrazo.length} de ${tarefas.length}
      demandas têm prazo. As outras ${sem} seguem sem data definida e não
      aparecem aqui.</p>` : ''}
    <div class="linha-tempo">
      ${Object.keys(grupos).sort().map((mes) => {
        const [ano, m] = mes.split('-');
        return `
          <div class="mes-tempo">
            <div class="rot-mes">${MES[Number(m) - 1]} de ${ano}</div>
            <div class="marcos">
              ${grupos[mes].map((t) => `
                <div class="marco st-${t.status}">
                  <span class="dia">${t.prazo.slice(8, 10)}</span>
                  <div>
                    <div class="desc-marco">${escapa(t.tarefa)}</div>
                    <div class="pe-no">${escapa(t.eixo_nome)}${t.resp ? ' · ' + escapa(t.resp) : ''}</div>
                  </div>
                </div>`).join('')}
            </div>
          </div>`;
      }).join('')}
    </div>`;
}

/* ============================================================= evolução */

function montaEvolucao(dados, historico) {
  const alvo = document.getElementById('painel-evolucao');
  const retratos = (historico.retratos || []).slice().sort((a, b) =>
    a.data.localeCompare(b.data));

  if (!retratos.length) {
    alvo.innerHTML = avisoVazio(
      'A série começa na primeira sincronização da planilha.');
    return;
  }

  const unico = retratos.length === 1;

  alvo.innerHTML = `
    <p class="secao-intro">
      ${unico
        ? 'Primeira medição registrada. A série se forma a cada sincronização — amanhã haverá dois pontos.'
        : `${retratos.length} medições, de ${curta(retratos[0].data)} a ${curta(retratos[retratos.length - 1].data)}.`}
    </p>
    <div class="grade-evolucao">
      <article class="cartao">
        <h3>Progresso médio</h3>
        <div id="graf-progresso"></div>
      </article>
      <article class="cartao">
        <h3>Evolução por status</h3>
        <div id="graf-status"></div>
        <div class="legenda-rede" style="margin-top:12px">
          ${ORDEM_STATUS.filter((s) => dados.resumo.por_status[s]).map((s) =>
            `<span><span class="bolinha" style="background:${COR_STATUS[s]}"></span>
             ${escapa(dados.rotulos_status[s])}</span>`).join('')}
        </div>
      </article>
    </div>`;

  desenhaProgressoTempo('#graf-progresso', retratos);
  desenhaStatusTempo('#graf-status', retratos, dados.rotulos_status);
}

/* ============================================================= demandas */

function montaDemandas(dados) {
  const alvo = document.getElementById('painel-demandas');
  const tarefas = dados.eixos.flatMap((e) => e.tarefas);
  const r = dados.resumo;

  let filtro = 'todos';
  let busca = '';

  const opcoes = [
    ['todos', 'Todas', r.total],
    ...ORDEM_STATUS.filter((s) => r.por_status[s])
      .map((s) => [s, dados.rotulos_status[s], r.por_status[s]]),
    ['travada', 'Travada por dependência', r.travadas],
    ['pronta', 'Pronta para iniciar', r.prontas],
    ['sem_prazo', 'Sem prazo definido', r.sem_prazo],
  ];

  function passa(t) {
    if (busca && !`${t.cod} ${t.tarefa} ${t.resp}`.toLowerCase()
      .includes(busca.toLowerCase())) return false;
    if (filtro === 'todos') return true;
    if (filtro === 'travada') return t.travada;
    if (filtro === 'pronta') return t.pronta;
    if (filtro === 'sem_prazo') return !t.prazo;
    return t.status === filtro;
  }

  function desenha() {
    const visiveis = tarefas.filter(passa);
    const porEixo = dados.eixos
      .map((e) => ({ ...e, visiveis: e.tarefas.filter(passa) }))
      .filter((e) => e.visiveis.length);

    alvo.innerHTML = `
      <div class="filtros" role="group" aria-label="Filtrar demandas">
        ${opcoes.map(([v, rot, n]) => `
          <button class="filtro" type="button" data-v="${escapa(v)}"
                  aria-pressed="${v === filtro}">
            ${escapa(rot)} <span class="conta">${n}</span>
          </button>`).join('')}
      </div>
      <input type="search" class="busca" id="busca-demanda"
             placeholder="Buscar demanda, código ou responsável…"
             value="${escapa(busca)}" aria-label="Buscar demanda">
      ${visiveis.length === 0
        ? '<p class="aviso-vazio">Nenhuma demanda encontrada.</p>'
        : porEixo.map((e) => `
          <details class="eixo-bloco" ${porEixo.length <= 2 ? 'open' : ''}>
            <summary>
              <span class="num-eixo">${e.id}</span>
              <span class="nome-eixo-bloco">${escapa(e.nome)}</span>
              <span class="trilho pequeno">
                <span class="preenchida" style="width:${e.progresso}%"></span>
              </span>
              <span class="pct-bloco">${Math.round(e.progresso)}%</span>
              <span class="fracao">${e.concluidas}/${e.total}</span>
            </summary>
            <div class="tarefas-eixo">
              ${e.visiveis.map((t) => `
                <div class="linha-tarefa st-${t.status}">
                  <span class="cod">${escapa(t.cod)}</span>
                  <div>
                    <div class="desc-linha">${escapa(t.tarefa)}</div>
                    <div class="pe-no">
                      ${escapa(dados.rotulos_status[t.status])}
                      ${t.travada ? ' · 🔒 travada' : ''}
                      ${t.pronta ? ' · 🚦 pronta' : ''}
                      · ${t.prazo ? curta(t.prazo) : 'sem prazo'}
                      ${t.resp ? ' · ' + escapa(t.resp) : ''}
                      ${t.depende_de.length ? ' · depende de ' + escapa(t.depende_de.join(', ')) : ''}
                    </div>
                  </div>
                </div>`).join('')}
            </div>
          </details>`).join('')}`;

    alvo.querySelectorAll('.filtro').forEach((b) =>
      b.addEventListener('click', () => { filtro = b.dataset.v; desenha(); }));

    const campo = document.getElementById('busca-demanda');
    campo.addEventListener('input', () => {
      busca = campo.value;
      const pos = campo.selectionStart;
      desenha();
      const novo = document.getElementById('busca-demanda');
      novo.focus();
      novo.setSelectionRange(pos, pos);
    });
  }

  desenha();
}

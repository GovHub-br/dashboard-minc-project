# -*- coding: utf-8 -*-
"""Testes do conversor da planilha dos eixos."""

import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import planilha_para_json as conv  # noqa: E402

CABECALHO = ("Prioridade,Eixo,Processo,Atividade,Cod_Task,Tarefa,"
             "Depende de,Responsável,Prazo,Status")


def planilha(*linhas):
    """Escreve um CSV temporário e devolve as tarefas já com a rede calculada."""
    arq = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    )
    arq.write(CABECALHO + "\n" + "\n".join(linhas) + "\n")
    arq.close()
    return conv.calcula_rede(conv.le_planilha(arq.name))


def por_cod(tarefas):
    return {t["cod"]: t for t in tarefas}


class TestLeitura(unittest.TestCase):
    def test_le_uma_tarefa(self):
        t = planilha("Alta,1 · Gestão,,,E1.1.1,Fazer algo,,SNH,10/09/2026,Em andamento")
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["cod"], "E1.1.1")
        self.assertEqual(t[0]["eixo"], 1)
        self.assertEqual(t[0]["eixo_nome"], "Gestão")
        self.assertEqual(t[0]["resp"], "SNH")
        self.assertEqual(t[0]["status"], "em_andamento")
        self.assertEqual(t[0]["progresso"], 50)

    def test_ignora_linha_sem_tarefa_ou_sem_eixo(self):
        t = planilha(
            "Alta,1 · Gestão,,,E1.1.1,Válida,,,,Não iniciado",
            "Alta,1 · Gestão,,,E1.1.2,,,,,Não iniciado",
            "Alta,,,,E9.9.9,Sem eixo,,,,Não iniciado",
        )
        self.assertEqual([x["cod"] for x in t], ["E1.1.1"])

    def test_prazo_em_varios_formatos(self):
        self.assertEqual(conv.le_prazo("10/09/2026"), "2026-09-10")
        self.assertEqual(conv.le_prazo("2026-09-10"), "2026-09-10")

    def test_prazo_nao_definido_vira_vazio(self):
        for bruto in ("não definido ainda", "a definir", "em aberto", "", "-"):
            self.assertEqual(conv.le_prazo(bruto), "", f"falhou em {bruto!r}")

    def test_prazo_ilegivel_nao_vira_atraso(self):
        """Data que não parseia vira sem prazo — nunca uma data no passado."""
        self.assertEqual(conv.le_prazo("semana que vem"), "")

    def test_dependencias_separadas_por_ponto_e_virgula(self):
        self.assertEqual(conv.le_dependencias("E1.1.1; E2.3.1"), ["E1.1.1", "E2.3.1"])
        self.assertEqual(conv.le_dependencias("-"), [])
        self.assertEqual(conv.le_dependencias(""), [])


class TestRede(unittest.TestCase):
    def test_passos_de_uma_cadeia(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Primeira,,,,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Segunda,E1.1.1,,,Não iniciado",
            "Alta,1 · A,,,E1.1.3,Terceira,E1.1.2,,,Não iniciado",
        ))
        self.assertEqual([t["E1.1.1"]["passo"], t["E1.1.2"]["passo"],
                          t["E1.1.3"]["passo"]], [0, 1, 2])

    def test_travada_enquanto_predecessor_nao_conclui(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Primeira,,,,Em andamento",
            "Alta,1 · A,,,E1.1.2,Segunda,E1.1.1,,,Não iniciado",
        ))
        self.assertFalse(t["E1.1.1"]["travada"])
        self.assertTrue(t["E1.1.2"]["travada"])

    def test_pronta_quando_predecessor_concluiu(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Primeira,,,,Concluído",
            "Alta,1 · A,,,E1.1.2,Segunda,E1.1.1,,,Não iniciado",
        ))
        self.assertFalse(t["E1.1.2"]["travada"])
        self.assertTrue(t["E1.1.2"]["pronta"])

    def test_tarefa_sem_dependencia_nao_e_pronta(self):
        """'Pronta' significa destravada por um predecessor concluído. Uma
        tarefa que nunca dependeu de nada não entra nessa contagem."""
        t = por_cod(planilha("Alta,1 · A,,,E1.1.1,Solta,,,,Não iniciado"))
        self.assertFalse(t["E1.1.1"]["pronta"])

    def test_segura_conta_descendentes_indiretos(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Raiz,,,,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Meio,E1.1.1,,,Não iniciado",
            "Alta,1 · A,,,E1.1.3,Folha,E1.1.2,,,Não iniciado",
        ))
        self.assertEqual(t["E1.1.1"]["segura"], 2)
        self.assertEqual(t["E1.1.2"]["segura"], 1)
        self.assertEqual(t["E1.1.3"]["segura"], 0)

    def test_dependencia_para_codigo_inexistente_e_ignorada(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Só,E9.9.9,,,Não iniciado",
        ))
        self.assertEqual(t["E1.1.1"]["depende_de"], [])
        self.assertFalse(t["E1.1.1"]["travada"])

    def test_ciclo_nao_trava_o_conversor(self):
        t = por_cod(planilha(
            "Alta,1 · A,,,E1.1.1,Uma,E1.1.2,,,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Outra,E1.1.1,,,Não iniciado",
        ))
        self.assertEqual(len(t), 2)
        for x in t.values():
            self.assertIsInstance(x["passo"], int)


class TestResumo(unittest.TestCase):
    def test_gargalo_e_a_nao_concluida_que_mais_segura(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Raiz,,,,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Meio,E1.1.1,,,Não iniciado",
            "Alta,1 · A,,,E1.1.3,Folha,E1.1.2,,,Não iniciado",
            "Alta,2 · B,,,E2.1.1,Outra raiz,,,,Não iniciado",
            "Alta,2 · B,,,E2.1.2,Dependente,E2.1.1,,,Não iniciado",
        )
        r = conv.resume(tarefas)
        self.assertEqual(r["gargalo"]["cod"], "E1.1.1")
        self.assertEqual(r["gargalo"]["segura"], 2)

    def test_concluida_nao_e_gargalo(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Raiz,,,,Concluído",
            "Alta,1 · A,,,E1.1.2,Meio,E1.1.1,,,Não iniciado",
            "Alta,1 · A,,,E1.1.3,Folha,E1.1.2,,,Não iniciado",
        )
        r = conv.resume(tarefas)
        self.assertEqual(r["gargalo"]["cod"], "E1.1.2")

    def test_progresso_medio(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Uma,,,,Concluído",
            "Alta,1 · A,,,E1.1.2,Outra,,,,Não iniciado",
        )
        self.assertEqual(conv.resume(tarefas)["progresso_medio"], 50.0)

    def test_conta_sem_prazo(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Uma,,,10/09/2026,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Outra,,,não definido ainda,Não iniciado",
        )
        self.assertEqual(conv.resume(tarefas)["sem_prazo"], 1)


class TestAlertas(unittest.TestCase):
    def test_prazo_vencido_entra(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Atrasada,,,01/01/2026,Em andamento")
        a = conv.monta_alertas(tarefas, "2026-09-04")
        self.assertEqual([x["motivo"] for x in a], ["prazo vencido"])

    def test_sem_prazo_nunca_entra_como_atrasada(self):
        """A distinção que justifica o marcador 'não definido ainda'."""
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Sem data,,,não definido ainda,Em andamento")
        self.assertEqual(conv.monta_alertas(tarefas, "2026-09-04"), [])

    def test_concluida_com_prazo_vencido_nao_alerta(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Feita,,,01/01/2026,Concluído")
        self.assertEqual(conv.monta_alertas(tarefas, "2026-09-04"), [])

    def test_bloqueada_e_em_risco_entram(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Travada,,,,Bloqueado",
            "Alta,1 · A,,,E1.1.2,Arriscada,,,,Em risco",
        )
        motivos = [x["motivo"] for x in conv.monta_alertas(tarefas, "2026-09-04")]
        self.assertEqual(motivos, ["bloqueada", "em risco"])


class TestEixos(unittest.TestCase):
    def test_agrupa_e_calcula_progresso_por_eixo(self):
        tarefas = planilha(
            "Alta,1 · Gestão,,,E1.1.1,Uma,,,,Concluído",
            "Alta,1 · Gestão,,,E1.1.2,Outra,,,,Não iniciado",
            "Alta,3 · Patrimônio,,,E3.1.1,Terceira,,,,Em andamento",
        )
        eixos = conv.agrupa_por_eixo(tarefas)
        self.assertEqual([e["id"] for e in eixos], [1, 3])
        self.assertEqual(eixos[0]["progresso"], 50.0)
        self.assertEqual(eixos[0]["concluidas"], 1)
        self.assertEqual(eixos[1]["progresso"], 50.0)

    def test_nome_do_eixo_perde_o_numero(self):
        self.assertEqual(conv.nome_do_eixo("1 · Gestão e Participação Social"),
                         "Gestão e Participação Social")
        self.assertEqual(conv.nome_do_eixo("8 · Cultura Digital"), "Cultura Digital")


class TestSaida(unittest.TestCase):
    def test_nenhum_campo_interno_vaza(self):
        tarefas = planilha(
            "Alta,1 · A,,,E1.1.1,Uma,,,,Não iniciado",
            "Alta,1 · A,,,E1.1.2,Outra,E1.1.1,,,Não iniciado",
        )
        for t in tarefas:
            internos = [k for k in t if k.startswith("_")]
            self.assertEqual(internos, [], f"{t['cod']} vazou {internos}")


if __name__ == "__main__":
    unittest.main()


class TestPlanilhaVazia(unittest.TestCase):
    """A planilha começa vazia: o painel tem de aguentar esse estado."""

    def test_resumo_de_planilha_sem_tarefas(self):
        r = conv.resume([])
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["cadeia_mais_longa"], 0)
        self.assertEqual(r["progresso_medio"], 0)
        self.assertIsNone(r["gargalo"])

    def test_agrupamento_sem_tarefas(self):
        self.assertEqual(conv.agrupa_por_eixo([]), [])

    def test_alertas_sem_tarefas(self):
        self.assertEqual(conv.monta_alertas([], "2026-09-04"), [])

    def test_cadeia_de_um_passo(self):
        tarefas = planilha("Alta,1 · A,,,E1.1.1,Só uma,,,,Não iniciado")
        self.assertEqual(conv.resume(tarefas)["cadeia_mais_longa"], 1)


class TestCodigoResistenteAPlanilha(unittest.TestCase):
    """O Google Sheets converte "1.1.1" em data sem avisar, o que quebraria a
    rede de dependências em silêncio. O prefixo de letra evita isso."""

    def test_codigo_com_prefixo_e_aceito(self):
        self.assertEqual(conv.le_codigo("E1.1.1"), "E1.1.1")
        self.assertEqual(conv.le_codigo("PNC2.3.1"), "PNC2.3.1")

    def test_codigo_sem_prefixo_continua_valendo(self):
        """Planilhas antigas e as que formatam a coluna como texto seguem
        funcionando."""
        self.assertEqual(conv.le_codigo("1.1.1"), "1.1.1")

    def test_data_convertida_pela_planilha_nao_vira_codigo_silencioso(self):
        """Se alguém colar sem prefixo e a planilha converter, o código lido é
        a data — o que é visível no painel, e não um vínculo perdido."""
        self.assertEqual(conv.le_codigo("01/01/2001"), "")

    def test_cadeia_com_prefixo_funciona(self):
        t = por_cod(planilha(
            "Alta,3 · Patrimônio,,,E3.1.1,Levantar acervos,,,,Concluído",
            "Alta,3 · Patrimônio,,,E3.1.2,Definir crosswalk,E3.1.1,,,Não iniciado",
            "Alta,3 · Patrimônio,,,E3.1.3,Executar coleta,E3.1.2,,,Não iniciado",
        ))
        self.assertEqual(t["E3.1.2"]["passo"], 1)
        self.assertTrue(t["E3.1.2"]["pronta"])
        self.assertTrue(t["E3.1.3"]["travada"])
        self.assertEqual(t["E3.1.1"]["segura"], 2)

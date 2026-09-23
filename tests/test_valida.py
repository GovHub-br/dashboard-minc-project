# -*- coding: utf-8 -*-
"""Testes do validador do acervo."""

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import valida  # noqa: E402


def acervo_valido():
    """Um acervo mínimo que passa em todas as verificações."""
    artefatos = [
        {"nome": f"Artefato {i}", "antes": "Não entregue",
         "agora": "Entregue", "onde": "Anexo I"}
        for i in range(19)
    ]
    artefatos.append(
        {"nome": "Pendente", "antes": "Parcial", "agora": "Parcial", "onde": ""}
    )
    # Os 20 artefatos cabem no primeiro dos 19 produtos; o que se testa aqui é
    # o fechamento e a integridade do vínculo, não a distribuição real.
    produtos = [
        {"meta": "01", "num": i, "nome": f"Produto {i}", "redacao": "…",
         "meta_nome": "Meta de teste",
         "balanco": "…", "meta_nome": "Meta de teste", "estado": "",
         "cobertura": {"3": {"tipo": "secao", "onde": "Meta 01"}},
         "artefatos": []}
        for i in range(1, 20)
    ]
    produtos[0]["artefatos"] = [
        {"nome": a["nome"], "situacao": a["agora"], "evidencia": "TED",
         "nota": ""}
        for a in artefatos
    ]
    return {
        "origem": {
            "relatorio": "3º Relatório Parcial",
            "periodo": "maio a agosto de 2026",
            "apurado_em": "2026-08-31",
        },
        "relatorios": [
            {"num": 3, "rotulo": "3º Relatório", "data": "2026-08-31",
             "periodo": "maio a agosto de 2026"}
        ],
        "artefatos": artefatos,
        "pendencias": [
            {"artefato": "Pendente", "situacao": "Parcial",
             "falta": "x", "destrava": "y", "quem": "UnB"}
        ],
        "produtos": produtos,
        "documentos": [
            {"arquivo": "um.pdf", "anexo": "Anexo I", "url": "https://x/um.pdf"}
        ],
    }


class TestValida(unittest.TestCase):
    def test_acervo_valido_nao_tem_problema(self):
        self.assertEqual(valida.valida(acervo_valido()), [])

    def test_quadro_que_nao_fecha_em_vinte(self):
        a = acervo_valido()
        a["artefatos"].pop()
        problemas = valida.valida(a)
        self.assertTrue(any("20" in p for p in problemas))

    def test_artefato_duplicado(self):
        a = acervo_valido()
        a["artefatos"][1]["nome"] = a["artefatos"][0]["nome"]
        problemas = valida.valida(a)
        self.assertTrue(any("duplicado" in p.lower() for p in problemas))

    def test_entregue_sem_lastro(self):
        a = acervo_valido()
        a["artefatos"][0]["onde"] = ""
        problemas = valida.valida(a)
        self.assertTrue(any("lastro" in p.lower() for p in problemas))

    def test_entregue_como_proposta_tambem_exige_lastro(self):
        a = acervo_valido()
        a["artefatos"][0]["agora"] = "Entregue como proposta"
        a["artefatos"][0]["onde"] = ""
        problemas = valida.valida(a)
        self.assertTrue(any("lastro" in p.lower() for p in problemas))

    def test_pendencia_de_artefato_inexistente(self):
        a = acervo_valido()
        a["pendencias"][0]["artefato"] = "Não existe"
        problemas = valida.valida(a)
        self.assertTrue(any("inexistente" in p.lower() for p in problemas))

    def test_pendencia_com_situacao_divergente(self):
        a = acervo_valido()
        a["pendencias"][0]["situacao"] = "Entregue"
        problemas = valida.valida(a)
        self.assertTrue(any("diverge" in p.lower() for p in problemas))

    def test_carimbo_de_origem_ausente(self):
        a = acervo_valido()
        del a["origem"]["apurado_em"]
        problemas = valida.valida(a)
        self.assertTrue(any("apurado_em" in p for p in problemas))

    def test_carimbo_com_data_malformada(self):
        a = acervo_valido()
        a["origem"]["apurado_em"] = "31/08/2026"
        problemas = valida.valida(a)
        self.assertTrue(any("AAAA-MM-DD" in p for p in problemas))

    def test_acervo_real_passa(self):
        """O ted.json versionado tem de passar em todas as verificações."""
        acervo = json.loads((RAIZ / "dados" / "ted.json").read_text("utf-8"))
        self.assertEqual(valida.valida(acervo), [])


if __name__ == "__main__":
    unittest.main()


class TestProdutos(unittest.TestCase):
    def test_produtos_que_nao_fecham_em_dezenove(self):
        a = acervo_valido()
        a["produtos"].pop()
        problemas = valida.valida(a)
        self.assertTrue(any("19" in p for p in problemas))

    def test_cobertura_em_relatorio_inexistente(self):
        a = acervo_valido()
        a["produtos"][0]["cobertura"]["9"] = {"tipo": "secao", "onde": "x"}
        problemas = valida.valida(a)
        self.assertTrue(any("não consta de relatorios" in p for p in problemas))

    def test_cobertura_de_tipo_desconhecido(self):
        a = acervo_valido()
        a["produtos"][0]["cobertura"]["3"]["tipo"] = "talvez"
        problemas = valida.valida(a)
        self.assertTrue(any("talvez" in p for p in problemas))

    def test_cobertura_sem_localizacao(self):
        a = acervo_valido()
        a["produtos"][0]["cobertura"]["3"]["onde"] = ""
        problemas = valida.valida(a)
        self.assertTrue(any("sem dizer onde" in p for p in problemas))

    def test_artefato_sem_produto(self):
        a = acervo_valido()
        a["produtos"][0]["artefatos"].pop()
        problemas = valida.valida(a)
        self.assertTrue(any("não pertence a produto" in p for p in problemas))

    def test_artefato_em_dois_produtos(self):
        a = acervo_valido()
        a["produtos"][1]["artefatos"] = [a["produtos"][0]["artefatos"][0]]
        problemas = valida.valida(a)
        self.assertTrue(any("mais de um produto" in p for p in problemas))

    def test_situacao_do_produto_diverge_do_quadro(self):
        a = acervo_valido()
        a["produtos"][0]["artefatos"][0]["situacao"] = "Parcial"
        problemas = valida.valida(a)
        self.assertTrue(any("no produto e" in p for p in problemas))

    def test_produto_vincula_artefato_fora_do_quadro(self):
        a = acervo_valido()
        a["produtos"][1]["artefatos"] = [
            {"nome": "Fantasma", "situacao": "Entregue", "evidencia": "TED",
             "nota": ""}
        ]
        problemas = valida.valida(a)
        self.assertTrue(any("inexistente no quadro" in p for p in problemas))


class TestTabelaDeProdutos(unittest.TestCase):
    """A tabela de scripts/produtos.py contra o acervo publicado."""

    @classmethod
    def setUpClass(cls):
        import produtos
        cls.produtos = produtos
        cls.acervo = json.loads(
            (RAIZ / "dados" / "ted.json").read_text("utf-8")
        )

    def test_todo_artefato_do_quadro_tem_produto(self):
        self.assertEqual(
            self.produtos.sem_vinculo(self.acervo["artefatos"]), []
        )

    def test_dezenove_produtos_pactuados(self):
        self.assertEqual(len(self.produtos.PRODUTOS), 19)

    def test_todo_produto_tem_meta_conhecida(self):
        for p in self.produtos.PRODUTOS:
            self.assertIn(p["meta"], self.produtos.METAS_TED)

    def test_todo_produto_foi_tratado_em_algum_relatorio(self):
        for p in self.produtos.PRODUTOS:
            self.assertTrue(
                p["cobertura"],
                f"Meta {p['meta']} · Produto {p['num']} sem cobertura.",
            )

    def test_numeracao_de_produto_sem_buraco(self):
        por_meta = {}
        for p in self.produtos.PRODUTOS:
            por_meta.setdefault(p["meta"], []).append(p["num"])
        for meta, nums in por_meta.items():
            self.assertEqual(
                sorted(nums), list(range(1, len(nums) + 1)),
                f"Meta {meta} tem numeração de produto com buraco.",
            )

    def test_monta_devolve_os_vinte_artefatos(self):
        _, produtos = self.produtos.monta(self.acervo["artefatos"])
        total = sum(len(p["artefatos"]) for p in produtos)
        self.assertEqual(total, len(self.acervo["artefatos"]))

    def test_todo_produto_tem_balanco(self):
        for p in self.produtos.PRODUTOS:
            self.assertIn((p["meta"], p["num"]), self.produtos.BALANCO)

    def test_todo_risco_tem_produto(self):
        self.assertEqual(self.produtos.sem_produto(self.acervo["riscos"]), [])

    def test_todo_documento_tem_endereco(self):
        for d in self.acervo["documentos"]:
            self.assertTrue(d["url"].startswith(self.produtos.BASE_DOCUMENTOS))

    def test_estado_de_produto_dentro_da_lista(self):
        self.assertEqual(self.produtos.estados_invalidos(), [])

    def test_toda_linha_de_estado_corresponde_a_um_produto(self):
        chaves = {(p["meta"], p["num"]) for p in self.produtos.PRODUTOS}
        self.assertEqual(set(self.produtos.ESTADO), chaves)


class TestEstadoNoValidador(unittest.TestCase):
    def test_estado_em_branco_passa(self):
        a = acervo_valido()
        self.assertEqual(valida.valida(a), [])

    def test_estado_fora_da_lista_reprova(self):
        a = acervo_valido()
        a["produtos"][0]["estado"] = "Quase"
        problemas = valida.valida(a)
        self.assertTrue(any("fora da lista" in p for p in problemas))

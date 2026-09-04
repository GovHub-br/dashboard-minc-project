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
    return {
        "origem": {
            "relatorio": "3º Relatório Parcial",
            "periodo": "maio a agosto de 2026",
            "apurado_em": "2026-08-31",
        },
        "artefatos": artefatos,
        "pendencias": [
            {"artefato": "Pendente", "situacao": "Parcial",
             "falta": "x", "destrava": "y", "quem": "UnB"}
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

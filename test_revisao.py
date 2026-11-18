import json
from pathlib import Path
import subprocess
import sys
import unittest
from unicodedata import normalize

from app import run


class RevisaoTest(unittest.TestCase):
    def test_fichas_equivalentes_se_referem_a_mesma_fonte(self):
        ficha = dict(questao="Questão", tese="União", fonte="Edição", localizador="Seção")
        colada = {campo: normalize("NFD", valor) for campo, valor in ficha.items()}
        resultado = run(dict(referencia="João", registros=[colada, ficha]))
        self.assertEqual(resultado["teses_com_fonte_unica"], 1)
        self.assertEqual(resultado["questoes"], {
            "Questão": [{"tese": "União", "fontes": {"Edição": ["Seção"]}}],
        })

    def test_revisao_omite_questoes_sem_pendencias(self):
        ficha = dict(questao="A", tese="Leitura", fonte="Obra A", localizador="p. 1")
        dados = dict(referencia="João", registros=[
            ficha, dict(ficha, fonte="Obra B"), dict(ficha, questao="B"),
        ])
        self.assertEqual(list(run(dados)["questoes"]), ["A", "B"])
        revisao = run(dados, apenas_fonte_unica=True)
        self.assertEqual(list(revisao["questoes"]), ["B"])
        self.assertEqual(revisao["teses_com_fonte_unica"], 1)

    def test_cli_filtra_o_exemplo(self):
        root = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, root / "app.py", root / "exemplo.json", "--fonte-unica"],
            check=True, capture_output=True,
        )
        relatorio = json.loads(result.stdout)
        teses = [t for grupo in relatorio["questoes"].values() for t in grupo]
        self.assertEqual(len(teses), 1)
        self.assertEqual(len(teses[0]["fontes"]), 1)

    def test_recusa_objeto_vazio_no_lugar_da_lista(self):
        with self.assertRaisesRegex(ValueError, "lista"):
            run({"referencia": "João", "registros": {}})

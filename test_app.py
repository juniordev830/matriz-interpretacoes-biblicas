import json
from pathlib import Path
import subprocess
import sys
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['teses_com_fonte_unica'], 1)

    def test_cli_com_exemplo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), str(ROOT / "exemplo.json")],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)['teses_com_fonte_unica'], 1)

    def test_rejeita_dados_incompletos(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            run({})

    def test_mesma_fonte_nao_duplica_contagem(self):
        item = dict(questao="Questão", tese="Tese", fonte="Obra A", localizador="p. 1")
        result = run(dict(referencia="João 15", registros=[item, dict(item), dict(item, localizador="p. 2")]))
        self.assertEqual(result["teses_com_fonte_unica"], 1)
        self.assertEqual(result["questoes"]["Questão"][0]["fontes"], {"Obra A": ["p. 1", "p. 2"]})

    def test_duas_fontes(self):
        item = dict(questao="Questão", tese="Tese", fonte="A", localizador="p. 1")
        self.assertEqual(run(dict(referencia="João 15", registros=[item, dict(item, fonte="B")]))["teses_com_fonte_unica"], 0)

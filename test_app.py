from tempfile import TemporaryDirectory
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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

    def test_cli_aceita_json_com_bom(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-bom.json"
            arquivo.write_text(exemplo, encoding="utf-8-sig")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
        self.assertEqual(json.loads(result.stdout), run(json.loads(exemplo)))

    def test_cli_rejeita_chave_json_repetida(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8").lstrip()
        chave = next(iter(json.loads(exemplo)))
        conteudo = "{" + json.dumps(chave) + ": null," + exemplo[1:]
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-repetido.json"
            arquivo.write_text(conteudo, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8",
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Campo JSON repetido", result.stderr)


class JsonEstritoCliTest(unittest.TestCase):
    def test_cli_rejeita_constantes_numericas_nao_padronizadas(self):
        exemplo = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.json"
            for constante in ("NaN", "Infinity", "-Infinity"):
                with self.subTest(constante=constante):
                    exemplo["metadados"] = {"observacao": "CONSTANTE_TESTE"}
                    entrada.write_text(
                        json.dumps(exemplo).replace('"CONSTANTE_TESTE"', constante),
                        encoding="utf-8",
                    )
                    resultado = subprocess.run(
                        [sys.executable, str(ROOT / "app.py"), str(entrada)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(resultado.returncode, 2)
                    self.assertIn(constante, resultado.stderr)
                    self.assertEqual(resultado.stdout, "")


class MinimoFontesTest(unittest.TestCase):
    def dados(self):
        item = dict(questao="Q", tese="T1", fonte="A", localizador="1")
        return dict(referencia="João 15", registros=[item, dict(item, fonte="B"),
                    dict(item, tese="T2"), dict(item, tese="T2", localizador="2")])

    def test_filtra_fontes_distintas(self):
        from app import run
        resultado = run(self.dados(), minimo_fontes=2)
        self.assertEqual([t["tese"] for t in resultado["questoes"]["Q"]], ["T1"])
        self.assertEqual(resultado["teses_com_fonte_unica"], 1)

    def test_sem_resultado(self):
        from app import run
        self.assertEqual(run(self.dados(), minimo_fontes=3)["questoes"], {})

    def test_filtros_incompativeis(self):
        from app import run
        with self.assertRaises(ValueError):
            run(self.dados(), minimo_fontes=2, apenas_fonte_unica=True)

    def test_rejeita_minimo_invalido(self):
        from app import run
        for value in (0, -1, True, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run(self.dados(), minimo_fontes=value)

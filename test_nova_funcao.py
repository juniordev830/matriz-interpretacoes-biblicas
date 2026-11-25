import unittest
from app import run
class Pesquisa(unittest.TestCase):
    def test_filtro(self):
        data={"referencia":"Jo 15","pesquisa":"uniao","registros":[{"questao":"União com Cristo","tese":"A","fonte":"F","localizador":"p. 1"},{"questao":"Fruto","tese":"B","fonte":"F","localizador":"p. 2"}]}
        result=run(data)
        self.assertEqual(list(result["questoes"]),["União com Cristo"])
        self.assertEqual(result["teses_com_fonte_unica"],1)
        data["pesquisa"]="inexistente"
        self.assertEqual(run(data)["questoes"],{})

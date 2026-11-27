import csv


def celula(valor):
    """Mantém texto com aparência de fórmula como texto em planilhas."""
    if not isinstance(valor, str):
        return valor
    prefixos = ("=", "+", "-", "@", "＝", "＋", "－", "＠")
    if valor.lstrip().startswith(prefixos) or valor.startswith(("\t", "\r", "\n")):
        return "'" + valor
    return valor


def linhas(relatorio):
    for questao, teses in relatorio["questoes"].items():
        for ficha in teses:
            for fonte, locais in ficha["fontes"].items():
                for local in locais:
                    yield relatorio["referencia"], questao, ficha["tese"], fonte, local


def escrever_csv(relatorio, destino):
    escritor = csv.writer(destino, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(('referencia', 'questao', 'tese', 'fonte', 'localizador'))
    for linha in linhas(relatorio):
        escritor.writerow([celula(valor) for valor in linha])

'Agrupe teses de leitura por questão e identifique quais têm apenas uma fonte cadastrada.'


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


def run(data):
    questoes = {}
    for item in data["registros"]:
        questao, tese = texto(item["questao"]), texto(item["tese"])
        fonte, local = texto(item["fonte"]), texto(item["localizador"])
        ficha = questoes.setdefault(questao, {}).setdefault(tese, {})
        ficha.setdefault(fonte, set()).add(local)
    matriz = {questao: [{"tese": tese, "fontes": {f: sorted(ls) for f, ls in fontes.items()}}
                        for tese, fontes in teses.items()]
              for questao, teses in questoes.items()}
    unica = sum(len(fontes) == 1 for teses in questoes.values() for fontes in teses.values())
    return {"referencia": texto(data["referencia"]), "questoes": matriz,
            "teses_com_fonte_unica": unica}


import argparse
import json
from pathlib import Path


def objeto_sem_campos_repetidos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo JSON repetido: {chave!r}.")
        objeto[chave] = valor
    return objeto


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(source, object_pairs_hook=objeto_sem_campos_repetidos)
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

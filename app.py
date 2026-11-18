'Agrupe teses de leitura por questão e identifique quais têm apenas uma fonte cadastrada.'

from unicodedata import normalize


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return normalize("NFC", value.strip())


def run(data, *, apenas_fonte_unica=False):
    if not isinstance(data, dict) or not isinstance(data.get("registros"), list):
        raise ValueError("O campo registros deve ser uma lista de fichas.")
    questoes = {}
    for numero, item in enumerate(data["registros"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"A ficha {numero} deve ser um objeto.")
        questao, tese = texto(item["questao"]), texto(item["tese"])
        fonte, local = texto(item["fonte"]), texto(item["localizador"])
        ficha = questoes.setdefault(questao, {}).setdefault(tese, {})
        ficha.setdefault(fonte, set()).add(local)
    matriz = {}
    unica = 0
    for questao, teses in questoes.items():
        for tese, fontes in teses.items():
            if len(fontes) == 1:
                unica += 1
            elif apenas_fonte_unica:
                continue
            ficha = {"tese": tese, "fontes": {f: sorted(locais) for f, locais in fontes.items()}}
            matriz.setdefault(questao, []).append(ficha)
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


def rejeitar_constante_json(constante):
    raise ValueError(f"Constante numérica inválida em JSON: {constante}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    parser.add_argument("--fonte-unica", action="store_true",
                        help="Mostrar apenas as teses com uma única fonte cadastrada")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(
                source,
                object_pairs_hook=objeto_sem_campos_repetidos,
                parse_constant=rejeitar_constante_json,
            )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data, apenas_fonte_unica=args.fonte_unica)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

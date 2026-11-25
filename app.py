'Agrupe teses de leitura por questão e identifique quais têm apenas uma fonte cadastrada.'

from unicodedata import combining, normalize


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
    pesquisa = data.get("pesquisa")
    def chave(value):
        return "".join(c for c in normalize("NFKD", texto(value).casefold()) if not combining(c))
    termo = chave(pesquisa) if pesquisa is not None else None
    matriz = {}
    unica = 0
    for questao, teses in questoes.items():
        if termo is not None and termo not in chave(questao):
            continue
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
from contextlib import nullcontext
import sys
from relatorio_csv import escrever_csv
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


MAX_JSON_BYTES = 1_000_000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Arquivo JSON com os dados ou - para a entrada padrão")
    parser.add_argument("--fonte-unica", action="store_true",
                        help="Mostrar apenas as teses com uma única fonte cadastrada")
    parser.add_argument("--csv", action="store_true", help="Exportar as teses com suas fontes e localizadores em CSV")
    args = parser.parse_args()

    try:
        entrada = nullcontext(sys.stdin.buffer) if args.entrada == "-" else Path(args.entrada).open("rb")
        with entrada as source:
            raw = source.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError("JSON excede o limite de 1 MB.")
        data = json.loads(
            raw.decode("utf-8-sig"),
                object_pairs_hook=objeto_sem_campos_repetidos,
                parse_constant=rejeitar_constante_json,
            )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data, apenas_fonte_unica=args.fonte_unica)
    except RecursionError:
        parser.exit(2, "O JSON tem níveis de aninhamento demais.\n")
    except (KeyError, TypeError, ValueError, UnicodeError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if args.csv:
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

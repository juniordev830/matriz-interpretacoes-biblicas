# Matriz de interpretações bíblicas

Agrupe teses de leitura por questão e identifique quais têm apenas uma fonte cadastrada.

## Rodar

Python 3.10 ou mais recente. Cada execução lê um JSON local e imprime outro JSON no terminal.

```bash
python app.py exemplo.json
python -m unittest -v
```

## Uso

Informe a questão, a tese em termos próprios, a fonte e o localizador. Use a mesma formulação para anotações sobre uma mesma tese. Compare argumentos e contexto antes de decidir sua leitura.

## Fontes e exemplos

Os exemplos incluem referências bíblicas, perguntas e anotações de demonstração. Consulte o texto e o contexto em uma [tradução publicada pela Sociedade Bíblica do Brasil](https://www.sbb.org.br/traducoes-da-biblia). Para aprofundar, o catálogo da [Nova Bíblia de Estudo Almeida](https://www.sbb.org.br/nova-almeida/biblias-de-estudo/biblia-de-estudo-almeida) e o do [Comentário Bíblico Pentecostal do Novo Testamento, CPAD](https://www.cpad.com.br/comentario-biblico-pentecostal-novo-testamento-/p) ajudam a identificar edições. Registre as páginas verificadas na sua própria consulta.

## Estado do projeto

Versão inicial funcional por linha de comando, sem interface web. Usa apenas a biblioteca padrão do Python. Os testes executam os exemplos e verificam as regras do projeto.

A contagem considera os nomes de fontes informados; não verifica independência editorial nem valida conclusões teológicas.

## Revisar teses com uma única fonte

Execute `python app.py exemplo.json --fonte-unica` para listar apenas as teses
que precisam de uma segunda referência, com a obra e os localizadores já
anotados. Questões sem teses nessa condição ficam fora da lista. Acentos
equivalentes em textos colados de editores diferentes contam como a mesma
grafia. Edições com nomes diferentes continuam separadas.

## Exportação para planilha

Use `python app.py exemplo.json --csv > relatorio.csv` para exportar as teses com suas fontes e localizadores. O CSV usa ponto e vírgula, conserva a ordem do relatório e inclui o cabeçalho mesmo quando a seleção está vazia. O JSON continua sendo a saída padrão.

Também é possível encadear a ferramenta com outro comando usando `-` como entrada. Exemplo em um terminal Bash:

```bash
cat exemplo.json | python app.py -
```

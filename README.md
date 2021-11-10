<img src="img/path28.png" alt="HHDB Logo">

<br>

# Ferramenta heurística para a Hemeroteca Digital Brasileira - H_HDB

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

Ferramenta de auxílio metodológico para pesquisa na [Hemeroteca Digital Brasileira](memoria.br.br) da Biblioteca Nacional.

Desenvolvida por [Eric Brasil](ericbrasiln.github.io) como parte de pesquisa acadêmica da área de História Digital.

>Essa ferramenta não possui fins lucrativos nem predende acessar dados sigilosos ou alterar informações nos servidores da instituição.

***

## Índice

- [Ferramenta heurística para a Hemeroteca Digital Brasileira - H_HDB](#ferramenta-heurística-para-a-hemeroteca-digital-brasileira---h_hdb)
  - [Índice](#índice)
  - [Introdução](#introdução)
  - [Instalação](#instalação)
    - [Python](#python)
      - [Bibliotecas e módulos](#bibliotecas-e-módulos)
  - [Definindo os parâmetros da busca](#definindo-os-parâmetros-da-busca)
  - [Resultados](#resultados)
  - [Como citar?](#como-citar)
  - [Agradecimentos](#agradecimentos)
  - [Licença](#licença)

## Introdução

Tem como objetivo auxilixar pesquisadores e pesquisadoras no processo de documentação e registro preciso das etapas de pesquisa e garantir o rigor metodológico. Portanto, é uma ferramenta heurística digital.

Seu desenvolvimento está no âmbito das pesquisas realizadas no curso de História do IHLM/Unilab e do [LABHDUFBA](http://www.labhd.ufba.br).

Os resultados da pesquisa serão publicados em artigo científico avaliado por pares e seu código e documentação serão disponibilizados publicamente, com [licença MIT](LICENSE).

Buscamos não sobrecarregar os servidores da Biblioteca Nacional e respeitar os termos de uso. 

***

## Instalação

### Python

Essa ferramenta foi escrita em [Python 3.9](https://www.python.org/). Esta é uma linguagem de programação que te permite trabalhar rapidamente e integrar diferentes sistemas com maior eficiência.

Para executar o arquivo `.py` é preciso instalar o Python3 em seu computador.

[Clique aqui](https://python.org.br/instalacao-windows/) para um tutorial de instalação do Python no Windows, [clique aqui](https://python.org.br/instalacao-linux/) para Linux e [clique aqui](https://python.org.br/instalacao-mac/)
para Mac.

Após a instalação, vc pode executar o arquivo .py direto do prompt de comando do Windows ou pelo terminal do Linux, ou utilizar as diversas [IDE](https://pt.wikipedia.org/wiki/Ambiente_de_desenvolvimento_integrado) disponíveis.

Exemplo de como executar utilizando o terminal do Linux, após instalar o Python3.8:

1. Acesse o diretório em que o arquivo .py está salvo:
   ```sh
   $ cd user/local
   ```
1. Instale as bibliotecas requeridas:
   ```sh
   $ pip3 install -r requirements.txt
   ```
1. Execute o arquivo usando Python3.8
   ```sh
   $ python3 h_hdb.py
   ```
#### Bibliotecas e módulos

- **urllib.requests**: módulo do Python que ajuda a acessar urls.
[Saiba mais.](https://docs.python.org/pt-br/3/library/urllib.request.htmll)
- **Selenium**: o [Selenium](https://www.selenium.dev/documentation/en/) é um conjunto de ferramentas para automatização de utilização de navegadores.
- **webdriver.manager**: biblioteca que auxilia na instalação e configuração dos drivers de navegadores. [Daiba mais](https://pypi.org/project/webdriver-manager/)
- **pandas**: [Pandas](https://pandas.pydata.org/) é uma biblioteca escrita em Python para manipulação e análise de dados. 

***

## Definindo os parâmetros da busca

Nessa versão do programa, a busca inicial é estabelecida pela opção local. 

``` 
1- Local
Orientações para busca:
      - O termo deve ser idêntico às opções listadas na página da HDB;
      - Esse parâmetro é case sensitive;
Digite o local de busca: 
``` 
É possível incluir uma opção de recorte temporal em seguida. 

```
2 - Período
Orientações para busca:
      - O recorte deve ser escerito de forma idêntica às opções listadas na página da HDB;
      - É possível buscar todos os periódicos digitando `Todos`
Digite o período de busca: 
``` 
A busca será efetuada em todos os acervos existentes para essa configuração (`3 - Periódico: Todos`), após a inclusão do termo da busca.

```
4 - Termo da busca
Orientações para busca:
      - Coloque o termo entre aspas duplas para espressões exatas;
      - Não use acentos;
      - Não mais que três palavras
Digite o termo de busca:
```

Portanto, a busca foi elaborada a partir das demandas de pesquisa e interesses pessoais e serão explicadas detalhadamente em artigo. 

A partir dos parâmetros de busca definidos pelo usuário, o programa retorna todos os acervos dos jornais com alguma ocorrência, até o limite de 100 jornais (ou seja, a segunda página de resultados).

***

## Resultados

O programa retorna os seguintes resultados:

1. Cria diretórios de armazenamento: `HDB/{termo da busca}/{data da busca}/`

2. `CSV`: Cria um diretório `HDB/{termo da busca}/{data da busca}/CSV` e, dentro dele, salva arquivo csv contendo os seguintes dados para cada ocorrência: `Termo da busca, Data da Busca, Acervo, Ano, Edição, Página, Nome do arquivo, Link`.

3. `RELATÓRIOS`: Cria um diretório `HDB/{termo da busca}/{data da busca}/RELATÓRIOS` e salva nele relatórios de busca para cada pesquisa.
   - GERAL: Com os dados gerais da pesquisa
        ``` 
        - Data e hora da busca
        - Local da busca
        - Período da busca
        - Periódico da busca: 
        - Termo da busca
        - Lista de acervos com ocorrências (máx. de 100) e quantidade de ocorrências
        - Total de acervos com ocorrências (máx. de 100)
        - Informações adicionais: Total de páginas pesquisadas; Total de acervos pesquisados; Total de ocorrências e Frequência de ocorrências por página.
        ```
        O título do arquivo tem o seguinte padrão: `GERAL_{termo da pesquisa}_{data e hora da busca}.txt`
   - Acervo: Com os dados de cada acervo
        ``` 
        - Data e hora da busca
        - Termo da busca
        - Acervo
        - Total de ocorrências
        - Link da lista de resultados
        ```
        O título do arquivo tem o seguinte padrão: `relatório_{nome do acervo}_{número do acervo}_{data e hora da busca}.txt`
   - ERRO: registra acervos que não puderam ser raspados
        ``` 
        - Data e hora da busca
        - Termo da busca
        - Acervo com ocorrência que não pode ser acessado
        ```
        O título do arquivo tem o seguinte padrão: `ERRO_{número do acervo}_{data e hora da busca}.txt`
   - INFORMAÇÕES GERAIS: registra dados gerais relativo ao quantitativo de acervos e páginas pesquisadas na busca e a quantidade de ocorrências, assim como a frequência de ocorrências por página.
        - Acervo
        - Total de Páginas
        - Total de Ocorrências
        - Frequência de ocorrências X páginas. 
        O título do arquivo tem o seguinte padrão: `{infos_acervos}_{período}_{page01 ou 02}.csv`
4. `ARQUIVOS_IMG`: Cria um diretório `HDB/{termo da busca}/{data da busca}/ARQUIVOS_IMG`e salva as imagens das páginas com ocorrências. O nome do arquivo é a combinação no número do acervo com o número geral da página. Ex: `168319_02_12603.jpg`

Estrutura de diretórios:

```
HDB
├── {termo da busca}
│   ├── {data}
│   │   ├── CSV
│   │   ├── RELATÓRIOS
│   │   ├── ARQUIVOS_IMG
```

***

## Como citar?

```
@misc{h_hdb2021,
  author = {Eric Brasil},
  title = {Ferramenta heurística para a Hemeroteca Digital Brasileira - H_HDB},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ericbrasiln/h_hdb}}
  note = {Online; accessed 10 Oct 2021}
}
```

***

## Agradecimentos

Agradeço ao LABHDUFBA pela parceria e possibilidades de aprendizado e desenvolvimento de ferramentas e reflexões para a pesquisa em história e humanidades digitais.

A **H_HDB** não seria possível sem a participação ativa de Leonardo F. Nascimento e Gabriel Andrade.

***

## Licença

MIT LICENSE

Copyright (c) 2021 [Eric Brasil](https://ericbrasiln.github.io/)
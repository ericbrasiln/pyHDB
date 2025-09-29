'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Ferramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).
Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.
Com esse script é possível pesquisar por uma lista de acervos específicos.
license: MIT
Python 3.11.9
email: ericbrasiln@protonmail.com
'''
# Importação de bibliotecas, módulos e funções
from scrape import scrapeDados
from reports import report_search_bib
from csv_final import df_final
from datetime import datetime
import os
import csv

CACHE_DIR_NAME = ".cache"  # ficará dentro de HDB/<termo>/<data>/.cache

def _last_occurrence_from_csv(csv_path: str) -> int:
    """
    Retorna o número da última ocorrência salva no CSV de cache,
    contando linhas de dados (exclui o cabeçalho).
    """
    if not os.path.exists(csv_path):
        return 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) <= 1:
            return 0
        return len(rows) - 1


# Define data e horário de início
now = datetime.now()
date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

# Imprimir informações gerais sobre o programa
print('=-' * 30)
print('\033[1;36mpyHDB - \033[0m\033[3;36mFerramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).\033[0m\n'
    '\n- Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.\n'
    '\n- Essa ferramenta não possui fins lucrativos nem pretende acessar dados sigilosos ou alterar \n'
    'informações nos servidores da instituição.\n'
    '\n- Tem como objetivo auxiliar pesquisadores e pesquisadoras a registrarem com precisão as '
    'etapas de sua pesquisa e garantir o rigor metodológico. Portanto, é uma ferramenta heurística digital.\n'
    '\n- Seu desenvolvimento está no âmbito das pesquisas realizadas no curso de História do IHLM/Unilab '
    'e do LABHDUFBA.\n'
    '\n- Esse script analisa um acervo, ou uma lista de acervos, definidas pelo usuário. Foi pensado para sanar\n'
    'erros no processo de raspagem que podem acontecer, principalmente em buscas com milhares de ocorrências.')
print('=-' * 30)

# Definição da lista de acervos
bibs_list = []
while True:
    bibs_list.append(str(input('Digite a numeração do acervo que deseja buscar: ')).strip())
    answer = str(input('Deseja inserir outro acervo? [S/N] ')).strip()
    if answer in 'Nn':
        print('-=-'*50)
        break

print('\n\033[4;36m- Termo da busca\033[0m')
print('Orientações para busca:\n'
      '- Coloque o termo entre aspas duplas para expressões exatas;\n'
      '- Não use acentos ou caracteres especiais;\n'
      '- É recomendado não utilizar mais do que três palavras.\n')
search_term = str(input('Digite o termo de busca: '))

# 1) Formato de saída
print('\n\033[4;36m1 - Formato de saída\033[0m')
print('1 - CSV (padrão)\n2 - CSV e JSON')
try:
    output_mode = int(input('Escolha o formato [1/2]: ') or '1')
    if output_mode not in (1, 2):
        print('Opção inválida. Usando padrão: 1 - CSV.')
        output_mode = 1
except Exception:
    output_mode = 1

# 2) Download de imagens
print('\n\033[4;36m2 - Download de imagens\033[0m')
print('Deseja baixar as imagens das páginas encontradas?\n'
      '- Responda "s" para baixar imagens (padrão);\n'
      '- Responda "n" para coletar apenas metadados (sem imagens).')
resp_img = input('Baixar imagens? [S/n]: ').strip().lower()
download_imagens = False if resp_img == 'n' else True
if not download_imagens:
    print('\033[1;33m[Modo metadados]\033[0m As imagens não serão baixadas; somente metadados serão coletados.')

# Adequar o termo da busca para ser usado na URL e nos caminhos
search_url = search_term.replace(' ', '%20')
safe_search = search_term.replace('"', '').replace(' ', '-')

# Criar estrutura: HDB/<termo>/<data>/{CSV,.cache}
base_path = os.path.join('HDB', os.path.join(safe_search, date))
os.makedirs(base_path, exist_ok=True)
csv_path = os.path.join(base_path, 'CSV')
os.makedirs(csv_path, exist_ok=True)
cache_dir = os.path.join(base_path, CACHE_DIR_NAME)
os.makedirs(cache_dir, exist_ok=True)

# Relatório geral para a lista de acervos (uma vez)
report_search_bib(base_path, safe_search, date_time, bibs_list)

# Iterar na lista de acervos
for final_bib in bibs_list:
    url = f"http://memoria.bn.br/docreader/docreader.aspx?bib={final_bib}&Pesq={search_url}"
    csv_name = os.path.join(csv_path, f"{safe_search}_{final_bib}.csv")
    cache_name = os.path.join(cache_dir, f"{safe_search}_{final_bib}.csv")

    # Se já existe o CSV final do acervo, segue para o próximo
    if os.path.exists(csv_name):
        print(f'[Skip] CSV final já existe para {final_bib}: {csv_name}')
        continue

    # Retomada via cache
    if os.path.exists(cache_name):
        last = _last_occurrence_from_csv(cache_name)
        start_from = last + 1
        print(f"[Retomada] Cache detectado ({cache_name}). Última ocorrência = {last}. Retomando em {start_from}.")
        scrapeDados(
            url, safe_search, final_bib, base_path, date, date_time,
            start_from=start_from, download_imagens=download_imagens
        )
    else:
        scrapeDados(
            url, safe_search, final_bib, base_path, date, date_time,
            start_from=1, download_imagens=download_imagens
        )

# Consolidação final (CSV + opcional JSON/JSONL)
df_final(csv_path, safe_search, output_mode=output_mode)
print('\n\033[1;36m=-=-=-=-=-Fim da raspagem (lista de acervos).=-=-=-=-=-\033[0m\n')

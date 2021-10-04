'''
title: H_HDB
author: Eric Brasil
description: Ferramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).
Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.
Com esse script é possível pesquisar por uma lista de acervos específicos.
license: MIT
Python 3.9.5
email: ericbrasiln@protonmail.com
'''
# Importação de bibliotecas, módulos e funções
from scrape import scrapeDados
from reports import report_search_bib
import os
from datetime import datetime
import pandas as pd
from csv_final import df_final

# Define data e horário de início
now = datetime.now()
date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
# Cria lista final para inserção dos dados que serão salvos no CSV
final_list = []

# Definição da lista de acervos
bibs_list= list()
while True:
    bibs_list.append(str(input('Digite a numeração do acervo que deseja buscar: ')))
    answer = str(input('Deseja inserir outro acervo? [S/N] '))
    if answer in 'Nn':
        print('-=-'*50)
        break
print('\n - Termo da busca')
print('Orientações para busca:\n'
      '- Coloque o termo entre aspas duplas para espressões exatas;\n'
      '- Não use acentos;\n'
      '- Não mais que três palavras\n')
search_term = str(input('Digite o termo de busca: '))

# Adequar o termo da busca para ser usado na url
search = search_term.replace(' ','%20')
search_alt = search_term.replace('"','')
search_alt = search_alt.replace(' ', '-')
final_search = os.path.join(search_alt, date)
# Criar pasta de armazenamento e conferência se a mesma já existe
directory = os.path.join('HDB', final_search)
if not os.path.exists(directory):
    os.makedirs(directory)  
else:
    print('pasta já existe.')
# Iterar na lista de acervos
for final_bib in bibs_list:
    url = "http://memoria.bn.br/docreader/docreader.aspx?bib=" + final_bib + "&Pesq=" + search
    # Chamar função para criar o relatório geral da busca por lista de acervos.
    report_search_bib(directory, search_alt, date_time, bibs_list)
    # Chamar função para raspar os dados
    scrapeDados(url, search_alt, final_bib, directory, date, date_time)
# Chamar função para criar csv final
csv_path = os.path.join(directory, 'CSV')
df_final(csv_path, search_alt)  
 
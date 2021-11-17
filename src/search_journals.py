'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas à busca em cada acervo da lista de acervos com ocorrências.
'''
from scrape import*
from csv_final import*
from datetime import datetime
import os

def journal_search(list_of_bibs, date, search_term, directory):
    '''
    Função para realizar a busca em cada acervo da lista de acervos com ocorrências e criar o csv final
    '''
    final_list = []
    # Lista com numeração dos jornais a serem pesquisados
    search = search_term.replace(' ','%20')
    search = search.replace('"','\"')
    # Iterção na lista de acervos
    for journal in list_of_bibs:
        # if csv of acervo exists pass
        search_term = search_term.replace('"','')
        search_term = search_term.replace(' ','-')
        csv_path = os.path.join(directory, 'CSV')
        csv_name = os.path.join(csv_path, search_term + '_' + journal + '.csv')
        if os.path.exists(csv_name):
            print('CSV já existe, passando para próximo acervo...')
            pass
        else:
            # Define a data e a hora
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            # Criação do caminho de armazenamento e conferência se a mesma já existe
            search_name_path = os.path.join(search_term, date)
            directory = os.path.join('HDB', search_name_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            url = "http://memoria.bn.br/docreader/docreader.aspx?bib=" + journal + "&Pesq=" + search
            # Função para raspar os dados
            scrapeDados(url, search_term, journal, directory, date, date_time)
    # Chamar função para criar o csv final
    df_final(csv_path, search_term)

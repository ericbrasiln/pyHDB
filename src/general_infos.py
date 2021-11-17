'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas à coleta de informações gerais da busca.
'''
import pandas as pd
import os
from bs4 import BeautifulSoup

def get_infos(driver):
    '''
    Função para coletar informações gerais da busca: Total de páginas analisadas,
    Total de Acervos analisados, Total de Ocorrências, Frequência de Ocorrências X Páginas.
    '''
    # Criar dicionário para armazenar as informações
    infos = {}
    # Usar BeautifulSoup para pegar o conteúo
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    totals_div = soup.find('div', id='totaisdiv')
    div_pages = totals_div.find('div', id='paginastotdiv')
    total_pages = div_pages.find('span', id='PaginasTotalLbl').text
    div_acervos = totals_div.find('div', id='acervostotdiv')
    total_acervos = div_acervos.find('span', id='AcervosTotalLbl').text
    div_occur = totals_div.find('div', id='ocortotdiv')
    total_occur = div_occur.find('span', id='OcorTotalLbl').text
    # Substituir '.' por ''
    int_pages = int(total_pages.replace('.', ''))
    int_occur = int(total_occur.replace('.', ''))
    # Calcular frequência de ocorrências
    freq_occur = int_pages / int_occur
    # Adicionar as informações ao dicionário
    infos['Total de páginas analisadas'] = total_pages
    infos['Total de Acervos analisados'] = total_acervos
    infos['Total de ocorrências encontradas'] = total_occur
    infos['Frequência de Ocorrências por Página'] = freq_occur
    return infos 

def get_infos_acervos(driver, directory, period, page):
    '''
    Função para coletar informações gerais de cada acervo: Total de páginas analisadas,
    Total de Acervos analisados, Total de Ocorrências, Frequência de Ocorrências X Páginas.
    '''
    # Criar lista para armazenar as informações
    infos_acervos_final = []
    # Encontrar tbody usando XPATH
    tbody = driver.find_element_by_xpath('//*[@id="ListaRadGrid_ctl00"]/tbody')
    # Encontrar todos os tr e iterar
    trs = tbody.find_elements_by_tag_name('tr')
    for tr in trs:
        tds = tr.find_elements_by_tag_name('td')
        acervo = tds[0].text
        total_pages = tds[1].text
        total_occur = tds[2].text
        if total_occur == '0':
            pass
        else:
            # Calcular frequência de ocorrências
            freq_occur = int(total_pages) / int(total_occur)
            # Lista para armazenar as informações e adicionar ao final da lista
            infos_acervos = [acervo, total_pages, total_occur, freq_occur]
            infos_acervos_final.append(infos_acervos)             
    # Criar diretório para armazenar os dados
    csv_path = os.path.join(directory, 'RELATÓRIOS')
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    csv_name = os.path.join(csv_path, f'infos_acervos_{period}_{page}.csv')
    # Criar arquivo CSV usando pandas
    df = pd.DataFrame(infos_acervos_final, columns=['Acervo', 'Total de Páginas', 'Total de Ocorrências', 'Frequência de ocorrências X páginas'])
    df.to_csv(csv_name, index=False)

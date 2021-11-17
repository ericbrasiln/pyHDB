'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas ao tratamento das listas de acervos a serem pesquisados.
'''
import re, time
from general_infos import get_infos_acervos

def get_bibs(driver, search, directory, period):
    '''
    Função para as numerações dos acervos (bibs) com ocorrências da busca.
    '''
    list_of_bibs = driver.find_elements_by_id('BibMaisButton')
    l_bibs = []
    for bib in list_of_bibs:
        value = bib.get_attribute('onmouseover')
        value1 = value.replace('javascript:showMenu(event,','')
        bib_final = value1.replace(');','')
        if '"0"' in bib_final:
            pass
        else:
            l_bibs.append(bib_final)
            #chama a função para encontrar infos gerais dos acervos
            get_infos_acervos(driver, directory, period, 'page01')
    if len(l_bibs) == 50:
        next_btn = driver.find_element_by_xpath('//*[@id="ListaRadGrid_ctl00"]/tfoot/tr/td/div/div[3]/button[1]').click()
        time.sleep(2)
        list_of_bibs = driver.find_elements_by_id('BibMaisButton')
        for bib in list_of_bibs:
            value = bib.get_attribute('onmouseover')
            value1 = value.replace('javascript:showMenu(event,','')
            bib_final = value1.replace(');','')
            if '"0"' in bib_final:
                pass
            else:
                l_bibs.append(bib_final)
                #chama a função para encontrar infos gerais dos acervos
                get_infos_acervos(driver, directory, period, 'page02')
    return l_bibs

def bib_list(bibs):
    '''
    Função para tratar a lista de acervos coletada na página de resultados da busca.
    '''
    l_bibs = []
    for i in bibs:
        bib = i.replace('"','')
        bib2 = re.sub("(,)(\d+)","", bib)
        l_bibs.append(bib2)
    return l_bibs

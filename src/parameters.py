'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas à definição de parâmetros para a pesquisa
'''
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

def set_place(driver, local):
    '''
    Função para encontrar e enviar o parâmetro Local
    '''
    # Encontrar e clicar na seta para abrir as opções de 'locais'
    local_arrow = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="UFCmb3_Arrow"]'))).click()
    in_local = driver.find_element(By.ID, 'UFCmb3_DropDown')
    time.sleep(2)
    try:
        # Encontrar o parâmetro do local a ser pesquisado
        estado = driver.find_element(By.XPATH, f"//*[text()='{local}']").click()
        time.sleep(2)
    except:
        print('\033[3;91m Local não encontrado!\033[0m\n\
        Verifique se o local foi digitado corretamente de acordo com a listagem no site da HDB \033[91m'+'<memoria.bn.br>'+ '\033[0m e tente novamente.')
        exit()

def set_time(driver, periodo):
    '''
    Função para encontrar o parâmetro período
    '''
    # Encontrar e clicar no box para abrir as opções de 'período'
    time_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PeriodoCmb3_Input"]')))
    time_box.click()
    time.sleep(3)
    periodo_Box = driver.find_element(By.ID, 'PeriodoCmb3_DropDown')
    # Encontrar o parâmetro do período a ser pesquisado
    try:
        time_op = driver.find_element(By.XPATH, f"//*[contains(text(), '{periodo}')]").click()
        time.sleep(3)
    except:
        print('\033[3;91m Período não encontrado!\033[0m\n\
        Verifique se o período foi digitado corretamente de acordo com a listagem no site da HDB \033[91m'+'<memoria.bn.br>'+ '\033[0m e tente novamente.')
        exit()

def set_journal(driver, periodico):
    '''
    Função para encontrar o parâmetro periódico
    '''
    # Encontrar e clicar na seta para abrir as opções de 'periódico' 
    p_arrow = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PeriodicoCmb3"]/span/button')))
    time.sleep(3)
    periodico_box = driver.find_element(By.ID, 'PeriodicoCmb3_DropDown')
    # Encontrar o parâmetro do periódico a ser pesquisado
    click_per = driver.find_element(By.XPATH, f"//*[contains(text(), '{periodico}')]")
    time.sleep(2)

def set_search(driver, search_term):
    '''
    Função para inserir o termo de busca
    '''
    # Enviar os dados para a caixa de busca'
    search_box =  driver.find_element(By.XPATH, '//*[@id="PesquisaTxt3"]')
    search_box.click()
    search_box.send_keys(search_term)
    time.sleep(2)
    

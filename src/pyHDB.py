"""
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Ferramenta de auxílio metodológico para pesquisa na Hemeroteca
Digital Brasileira (BN).
Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de
História Digital.
license: MIT
Python 3.9.5
email: ericbrasiln@proton.me
"""
# Importação de bibliotecas, módulos e funções
from parameters import set_journal, set_place, set_search, set_time
from validate_period import validate_period
from bibs import get_bibs, bib_list
from search_journals import journal_search
from reports import *
from general_infos import get_infos
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Definição de variáveis globais: url e data
url = 'http://memoria.bn.br/hdb/'
now = datetime.now()
date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

# Imprimir informações gerais sobre o programa
print('=-'*50)
print('\033[1;36mpyHDB - \033[0m\033[3;36mFerramenta de auxílio metodológico \
para pesquisa na Hemeroteca Digital Brasileira (BN).\033[0m\n'
      '\n- Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da \
área de História Digital.\n'
      '\n- Essa ferramenta não possui fins lucrativos nem pretende acessar\
dados sigilosos ou alterar informações nos servidores da instituição.\n'
      '\n- Tem como objetivo auxiliar pesquisadores e pesquisadoras a registra\
rem com precisão as etapas de sua pesquisa e garantir o rigor metodológi\
co. Portanto, é uma ferramenta heurística digital.\n'
      '\n- Seu desenvolvimento está no âmbito das pesquisas realizadas no curs\
o de História do IHLM/Unilab e do LABHDUFBA.\n'
      '\n- Os resultados da pesquisa foram publicados na revista História da H\
istoriografia (https://doi.org/10.15848/hh.v15i40.1904) e seu código e d\
ataset estão disponibilizados publicamente, com licença MIT.\n'
      '\n- Buscamos não sobrecarregar os servidores da Biblioteca Nacional e r\
espeitar os termos de uso.\n'
      '\n- A busca foi elaborada a partir das demandas de pesquisa pessoais e \
são explicadas no artigo.\n'
      '\n- A partir dos parâmetros de busca definidos pelo usuário, o programa\
retorna todos os acervos dos jornais com alguma ocorrência, até o limite\
de 100 jornais (segunda página de resultados).\n')
print('=-'*50)

# Definição das opções do driver
options = Options()
# Adiciona argumentos às opções
options.set_preference("intl.accept_languages", "pt-BR, pt")
options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
driver = webdriver.Firefox(options=options)

# Passa a url para o driver
driver.get(url)

# Imprime informações sobre os parâmetros de busca
print(
      '\n\033[3;36m-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Definindo os parâmetros d\
a busca -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\033[0m\n'
      '\nNessa versão do programa, a busca inicial é estabelecida pela opção \
local.\n'
      'É possível incluir uma opção de recorte temporal em seguida.\n'
      'A busca será efetuada em todos os acervos existentes para essa configur\
ação.'
      )
print('=-'*50)
print('\n\033[4;36m1 - Local\033[0m')
print('Orientações para busca:\n'
      '- O termo deve ser idêntico às opções listadas na página da HDB;\n'
      '- Não é possível buscar por "Todos";\n'
      '- Esse parâmetro é "case sensitive".\n')
place = str(input('Digite o local de busca: '))
print('\n\033[4;36m2 - Período\033[0m')
print('Orientações para busca:\n'
      '- O recorte deve ser escrito de forma idêntica às opções listadas na pá\
gina da HDB;\n\
            Ex: \033[1;91m1910 - 1919\033[0m\n'
      '- É possível buscar todos os periódicos digitando "Todos";\n\
            Esse parâmetro é "case sensitive".\n')
period = str(input('Digite o período de busca: '))
# call the function
test_period = validate_period(period)
if test_period is False:
    print('\033[1;31mO período informado não corresponde ao padrão da HDB.\n\
      Por favor, verifique o período e tente novamente.\033[0m')
    exit()
# Nessa versão, a busca acontecerá em todos os periódicos existentes
# de acordo com a definição de Local e Período.
print('\n\033[4;36m3 - Periódico\033[0m: Todos')
journal = 'Todos'
print('\n\033[4;36m4 - Termo da busca\033[0m')
print('Orientações para busca:\n'
      '- Coloque o termo entre aspas duplas para expressões exatas;\n'
      '- Não use acentos ou caracteres especiais;\n'
      '- É recomendado não utilizar mais do que três palavras.\n')
search_term = str(input('Digite o termo de busca: '))
option = driver.find_element(By.XPATH, '//*[@id="RadTabStrip1"]/div')
lis_options = option.find_elements(By.TAG_NAME, 'li')
# Seleciona a opção inicial de buscar pelo Local e clica no botão de busca
# [0]=periódico [1]=período [2]=local
lis_local = lis_options[2]
lis_local.click()

print(f'\n\033[1;36m- Definindo parâmetros da busca...\033[0m')

# Chama a função para encontrar e clicar na seta para abrir as opções de
# 'locais'
set_place(driver, place)

# Função para encontrar o parâmetro período
set_time(driver, period)

# Função para encontrar o parâmetro periódico
set_journal(driver, journal)

# Função para inserir o termo de busca
set_search(driver, search_term)

# Encontra botão para submeter a busca
search_panel = driver.find_element(By.ID, 'PesquisarBtn3Panel')
search_btn = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="PesquisarBtn3"]')))
# Clica no botão de pesquisa
time.sleep(1)
search_btn.click()
time.sleep(1)

# Muda para a janela dos resultados
driver.switch_to.window(driver.window_handles[1])

# Copia a url da janela de resultados a serem carregados
url = driver.current_url
# Cria uma variável com local e termo da busca no padrão a ser
# usado na url de resultados caso ela não carregue corretamente
code_search = 'pasta=ano%20'+period[:3]+'&pesq='+search_term

# Se a página de resultados não carregar corretamente,
# e, portanto, terminar em 'Pesq=', alterar esse final para
# a variável 'code_search'
if url[-5:] == 'Pesq=':
    url = url[:-5] + code_search
    # passa url para o driver
    driver.get(url)
    # refresh a página
    driver.refresh()
    # Aguarda carregar a página
    print('\n\033[5;91m- Aguardando os resultados serem carregados...\033[0m')
    time.sleep(10)
# Se a página de resultado carregar normalmente:
else:
    # Aguarda carregar a página
    print('\n\033[1;91m- Aguardando os resultados serem carregados...\033[0m')
    time.sleep(3)
    if driver.current_url == "about:blank":
        print('\033[1;91m- A página de resultados não carregou corretamente. T\
entando novamente...\033[0m')
        # recarregar a página
        driver.refresh()
        print('\033[1;91m- Aguardando os resultados serem carregados novamente\
        ...\033[0m')
        time.sleep(1)
        if driver.current_url[-5:] == 'Pesq=':
            url = driver.current_url[:-5] + code_search
            # passa url para o driver
            driver.get(url)
            # refresh a página
            driver.refresh()
            # Aguarda carregar a página
            time.sleep(1)
        load_pag = WebDriverWait(driver, 360).until(
            EC.invisibility_of_element((By.ID, 'RadAjaxLoadingPanel1')
                                       ))
        print('\033[1;36m- Página de resultados carregada. Coletando dados ger\
ais...\033[0m')
        time.sleep(5)
# Remove aspas e espaços do termo de busca
search = search_term.replace('"', '')
search = search.replace(' ', '-')
# Define caminho dos diretórios
final_search = os.path.join(search, date)
directory = os.path.join('HDB', final_search)

# Chamar a função para encontrar as numerações das bibliotecas de cada jornal
# e verifica se há ocorrências
l_bibs = get_bibs(driver, directory, place, period)
# Função para tratar a lista de acervos
final_bibs = bib_list(l_bibs)
print(f'\n- Encontradas {len(final_bibs)} bibliotecas com ocorrências.')
# Chamar a função para encontrar informações gerais da busca
if len(final_bibs) > 0:
    infos_dict = get_infos(driver)
    print(f'\n- Total de acervos com ocorrências (máx. de 100): \
    {len(l_bibs)}\n')
else:
    pass
# Se a lista não possuir valores, resultados não foram encontrados e o
# programa se encerra.
if len(l_bibs) == 0:
    print('\033[1;36m=-=-=-=-=-Fim da raspagem.=-=-=-=-=-\033[0m'
          '\n- Se esse resultado for incoerente com os resultados encontrados \
    diretamente na página da HDB, tente novamente. Se o erro persistir, crie u\
    ma issue no repositório da ferramenta: \033[4;36mhttps://github.com/ericbr\
    asiln/pyHDB/issues \033[0m')
    driver.quit()
else:
    # Chamar a função para criar o relatório geral da busca
    report_search(
        directory, search_term, date_time, l_bibs, place, period, journal,
        infos_dict
    )
    # Chamar função para realizar a busca e a raspagem em cada acervo
    journal_search(final_bibs, date, search_term, directory)
    print('\n\033[1;36m=-=-=-=-=-Fim da raspagem.=-=-=-=-=-\033[0m\n')
# Limpando cache do Selenium
driver.delete_all_cookies()
# Fechar todos os navegadores abertos
driver.quit()
# kill processo do driver
os.system('pkill geckodriver')

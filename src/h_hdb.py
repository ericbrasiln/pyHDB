'''
title: H_HDB
author: Eric Brasil
date: 2021-10-04
description: Ferramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).
Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.
license: MIT
Python 3.9.5
email: ericbrasiln@protonmail.com
'''
# Importação de bibliotecas, módulos e funções
from parameters import set_journal, set_place, set_search, set_time
from bibs import get_bibs, bib_list
from search_journals import journal_search
from reports import*
from general_infos import get_infos
import time, os
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

# Definição de variáveis globais: url e data
url = 'http://memoria.bn.br/hdb/'
now = datetime.now()
date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

# Imprimir informações gerais sobre o programa
print('=-'*50)
print('\nFerramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).\n'
    '\n- Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.\n'
    '\n- Essa ferramenta não possui fins lucrativos nem predende acessar dados sigilosos ou alterar\n'
    'informações nos servidores da instituição.\n'
    '\n- Tem como objetivo auxilixar pesquisadores e pesquisadoras a registrarem com precisão as\n'
    'etapas de sua pesquisa e garantir o rigor metodológico.\n'
    '\nPortanto, é uma ferramenta heurística digital. Seu desenvolvimento está no âmbito das\n'
    'pesquisas realizadas no curso de História do IHLM/Unilab e do LABHDUFBA.\n'
    '\n- Os resultados da pesquisa serão publicados em artigo científico avaliado por pares e\n'
    'seu código e dataset serão disponibilizados publicamente, com licença MIT. \n'
    '\n- Buscamos não sobrecarregar os servidores da Biblioteca Nacional e respeitar os termos de uso.\n'
    '\n- A busca foi elaborada a partir das demandas de pesquisa pessoais e serão explicadas no artigo.\n'
    '\n- A partir dos parâmetros de busca definidos pelo usuário, o programa retorna todos os acervos dos\n'
    '\njornais com alguma ocorrência, até o limite de 100 jornais (segunda página de resultados).\n')
print('=-'*50)

# Definição das opções do driver
chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
# Passa a url para o driver
driver.get(url)

# Imprimir informações sobre os parâmetros de busca
print(
      '-=-=-=-=-=-=- Definindo os parâmetros da busca -=-=-=-=-=-=-\n'
      'Nessa versão do programa, a busca inicial é estabelecida pela opção local. É possível\n'
      'incluir uma opção de recorte temporal em seguida. A busca será efetuada em todos os acervos\n'
      'existentes para essa configuração.'
      )
print('=-'*50)
print('\n1 - Local')
print('Orientações para busca:\n'
      '- O termo deve ser idêntico às opções listadas na página da HDB;\n'
      '- Esse parâmetro é case sensitive;\n')
place = str(input('Digite o local de busca: '))
print('\n2 - Período')
print('Orientações para busca:\n'
      '- O recorte deve ser escerito de forma idêntica às opções listadas na página da HDB;\n'
      '- É possível buscar todos os periódicos digitando `Todos`\n')
period = str(input('Digite o período de busca: '))
#Nessa versão, a busca acontecerá em todos os periódicos existentes
#de acordo com a definição de Local e Período.
print('\n3 - Periódico: Todos')
journal = 'Todos'
print('\n4 - Termo da busca')
print('Orientações para busca:\n'
      '- Coloque o termo entre aspas duplas para expressões exatas;\n'
      '- Não use acentos;\n'
      '- Não mais que três palavras\n')
search_term = str(input('Digite o termo de busca: '))

option = driver.find_element_by_xpath('//*[@id="RadTabStrip1"]/div')
lis_options = option.find_elements_by_tag_name('li')
#Seleciona a opção inicial de buscar pelo Local e clica no botão de busca
#[0]=periódico [1]=período [2]=local
lis_local = lis_options[2]
lis_local.click()

print(f'\n- Definindo parâmetros da busca...')

# Chama a função para encontrar e clicar na seta para abrir as opções de 'locais'
set_place(driver, place)

# Função para encontrar o parêmtro período
set_time(driver, period)

# Função para encontrar o parêmetro periódico
set_journal(driver, journal)

# Função para inserir o termo de busca
set_search(driver,search_term)

# Encontra botão para submeter a busca
search_panel = driver.find_element_by_id('PesquisarBtn3Panel')
search_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PesquisarBtn3"]')))
# Clica no botão de pesquisa
time.sleep(1)
search_btn.click()
time.sleep(1)

#Muda para a janela dos resultados
driver.switch_to.window(driver.window_handles[1])

#Aguarda carregar a página
print('\n- Aguardando os resultados serem carregados...')
load_pag = WebDriverWait(driver, 180).until(EC.invisibility_of_element((By.ID, 'RadAjaxLoadingPanel1')))
time.sleep(1)

# Remove aspas e espaços do termo de busca
search = search_term.replace('"','')
search = search.replace(' ','-')
# Define caminho dos diretórios
final_search = os.path.join(search, date)
directory = os.path.join('HDB', final_search)

# Chamar a função para encontrar as numerações das bibliotecas de cada jornal e verifica se há ocorrências
l_bibs = get_bibs(driver, search, directory, period)
# Função para tratar a lista de acervos
final_bibs = bib_list(l_bibs)
# Chamar a função para encontrar informações gerais da busca
infos_dict = get_infos(driver)
print(f'\n- Total de acervos com ocorrências (máx. de 100): {len(l_bibs)}\n')
# Se a lista não possuir valores, resultados não foram encontrados e o programa se encerra.
if len(l_bibs) == 0:
      print(
            'Sem resultados encontrados.\n'
            '=-=-=-=-=-Fim da raspagem.=-=-=-=-=-')
else:
      # Chamar a função para criar o relatório geral da busca
      report_search(directory, search_term, date_time, l_bibs, place, period, journal, infos_dict)
      # Chamar função para realizar a busca e a raspagem em cada acervo
      journal_search(final_bibs, date, search_term, directory)
      print('\n=-=-=-=-=-Fim da raspagem.=-=-=-=-=-\n')
# Fechar todos os navegadores abertos 
driver.quit()
    
'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Ferramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).
Desenvolvida por Eric Brasil como parte de pesquisa acadêmica da área de História Digital.
license: MIT
Python 3.11.9
email: ericbrasiln@proton.me
'''
# Importação de bibliotecas, módulos e funções
from parameters import set_journal, set_place, set_search, set_time, human_behavior
from validate_period import validate_period
from bibs import get_bibs, bib_list
from search_journals import journal_search
from reports import*
from general_infos import get_infos
import time, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium_stealth import stealth

# Definição de variáveis globais: url e data
url = 'http://memoria.bn.br/hdb/'
now = datetime.now()
date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

# Imprimir informações gerais sobre o programa
print('=-' * 30)
print('\033[1;36mpyHDB - \033[0m\033[3;36mFerramenta de auxílio metodológico para pesquisa na Hemeroteca Digital Brasileira (BN).\033[0m\n'\
        '\n- Para mais informações, acesse o repositório do projeto no GitHub: \033[4;36mhttps://github.com/ericbrasiln/pyHDB\033[0m ou entre em contato: \033[4;36mericbrasil.com.br/contact\033[0m\n')
print('=-' * 30)

# Opção para remover a impressão de logs na tela
os.environ['WDM_LOG_LEVEL'] = '0'
# Definição das opções do driver
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36')

driver = uc.Chrome(options=options)
# Adiciona parâmetros para evitar detecção do Selenium
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Remove a propriedade webdriver para evitar detecção
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    '''
})

driver.get(url)

# Imprime informações sobre os parâmetros de busca
print(
      '\n\033[3;36m-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Definindo os parâmetros da busca -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\033[0m\n'
        '\nOBS: Nessa versão do programa, a busca inicial é estabelecida pela opção local e o parâmetro "Periódico" está definido como "Todos" por padrão.'
      )
print('=-' * 30)
print('\n\033[4;36m1 - Local\033[0m')
print('Orientações para busca:\n'
      '- O termo deve ser idêntico às opções listadas na página da HDB;\n'
      '- Não é possível buscar por "Todos";\n'
      '- Esse parâmetro é "case sensitive".\n')
place = str(input('Digite o local de busca: '))
print('\n\033[4;36m2 - Período\033[0m')
print('Orientações para busca:\n'
      '- O recorte deve ser escrito de forma idêntica às opções listadas na página da HDB;\n\
            Ex: \033[1;91m1910 - 1919\033[0m\n'
      '- É possível buscar todos os periódicos digitando "Todos";\n\
            Esse parâmetro é "case sensitive".\n')
period = str(input('Digite o período de busca: '))
# Testa se o período está no formato correto
test_period = validate_period(period)
if test_period == False:
    print('\033[1;31mO período informado não corresponde ao padrão da HDB.\n\
      Por favor, verifique o período e tente novamente.\033[0m')
    exit()
#Nessa versão, a busca acontecerá em todos os periódicos existentes
#de acordo com a definição de Local e Período.
print('\n\033[4;36m3 - Periódico\033[0m: Todos')
journal = 'Todos'
print('\n\033[4;36m4 - Termo da busca\033[0m')
print('Orientações para busca:\n'
      '- Coloque o termo entre aspas duplas para expressões exatas;\n'
      '- Evite acentos ou caracteres especiais;\n'
      '- É recomendado não utilizar mais do que três palavras.\n')
search_term = str(input('Digite o termo de busca: '))
print('\n\033[4;36m5 - Formato de saída\033[0m')
print('1 - CSV (padrão)\n2 - CSV e JSON')
try:
    output_mode = int(input('Escolha o formato [1/2]: ') or '1')
    if output_mode not in (1, 2):
        print('Opção inválida. Usando padrão: 1 - CSV.')
        output_mode = 1
except Exception:
    output_mode = 1
print('\n\033[4;36m6 - Download de imagens\033[0m')
print('1 - baixar imagens (padrão);\n2 - Coletar apenas metadados (sem imagens).')
try:
    resp_img = int(input('Escolha a opção [1/2]: ') or '1')
    if resp_img not in (1, 2):
        print('Opção inválida. Usando padrão: 1 - baixar imagens.')
        resp_img = 1
except Exception:
    resp_img = 1
download_imagens = True if resp_img == 1 else False
if not download_imagens:
    print('\033[1;33m[Modo metadados]\033[0m As imagens não serão baixadas; somente metadados serão coletados.')

option = driver.find_element(By.XPATH, '//*[@id="RadTabStrip1"]/div')
lis_options = option.find_elements(By.TAG_NAME, 'li')
#Seleciona a opção inicial de buscar pelo Local e clica no botão de busca
lis_local = lis_options[2]
lis_local.click()

print(f'\n\033[1;36m- Definindo parâmetros da busca...\033[0m')

# Chama a função para encontrar e clicar na seta para abrir as opções de 'locais'
set_place(driver, place)
human_behavior(driver)

# Função para encontrar o parâmetro período
set_time(driver, period)
human_behavior(driver)

# Função para encontrar o parâmetro periódico
set_journal(driver, journal)
human_behavior(driver)

# Função para inserir o termo de busca
set_search(driver,search_term)
human_behavior(driver)

# Encontra botão para submeter a busca
search_panel = driver.find_element(By.ID, 'PesquisarBtn3Panel')
search_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PesquisarBtn3"]')))
# Clica no botão de pesquisa
time.sleep(1)
search_btn.click()
time.sleep(1)

#Muda para a janela dos resultados
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
    driver.get(url)
    driver.refresh()
    print('\n\033[5;91m- Aguardando os resultados serem carregados...\033[0m')
    time.sleep(10)
# Se a página de resultado carregar normalmente:
else:
      print('\n\033[1;91m- Aguardando os resultados serem carregados...\033[0m')
      load_pag = WebDriverWait(driver, 360).until(EC.invisibility_of_element((By.ID, 'RadAjaxLoadingPanel1')))
      time.sleep(5)

# Remove aspas e espaços do termo de busca
search = search_term.replace('"','')
search = search.replace(' ','-')
# Define caminho dos diretórios
final_search = os.path.join(search, date)
directory = os.path.join('HDB', final_search)

# Chamar a função para encontrar as numerações dos acervos de cada jornal e verifica se há ocorrências
l_bibs = get_bibs(driver, directory, place, period)
# Função para tratar a lista de acervos
final_bibs = bib_list(l_bibs)
print(f'\n- Encontrados {len(final_bibs)} acervos com ocorrências.\n')
# Chamar a função para encontrar informações gerais da busca
if len(final_bibs) > 0:
      infos_dict = get_infos(driver)
else:
      pass
# Se a lista não possuir valores, resultados não foram encontrados e o programa se encerra.
if len(l_bibs) == 0:
      print('\033[1;36m=-=-=-=-=-Fim da raspagem.=-=-=-=-=-\033[0m'\
            '\n- Se esse resultado for incoerente com os resultados encontrados diretamente na página da HDB, tente novamente. Se o erro persistir, crie uma issue no repositório da ferramenta: \033[4;36mhttps://github.com/ericbrasiln/pyHDB/issues \033[0m')
      driver.quit()
else:
      # Chamar a função para criar o relatório geral da busca
      report_search(directory, search_term, date_time, l_bibs, place, period, journal, infos_dict)
      # Chamar função para realizar a busca e a raspagem em cada acervo
      journal_search(final_bibs, date, search_term, directory, output_mode=output_mode, download_imagens=download_imagens)
      print('\n\033[1;36m=-=-=-=-=-Fim da coleta.=-=-=-=-=-\033[0m\n')

# Fechar todos os navegadores abertos 
driver.quit()

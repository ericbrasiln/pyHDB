'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas às imagens das páginas de jornais com ocorrências
'''
import time, urllib.request, os
import wget
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def zoom_in(driver):
    '''
    Função para clicar no botão "Zoom In"
    '''
    # Encontra e move até a barra de botões flutuantes
    actions = ActionChains(driver)
    screen = driver.find_element(By.XPATH, '//*[@id="DocumentoImg"]')
    actions.move_to_element(screen).perform()
    btns = driver.find_element(By.ID, 'ZoomUpdatePanel')
    actions.move_to_element(btns).perform()
    # Clica no botão de zoom
    original = driver.find_element(By.XPATH, '//*[@id="ZoomInBtn"]').click()
    # Aguarda carregar a página
    load_img = WebDriverWait(driver, 30).until(EC.invisibility_of_element((By.ID, 'updateprogressloaddiv')))
    time.sleep(3)

def get_img(driver, bib_final, pag, diretorio):
    '''
    Função para pegar os cookies e salvar a imagem após zoom
    '''
    # Encontra o link para a imagem
    img_large = driver.find_element(By.CSS_SELECTOR, "#DocumentoImg").get_attribute('src')
    link_img = 'http://memoria.bn.br/docreader/'+str(img_large)
    img_name = bib_final +'_'+pag+'.jpg'
    # Criação da pasta de armazenamento e conferência se a mesma já existe
    img_path = os.path.join(diretorio, 'ARQUIVOS_IMG')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    full_name = os.path.join(img_path, img_name)
    # Confere se a imagem já existe na pasta e salva
    if not os.path.exists(full_name):
        # Captura os cookies para poder realizar o download da imagem
        cookies = (driver.get_cookies())
        for cook in cookies:
            if (cook['name'] == 'ARRAffinity'):
                Arrafinity = str(cook['value'])
            elif (cook['name'] == 'ASP.NET_SessionId'):
                AsP = (cook['value'])
        dic_cookies = {'Arrafinity': Arrafinity, 'ASP.NET_SessionId': AsP}
        Done = False
        trying = 0
        while not Done:
            time.sleep(1)
            try:
                trying += 1
                # Caputrando os Cookies do Selenium para fazer o download das imagens
                cookies = (driver.get_cookies())
                for cook in cookies:
                    if (cook['name'] == 'ARRAffinity'):
                        Arrafinity = str(cook['value'])
                    elif (cook['name'] == 'ASP.NET_SessionId'):
                        AsP = (cook['value'])
                dic_cookies = {'Arrafinity': Arrafinity, 'ASP.NET_SessionId': AsP}
                if (int(trying) > 100):
                    print ('Erro ao baixar imagem')
                    break
                try:
                    # Configurando Cookies
                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
                               'Accept': '*/*', 'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                                'Accept-Encoding': 'gzip, deflate, br'}
                    headers['Referer'] = str(driver.current_url)
                    headers['ARRAffinity'] = Arrafinity
                    headers['ASP.NET_SessionId'] = AsP
                    headers['Accept'] = 'image/png, image/svg+xml, image/*; q=0.8, */*; q=0.5'
                    headers['Cache-Control'] = 'no-cache'
                    # Acessa a url da imagem
                    response = urllib.request.Request(img_large, headers=headers)
                    response = urllib.request.urlopen(response, timeout=20)
                except Exception as e:
                    print (e)
                if (response.headers['Content-Type'] == "image/jpeg"):
                    print(f'- Baixando imagem {img_name} com zoom.')
                    # Salva a imagem
                    with open(full_name, 'wb') as f:
                        f.write(response.read())
                        f.close()
                    print ("- Imagem baixada")
                    Done = True
                    continue
                else:
                    raise Exception
                Done = True
            except Exception as a:
                continue
        return img_name
    else:
        print('Imagem já existe no diretório')
        return img_name

def get_img_small(driver,bib_final,pag,diretorio):
    '''
    Função para salvar a imagem na resolução inicial.
    '''
    try:
        img_large = driver.find_element(By.CSS_SELECTOR, "#DocumentoImg").get_attribute('src')
        link_img = 'http://memoria.bn.br/docreader/'+img_large
        img_name = bib_final +'_'+pag+'.jpg'
        img_path = os.path.join(diretorio, 'ARQUIVOS_IMG')
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        full_name = os.path.join(img_path, img_name)
        if not os.path.exists(full_name):
            print(f'- Baixando imagem {img_name} na resolução inicial.')
            pagJpg = wget.download(link_img, out=full_name)
        else:
            print('Imagem já existe no diretório')
    except Exception as e:
        print(f'- Erro no download da img: {e}')
        img_name = f'erro {e}'
    return img_name

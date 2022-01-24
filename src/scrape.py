'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas às raspagens de dados dos acervos com ocorrências.
'''
import time
import pandas as pd
from imgs import*
from reports import*
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service

def scrapeDados(url, search, final_bib, directory, date, date_time):
    '''
    Função para raspar todos os dados de cada página com ocorrências de todos os jornais listados.
    Também cria os relatórios da raspagem de cada acervo.
    '''
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    s=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    try:
        driver.get(url)
        time.sleep(1)
    except WebDriverException as e:
        print(e)
        # Salvar txt com o erro
        with open(directory + 'ERRO_OPEN_URL.txt', 'a') as f:
            f.write(final_bib + '\n')
        driver.quit()
        return
    # Lista para registrar erros
    errors_list = []
    #lista csv do acervo
    acervo_list = []
    try:
        # Buscar aviso de que o jornal possui direitos específicos de uso
        warning = driver.find_element_by_id('RadWindowWrapper_PesqOpniaoRadWindow')
        print('- Aviso:\nEste material é detentor do direito autoral, patrimonial '
            'e moral, com base nos incisos do art. 7º da Lei n. 9.279 de 1996 (LPI)'
            'e artigo 5°, inciso XXIX, da Constituição de 1988.\n'
            'Uso indevido está sujeito a indenizações. Para reproduzi-lo entre em contato com\n'
            'cpdoc@jb.com.br\n'
            '- Fechando "Aviso"...\n')
        # Clicar para fechar o aviso
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="RadWindowWrapper_PesqOpniaoRadWindow"]/div[1]/div/ul/li/span')
            )).click()
    except:
        warning = None
        pass
    # Aguardar a imagem da página ser carregada
    done = False
    trying = 0
    while not done:
        try:
            time.sleep(1)
            trying += 1
            img_present = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="DocumentoImg"]')))
            if (int(trying) > 10):
                print ('Erro!')
                break
            done = True
        except:
            continue
        done = True
    # Executar a função de clicar no botão de zoom duas vezes se o jornal não possuir restrição
    if warning != None:
        print('Jornal com restrição de uso. Download da imagem não será realizado.')
    else:
        try:
            zoom_in(driver)
        except:
            print('Botão zoom não foi clicado')
        try:
            zoom_in(driver)
        except:
            print('Botão zoom não foi clicado')
    try:
        # Buscar ocorrências e respectivos dados
        cur, tot = driver.find_element(By.ID, "OcorNroLbl").text.strip().split("/")
        time.sleep(2)
        for i in range(1,int(tot)+1):
            term = driver.find_element(By.ID, "PesquisarTxt").get_attribute("value")
            folder = driver.find_element(By.ID, "AcervoDescLbl").text
            folder = folder.replace(',',' ')
            pag = driver.find_element(By.ID, "hPagFis").get_attribute("value")
            p = driver.find_element(By.ID, "PagAtualTxt").get_attribute("value")
            # Tentar encontrar Ano e Edição no padrão recorrente, se estiver fora do padrão
            # insere NA para ambas
            try:
                year, issue = driver.find_element(By.ID, "PastaTxt").get_attribute("title").strip().split("\\")
            except:
                year = 'Ano NA'
                issue = 'Edição   NA'
            link = "http://memoria.bn.br/docreader/" + final_bib + "/" + pag
            print('=-'*50)
            print ("[" + str(i) + "/" + tot + "]\n")
            print(
                f'- Data e hora da busca: {date_time};\n'
                f'- Termo da pesquisa: {term}\n'
                f'- Acervo: {folder}, \n- Ano: {year[4:]}, \n'
                f'- Edição: {issue[9:]}, \n- Página: {p}, \n- Link: {link}\n'
                )
            print('=-'*50)
            # Chamar funções para baixar imagem se o jornal não possuir restrição
            if warning != None:
                print('Jornal com restrição de uso. Download da imagem não será realizado.')
                img_name = 'NA'
            else:
                try:
                    # Tentar executar a função de salvar a imagem com zoom.
                    img_name = get_img(driver, final_bib, pag, directory)
                except:
                    # Se não conseguir, baixa com a imagem em tamanho inicial
                    img_name = get_img_small(driver,final_bib,pag,directory)                                           
            # Definir a lista com os dados e em seguida inseri essa lista na lista final
            # que será incluída no CSV final
            inner_list = [term, date, folder, year[4:], issue[9:], p, img_name, link]
            acervo_list.append(inner_list)
            time.sleep(2)
            # Buscar próxima página de ocorrência
            if (i!=int(tot)):
                next_pg = driver.find_element(By.ID, "OcorPosBtn")
                ActionChains(driver).move_to_element(next_pg).click(next_pg).perform()
                WebDriverWait(driver, 50).until(
                    EC.text_to_be_present_in_element(
                        (By.ID, 'OcorNroLbl'), str(i+1)+'/'+tot)
                )
        # Chamar Função para criar o relatório de busca específica do acervof
        report_journal(directory, folder, final_bib, date_time, term, tot, url)
        # Salvar a acervo_list em csv com pandas
        df = pd.DataFrame(acervo_list, columns=['Termo da busca','Data da Busca','Acervo','Ano','Edição','Página', 'Nome do arquivo','Link'])
        csv_path = os.path.join(directory, 'CSV')
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)
        csv_name = os.path.join(csv_path, search + '_' + final_bib + '.csv')
        df.to_csv(csv_name)

    except:
        # Se acontecer algum erro nesse processo, será salvo relatório de erros
        # com os acervos que não puderam ser salvos
        print('- Não foi possível encontrar as ocorrências.\n- Salvando relatório de erro.')
        errors_list.append(final_bib)
        report_erro (directory, search, errors_list, date_time)
        print('=-'*50)
    print(f'Acervo não raspado: {errors_list}\n')
    # Fecha o navegador
    driver.quit()

'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas com a criação e concatenação de CSV gerados.
'''
import pandas as pd 
import os
import time
import glob

#Define o dia e a hora
date_time = time.strftime("%Y-%m-%d_%H-%M-%S") 

def report_df(csv_path,search, csvs_names):
    '''
    Função para criar relatório com erro inicial.
    '''
    #Cria relatório
    report = open(f'{csv_path}_RELATÓRIO_{date_time}.txt', 'w')
    #Inseri dados no relatório
    report.write(
        f'=-=-=-=-=-Relatório de concatenação de CSVs de uma dada busca-=-=-=-=-=\n'
        f'- Data e hora da operação: {date_time};\n'
        f'- Termo da busca: {search};\n'
        f'- Lista de CSVs concatenados: {csvs_names};\n'
        )
    report.close

def df_final(csvs_path, search):
    '''
    Função para unir todos os arquivos CSV e gerar CSV final
    '''
    #Acessa o diretório onde os arquivos CSV foram salvos
    os.chdir(csvs_path)
    #Lista de arquivos CSV existentes
    csvs_list = []
    #Lista com os nomes dos arquivos .csv
    csv_names = []
    #Iteração no diretório buscando arquivos que terminem com '.csv'
    for f in glob.glob("*.csv"):
       #Inclusão do CSV na lista
       df = pd.read_csv(f)
       df = df.astype(str)
       csvs_list.append(df)
       #Inclusão dos nomes dos arquivos CSV na lista
       csv_names.append(f)
    #Pandas concatena todos os arquivos CSV, ignorando o antigo index
    frame = pd.concat(csvs_list, ignore_index=True)
    frame.drop(columns={'Unnamed: 0'}, inplace = True)
    frame['Ano'] = frame['Ano'].str.replace('.0','', regex=False)
    # Criar diretório para CSV final
    csvFinal = os.path.join('CSV_FINAL') 
    if not os.path.exists(csvFinal):
      os.makedirs(csvFinal)
    #Acessa o diretório
    os.chdir(csvFinal) 
    #Exportar para CSV
    frame.to_csv( f"{search}_{date_time}.csv", index=True, encoding='utf-8-sig')
    #Função para criar relatório dos arquivos concatenados
    report_df(csvFinal,search, csv_names)

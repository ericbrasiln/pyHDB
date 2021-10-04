'''
title: H_HDB
author: Eric Brasil
description: Funções relacionadas a criação de relatórios das buscas e raspagens.
'''
import os

def report_path(directory, dir_name):
    '''
    Função para criar caminho do relatório
    '''
    # Criar pasta para salvar relatórios
    report_path = os.path.join(directory, 'RELATÓRIOS')
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    out_report = os.path.join(report_path, dir_name)
    return out_report

def report_erro (directory,search, bibs, date_time):
    '''
    Função para criar relatório com erro inicial.
    '''
    # Criar pasta para salvar relatórios
    if type(bibs) == list:
        bibs = ', '.join(bibs)
    # Chamar função para criar caminho do relatório
    out_report = report_path(directory, 'ERRO')
    # Criar relatório
    report = open(f'{out_report}_{bibs}_{search}_{date_time}.txt', 'w')
    # Inserir dados no relatório
    report.write(
        f'=-=-=-=-=-Relatório de erro da raspagem da HDB-=-=-=-=-=\n'
        f'- Data e hora da busca: {date_time};\n'
        f'- Termo da busca: {search};\n'
        f'- Acervo com ocorrências que não pode ser acessado: {bibs};\n'
        )
    report.close

def report_search(directory, search, date_time, l_bibs, local, periodo, periodico, info_dict):
    '''
    Função para criar o relatório geral da busca
    '''
    # Chamar função para criar caminho do relatório
    out_report = report_path(directory, 'GERAL')
    # Criar relatório
    report = open(f'{out_report}_{date_time}.txt', 'w')
    # Inserir dados no relatório
    report.write(
        f'=-=-=-=-=-Relatório geral da raspagem da HDB-=-=-=-=-=\n'
        f'- Data e hora da busca: {date_time};\n'
        f'- Local da busca: {local};\n'
        f'- Período da busca: {periodo};\n'
        f'- Periódico da busca: {periodico};\n'
        f'- Termo da busca: {search};\n'
        f'- Lista de acervos com ocorrências (máx. de 100) e quantidade de ocorrências: {l_bibs};\n'
        f'- Total de acervos com ocorrências (máx. de 100): {len(l_bibs)}\n'
        f'- Informações adicionais: {info_dict}'
        )
    report.close

def report_journal(directory, pasta, bib_final, date_time, search, tot, url):
    '''
    Função para criar relatório específico de acervo
    '''
    # Chamar função para criar caminho do relatório
    out_report = report_path(directory, f'relatório_{pasta}')
    if not os.path.exists(out_report):
        # Criar relatório
        report = open(f'{out_report}_{bib_final}_{date_time}.txt', 'w')
        # Inserir dados no relatório
        report.write(
            f'=-=-=-=-=-Relatório de acervo da Raspagem da HDB-=-=-=-=-=\n'
            f'- Data e hora da busca: {date_time}\n'
            f'- Termo da busca: {search};\n'
            f' - Acervo: {pasta};\n'
            f'- Total de ocorrências: {tot};\n'
            f'- Link da lista de resultados: {url}'
            )
        report.close
    else:
        print('Relatório já criado')

def report_search_bib(directory, search, date_time, bibs):
    '''
    Função para criar o relatório geral da busca de uma lista de acervos
    '''
    # Chamar função para criar caminho do relatório
    out_report = report_path(directory, 'GERAL')
    bibsString = '_'.join(bibs)
    bibsString = bibsString.replace("'","")
    # Criar relatório
    report = open(f'{out_report}_{bibsString}_{search}_{date_time}.txt', 'w')
    # Inserir dados no relatório
    report.write(
        f'=-=-=-=-=-Relatório geral da raspagem da HDB com lista de acervos-=-=-=-=-=\n'
        f'- Data e hora da busca: {date_time};\n'
        f'- Termo da busca: {search};\n'
        f'- Total de acervos: {len(bibs)};\n'
        f'- Lista de acervos: {bibs}\n'
        )
    report.close

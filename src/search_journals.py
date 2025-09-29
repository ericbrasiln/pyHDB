'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas à busca em cada acervo da lista de acervos com ocorrências.
'''
from scrape import *
from csv_final import *
from datetime import datetime
import os
import csv

CACHE_DIR_NAME = ".cache" 

def _last_occurrence_from_csv(csv_path: str) -> int:
    """
    Retorna o número da última ocorrência salva no CSV de cache,
    contando linhas de dados (exclui o cabeçalho).
    """
    if not os.path.exists(csv_path):
        return 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) <= 1:
            return 0
        return len(rows) - 1


def journal_search(list_of_bibs, date, search_term, directory, output_mode: int = 1, download_imagens: bool = True):
    '''
    Realiza a busca em cada acervo com ocorrências e cria o CSV final consolidado.
    - output_mode: 1 = CSV (padrão); 2 = CSV + JSON/JSONL.
    - download_imagens: quando False, coleta apenas metadados (não baixa imagens).
    Suporta retomada a partir do cache localizado em HDB/<termo>/<data>/.cache/.
    '''
    # Normaliza termo
    search_url = search_term.replace(' ', '%20').replace('"', '\"')
    safe_search = search_term.replace('"', '').replace(' ', '-')

    # Define base da busca: HDB/<termo>/<data>
    base_path = os.path.join('HDB', os.path.join(safe_search, date))
    os.makedirs(base_path, exist_ok=True)

    # Diretório do CSV final e do cache (ambos sob base_path)
    csv_path = os.path.join(base_path, 'CSV')
    os.makedirs(csv_path, exist_ok=True)
    cache_dir = os.path.join(base_path, CACHE_DIR_NAME)
    os.makedirs(cache_dir, exist_ok=True)

    for journal in list_of_bibs:
        csv_name = os.path.join(csv_path, f"{safe_search}_{journal}.csv")
        cache_name = os.path.join(cache_dir, f"{safe_search}_{journal}.csv")

        if os.path.exists(csv_name):
            print(f'CSV {journal} já existe, passando para próximo acervo...')
            continue

        # Timestamp para relatórios/logs
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

        # URL do acervo com termo
        url = f"http://memoria.bn.br/docreader/docreader.aspx?bib={journal}&Pesq={search_url}"

        # Retomada a partir do cache em HDB/<termo>/<data>/.cache/
        if os.path.exists(cache_name):
            last = _last_occurrence_from_csv(cache_name)
            start_from = last + 1
            # imprimir nome do cache mas fatiando o caminho para mostrar só o nome do arquivo
            print(f"CSV {os.path.basename(cache_name)} em cache detectado.")
            scrapeDados(
                url, safe_search, journal, base_path, date, date_time,
                start_from=start_from, download_imagens=download_imagens
            )
        else:
            scrapeDados(
                url, safe_search, journal, base_path, date, date_time,
                start_from=1, download_imagens=download_imagens
            )

    # CSV final consolidado (concatena tudo que está em CSV/)
    df_final(csv_path, safe_search, output_mode=output_mode)

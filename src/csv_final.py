'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Funções relacionadas com a criação, concatenação de CSV gerados e (opcionalmente) conversão para JSON/JSONL.
'''
from __future__ import annotations

import pandas as pd
import os
import time
import glob
import json
from typing import Dict, Any, Iterable

# Define o dia e a hora
date_time = time.strftime("%Y-%m-%d_%H-%M-%S")


def report_df(csv_path: str, search: str, csvs_names: Iterable[str]) -> None:
    '''
    Função para criar relatório simples do processo de concatenação.
    '''
    # Cria relatório (no diretório atual, prefixado com o nome passado)
    report = open(f'{csv_path}_RELATÓRIO_{date_time}.txt', 'w', encoding='utf-8')
    report.write(
        '=-=-=-=-=-Relatório de concatenação de CSVs de uma dada busca-=-=-=-=-=\n'
        f'- Data e hora da operação: {date_time};\n'
        f'- Termo da busca: {search};\n'
        f'- Lista de CSVs concatenados: {list(csvs_names)};\n'
    )
    report.close()


# =========================
# Utilitários para JSON
# =========================

def _coerce_year(value: Any) -> int | None:
    """Converte valores como '2020', '2020.0', ' 2020 ' etc. para int, senão None."""
    if value is None:
        return None
    try:
        # aceita string/float/int
        s = str(value).strip()
        if s == '' or s.lower() == 'nan':
            return None
        # remove sufixo .0 comum
        if s.endswith('.0'):
            s = s[:-2]
        return int(float(s))
    except Exception:
        return None


def _df_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara um DataFrame para exportar como JSON:
    - Mantém tipos 'naturais' quando possível (converte 'Ano' para int).
    - Substitui NaN/NA por None (null no JSON).
    """
    df_json = df.copy()

    # Tentativa de tipar 'Ano' como inteiro (nullable)
    if 'Ano' in df_json.columns:
        df_json['Ano'] = df_json['Ano'].map(_coerce_year)

    # Padroniza vazios como None (em vez de NaN)
    df_json = df_json.where(pd.notna(df_json), None)
    return df_json


def _dump_json_variants(df: pd.DataFrame, out_prefix: str, metadata: Dict[str, Any]) -> None:
    """
    Gera dois formatos:
      - .jsonl: um objeto por linha (ideal para ES/Kibana, BigQuery, etc.)
      - .json:   pacote com {"metadata": {...}, "records": [...]}
    """
    # Garantir diretório de saída
    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)

    # Registros como dicionários
    records = _df_for_json(df).to_dict(orient='records')

    # JSONL
    with open(out_prefix + '.jsonl', 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # JSON "envelopado"
    payload = {
        'metadata': dict(metadata),
        'records': records
    }
    with open(out_prefix + '.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _convert_individual_csvs_to_json(csvs_dir: str) -> None:
    """
    Converte todos os CSVs individuais em csvs_dir para JSON/JSONL.
    Saída em <parent>/JSON/<nome>.jsonl|json (onde <parent> é o diretório pai de csvs_dir).
    """
    parent_dir = os.path.abspath(os.path.join(csvs_dir, os.pardir))
    json_dir = os.path.join(parent_dir, 'JSON')
    os.makedirs(json_dir, exist_ok=True)

    for fpath in glob.glob(os.path.join(csvs_dir, '*.csv')):
        try:
            # Lemos sem forçar tudo para string para preservar NaN e depois normalizar
            df = pd.read_csv(fpath, dtype=str)
            base = os.path.splitext(os.path.basename(fpath))[0]
            out_prefix = os.path.join(json_dir, base)
            _dump_json_variants(
                df,
                out_prefix=out_prefix,
                metadata={
                    'generated_at': date_time,
                    'source': 'pyHDB',
                    'kind': 'per-acervo',
                    'from_csv': os.path.basename(fpath)
                }
            )
        except Exception as e:
            print(f'[AVISO] Falha ao converter {fpath} para JSON: {e}')


# =========================
# Pipeline CSV (compatível)
# =========================

def df_final(csvs_path: str, search: str, output_mode: int = 1) -> None:
    '''
    Função para unir todos os arquivos CSV e gerar CSV final.
    Se output_mode == 2, também gera JSON/JSONL dos CSVs individuais e do CSV final.
    '''
    # Guardamos caminhos absolutos para trabalhar independente de chdir
    csvs_path_abs = os.path.abspath(csvs_path)
    final_root_abs = os.path.abspath(os.path.join(csvs_path_abs, os.pardir))  # .../<termo>/<data>/

    # Acessa o diretório onde os arquivos CSV foram salvos
    os.chdir(csvs_path_abs)

    # Lista de DataFrames e nomes
    csvs_list = []
    csv_names = []

    # Iteração no diretório buscando arquivos que terminem com '.csv'
    for fname in glob.glob('*.csv'):
        # Inclusão do CSV na lista
        df = pd.read_csv(fname)
        df = df.astype(str)
        csvs_list.append(df)
        # Inclusão dos nomes dos arquivos CSV na lista
        csv_names.append(fname)

    # Pandas concatena todos os arquivos CSV, ignorando o antigo index
    frame = pd.concat(csvs_list, ignore_index=True)
    if 'Ano' in frame.columns:
        frame['Ano'] = frame['Ano'].str.replace('.0', '', regex=False)

    # Criar diretório para CSV final (dentro de CSV/)
    csv_final_dir = os.path.join('CSV_FINAL')
    if not os.path.exists(csv_final_dir):
        os.makedirs(csv_final_dir)

    # Acessa o diretório CSV_FINAL
    os.chdir(csv_final_dir)

    # Exportar para CSV (mantém comportamento atual)
    final_csv_name = f"{search}_{date_time}.csv"
    frame.to_csv(final_csv_name, index=True, encoding='utf-8-sig')

    # Função para criar relatório dos arquivos concatenados
    report_df('CSV_FINAL', search, csv_names)

    # =========================
    # Saídas JSON (opcional)
    # =========================
    if int(output_mode) == 2:
        # 1) Converter CSVs individuais (em CSV/) -> JSON/
        _convert_individual_csvs_to_json(csvs_path_abs)

        # 2) Gerar JSON do CSV final -> JSON_FINAL/
        json_final_dir = os.path.join(final_root_abs, 'JSON_FINAL')
        out_prefix = os.path.join(json_final_dir, os.path.splitext(final_csv_name)[0])

        # Para o JSON final, usamos o DataFrame já concatenado,
        # mas normalizado para tipos e nulls adequados.
        _dump_json_variants(
            frame,
            out_prefix=out_prefix,
            metadata={
                'generated_at': date_time,
                'source': 'pyHDB',
                'kind': 'final',
                'search_term': search
            }
        )

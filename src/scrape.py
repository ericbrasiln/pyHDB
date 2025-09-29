'''
title: pyHDB - Ferramenta Heurística para a Hemeroteca Digital Brasileira
author: Eric Brasil
description: Rotinas de raspagem por ocorrência com retomada via CSV de cache,
             armazenado em HDB/<termo>/<data>/.cache/
'''

import os
import csv
import time
import shutil
import sys

import undetected_chromedriver as uc
from selenium_stealth import stealth

from imgs import *           # zoom_in, get_img, get_img_small
from reports import *        # report_journal, report_erro

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)


# =========================
# Helpers utilitários
# =========================

def _append_to_cache(cache_path: str, row: list, header: list):
    """Acrescenta uma linha ao CSV de cache, criando com cabeçalho se ainda não existir."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    file_exists = os.path.exists(cache_path)
    with open(cache_path, mode="a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists and header:
            w.writerow(header)
        w.writerow(row)


def _read_label(driver) -> str:
    """Lê o texto do span #OcorNroLbl (ex.: '123/456') de modo mais estável via JS, com fallback."""
    try:
        txt = driver.execute_script(
            'var e=document.getElementById("OcorNroLbl"); return e? e.textContent.trim(): null;'
        )
        if txt:
            return txt
    except Exception:
        pass
    return driver.find_element(By.ID, "OcorNroLbl").text.strip()


def _click_next(driver):
    """Clica no botão 'Próxima ocorrência' de forma resiliente."""
    btn = WebDriverWait(driver, 20, poll_frequency=0.5,
                        ignored_exceptions=(StaleElementReferenceException,)).until(
        EC.element_to_be_clickable((By.ID, "OcorPosBtn"))
    )
    ActionChains(driver).move_to_element(btn).pause(0.05).click(btn).perform()


def _fmt_hms(secs: float) -> str:
    if secs is None or secs == float('inf'):
        return "—"
    secs = int(max(0, secs))
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def _wait_label_change(driver, prev_label: str, timeout: int = 60) -> str:
    """
    Espera o label #OcorNroLbl mudar de prev_label, tolerando 'stale'.
    Retorna o novo texto do label.
    """
    end = time.time() + timeout
    while time.time() < end:
        try:
            txt = _read_label(driver)
            if txt and txt != prev_label:
                return txt
        except StaleElementReferenceException:
            pass
        # às vezes há overlay de loading:
        try:
            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element((By.ID, "updateprogressloaddiv"))
            )
        except Exception:
            pass
        time.sleep(0.1)
    raise TimeoutException("Timeout esperando mudança no OcorNroLbl")


class FastForwardError(Exception):
    """Erro durante o avanço automático para uma ocorrência-alvo."""
    def __init__(self, message, last_occurrence=None):
        super().__init__(message)
        self.last_occurrence = last_occurrence


def _fast_forward_to(driver, target: int, total: int, log_every: int = 5,
                     click_pause: float = 1.0, max_retries_per_click: int = 3,
                     progress_width: int = 40):
    """
    Avança da ocorrência atual até 'target' clicando no botão Próxima.
    Exibe uma barra de progresso em **uma única linha** (estilo wget):
      [#####-----]  32.5%  211/1017 | 09:35 elapsed | ETA 20:10 | 0.45 occ/s
    """
    label = _read_label(driver)
    if not label or "/" not in label:
        raise FastForwardError("Não foi possível ler o contador inicial (OcorNroLbl).")
    try:
        cur = int(label.split("/")[0])
    except Exception:
        raise FastForwardError(f"Contador inesperado: '{label}'")

    if target <= cur:
        print(f"Já estamos em {cur}.")
        return

    start = cur
    steps_total = target - start
    started_at = time.time()

    # header simples (opcional)
    print(f"Avançando de {start} para {target}…")

    def _render_line(cur_now: int):
        done = cur_now - start
        pct = min(1.0, max(0.0, done / max(1, steps_total)))
        filled = int(progress_width * pct)
        bar = "█" * filled + "·" * (progress_width - filled)

        elapsed = time.time() - started_at
        speed = (done / elapsed) if elapsed > 0 else 0.0
        eta = (steps_total - done) / speed if speed > 0 else float('inf')

        sys.stdout.write(
            f"\r[{bar}] {pct*100:6.2f}%  {cur_now}/{target} | "
            f"{_fmt_hms(elapsed)} elapsed | ETA {_fmt_hms(eta)} | {speed:.2f} occ/s"
        )
        sys.stdout.flush()

    # imprime o estado inicial
    _render_line(cur)

    for step_idx in range(steps_total):
        prev_label = _read_label(driver) or f"{cur}/{total}"

        # clicar com re-tentativas
        clicked = False
        for _try in range(max_retries_per_click):
            try:
                _click_next(driver)
                clicked = True
                break
            except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
                time.sleep(min(click_pause, 1.5))
                continue
            except Exception:
                try:
                    btn = driver.find_element(By.ID, "OcorPosBtn")
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    break
                except Exception:
                    time.sleep(min(click_pause, 1.5))
                    continue

        if not clicked:
            # quebra a linha antes de sair para não “colar” com o próximo print
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise FastForwardError("Falha ao clicar no botão de próxima ocorrência.", last_occurrence=cur)

        # aguarda mudança do label
        time.sleep(click_pause)
        try:
            new_txt = _wait_label_change(driver, prev_label, timeout=60)
            cur = int(new_txt.split("/")[0])
        except TimeoutException:
            try:
                rel = _read_label(driver)
                if rel != prev_label:
                    cur = int(rel.split("/")[0])
                else:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise FastForwardError("Timeout aguardando mudança do rótulo de ocorrência.", last_occurrence=cur)
            except Exception:
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise FastForwardError("Não foi possível confirmar avanço de ocorrência.", last_occurrence=cur)
        except Exception:
            time.sleep(0.5)
            try:
                rel = _read_label(driver)
                cur = int(rel.split("/")[0])
            except Exception:
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise FastForwardError("Não foi possível ler o rótulo após clique.", last_occurrence=cur)

        # atualiza a barra (apenas uma linha)
        if (step_idx + 1) % max(1, log_every) == 0 or cur == target:
            _render_line(cur)

    # termina a linha com quebra
    sys.stdout.write("\n")
    sys.stdout.flush()
    print(f"Alcançada ocorrência {target}/{total}.")


# =========================
# Função principal
# =========================

def scrapeDados(
    url,
    search,
    final_bib,
    directory,
    date,
    date_time,
    start_from=1,
    ff_click_pause=1.0,
    download_imagens: bool = True,
):
    """
    Raspa todas as ocorrências de um acervo, com retomada por cache.
    - directory: base HDB/<termo>/<data>
    - start_from: ocorrência alvo para retomar (1-indexed)
    - ff_click_pause: pausa entre cliques (segundos) na etapa de fast-forward e no loop
    - download_imagens: quando False, coleta apenas metadados (não baixa imagens)
    """
    # ===== Driver (undetected_chromedriver + stealth) =====
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36')
    driver = uc.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    # ===== Abre URL =====
    try:
        driver.get(url)
        time.sleep(0.8)
    except WebDriverException as e:
        print(e)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, 'ERRO_OPEN_URL.txt'), 'a', encoding='utf-8') as f:
            f.write(final_bib + '\n')
        driver.quit()
        return

    errors_list = []

    # ===== Fecha aviso (se houver) =====
    try:
        warning = driver.find_element(By.ID, "RadWindowWrapper_PesqOpniaoRadWindow")
        print('- Aviso de direitos detectado. Fechando…')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="RadWindowWrapper_PesqOpniaoRadWindow"]/div[1]/div/ul/li/span')
        )).click()
    except Exception:
        warning = None

    # ===== Garante imagem base carregada (a página em si) =====
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'DocumentoImg')))

    # ===== Lê contador e fast-forward (se necessário) =====
    def read_counter():
        txt = _read_label(driver)
        if not txt or "/" not in txt:
            txt = driver.find_element(By.ID, "OcorNroLbl").text.strip()
        a, b = [int(x) for x in txt.split("/")]
        return a, b

    try:
        cur, tot = read_counter()
    except Exception:
        time.sleep(0.5)
        cur, tot = read_counter()

    target = max(1, int(start_from) if start_from else 1)
    if target > tot:
        print(f"Ocorrência inicial ({target}) > total ({tot}). Nada a fazer para este acervo.")
        driver.quit()
        return

    if target > cur:
        try:
            _fast_forward_to(driver, target, tot, log_every=10, click_pause=ff_click_pause)
        except FastForwardError as e:
            pos = e.last_occurrence if e.last_occurrence is not None else cur
            print(f"\n[AVISO] Falha durante a retomada em {pos}/{tot}. Motivo: {e}")
            print("O cache foi preservado. Execute novamente para continuar a partir deste ponto.")
            try:
                report_erro(directory, search, [final_bib], date_time)
            except Exception:
                pass
            driver.quit()
            return
        except TypeError:
            # fallback caso a assinatura anterior não tenha click_pause
            _fast_forward_to(driver, target, tot, log_every=10)

        # revalida onde chegamos
        try:
            cur, tot = read_counter()
        except Exception:
            time.sleep(0.5)
            cur, tot = read_counter()

    # ===== Zoom (somente se iremos baixar imagens e não houver restrição) =====
    if warning is not None:
        print('Jornal com restrição de uso. Download de imagens será pulado.')
    elif download_imagens:
        for _ in range(2):
            try:
                zoom_in(driver)
            except Exception:
                pass

    # ===== Caminhos de saída (CSV final + cache) =====
    csv_path = os.path.join(directory, 'CSV')
    os.makedirs(csv_path, exist_ok=True)
    csv_name = os.path.join(csv_path, f"{search}_{final_bib}.csv")

    cache_dir = os.path.join(directory, '.cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{search}_{final_bib}.csv")

    header = ['Termo da busca', 'Data da Busca', 'Acervo', 'Ano', 'Edição', 'Página', 'Nome do arquivo', 'Link']

    # ===== Loop principal de coleta =====
    try:
        # garante contador atualizado
        cur, tot = read_counter()

        for i in range(cur, tot + 1):
            # metadados
            term = driver.find_element(By.ID, "PesquisarTxt").get_attribute("value")
            folder = driver.find_element(By.ID, "AcervoDescLbl").text.replace(',', ' ')
            pag = driver.find_element(By.ID, "hPagFis").get_attribute("value")
            p = driver.find_element(By.ID, "PagAtualTxt").get_attribute("value")
            try:
                year, issue = driver.find_element(By.ID, "PastaTxt").get_attribute("title").strip().split("\\")
            except Exception:
                year, issue = 'Ano NA', 'Edição   NA'
            link = f"http://memoria.bn.br/docreader/{final_bib}/{pag}"

            print('=-' * 30)
            print(f"[{i}/{tot}]\n"
                  f"- Data e hora da busca: {date_time}\n"
                  f"- Termo da pesquisa: {term}\n"
                  f"- Acervo: {folder}\n- Ano: {year[4:] if len(year) >= 4 else year}\n"
                  f"- Edição: {issue[9:] if len(issue) >= 9 else issue}\n- Página: {p}\n- Link: {link}\n")

            # imagem (só se permitido e desejado)
            if (warning is not None) or (not download_imagens):
                img_name = 'NA'
            else:
                try:
                    img_name = get_img(driver, final_bib, pag, directory)
                except Exception:
                    img_name = get_img_small(driver, final_bib, pag, directory)

            row = [term, date, folder,
                   year[4:] if len(year) >= 4 else year,
                   issue[9:] if len(issue) >= 9 else issue,
                   p, img_name, link]
            _append_to_cache(cache_path, row, header)

            # próxima ocorrência (espera robusta por mudança do label)
            if i != tot:
                prev_label = _read_label(driver) or f"{i}/{tot}"
                try:
                    _click_next(driver)
                    time.sleep(ff_click_pause)
                    _wait_label_change(driver, prev_label, timeout=60)
                except TimeoutException:
                    # segundo intento com backoff leve
                    try:
                        time.sleep(max(1.0, ff_click_pause * 1.5))
                        _click_next(driver)
                        time.sleep(ff_click_pause)
                        _wait_label_change(driver, prev_label, timeout=60)
                    except Exception as e2:
                        print(f"[AVISO] Falha ao avançar para a próxima ocorrência em {i}/{tot}: {e2}")
                        raise

        # relatório do acervo
        report_journal(directory, folder, final_bib, date_time, term, str(tot), url)

        # finaliza: copia cache para CSV e remove cache
        shutil.copyfile(cache_path, csv_name)
        try:
            os.remove(cache_path)
        except Exception as rm_err:
            print(f"[Aviso] Não foi possível remover o cache {cache_path}: {rm_err}")

    except Exception as e:
        print(f'[Aviso] Não foi possível completar a coleta.\n- Salvando relatório de erro. Detalhe: {e}')
        try:
            report_erro(directory, search, [final_bib], date_time)
        except Exception:
            pass
        print('=-' * 30)

    driver.quit()

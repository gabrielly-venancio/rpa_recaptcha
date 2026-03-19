"""
Ponto de entrada: N tentativas na demo do reCAPTCHA, com intervalo e retry com backoff.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from selenium.common.exceptions import TimeoutException

from .config import carregar_configuracao
from .logging_setup import configurar_logging
from .navegador import criar_driver
from .recaptcha_fluxo import abrir_pagina_demo, tentar_resolver_recaptcha


def _parse_headless(valor: str | None) -> bool | None:
    if valor is None:
        return None
    return valor.strip().lower() in ("1", "true", "yes", "sim", "on")


def _clicar_enviar_demo(driver, timeout: int) -> None:
    """Envia o formulário da página de demo após token válido (opcional)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(driver, timeout)
    try:
        botao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")))
        botao.click()
        log.info("Formulário da demo enviado.")
    except Exception as exc:  # noqa: BLE001
        log.debug("Não foi possível clicar em enviar (pode ser opcional): %s", exc)


def executar_tentativas() -> int:
    parser = argparse.ArgumentParser(description="Automação RPA — demo reCAPTCHA v2.")
    parser.add_argument("--headless", type=str, default=None, help="true ou false (sobrescreve .env)")
    parser.add_argument("--browser", type=str, default=None, choices=("chrome", "firefox"), help="chrome ou firefox")
    args = parser.parse_args()

    cfg = carregar_configuracao(navegador=args.browser, headless=_parse_headless(args.headless))
    global log  # noqa: PLW0603
    log = configurar_logging(cfg.nivel_log)

    falhas_consecutivas = 0
    sucesso_algum = False

    for num in range(1, cfg.tentativas + 1):
        log.info("Iniciando tentativa %s/%s — abrindo página do reCAPTCHA.", num, cfg.tentativas)
        log.info("Modo de execução: headless=%s, browser=%s.", cfg.headless, cfg.navegador)

        driver = None
        try:
            driver = criar_driver(navegador=cfg.navegador, headless=cfg.headless)
            driver.set_window_size(1280, 900)

            abrir_pagina_demo(driver, cfg.url_demo, cfg.timeout_pagina)

            ok = tentar_resolver_recaptcha(
                driver,
                timeout_elemento=cfg.timeout_elemento,
                permitir_manual=cfg.permitir_conclusao_manual,
                espera_desafio_segundos=cfg.tempo_max_espera_desafio_segundos,
            )
            if ok:
                _clicar_enviar_demo(driver, cfg.timeout_elemento)
                sucesso_algum = True
                falhas_consecutivas = 0
            else:
                falhas_consecutivas += 1

        except TimeoutException:
            log.error("Falha ao resolver reCAPTCHA: Timeout ao localizar iframe.")
            falhas_consecutivas += 1
        except Exception as exc:  # noqa: BLE001
            log.exception("Erro inesperado na tentativa %s/%s: %s", num, cfg.tentativas, exc)
            falhas_consecutivas += 1
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:  # noqa: BLE001
                    pass

        log.info("Finalizando tentativa %s/%s.", num, cfg.tentativas)

        if num < cfg.tentativas:
            if falhas_consecutivas > 0:
                backoff = min(60, 2 ** min(falhas_consecutivas, 5))
                log.error(
                    "Tentativa %s/%s falhou, aplicando retry com backoff.",
                    num,
                    cfg.tentativas,
                )
                log.info("Aguardando backoff de %s segundos antes do intervalo padrão.", backoff)
                time.sleep(backoff)
            log.info("Aguardando %s segundos até a próxima tentativa.", cfg.intervalo_segundos)
            time.sleep(cfg.intervalo_segundos)

    if sucesso_algum:
        log.info("Execução encerrada: houve pelo menos uma resolução bem-sucedida.")
        return 0
    log.error("Execução encerrada: nenhuma tentativa concluiu o reCAPTCHA.")
    return 1


if __name__ == "__main__":
    sys.exit(executar_tentativas())

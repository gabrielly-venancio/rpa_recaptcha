"""
Fluxo reCAPTCHA v2 na página de demo: iframe âncora, checkbox e desafio opcional.

Sem serviços pagos, o grid de imagens não tem classificação confiável em código simples.
Quando o desafio aparece, o modo assistido aguarda o token (usuário conclui no navegador).
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

log = logging.getLogger("rpa_recaptcha")

IFRAME_ANCORA = "iframe[src*='google.com/recaptcha/api2/anchor']"
IFRAME_DESAFIO = "iframe[src*='google.com/recaptcha/api2/bframe']"
SELETOR_CHECKBOX = "#recaptcha-anchor, .recaptcha-checkbox-border"


def _aguardar(driver: WebDriver, timeout: int):
    return WebDriverWait(driver, timeout)


def localizar_iframe_ancora(driver: WebDriver, timeout: int):
    log.info("Localizando iframe do reCAPTCHA.")
    wait = _aguardar(driver, timeout)
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, IFRAME_ANCORA)))
    log.info("iframe encontrado — alternando contexto.")
    return iframe


def clicar_checkbox_nao_sou_robo(driver: WebDriver, timeout: int) -> None:
    iframe = localizar_iframe_ancora(driver, timeout)
    driver.switch_to.frame(iframe)
    try:
        log.info('Clicando no checkbox "Não sou um robô".')
        wait = _aguardar(driver, timeout)
        caixa = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELETOR_CHECKBOX)))
        caixa.click()
    finally:
        driver.switch_to.default_content()


def _desafio_visivel(driver: WebDriver, timeout_curto: float = 2.0) -> bool:
    """Verifica se o iframe do desafio (bframe) está presente e exibido."""
    fim = time.time() + timeout_curto
    while time.time() < fim:
        iframes = driver.find_elements(By.CSS_SELECTOR, IFRAME_DESAFIO)
        for fr in iframes:
            try:
                if fr.is_displayed():
                    return True
            except Exception:
                continue
        time.sleep(0.2)
    return False


def _texto_instrucao_desafio(driver: WebDriver, timeout: int) -> str:
    iframes = driver.find_elements(By.CSS_SELECTOR, IFRAME_DESAFIO)
    for fr in iframes:
        if not fr.is_displayed():
            continue
        driver.switch_to.frame(fr)
        try:
            wait = _aguardar(driver, min(timeout, 10))
            # Instrução principal do grid (pode variar idioma/classe)
            for seletor in (
                ".rc-imageselect-desc-wrapper",
                ".rc-imageselect-desc-no-canonical",
                "#recaptcha-anchor-label",
            ):
                try:
                    el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor)))
                    texto = (el.text or "").strip()
                    if texto:
                        return texto.replace("\n", " ")
                except TimeoutException:
                    continue
            return "desconhecido"
        finally:
            driver.switch_to.default_content()
    return "desconhecido"


def token_recaptcha_preenchido(driver: WebDriver) -> bool:
    try:
        ta = driver.find_element(By.CSS_SELECTOR, "textarea#g-recaptcha-response")
        v = (ta.get_attribute("value") or "").strip()
        return len(v) > 20
    except Exception:
        return False


def aguardar_token_ou_timeout(driver: WebDriver, segundos: int) -> bool:
    """Retorna True se o token foi preenchido dentro do prazo."""
    fim = time.time() + segundos
    while time.time() < fim:
        if token_recaptcha_preenchido(driver):
            return True
        time.sleep(0.5)
    return False


def tentar_resolver_recaptcha(
    driver: WebDriver,
    *,
    timeout_elemento: int,
    permitir_manual: bool,
    espera_desafio_segundos: int,
) -> bool:
    """
    Clica no checkbox; se aparecer desafio de imagem, registra logs e aguarda token.
    """
    clicar_checkbox_nao_sou_robo(driver, timeout_elemento)
    time.sleep(2)

    if token_recaptcha_preenchido(driver):
        log.info("reCAPTCHA resolvido com sucesso.")
        return True

    if not _desafio_visivel(driver, timeout_curto=4.0):
        # Às vezes o token demora sem iframe de desafio
        if aguardar_token_ou_timeout(driver, min(30, espera_desafio_segundos)):
            log.info("reCAPTCHA resolvido com sucesso.")
            return True
        log.warning("Checkbox acionado, mas token não apareceu no tempo esperado.")
        return False

    log.warning("Challenge de imagem detectado — iniciando rotina de resolução.")
    time.sleep(1)
    log.info("Grid carregado — coletando labels e imagens.")
    instrucao = _texto_instrucao_desafio(driver, timeout_elemento)
    # Extrai palavra-chave curta para o log (ex.: ônibus, carros)
    log.info('Selecionando imagens correspondentes ao desafio: "%s".', instrucao)

    if not permitir_manual:
        log.error(
            "Desafio de imagem exige conclusão humana ou método não permitido pelo case "
            "(sem serviços pagos). HEADLESS com ALLOW_MANUAL_SOLVE=false não pode concluir."
        )
        return False

    log.info(
        "Modo assistido: conclua o desafio no navegador (selecione imagens e confirme). "
        "Aguardando até %s s pelo token.",
        espera_desafio_segundos,
    )
    # Usuário clica em Verificar; aguardamos o token na página principal
    if aguardar_token_ou_timeout(driver, espera_desafio_segundos):
        log.info("Submetendo resposta do challenge.")
        log.info("reCAPTCHA resolvido com sucesso.")
        return True

    log.error("Falha ao resolver reCAPTCHA: tempo esgotado aguardando token após o desafio.")
    return False


def abrir_pagina_demo(driver: WebDriver, url: str, timeout_pagina: int) -> None:
    driver.set_page_load_timeout(timeout_pagina)
    driver.get(url)
    log.info("Página carregada com sucesso.")

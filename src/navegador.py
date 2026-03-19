from __future__ import annotations

from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


def criar_driver(*, navegador: str, headless: bool) -> WebDriver:
    
    navegador = navegador.lower().strip()

    if navegador == "chrome":
        return _criar_chrome(headless=headless)
    return _criar_firefox(headless=headless)


def _criar_chrome(headless: bool) -> WebDriver:
    
    #Usa undetected-chromedriver para reduzir bloqueios comuns no checkbox.
    #Se falhar, volta para Selenium + ChromeDriverManager.

    import logging

    log_uc = logging.getLogger("rpa_recaptcha")
    try:
        import undetected_chromedriver as uc

        opcoes = uc.ChromeOptions()
        opcoes.add_argument("--disable-dev-shm-usage")
        opcoes.add_argument("--no-sandbox")
        if headless:
            opcoes.add_argument("--headless=new")
            opcoes.add_argument("--window-size=1920,1080")

        return uc.Chrome(options=opcoes, use_subprocess=True)
    except Exception as exc:  # noqa: BLE001
        log_uc.warning("undetected-chromedriver indisponível ou com erro (%s). Usando Selenium puro.", exc)
        return criar_chrome_selenium_puro(headless)


def _criar_firefox(headless: bool) -> WebDriver:
    opcoes = FirefoxOptions()
    if headless:
        opcoes.add_argument("-headless")
    servico = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=servico, options=opcoes)


def criar_chrome_selenium_puro(headless: bool) -> WebDriver:
    #Alternativa sem undetected (útil se UC falhar no ambiente).
    from selenium.webdriver.chrome.options import Options as ChromeOptions

    opcoes = ChromeOptions()
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--no-sandbox")
    if headless:
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--window-size=1920,1080")
    servico = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=servico, options=opcoes)

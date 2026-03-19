"""Carrega configuração a partir de variáveis de ambiente e argumentos CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _bool_env(nome: str, padrao: bool = False) -> bool:
    v = os.getenv(nome)
    if v is None:
        return padrao
    return v.strip().lower() in ("1", "true", "yes", "sim", "on")


def _int_env(nome: str, padrao: int) -> int:
    try:
        return int(os.getenv(nome, str(padrao)))
    except ValueError:
        return padrao


@dataclass(frozen=True)
class Configuracao:
    """Parâmetros da execução (headless, navegador, tentativas, timeouts)."""

    navegador: str  # "chrome" ou "firefox"
    headless: bool
    tentativas: int
    intervalo_segundos: int
    timeout_pagina: int
    timeout_elemento: int
    nivel_log: str
    # Se True e desafio de imagem aparecer: aguarda token (ex.: usuário resolve no browser).
    permitir_conclusao_manual: bool
    tempo_max_espera_desafio_segundos: int
    url_demo: str = "https://www.google.com/recaptcha/api2/demo"


def carregar_configuracao(
    *,
    navegador: str | None = None,
    headless: bool | None = None,
) -> Configuracao:
    nav = (navegador or os.getenv("BROWSER", "chrome")).strip().lower()
    if nav not in ("chrome", "firefox"):
        nav = "chrome"

    hl = headless if headless is not None else _bool_env("HEADLESS", False)

    # Em headless, por padrão não há como resolver desafio visual sem serviço pago.
    manual_padrao = not hl
    permitir_manual = _bool_env("ALLOW_MANUAL_SOLVE", manual_padrao)

    return Configuracao(
        navegador=nav,
        headless=hl,
        tentativas=_int_env("ATTEMPTS", 10),
        intervalo_segundos=_int_env("INTERVAL_SECONDS", 4),
        timeout_pagina=_int_env("PAGE_LOAD_TIMEOUT", 30),
        timeout_elemento=_int_env("ELEMENT_TIMEOUT", 15),
        nivel_log=os.getenv("LOG_LEVEL", "INFO").upper(),
        permitir_conclusao_manual=permitir_manual,
        tempo_max_espera_desafio_segundos=_int_env("CHALLENGE_WAIT_SECONDS", 120),
    )

"""Configuração de logs em arquivo e console, formato estruturado simples."""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def configurar_logging(nivel: str, diretorio_logs: Path | None = None) -> logging.Logger:
    """
    Nível: DEBUG, INFO, WARNING, ERROR.
    Grava em logs/automacao.log (se diretorio_logs for informado ou padrão projeto).
    """
    log = logging.getLogger("rpa_recaptcha")
    log.handlers.clear()
    log.setLevel(getattr(logging, nivel.upper(), logging.INFO))

    formato = logging.Formatter(
        fmt="[%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formato)
    log.addHandler(console)

    base = diretorio_logs or Path(__file__).resolve().parent.parent / "logs"
    base.mkdir(parents=True, exist_ok=True)
    arquivo = base / "automacao.log"
    fh = logging.FileHandler(arquivo, encoding="utf-8")
    fh.setFormatter(formato)
    log.addHandler(fh)

    return log

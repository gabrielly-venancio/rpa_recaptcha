"""Permite executar: python -m src"""

import sys

from .principal import executar_tentativas

if __name__ == "__main__":
    sys.exit(executar_tentativas())

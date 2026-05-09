"""
version.py
Le o arquivo VERSION e expoe a string da versao do app.
Funciona tanto no modo dev (script) quanto compilado (PyInstaller).
"""

import sys
from pathlib import Path


def get_version() -> str:
    """
    Le a versao do arquivo VERSION na raiz do projeto.
    Retorna 'unknown' se o arquivo nao existir (defesa contra builds quebrados).
    """
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    version_file = base_path / "VERSION"
    if version_file.exists():
        try:
            return version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return "unknown"


__version__ = get_version()

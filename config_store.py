"""
config_store.py
Salva e carrega configuracoes do usuario em config.json no APPDATA.
"""

import json
from pathlib import Path
from rclone_manager import get_app_data_dir


CONFIG_FILE = get_app_data_dir() / "config.json"

DEFAULT_CONFIG = {
    # Configs principais
    "drive_folder_url": "",
    "watch_folder": "",
    "filter_mode": "pattern",  # "exact" ou "pattern"
    "filter_value": "*.mp4",
    "move_after_upload": False,
    "move_destination": "",
    "shutdown_after": False,
    "stable_seconds": 30,

    # Configs de aparencia/comportamento
    "language": "",  # vazio = autodetectar no primeiro uso
    "color_scheme": "light",  # "light" ou "dark"

    # Som ao terminar
    "play_sound_enabled": False,
    "sound_type": "beep",  # "beep", "windows" ou "custom"
    "sound_custom_path": "",
}


def load_config() -> dict:
    """Carrega config do disco. Retorna defaults se nao existir ou estiver corrompido."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge com defaults pra garantir que campos novos existam
        merged = DEFAULT_CONFIG.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Salva config no disco."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

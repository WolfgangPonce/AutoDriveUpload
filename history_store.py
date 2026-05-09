"""
history_store.py
Persiste historico de uploads (JSONL) e log de erros (texto simples)
em %APPDATA%\\AutoDriveUploader\\.
"""

import json
import time
from pathlib import Path
from rclone_manager import get_app_data_dir


HISTORY_FILE = get_app_data_dir() / "upload_history.jsonl"
ERROR_LOG_FILE = get_app_data_dir() / "errors.log"


def add_history_entry(
    filename: str,
    file_size_bytes: int,
    status: str,  # "ok" ou "fail"
    error_msg: str = "",
):
    """
    Adiciona uma entrada ao historico (formato JSONL: 1 JSON por linha).
    JSONL e melhor que JSON pra append: nao precisa rescrever o arquivo todo.
    """
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "size_bytes": file_size_bytes,
        "status": status,
        "error": error_msg,
    }
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # nunca quebra o app por causa de log
        pass


def read_history() -> list[dict]:
    """Le o historico todo. Retorna lista de dicts ordenada do mais recente pro mais antigo."""
    if not HISTORY_FILE.exists():
        return []
    entries = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []
    return list(reversed(entries))


def clear_history() -> bool:
    """Apaga o historico."""
    try:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        return True
    except Exception:
        return False


def log_error(context: str, message: str):
    """Adiciona entrada ao log de erros."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{context}] {message}\n"
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def format_size(num_bytes: int) -> str:
    """Formata tamanho em bytes pra string legivel."""
    if num_bytes is None or num_bytes < 0:
        return "-"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"

"""
rclone_manager.py
Gerencia o rclone embutido: autenticacao OAuth, leitura/escrita do config,
e execucao de uploads pro Google Drive.
"""

import os
import sys
import subprocess
import re
import threading
from pathlib import Path


def get_app_data_dir() -> Path:
    """Retorna a pasta %APPDATA%/AutoDriveUploader, criando se nao existir."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = str(Path.home() / "AppData" / "Roaming")
    app_dir = Path(appdata) / "AutoDriveUploader"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_rclone_path() -> str:
    """
    Retorna o caminho do rclone.exe embutido.
    Quando rodando como .exe (PyInstaller), usa _MEIPASS.
    Quando rodando como script Python, usa a pasta bin/ do projeto.
    """
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    rclone_exe = base_path / "bin" / "rclone.exe"
    if not rclone_exe.exists():
        raise FileNotFoundError(
            f"rclone.exe nao encontrado em {rclone_exe}. "
            "Baixe em https://rclone.org/downloads/ e coloque na pasta bin/"
        )
    return str(rclone_exe)


def get_rclone_config_path() -> Path:
    """Retorna o caminho do rclone.conf usado pelo app."""
    return get_app_data_dir() / "rclone.conf"


# Flags pra rodar subprocess sem janela de console no Windows
def _no_window_kwargs():
    if sys.platform == "win32":
        return {
            "creationflags": subprocess.CREATE_NO_WINDOW,
            "startupinfo": None,
        }
    return {}


def is_drive_authenticated() -> bool:
    """Checa se ja existe um remote 'gdrive' configurado."""
    config_path = get_rclone_config_path()
    if not config_path.exists():
        return False

    try:
        content = config_path.read_text(encoding="utf-8")
        return "[gdrive]" in content and "token" in content
    except Exception:
        return False


def authenticate_drive(on_progress=None) -> tuple[bool, str]:
    """
    Roda 'rclone authorize "drive"' que abre navegador pra usuario autenticar.
    Captura o token retornado e escreve no rclone.conf.

    Args:
        on_progress: callback opcional chamado com mensagens de status

    Returns:
        (sucesso, mensagem)
    """
    rclone = get_rclone_path()
    config_path = get_rclone_config_path()

    def log(msg):
        if on_progress:
            on_progress(msg)

    log("Abrindo navegador para autenticacao...")

    try:
        # rclone authorize abre o navegador, espera o usuario logar,
        # e retorna o token via stdout
        proc = subprocess.Popen(
            [rclone, "authorize", "drive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **_no_window_kwargs(),
        )

        stdout, stderr = proc.communicate(timeout=300)  # 5 min pra autorizar

        if proc.returncode != 0:
            return False, f"Falha na autorizacao: {stderr}"

        # Extrai o JSON do token do stdout
        # Output tipico tem uma linha: '{"access_token":"...","token_type":"Bearer",...}'
        token_match = re.search(r'(\{[^{}]*"access_token"[^{}]*\})', stdout)
        if not token_match:
            return False, f"Nao foi possivel extrair token. Output: {stdout[:200]}"

        token_json = token_match.group(1)

        # Escreve config do rclone
        config_content = f"""[gdrive]
type = drive
scope = drive
token = {token_json}
team_drive = 

"""
        config_path.write_text(config_content, encoding="utf-8")
        log("Autenticacao concluida com sucesso!")
        return True, "Autenticado"

    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "Timeout: usuario demorou demais pra autorizar"
    except Exception as e:
        return False, f"Erro: {e}"


def disconnect_drive() -> bool:
    """Remove a configuracao do rclone (desconecta a conta)."""
    config_path = get_rclone_config_path()
    if config_path.exists():
        try:
            config_path.unlink()
            return True
        except Exception:
            return False
    return True


def get_authenticated_account_email() -> str | None:
    """
    Tenta descobrir o email da conta autenticada usando o rclone.
    Roda 'rclone about gdrive: --json' que retorna info da conta.
    Tambem tenta 'rclone backend get gdrive: -o user' como fallback.

    Retorna None se nao for possivel descobrir.
    """
    if not is_drive_authenticated():
        return None

    rclone = get_rclone_path()
    config_path = get_rclone_config_path()

    # Estrategia 1: rclone config userinfo (retorna email se OAuth tem scope)
    try:
        proc = subprocess.run(
            [rclone, "config", "userinfo", "gdrive", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=15,
            **_no_window_kwargs(),
        )
        if proc.returncode == 0:
            # Output tipico: "email: foo@bar.com\nname: ..."
            for line in proc.stdout.splitlines():
                if line.lower().startswith("email"):
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        email = parts[1].strip()
                        if "@" in email:
                            return email
    except Exception:
        pass

    # Estrategia 2: rclone about --json (tem campo user em alguns casos)
    try:
        proc = subprocess.run(
            [rclone, "about", "gdrive:", "--json", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=15,
            **_no_window_kwargs(),
        )
        if proc.returncode == 0:
            import json
            data = json.loads(proc.stdout)
            user = data.get("user") or data.get("owner")
            if user and "@" in str(user):
                return str(user)
    except Exception:
        pass

    return None


def extract_folder_id(url_or_id: str) -> str | None:
    """
    Aceita URL completa do Drive ou ID puro e retorna o ID.

    Formatos suportados:
    - https://drive.google.com/drive/folders/ABC123
    - https://drive.google.com/drive/u/0/folders/ABC123?usp=sharing
    - ABC123 (ID puro)
    """
    s = url_or_id.strip()

    # Tenta extrair de URL
    m = re.search(r"/folders/([a-zA-Z0-9_-]+)", s)
    if m:
        return m.group(1)

    # Se e ID puro (sem barras nem espacos), retorna direto
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", s):
        return s

    return None


def upload_file(
    file_path: str,
    folder_id: str,
    on_progress=None,
) -> tuple[bool, str]:
    """
    Faz upload de um arquivo pra pasta especifica do Drive.

    Args:
        file_path: caminho local do arquivo
        folder_id: ID da pasta destino no Drive
        on_progress: callback chamado com strings de progresso

    Returns:
        (sucesso, mensagem)
    """
    rclone = get_rclone_path()
    config_path = get_rclone_config_path()

    cmd = [
        rclone,
        "copy",
        file_path,
        "gdrive:",
        f"--drive-root-folder-id={folder_id}",
        "--config", str(config_path),
        "--progress",
        "--stats=2s",
        "--stats-one-line",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            **_no_window_kwargs(),
        )

        if on_progress:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    on_progress(line)

        proc.wait()

        if proc.returncode == 0:
            return True, "Upload concluido"
        else:
            return False, f"Upload falhou (codigo {proc.returncode})"

    except Exception as e:
        return False, f"Erro durante upload: {e}"

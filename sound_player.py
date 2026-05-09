"""
sound_player.py
Toca sons de notificacao quando um upload termina.

No Windows usa winsound (stdlib) pra beep e wav. Pra mp3, tenta playsound
com fallback pra abrir no player padrao do sistema.
"""

import sys
import os
import threading
from pathlib import Path


def play_beep():
    """Beep curto generico."""
    if sys.platform == "win32":
        try:
            import winsound
            winsound.Beep(880, 200)
            winsound.Beep(1320, 300)
        except Exception:
            pass
    else:
        # Linux/Mac: print BEL (mais por compatibilidade no dev)
        print("\a", end="", flush=True)


def play_windows_notification():
    """Som padrao de notificacao do Windows."""
    if sys.platform == "win32":
        try:
            import winsound
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            play_beep()
    else:
        play_beep()


def play_custom_file(file_path: str) -> tuple[bool, str]:
    """
    Toca um arquivo de audio customizado (.wav ou .mp3).

    Pra .wav usa winsound (stdlib).
    Pra .mp3 tenta usar playsound se disponivel; se nao, abre no player padrao.

    Returns: (sucesso, msg_erro)
    """
    if not file_path or not Path(file_path).exists():
        return False, f"File not found: {file_path}"

    ext = Path(file_path).suffix.lower()

    if sys.platform == "win32":
        try:
            import winsound
            if ext == ".wav":
                winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True, ""
            elif ext == ".mp3":
                # winsound nao toca mp3. Usa fallback.
                return _play_mp3_windows(file_path)
            else:
                return False, f"Unsupported format: {ext}"
        except Exception as e:
            return False, str(e)
    else:
        return False, "Sound playback only supported on Windows"


def _play_mp3_windows(file_path: str) -> tuple[bool, str]:
    """
    Toca mp3 no Windows usando winmm (mciSendString via ctypes).
    Funciona sem dependencia externa.
    """
    try:
        import ctypes
        from ctypes import wintypes

        # mciSendString permite tocar mp3 nativamente no Windows
        winmm = ctypes.WinDLL("winmm")
        mci = winmm.mciSendStringW
        mci.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, wintypes.HANDLE]
        mci.restype = wintypes.DWORD

        # Usa alias unico pra nao conflitar com outras chamadas
        alias = "audupld_sound"

        # Fecha qualquer reproducao anterior com esse alias
        mci(f'close {alias}', None, 0, None)

        ret = mci(f'open "{file_path}" type mpegvideo alias {alias}', None, 0, None)
        if ret != 0:
            return False, f"mciSendString open failed (code {ret})"

        ret = mci(f'play {alias}', None, 0, None)
        if ret != 0:
            return False, f"mciSendString play failed (code {ret})"

        return True, ""
    except Exception as e:
        return False, str(e)


def play_sound(sound_type: str, custom_path: str = "") -> tuple[bool, str]:
    """
    API publica. Toca som conforme o tipo selecionado nas configs.

    Roda em thread separada pra nao bloquear a GUI.

    Args:
        sound_type: "beep", "windows", ou "custom"
        custom_path: caminho do arquivo se sound_type == "custom"

    Returns: (sucesso, msg) - sempre retorna sucesso=True (erros sao silenciosos)
    """
    def worker():
        try:
            if sound_type == "beep":
                play_beep()
            elif sound_type == "windows":
                play_windows_notification()
            elif sound_type == "custom":
                ok, _ = play_custom_file(custom_path)
                if not ok:
                    play_beep()  # fallback
            else:
                play_beep()
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()
    return True, ""

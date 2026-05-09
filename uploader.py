"""
uploader.py
Logica de monitoramento de pasta. Detecta quando arquivos terminaram de
ser escritos (tamanho estavel) e dispara upload via rclone_manager.
"""

import os
import time
import threading
import fnmatch
import shutil
from pathlib import Path
from typing import Callable

import rclone_manager
import history_store
import sound_player


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi"}


class UploadMonitor:
    """
    Monitora uma pasta esperando arquivos novos cujo tamanho fique estavel.
    Quando detecta, faz upload e opcionalmente move o arquivo.
    """

    def __init__(
        self,
        watch_folder: str,
        drive_folder_id: str,
        filter_mode: str,  # "exact" ou "pattern"
        filter_value: str,
        stable_seconds: int = 30,
        move_destination: str = "",
        on_log: Callable[[str], None] = None,
        on_status: Callable[[str], None] = None,
        on_finished_all: Callable[[], None] = None,
        on_upload_complete: Callable[[], None] = None,  # toca som
        translator=None,  # i18n.Translator - opcional, se None usa strings cruas
    ):
        self.watch_folder = Path(watch_folder)
        self.drive_folder_id = drive_folder_id
        self.filter_mode = filter_mode
        self.filter_value = filter_value.strip()
        self.stable_seconds = stable_seconds
        self.move_destination = move_destination
        self.on_log = on_log or (lambda s: None)
        self.on_status = on_status or (lambda s: None)
        self.on_finished_all = on_finished_all or (lambda: None)
        self.on_upload_complete = on_upload_complete or (lambda: None)
        self._t = translator

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._existing_files: set[str] = set()
        self._processed_files: set[str] = set()
        self._uploads_done = 0

    def _tr(self, key: str, **kwargs) -> str:
        """Helper de traducao com fallback."""
        if self._t:
            return self._t.t(key, **kwargs)
        return key

    def _matches_filter(self, filename: str) -> bool:
        """
        Checa se o arquivo passa pelos filtros (extensao de video + filtro do usuario).
        Comparacao case-insensitive em ambos os modos pra consistencia entre OS.
        """
        ext = Path(filename).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            return False

        name_lower = filename.lower()
        value_lower = self.filter_value.lower()

        if self.filter_mode == "exact":
            return name_lower == value_lower
        else:  # pattern
            return fnmatch.fnmatch(name_lower, value_lower)

    def _list_matching_files(self) -> list[Path]:
        """Lista arquivos da pasta monitorada que passam pelos filtros."""
        if not self.watch_folder.exists():
            return []
        try:
            return [
                p for p in self.watch_folder.iterdir()
                if p.is_file() and self._matches_filter(p.name)
            ]
        except Exception as e:
            self.on_log(self._tr("log_failed_list", err=str(e)))
            history_store.log_error("LIST_FOLDER", str(e))
            return []

    def _wait_until_stable(self, file_path: Path) -> bool:
        """
        Espera o arquivo ter tamanho estavel por self.stable_seconds.
        Retorna True se ficou estavel, False se foi cancelado.
        """
        last_size = -1
        stable_start = None
        logged_waiting = False

        while not self._stop_event.is_set():
            try:
                current_size = file_path.stat().st_size
            except FileNotFoundError:
                return False

            if current_size == last_size and current_size > 0:
                if stable_start is None:
                    stable_start = time.time()
                    if not logged_waiting:
                        self.on_log(self._tr(
                            "log_waiting_stable",
                            sec=self.stable_seconds,
                            name=file_path.name,
                        ))
                        logged_waiting = True
                elif time.time() - stable_start >= self.stable_seconds:
                    return True
            else:
                stable_start = None
                last_size = current_size

            for _ in range(2):
                if self._stop_event.is_set():
                    return False
                time.sleep(1)

        return False

    def _process_file(self, file_path: Path):
        """Processa um arquivo: espera estabilizar, faz upload, move se configurado."""
        self.on_status(self._tr("waiting_for", name=file_path.name))
        self.on_log(self._tr("log_detected", name=file_path.name))

        if not self._wait_until_stable(file_path):
            self.on_log(self._tr("log_cancelled", name=file_path.name))
            return

        # Pega tamanho antes do upload pra registrar no historico
        try:
            file_size = file_path.stat().st_size
        except Exception:
            file_size = 0

        self.on_status(self._tr("uploading", name=file_path.name))
        self.on_log(self._tr("log_uploading", name=file_path.name))

        success, msg = rclone_manager.upload_file(
            str(file_path),
            self.drive_folder_id,
            on_progress=lambda line: self.on_log(f"  {line}"),
        )

        if not success:
            self.on_log(self._tr("log_error", msg=msg))
            self.on_status(self._tr("upload_failed"))
            history_store.add_history_entry(
                filename=file_path.name,
                file_size_bytes=file_size,
                status="fail",
                error_msg=msg,
            )
            history_store.log_error("UPLOAD", f"{file_path.name}: {msg}")
            return

        self.on_log(self._tr("log_upload_ok", name=file_path.name))
        history_store.add_history_entry(
            filename=file_path.name,
            file_size_bytes=file_size,
            status="ok",
        )
        self._uploads_done += 1

        # Dispara callback de som apos upload bem sucedido
        try:
            self.on_upload_complete()
        except Exception as e:
            history_store.log_error("SOUND", str(e))

        # Move se configurado
        if self.move_destination:
            try:
                dest_dir = Path(self.move_destination)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / file_path.name

                if dest_path.exists():
                    stem = dest_path.stem
                    suffix = dest_path.suffix
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"

                shutil.move(str(file_path), str(dest_path))
                self.on_log(self._tr("log_moved", path=str(dest_path)))
            except Exception as e:
                self.on_log(self._tr("log_move_failed", err=str(e)))
                history_store.log_error("MOVE", f"{file_path.name}: {e}")

        self._processed_files.add(str(file_path))

    def _run(self):
        """Loop principal do monitor."""
        self.on_log(self._tr("log_monitoring", path=str(self.watch_folder)))
        self.on_log(self._tr("log_filter", mode=self.filter_mode, value=self.filter_value))
        self.on_log(self._tr("log_drive_id", id=self.drive_folder_id))
        if self.move_destination:
            self.on_log(self._tr("log_move_dest", path=self.move_destination))
        self.on_log("")

        # Captura arquivos que ja existem pra ignorar
        for p in self._list_matching_files():
            self._existing_files.add(str(p))

        if self._existing_files:
            self.on_log(self._tr("log_ignoring_existing", n=len(self._existing_files)))

        self.on_status(self._tr("monitoring"))

        while not self._stop_event.is_set():
            files = self._list_matching_files()
            for f in files:
                if self._stop_event.is_set():
                    break
                fp = str(f)
                if fp in self._existing_files or fp in self._processed_files:
                    continue
                self._process_file(f)
                self.on_status(self._tr("monitoring"))

            for _ in range(5):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

        self.on_log(self._tr("log_monitor_stopped", n=self._uploads_done))
        self.on_status(self._tr("stopped"))
        if self._uploads_done > 0:
            self.on_finished_all()

    def start(self):
        """Inicia o monitor em thread separada."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Para o monitor."""
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def uploads_done(self) -> int:
        return self._uploads_done

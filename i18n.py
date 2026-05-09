"""
i18n.py
Sistema de internacionalizacao simples. Suporta pt-BR e en-US.
"""

import locale


TRANSLATIONS = {
    "pt": {
        # App geral
        "app_title": "AutoDrive Uploader",
        "ready": "Pronto",
        "yes": "Sim",
        "no": "Nao",
        "cancel": "Cancelar",
        "ok": "OK",
        "close": "Fechar",
        "browse": "Procurar...",

        # Tabs
        "tab_main": "Principal",
        "tab_settings": "Configuracoes",

        # Auth
        "drive_account": "Conta Google Drive",
        "not_connected": "Nao conectado",
        "connected_as": "Conectado: {email}",
        "connected": "Conectado",
        "connect": "Conectar",
        "reconnect": "Reconectar",
        "disconnect": "Desconectar",
        "disconnect_confirm": "Desconectar a conta do Google Drive?",
        "auth_starting": "Iniciando autenticacao com Google Drive...",
        "auth_browser_will_open": "Uma janela do navegador vai abrir. Faca login e autorize.",
        "auth_success": "Conta conectada com sucesso!",
        "auth_failed": "Falha ao conectar:\n{msg}",
        "account_disconnected": "Conta desconectada.",
        "fetching_account": "Identificando conta...",

        # Drive folder
        "drive_folder_title": "Pasta destino no Drive",
        "drive_folder_label": "Cole o link da pasta:",

        # Watch folder
        "watch_folder_title": "Pasta a monitorar",
        "select_watch_folder": "Selecione a pasta a monitorar",

        # Filter
        "filter_title": "Qual arquivo monitorar",
        "filter_pattern": "Padrao (ex: *.mp4, render_*.mov)",
        "filter_exact": "Nome exato (ex: meuvideo.mp4)",
        "filter_extensions_note": "So aceita videos: .mp4, .mov, .mkv, .avi",

        # Move
        "move_title": "Mover para depois do upload (opcional)",
        "move_enabled": "Mover arquivo apos upload concluido",
        "select_move_dest": "Selecione a pasta destino",

        # Final options
        "shutdown_after": "Desligar PC apos terminar (so se ja teve pelo menos 1 upload)",
        "play_sound_after": "Tocar som ao terminar upload",

        # Buttons
        "start_monitoring": "Iniciar monitoramento",
        "stop": "Parar",
        "view_history": "Ver historico",

        # Status
        "monitoring": "Monitorando...",
        "stopped": "Parado",
        "waiting_for": "Aguardando: {name}",
        "uploading": "Enviando: {name}",
        "upload_failed": "Falha no upload",

        # Validation
        "err_not_authenticated": "Voce precisa conectar uma conta do Google Drive primeiro.",
        "err_drive_url_empty": "Cole o link da pasta de destino do Drive.",
        "err_drive_url_invalid": "Link da pasta do Drive invalido. Cole a URL completa da pasta.",
        "err_watch_folder_invalid": "Pasta a monitorar invalida.",
        "err_filter_empty": "Defina o filtro de arquivo.",
        "err_move_dest_empty": "Voce marcou 'mover apos upload' mas nao definiu a pasta destino.",

        # Log messages
        "log_monitoring": "=== Monitorando: {path} ===",
        "log_filter": "Filtro: {mode} = '{value}'",
        "log_drive_id": "Pasta Drive ID: {id}",
        "log_move_dest": "Mover apos upload para: {path}",
        "log_ignoring_existing": "[INFO] Ignorando {n} arquivo(s) ja existente(s).",
        "log_detected": "[NOVO] Detectado: {name}",
        "log_waiting_stable": "[...] Aguardando {sec}s de estabilidade: {name}",
        "log_uploading": "[UPLOAD] Enviando {name} pro Drive...",
        "log_upload_ok": "[OK] Upload concluido: {name}",
        "log_moved": "[MOVIDO] -> {path}",
        "log_move_failed": "[ERRO] Falha ao mover: {err}",
        "log_cancelled": "[CANCELADO] {name}",
        "log_error": "[ERRO] {msg}",
        "log_monitor_stopped": "=== Monitor parado. Total enviado: {n} ===",
        "log_shutdown": "[SHUTDOWN] PC sera desligado em 60s. Comando: shutdown /s /t 60",
        "log_shutdown_cancelled": "[INFO] Shutdown cancelado pelo usuario.",
        "log_failed_list": "[ERRO] Falha ao listar pasta: {err}",
        "log_shutdown_fail": "[ERRO] Falha ao agendar shutdown: {err}",

        # Shutdown dialog
        "shutdown_question": "Upload(s) concluido(s).\n\nO PC sera desligado em 60 segundos.\nDeseja desligar agora? (Clique em Nao para cancelar)",
        "shutdown_scheduled": "PC vai desligar em 60s.\n\nPra cancelar, abra o cmd e rode: shutdown /a",

        # Close confirm
        "close_while_running": "Monitor ainda esta rodando. Fechar mesmo assim?",

        # Settings
        "settings_language": "Idioma",
        "settings_color_scheme": "Tema",
        "color_light": "Claro",
        "color_dark": "Escuro",
        "settings_sound": "Som ao terminar",
        "sound_beep": "Beep curto",
        "sound_plim": "Notificacao Windows",
        "sound_custom": "Personalizado (.wav/.mp3)",
        "sound_test": "Testar som",
        "settings_history": "Historico",
        "clear_history_btn": "Apagar historico",
        "clear_history_confirm": "Apagar todo o historico de uploads?\n\nEssa acao nao pode ser desfeita.",
        "history_cleared": "Historico apagado.",
        "select_sound_file": "Selecione o arquivo de som",

        # History window
        "history_title": "Historico de uploads",
        "history_empty": "Nenhum upload registrado ainda.",
        "history_col_date": "Data/Hora",
        "history_col_file": "Arquivo",
        "history_col_size": "Tamanho",
        "history_col_status": "Status",
        "history_status_ok": "OK",
        "history_status_fail": "Falhou",
        "history_open_log": "Abrir log de erros",
        "history_log_not_found": "Log de erros nao existe ainda.",
    },
    "en": {
        # App geral
        "app_title": "AutoDrive Uploader",
        "ready": "Ready",
        "yes": "Yes",
        "no": "No",
        "cancel": "Cancel",
        "ok": "OK",
        "close": "Close",
        "browse": "Browse...",

        # Tabs
        "tab_main": "Main",
        "tab_settings": "Settings",

        # Auth
        "drive_account": "Google Drive Account",
        "not_connected": "Not connected",
        "connected_as": "Connected: {email}",
        "connected": "Connected",
        "connect": "Connect",
        "reconnect": "Reconnect",
        "disconnect": "Disconnect",
        "disconnect_confirm": "Disconnect the Google Drive account?",
        "auth_starting": "Starting Google Drive authentication...",
        "auth_browser_will_open": "A browser window will open. Sign in and authorize.",
        "auth_success": "Account connected successfully!",
        "auth_failed": "Failed to connect:\n{msg}",
        "account_disconnected": "Account disconnected.",
        "fetching_account": "Identifying account...",

        # Drive folder
        "drive_folder_title": "Drive destination folder",
        "drive_folder_label": "Paste the folder link:",

        # Watch folder
        "watch_folder_title": "Folder to watch",
        "select_watch_folder": "Select the folder to watch",

        # Filter
        "filter_title": "Which file to watch",
        "filter_pattern": "Pattern (e.g. *.mp4, render_*.mov)",
        "filter_exact": "Exact name (e.g. myvideo.mp4)",
        "filter_extensions_note": "Only video files: .mp4, .mov, .mkv, .avi",

        # Move
        "move_title": "Move file after upload (optional)",
        "move_enabled": "Move file after upload completes",
        "select_move_dest": "Select destination folder",

        # Final options
        "shutdown_after": "Shutdown PC after finishing (only if at least 1 upload happened)",
        "play_sound_after": "Play sound when upload finishes",

        # Buttons
        "start_monitoring": "Start monitoring",
        "stop": "Stop",
        "view_history": "View history",

        # Status
        "monitoring": "Monitoring...",
        "stopped": "Stopped",
        "waiting_for": "Waiting: {name}",
        "uploading": "Uploading: {name}",
        "upload_failed": "Upload failed",

        # Validation
        "err_not_authenticated": "You need to connect a Google Drive account first.",
        "err_drive_url_empty": "Paste the destination Drive folder link.",
        "err_drive_url_invalid": "Invalid Drive folder link. Paste the full folder URL.",
        "err_watch_folder_invalid": "Invalid watch folder.",
        "err_filter_empty": "Define the file filter.",
        "err_move_dest_empty": "You enabled 'move after upload' but did not set a destination.",

        # Log messages
        "log_monitoring": "=== Watching: {path} ===",
        "log_filter": "Filter: {mode} = '{value}'",
        "log_drive_id": "Drive folder ID: {id}",
        "log_move_dest": "Move after upload to: {path}",
        "log_ignoring_existing": "[INFO] Ignoring {n} existing file(s).",
        "log_detected": "[NEW] Detected: {name}",
        "log_waiting_stable": "[...] Waiting {sec}s of stability: {name}",
        "log_uploading": "[UPLOAD] Sending {name} to Drive...",
        "log_upload_ok": "[OK] Upload complete: {name}",
        "log_moved": "[MOVED] -> {path}",
        "log_move_failed": "[ERROR] Failed to move: {err}",
        "log_cancelled": "[CANCELLED] {name}",
        "log_error": "[ERROR] {msg}",
        "log_monitor_stopped": "=== Monitor stopped. Total uploaded: {n} ===",
        "log_shutdown": "[SHUTDOWN] PC will shut down in 60s. Command: shutdown /s /t 60",
        "log_shutdown_cancelled": "[INFO] Shutdown cancelled by user.",
        "log_failed_list": "[ERROR] Failed to list folder: {err}",
        "log_shutdown_fail": "[ERROR] Failed to schedule shutdown: {err}",

        # Shutdown dialog
        "shutdown_question": "Upload(s) complete.\n\nThe PC will shut down in 60 seconds.\nShut down now? (Click No to cancel)",
        "shutdown_scheduled": "PC will shut down in 60s.\n\nTo cancel, open cmd and run: shutdown /a",

        # Close confirm
        "close_while_running": "Monitor is still running. Close anyway?",

        # Settings
        "settings_language": "Language",
        "settings_color_scheme": "Theme",
        "color_light": "Light",
        "color_dark": "Dark",
        "settings_sound": "Sound on finish",
        "sound_beep": "Short beep",
        "sound_plim": "Windows notification",
        "sound_custom": "Custom (.wav/.mp3)",
        "sound_test": "Test sound",
        "settings_history": "History",
        "clear_history_btn": "Clear history",
        "clear_history_confirm": "Clear all upload history?\n\nThis action cannot be undone.",
        "history_cleared": "History cleared.",
        "select_sound_file": "Select sound file",

        # History window
        "history_title": "Upload history",
        "history_empty": "No uploads recorded yet.",
        "history_col_date": "Date/Time",
        "history_col_file": "File",
        "history_col_size": "Size",
        "history_col_status": "Status",
        "history_status_ok": "OK",
        "history_status_fail": "Failed",
        "history_open_log": "Open error log",
        "history_log_not_found": "Error log doesn't exist yet.",
    },
}


class Translator:
    """Helper de traducao com fallback pro ingles e depois pra chave crua."""

    def __init__(self, lang_code: str = "en"):
        self.lang = lang_code if lang_code in TRANSLATIONS else "en"

    def set_language(self, lang_code: str):
        if lang_code in TRANSLATIONS:
            self.lang = lang_code

    def t(self, key: str, **kwargs) -> str:
        msg = TRANSLATIONS.get(self.lang, {}).get(key)
        if msg is None:
            # fallback pro ingles
            msg = TRANSLATIONS["en"].get(key, key)
        try:
            return msg.format(**kwargs) if kwargs else msg
        except (KeyError, IndexError):
            return msg


def detect_system_language() -> str:
    """Detecta idioma do sistema. Retorna 'pt' se PT/BR, senao 'en'."""
    try:
        lang = locale.getdefaultlocale()[0] or ""
        if lang.lower().startswith("pt"):
            return "pt"
    except Exception:
        pass
    return "en"

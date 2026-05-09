"""
main.py
AutoDrive Uploader - GUI principal com tabs, settings e historico.
"""

import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

import rclone_manager
import config_store
import history_store
import sound_player
from i18n import Translator, detect_system_language
from uploader import UploadMonitor
from version import __version__


APP_NAME = "AutoDrive Uploader"


# Paletas de cor pra dark/light mode
LIGHT_COLORS = {
    "bg": "#f5f5f5",
    "fg": "#1a1a1a",
    "panel_bg": "#ffffff",
    "log_bg": "#ffffff",
    "log_fg": "#1a1a1a",
    "accent": "#0a7d3a",
    "danger": "#c33333",
    "muted": "#666666",
    "entry_bg": "#ffffff",
    "entry_fg": "#1a1a1a",
}

DARK_COLORS = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "panel_bg": "#2a2a2a",
    "log_bg": "#1a1a1a",
    "log_fg": "#d4d4d4",
    "accent": "#4ade80",
    "danger": "#f87171",
    "muted": "#9ca3af",
    "entry_bg": "#2a2a2a",
    "entry_fg": "#e0e0e0",
}


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = config_store.load_config()

        # Inicializa idioma
        if not self.config.get("language"):
            self.config["language"] = detect_system_language()
            config_store.save_config(self.config)
        self.t = Translator(self.config["language"])

        self.root.title(f"{APP_NAME} v{__version__}")
        self.root.geometry("760x720")
        self.root.minsize(680, 640)

        self.monitor: UploadMonitor | None = None
        self._shutdown_pending = False

        self._apply_theme()
        self._build_ui()
        self._refresh_auth_status()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----------------------- Theme -----------------------

    def _apply_theme(self):
        scheme = self.config.get("color_scheme", "light")
        self.colors = DARK_COLORS if scheme == "dark" else LIGHT_COLORS

        style = ttk.Style()
        if scheme == "dark":
            try:
                style.theme_use("clam")
            except Exception:
                pass
        else:
            try:
                if "vista" in style.theme_names():
                    style.theme_use("vista")
                elif "clam" in style.theme_names():
                    style.theme_use("clam")
            except Exception:
                pass

        c = self.colors
        self.root.configure(bg=c["bg"])

        style.configure(".", background=c["bg"], foreground=c["fg"])
        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        style.configure("TLabelframe", background=c["bg"], foreground=c["fg"])
        style.configure("TLabelframe.Label", background=c["bg"], foreground=c["fg"])
        style.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
        style.configure("TRadiobutton", background=c["bg"], foreground=c["fg"])
        style.configure("TNotebook", background=c["bg"])
        style.configure("TNotebook.Tab", background=c["panel_bg"], foreground=c["fg"], padding=[12, 6])

        if scheme == "dark":
            style.map("TNotebook.Tab",
                background=[("selected", c["bg"])],
                foreground=[("selected", c["fg"])])
            style.configure("TButton", background=c["panel_bg"], foreground=c["fg"])
            style.map("TButton",
                background=[("active", c["bg"])],
                foreground=[("active", c["fg"])])
            style.configure("TEntry", fieldbackground=c["entry_bg"], foreground=c["entry_fg"], insertcolor=c["fg"])
            style.configure("TCombobox", fieldbackground=c["entry_bg"], background=c["panel_bg"], foreground=c["entry_fg"])
            style.configure("Treeview", background=c["panel_bg"], foreground=c["fg"], fieldbackground=c["panel_bg"])
            style.configure("Treeview.Heading", background=c["bg"], foreground=c["fg"])

        style.configure("Accent.TLabel", background=c["bg"], foreground=c["accent"])
        style.configure("Danger.TLabel", background=c["bg"], foreground=c["danger"])
        style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])

    # ----------------------- UI -----------------------

    def _build_ui(self):
        # Limpa qualquer widget existente (caso seja rebuild apos mudar idioma/tema)
        for widget in self.root.winfo_children():
            widget.destroy()

        container = ttk.Frame(self.root, padding=8)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 6))
        ttk.Label(header, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Label(
            header, text=f"v{__version__}", style="Muted.TLabel",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(8, 0), pady=(8, 0), anchor="s")

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.main_tab = ttk.Frame(self.notebook, padding=10)
        self.settings_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.main_tab, text=self.t.t("tab_main"))
        self.notebook.add(self.settings_tab, text=self.t.t("tab_settings"))

        self._build_main_tab(self.main_tab)
        self._build_settings_tab(self.settings_tab)

    def _build_main_tab(self, parent):
        auth_frame = ttk.LabelFrame(parent, text=self.t.t("drive_account"), padding=10)
        auth_frame.pack(fill="x", pady=(0, 8))

        self.auth_status_label = ttk.Label(auth_frame, text=self.t.t("not_connected"))
        self.auth_status_label.pack(side="left")

        self.disconnect_btn = ttk.Button(
            auth_frame, text=self.t.t("disconnect"), command=self._on_disconnect_clicked
        )
        self.disconnect_btn.pack(side="right")

        self.connect_btn = ttk.Button(
            auth_frame, text=self.t.t("connect"), command=self._on_connect_clicked
        )
        self.connect_btn.pack(side="right", padx=(0, 8))

        drive_frame = ttk.LabelFrame(parent, text=self.t.t("drive_folder_title"), padding=10)
        drive_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(drive_frame, text=self.t.t("drive_folder_label")).pack(anchor="w")
        self.drive_url_var = tk.StringVar(value=self.config.get("drive_folder_url", ""))
        ttk.Entry(drive_frame, textvariable=self.drive_url_var).pack(fill="x", pady=(2, 0))

        watch_frame = ttk.LabelFrame(parent, text=self.t.t("watch_folder_title"), padding=10)
        watch_frame.pack(fill="x", pady=(0, 8))

        watch_row = ttk.Frame(watch_frame)
        watch_row.pack(fill="x")
        self.watch_var = tk.StringVar(value=self.config.get("watch_folder", ""))
        ttk.Entry(watch_row, textvariable=self.watch_var).pack(side="left", fill="x", expand=True)
        ttk.Button(watch_row, text=self.t.t("browse"), command=self._browse_watch).pack(
            side="right", padx=(8, 0)
        )

        filter_frame = ttk.LabelFrame(parent, text=self.t.t("filter_title"), padding=10)
        filter_frame.pack(fill="x", pady=(0, 8))

        self.filter_mode_var = tk.StringVar(value=self.config.get("filter_mode", "pattern"))
        radio_row = ttk.Frame(filter_frame)
        radio_row.pack(fill="x")
        ttk.Radiobutton(
            radio_row, text=self.t.t("filter_pattern"),
            variable=self.filter_mode_var, value="pattern",
        ).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(
            radio_row, text=self.t.t("filter_exact"),
            variable=self.filter_mode_var, value="exact",
        ).pack(side="left")

        self.filter_value_var = tk.StringVar(value=self.config.get("filter_value", "*.mp4"))
        ttk.Entry(filter_frame, textvariable=self.filter_value_var).pack(fill="x", pady=(6, 0))

        ttk.Label(
            filter_frame, text=self.t.t("filter_extensions_note"),
            style="Muted.TLabel", font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(2, 0))

        move_frame = ttk.LabelFrame(parent, text=self.t.t("move_title"), padding=10)
        move_frame.pack(fill="x", pady=(0, 8))

        self.move_enabled_var = tk.BooleanVar(value=self.config.get("move_after_upload", False))
        ttk.Checkbutton(
            move_frame, text=self.t.t("move_enabled"),
            variable=self.move_enabled_var, command=self._toggle_move_field,
        ).pack(anchor="w")

        move_row = ttk.Frame(move_frame)
        move_row.pack(fill="x", pady=(4, 0))
        self.move_dest_var = tk.StringVar(value=self.config.get("move_destination", ""))
        self.move_dest_entry = ttk.Entry(move_row, textvariable=self.move_dest_var)
        self.move_dest_entry.pack(side="left", fill="x", expand=True)
        self.move_dest_btn = ttk.Button(
            move_row, text=self.t.t("browse"), command=self._browse_move_dest
        )
        self.move_dest_btn.pack(side="right", padx=(8, 0))
        self._toggle_move_field()

        options_frame = ttk.Frame(parent)
        options_frame.pack(fill="x", pady=(0, 8))

        self.shutdown_var = tk.BooleanVar(value=self.config.get("shutdown_after", False))
        ttk.Checkbutton(
            options_frame, text=self.t.t("shutdown_after"),
            variable=self.shutdown_var,
        ).pack(anchor="w")

        self.play_sound_var = tk.BooleanVar(value=self.config.get("play_sound_enabled", False))
        ttk.Checkbutton(
            options_frame, text=self.t.t("play_sound_after"),
            variable=self.play_sound_var,
        ).pack(anchor="w")

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=(4, 8))
        self.start_btn = ttk.Button(
            btn_row, text=self.t.t("start_monitoring"), command=self._on_start
        )
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            btn_row, text=self.t.t("stop"), command=self._on_stop, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(8, 0))

        ttk.Button(btn_row, text=self.t.t("view_history"), command=self._show_history_window).pack(
            side="left", padx=(8, 0)
        )

        self.status_var = tk.StringVar(value=self.t.t("ready"))
        ttk.Label(btn_row, textvariable=self.status_var, style="Accent.TLabel").pack(side="right")

        log_frame = ttk.LabelFrame(parent, text="Log", padding=6)
        log_frame.pack(fill="both", expand=True)

        c = self.colors
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=8, font=("Consolas", 9), state="disabled",
            bg=c["log_bg"], fg=c["log_fg"], insertbackground=c["log_fg"],
        )
        self.log_text.pack(fill="both", expand=True)

    def _build_settings_tab(self, parent):
        # Idioma
        lang_frame = ttk.LabelFrame(parent, text=self.t.t("settings_language"), padding=10)
        lang_frame.pack(fill="x", pady=(0, 8))

        self.lang_var = tk.StringVar(value=self.config.get("language", "en"))
        for label, code in [("Portugues", "pt"), ("English", "en")]:
            ttk.Radiobutton(
                lang_frame, text=label, variable=self.lang_var, value=code,
                command=self._on_language_changed,
            ).pack(anchor="w")

        # Tema
        theme_frame = ttk.LabelFrame(parent, text=self.t.t("settings_color_scheme"), padding=10)
        theme_frame.pack(fill="x", pady=(0, 8))

        self.theme_var = tk.StringVar(value=self.config.get("color_scheme", "light"))
        ttk.Radiobutton(
            theme_frame, text=self.t.t("color_light"),
            variable=self.theme_var, value="light",
            command=self._on_theme_changed,
        ).pack(anchor="w")
        ttk.Radiobutton(
            theme_frame, text=self.t.t("color_dark"),
            variable=self.theme_var, value="dark",
            command=self._on_theme_changed,
        ).pack(anchor="w")

        # Som
        sound_frame = ttk.LabelFrame(parent, text=self.t.t("settings_sound"), padding=10)
        sound_frame.pack(fill="x", pady=(0, 8))

        self.sound_type_var = tk.StringVar(value=self.config.get("sound_type", "beep"))
        ttk.Radiobutton(
            sound_frame, text=self.t.t("sound_beep"),
            variable=self.sound_type_var, value="beep",
            command=self._on_sound_type_changed,
        ).pack(anchor="w")
        ttk.Radiobutton(
            sound_frame, text=self.t.t("sound_plim"),
            variable=self.sound_type_var, value="windows",
            command=self._on_sound_type_changed,
        ).pack(anchor="w")
        ttk.Radiobutton(
            sound_frame, text=self.t.t("sound_custom"),
            variable=self.sound_type_var, value="custom",
            command=self._on_sound_type_changed,
        ).pack(anchor="w")

        custom_row = ttk.Frame(sound_frame)
        custom_row.pack(fill="x", pady=(6, 0))
        self.sound_custom_var = tk.StringVar(value=self.config.get("sound_custom_path", ""))
        self.sound_custom_entry = ttk.Entry(custom_row, textvariable=self.sound_custom_var)
        self.sound_custom_entry.pack(side="left", fill="x", expand=True)
        self.sound_custom_btn = ttk.Button(
            custom_row, text=self.t.t("browse"), command=self._browse_sound_file
        )
        self.sound_custom_btn.pack(side="right", padx=(8, 0))

        ttk.Button(sound_frame, text=self.t.t("sound_test"), command=self._test_sound).pack(
            anchor="w", pady=(8, 0)
        )

        self._update_custom_sound_state()

        # Historico
        hist_frame = ttk.LabelFrame(parent, text=self.t.t("settings_history"), padding=10)
        hist_frame.pack(fill="x", pady=(0, 8))

        ttk.Button(
            hist_frame, text=self.t.t("clear_history_btn"),
            command=self._clear_history_clicked,
        ).pack(anchor="w")

    # ----------------------- Settings handlers -----------------------

    def _on_language_changed(self):
        new_lang = self.lang_var.get()
        if new_lang == self.config.get("language"):
            return
        self._sync_state_to_config()
        self.config["language"] = new_lang
        config_store.save_config(self.config)
        self.t.set_language(new_lang)
        self._build_ui()
        self.notebook.select(self.settings_tab)
        self._refresh_auth_status()

    def _on_theme_changed(self):
        new_theme = self.theme_var.get()
        if new_theme == self.config.get("color_scheme"):
            return
        self._sync_state_to_config()
        self.config["color_scheme"] = new_theme
        config_store.save_config(self.config)
        self._apply_theme()
        self._build_ui()
        self.notebook.select(self.settings_tab)
        self._refresh_auth_status()

    def _on_sound_type_changed(self):
        self.config["sound_type"] = self.sound_type_var.get()
        config_store.save_config(self.config)
        self._update_custom_sound_state()

    def _update_custom_sound_state(self):
        is_custom = self.sound_type_var.get() == "custom"
        state = "normal" if is_custom else "disabled"
        try:
            self.sound_custom_entry.config(state=state)
            self.sound_custom_btn.config(state=state)
        except Exception:
            pass

    def _browse_sound_file(self):
        path = filedialog.askopenfilename(
            title=self.t.t("select_sound_file"),
            filetypes=[("Audio", "*.wav *.mp3"), ("All", "*.*")],
        )
        if path:
            self.sound_custom_var.set(path)
            self.config["sound_custom_path"] = path
            config_store.save_config(self.config)

    def _test_sound(self):
        sound_type = self.sound_type_var.get()
        custom_path = self.sound_custom_var.get().strip()
        self.config["sound_custom_path"] = custom_path
        config_store.save_config(self.config)
        sound_player.play_sound(sound_type, custom_path)

    def _clear_history_clicked(self):
        if not messagebox.askyesno(APP_NAME, self.t.t("clear_history_confirm")):
            return
        if history_store.clear_history():
            messagebox.showinfo(APP_NAME, self.t.t("history_cleared"))

    def _sync_state_to_config(self):
        """Le valores atuais dos widgets e salva na config (pra persistir antes de rebuild)."""
        try:
            self.config.update({
                "drive_folder_url": self.drive_url_var.get().strip(),
                "watch_folder": self.watch_var.get().strip(),
                "filter_mode": self.filter_mode_var.get(),
                "filter_value": self.filter_value_var.get().strip(),
                "move_after_upload": self.move_enabled_var.get(),
                "move_destination": self.move_dest_var.get().strip(),
                "shutdown_after": self.shutdown_var.get(),
                "play_sound_enabled": self.play_sound_var.get(),
                "sound_type": self.sound_type_var.get(),
                "sound_custom_path": self.sound_custom_var.get().strip(),
            })
            config_store.save_config(self.config)
        except Exception:
            pass

    # ----------------------- History window -----------------------

    def _show_history_window(self):
        win = tk.Toplevel(self.root)
        win.title(self.t.t("history_title"))
        win.geometry("700x420")
        win.configure(bg=self.colors["bg"])

        entries = history_store.read_history()

        if not entries:
            ttk.Label(win, text=self.t.t("history_empty"), padding=20).pack(expand=True)
        else:
            cols = ("date", "file", "size", "status")
            tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
            tree.heading("date", text=self.t.t("history_col_date"))
            tree.heading("file", text=self.t.t("history_col_file"))
            tree.heading("size", text=self.t.t("history_col_size"))
            tree.heading("status", text=self.t.t("history_col_status"))
            tree.column("date", width=140)
            tree.column("file", width=300)
            tree.column("size", width=90)
            tree.column("status", width=80)

            for e in entries:
                status_text = (
                    self.t.t("history_status_ok") if e.get("status") == "ok"
                    else self.t.t("history_status_fail")
                )
                tree.insert("", "end", values=(
                    e.get("timestamp", "-"),
                    e.get("filename", "-"),
                    history_store.format_size(e.get("size_bytes", 0)),
                    status_text,
                ))

            scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
            scrollbar.pack(side="left", fill="y", pady=8)

        btn_row = ttk.Frame(win)
        btn_row.pack(side="bottom", fill="x", padx=8, pady=8)
        ttk.Button(btn_row, text=self.t.t("history_open_log"), command=self._open_error_log).pack(side="left")
        ttk.Button(btn_row, text=self.t.t("close"), command=win.destroy).pack(side="right")

    def _open_error_log(self):
        log_path = history_store.ERROR_LOG_FILE
        if not log_path.exists():
            messagebox.showinfo(APP_NAME, self.t.t("history_log_not_found"))
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(log_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(log_path)])
            else:
                subprocess.run(["xdg-open", str(log_path)])
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    # ----------------------- UI helpers -----------------------

    def _toggle_move_field(self):
        state = "normal" if self.move_enabled_var.get() else "disabled"
        self.move_dest_entry.config(state=state)
        self.move_dest_btn.config(state=state)

    def _browse_watch(self):
        path = filedialog.askdirectory(title=self.t.t("select_watch_folder"))
        if path:
            self.watch_var.set(path)

    def _browse_move_dest(self):
        path = filedialog.askdirectory(title=self.t.t("select_move_dest"))
        if path:
            self.move_dest_var.set(path)

    def _log(self, msg: str):
        def append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, append)

    def _set_status(self, msg: str):
        self.root.after(0, lambda: self.status_var.set(msg))

    # ----------------------- Auth -----------------------

    def _refresh_auth_status(self):
        if rclone_manager.is_drive_authenticated():
            self.auth_status_label.config(text=self.t.t("connected"), style="Accent.TLabel")
            self.connect_btn.config(text=self.t.t("reconnect"))

            def fetch_email():
                email = rclone_manager.get_authenticated_account_email()
                if email:
                    self.root.after(0, lambda: self.auth_status_label.config(
                        text=self.t.t("connected_as", email=email)
                    ))
            threading.Thread(target=fetch_email, daemon=True).start()
        else:
            self.auth_status_label.config(text=self.t.t("not_connected"), style="Danger.TLabel")
            self.connect_btn.config(text=self.t.t("connect"))

    def _on_connect_clicked(self):
        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="disabled")
        self._log(self.t.t("auth_starting"))
        self._log(self.t.t("auth_browser_will_open"))

        def worker():
            success, msg = rclone_manager.authenticate_drive(
                on_progress=lambda s: self._log(f"  {s}")
            )
            self.root.after(0, lambda: self._after_auth(success, msg))

        threading.Thread(target=worker, daemon=True).start()

    def _after_auth(self, success: bool, msg: str):
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="normal")
        self._refresh_auth_status()
        if success:
            messagebox.showinfo(APP_NAME, self.t.t("auth_success"))
        else:
            messagebox.showerror(APP_NAME, self.t.t("auth_failed", msg=msg))
            self._log(self.t.t("log_error", msg=msg))
            history_store.log_error("AUTH", msg)

    def _on_disconnect_clicked(self):
        if not messagebox.askyesno(APP_NAME, self.t.t("disconnect_confirm")):
            return
        rclone_manager.disconnect_drive()
        self._refresh_auth_status()
        self._log(self.t.t("account_disconnected"))

    # ----------------------- Start/stop monitor -----------------------

    def _validate_inputs(self) -> tuple[bool, str]:
        if not rclone_manager.is_drive_authenticated():
            return False, self.t.t("err_not_authenticated")

        url = self.drive_url_var.get().strip()
        if not url:
            return False, self.t.t("err_drive_url_empty")

        folder_id = rclone_manager.extract_folder_id(url)
        if not folder_id:
            return False, self.t.t("err_drive_url_invalid")

        watch = self.watch_var.get().strip()
        if not watch or not Path(watch).is_dir():
            return False, self.t.t("err_watch_folder_invalid")

        filter_value = self.filter_value_var.get().strip()
        if not filter_value:
            return False, self.t.t("err_filter_empty")

        if self.move_enabled_var.get():
            move_dest = self.move_dest_var.get().strip()
            if not move_dest:
                return False, self.t.t("err_move_dest_empty")

        return True, ""

    def _on_start(self):
        ok, err = self._validate_inputs()
        if not ok:
            messagebox.showerror(APP_NAME, err)
            return

        self._sync_state_to_config()

        folder_id = rclone_manager.extract_folder_id(self.drive_url_var.get().strip())
        move_dest = self.move_dest_var.get().strip() if self.move_enabled_var.get() else ""

        def on_upload_complete():
            if self.play_sound_var.get():
                sound_player.play_sound(
                    self.config.get("sound_type", "beep"),
                    self.config.get("sound_custom_path", ""),
                )

        self.monitor = UploadMonitor(
            watch_folder=self.watch_var.get().strip(),
            drive_folder_id=folder_id,
            filter_mode=self.filter_mode_var.get(),
            filter_value=self.filter_value_var.get().strip(),
            move_destination=move_dest,
            on_log=self._log,
            on_status=self._set_status,
            on_finished_all=self._on_monitor_finished,
            on_upload_complete=on_upload_complete,
            translator=self.t,
        )
        self.monitor.start()

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def _on_stop(self):
        if self.monitor:
            self.monitor.stop()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._shutdown_pending = False

    def _on_monitor_finished(self):
        if self.shutdown_var.get():
            self.root.after(0, self._initiate_shutdown)

    def _initiate_shutdown(self):
        if self._shutdown_pending:
            return
        self._shutdown_pending = True

        confirm = messagebox.askyesno(APP_NAME, self.t.t("shutdown_question"))

        if confirm:
            self._log(self.t.t("log_shutdown"))
            try:
                subprocess.run(
                    ["shutdown", "/s", "/t", "60", "/c", "AutoDrive Uploader"],
                    check=False,
                )
                messagebox.showinfo(APP_NAME, self.t.t("shutdown_scheduled"))
            except Exception as e:
                self._log(self.t.t("log_shutdown_fail", err=str(e)))
                history_store.log_error("SHUTDOWN", str(e))
        else:
            self._log(self.t.t("log_shutdown_cancelled"))
            self._shutdown_pending = False

    # ----------------------- Close -----------------------

    def _on_close(self):
        if self.monitor and self.monitor.is_running:
            if not messagebox.askyesno(APP_NAME, self.t.t("close_while_running")):
                return
            self.monitor.stop()

        try:
            self._sync_state_to_config()
        except Exception:
            pass

        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

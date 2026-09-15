# -*- mode: python ; coding: utf-8 -*-
"""Config UI dialog (shell) -- each tab lives in its own file.

* ``tab_settings.py`` -- Settings tab
* ``tab_logs.py`` -- Logs tab
* ``tab_support.py`` -- Support tab (QR codes in ``Support/``)

Wired up through ``mw.addonManager.setConfigAction`` so the *Config*
button in the add-ons list opens this dialog instead of the raw JSON editor.
"""
from __future__ import annotations
from typing import Any
from aqt import mw
from aqt.qt import (
    QDialog, QHBoxLayout, QListWidgetItem, QMessageBox, QPushButton,
    QTabWidget, QTimer, QVBoxLayout,
)
from .config import get_config, save_config, refresh_settings
from .constants import (
    CFG_CONTENT, CFG_SEPARATOR, CFG_TAG_SEPARATOR, CFG_MAX_TAGS,
    CFG_IGNORED_TAGS, CFG_SHOW_SUBDECK, CFG_SUBDECK_FORMAT, CFG_USE_ARGV0,
    DEFAULTS,
)
from .tab_logs import LogsTabMixin
from .tab_settings import SettingsTabMixin
from .tab_support import SupportTabMixin


def _standard_button(name: str):
    """Return a QMessageBox.StandardButton that works on PyQt6 and PyQt5."""
    try:
        return getattr(QMessageBox.StandardButton, name)
    except AttributeError:
        return getattr(QMessageBox, name)


def _run_dialog(dialog: QDialog) -> None:
    if hasattr(dialog, "exec"):
        dialog.exec()
    else:
        dialog.exec_()


class SettingsDialog(LogsTabMixin, SettingsTabMixin, SupportTabMixin, QDialog):
    """Qt window where the user configures what appears in the title bar."""

    def __init__(self, parent=None, initial_tab: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Deck Name & Tags in Title — Settings")
        self.setMinimumWidth(640)
        self._log_timer = None
        self._build_ui(initial_tab=initial_tab)
        self._load_values()
        try:
            self.load_supporter_state()
        except Exception:
            pass
        self._refresh_logs()
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1000)
        self._log_timer.timeout.connect(self._refresh_logs)
        self._log_timer.start()

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if self._log_timer is not None:
            self._log_timer.stop()
            self._log_timer = None
        super().closeEvent(event)

    def _build_ui(self, initial_tab: str | None = None) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_settings_tab(), "Settings")
        self.tabs.addTab(self._build_logs_tab(), "Logs")
        self.tabs.addTab(self._create_support_tab(), "Support")
        root.addWidget(self.tabs)
        if initial_tab:
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i).lower() == str(initial_tab).lower():
                    self.tabs.setCurrentIndex(i)
                    break
        buttons = QHBoxLayout()
        btn_reset = QPushButton("Reset to defaults")
        btn_reset.clicked.connect(self._on_reset)
        buttons.addWidget(btn_reset)
        buttons.addStretch(1)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        buttons.addWidget(btn_close)
        btn_save = QPushButton("Save")
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        buttons.addWidget(btn_save)
        root.addLayout(buttons)

    def _load_values(self) -> None:
        cfg = get_config()
        default_content = DEFAULTS[CFG_CONTENT]
        for i in range(self.combo_content.count()):
            if self.combo_content.itemData(i) == cfg.get(CFG_CONTENT, default_content):
                self.combo_content.setCurrentIndex(i)
                break
        self.edit_separator.setText(str(cfg.get(CFG_SEPARATOR, DEFAULTS[CFG_SEPARATOR])))
        self.edit_tag_separator.setText(str(cfg.get(CFG_TAG_SEPARATOR, DEFAULTS[CFG_TAG_SEPARATOR])))
        self.spin_max_tags.setValue(int(cfg.get(CFG_MAX_TAGS, DEFAULTS[CFG_MAX_TAGS]) or 0))
        self._load_all_tags()
        self._set_ignored_list(self._split_tags(cfg.get(CFG_IGNORED_TAGS)))
        self.cb_subdeck.setChecked(bool(cfg.get(CFG_SHOW_SUBDECK, DEFAULTS[CFG_SHOW_SUBDECK])))
        self.edit_subdeck_format.setText(str(cfg.get(CFG_SUBDECK_FORMAT, DEFAULTS[CFG_SUBDECK_FORMAT])))
        self.cb_argv0.setChecked(bool(cfg.get(CFG_USE_ARGV0, DEFAULTS[CFG_USE_ARGV0])))

    def _collect_config(self) -> dict[str, Any]:
        cfg = dict(get_config())
        cfg[CFG_CONTENT] = self.combo_content.currentData()
        cfg[CFG_SEPARATOR] = self.edit_separator.text()
        cfg[CFG_TAG_SEPARATOR] = self.edit_tag_separator.text()
        cfg[CFG_MAX_TAGS] = int(self.spin_max_tags.value())
        cfg[CFG_IGNORED_TAGS] = list(self._get_ignored_list())
        cfg[CFG_SHOW_SUBDECK] = bool(self.cb_subdeck.isChecked())
        cfg[CFG_SUBDECK_FORMAT] = self.edit_subdeck_format.text()
        cfg[CFG_USE_ARGV0] = bool(self.cb_argv0.isChecked())
        return cfg

    @staticmethod
    def _split_tags(value: Any) -> list[str]:
        import re
        if value is None:
            return []
        if isinstance(value, str):
            parts = re.split(r"[,\s;]+", value)
        elif isinstance(value, (list, tuple)):
            parts = list(value)
        else:
            parts = [value]
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in parts:
            text = str(item).strip().strip(",;")
            if not text:
                continue
            lowered = text.lower()
            if lowered not in seen:
                seen.add(lowered)
                cleaned.append(text)
        return cleaned

    def _collection_tags(self) -> list[str]:
        tags: list[str] = []
        try:
            col = getattr(mw, "col", None)
            manager = getattr(col, "tags", None) if col is not None else None
            fetched = manager.all() if manager is not None else []
            tags = sorted(str(name) for name in (fetched or []) if str(name).strip())
        except Exception:
            tags = []
        return tags

    def _load_all_tags(self) -> None:
        self.ignored_model.setStringList(self._collection_tags())

    def _get_ignored_list(self) -> list[str]:
        return [
            str(self.list_ignored.item(row).text())
            for row in range(self.list_ignored.count())
            if self.list_ignored.item(row) is not None
        ]

    def _set_ignored_list(self, tags: list[str]) -> None:
        self.list_ignored.clear()
        for tag in self._split_tags(tags):
            self.list_ignored.addItem(QListWidgetItem(tag))
        self.ignored_edit.clear()

    def _add_ignored_tags(self, tags: list[str]) -> None:
        existing = {text.lower() for text in self._get_ignored_list()}
        for tag in self._split_tags(tags):
            if tag.lower() not in existing:
                existing.add(tag.lower())
                self.list_ignored.addItem(QListWidgetItem(tag))
        self.ignored_edit.clear()

    def _on_add_ignored(self) -> None:
        self._add_ignored_tags([self.ignored_edit.text()])

    def _on_remove_ignored(self) -> None:
        for item in self.list_ignored.selectedItems():
            row = self.list_ignored.row(item)
            self.list_ignored.takeItem(row)

    def _on_save(self) -> None:
        save_config(self._collect_config())
        refresh_settings()
        self.accept()

    def _on_reset(self) -> None:
        yes = _standard_button("Yes")
        no = _standard_button("No")
        result = QMessageBox.question(
            self, "Reset to defaults", "Reset all settings to their defaults?",
            yes | no, no,
        )
        if result == yes:
            save_config(dict(DEFAULTS))
            refresh_settings()
            self._load_values()


def open_settings(*_args, initial_tab: str | None = None, **_kwargs) -> None:
    """Open the settings dialog (pick compatible exec)."""
    _run_dialog(SettingsDialog(mw, initial_tab=initial_tab))


def register_config_action() -> None:
    """Bind the Config button in the add-ons list to our dialog."""
    try:
        mw.addonManager.setConfigAction(__name__, open_settings)
    except Exception:
        from aqt.qt import QAction
        action = QAction("Deck Name & Tags in Title — Settings", mw)
        action.triggered.connect(open_settings)
        mw.form.menuTools.addAction(action)

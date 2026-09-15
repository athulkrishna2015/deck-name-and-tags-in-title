# -*- mode: python ; coding: utf-8 -*-
"""Config UI dialog.

This module provides a small Qt settings window (opened from **Tools →
Add-ons → deck_name_and_tags_in_title → Config**) that lets the user pick
which information appears in the window title:
deck name, current card tags, both (default), or nothing — plus the various
separators and formatting options.

It is wired up through ``mw.addonManager.setConfigAction``, so clicking the
usual *Config* button in the add-ons list opens this dialog instead of the
raw JSON editor.  If the config action API is unavailable on an older Anki
build, a fallback entry is added to the **Tools** menu.
"""

from __future__ import annotations

from typing import Any

from aqt import mw
from aqt.qt import (
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDesktopServices,
    QDialog,
    QFont,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit, QPushButton, QSpinBox, QStringListModel,
    QTabWidget, QTimer, QUrl, QVBoxLayout, QWidget,
)

from . import logging as logmod
from .config import get_config, save_config, refresh_settings
from .constants import (
    CFG_CONTENT,
    CFG_SEPARATOR,
    CFG_TAG_SEPARATOR,
    CFG_MAX_TAGS,
    CFG_IGNORED_TAGS,
    CFG_SHOW_SUBDECK,
    CFG_SUBDECK_FORMAT,
    CFG_USE_ARGV0,
    CONTENT_LABELS,
    DEFAULTS,
)


def _standard_button(name: str):
    """Return a QMessageBox.StandardButton that works on PyQt6 and PyQt5."""
    try:
        return getattr(QMessageBox.StandardButton, name)
    except AttributeError:  # PyQt5 fallback
        return getattr(QMessageBox, name)


def _run_dialog(dialog: QDialog) -> None:
    """Run ``dialog`` with PyQt6/PyQt5 compatible ``exec``."""
    if hasattr(dialog, "exec"):
        dialog.exec()
    else:  # PyQt5 provides exec_()
        dialog.exec_()


class SettingsDialog(QDialog):
    """Qt window where the user configures what appears in the title bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deck Name & Tags in Title — Settings")
        self.setMinimumWidth(640)
        self._log_timer = None
        self._build_ui()
        self._load_values()
        self._refresh_logs()
        # Live-refresh the Logs tab while the dialog is open.
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1000)
        self._log_timer.timeout.connect(self._refresh_logs)
        self._log_timer.start()

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if self._log_timer is not None:
            self._log_timer.stop()
            self._log_timer = None
        super().closeEvent(event)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        self.tabs = QTabWidget()

        # ===== Settings tab ================================================
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(12)

        # --- What to show -------------------------------------------------
        group_content = QGroupBox("Title content")
        content_form = QFormLayout(group_content)
        content_form.setContentsMargins(10, 14, 10, 10)

        self.combo_content = QComboBox()
        for value, label in CONTENT_LABELS.items():
            self.combo_content.addItem(label, value)
        content_form.addRow("Show in the window title:", self.combo_content)
        content_form.addRow(
            "",
            QLabel(
                "Deck names come from the deck you are in; tags come from the "
                "note behind the reviewed card (they only appear during review)."
            ),
        )
        settings_layout.addWidget(group_content)

        # --- Formatting -----------------------------------------------------
        group_fmt = QGroupBox("Formatting")
        fmt = QFormLayout(group_fmt)
        fmt.setContentsMargins(10, 14, 10, 10)

        self.edit_separator = QLineEdit()
        fmt.addRow("Title separator:", self.edit_separator)

        self.edit_tag_separator = QLineEdit()
        fmt.addRow("Tag separator:", self.edit_tag_separator)

        self.spin_max_tags = QSpinBox()
        self.spin_max_tags.setRange(0, 50)
        self.spin_max_tags.setSpecialValueText("No limit")
        fmt.addRow("Maximum tags shown:", self.spin_max_tags)

        self.ignored_edit = QLineEdit()
        self.ignored_completer = QCompleter(self)
        self.ignored_completer.setCaseSensitivity(0)  # Qt.CaseInsensitive
        self.ignored_model = QStringListModel(self)
        self.ignored_completer.setModel(self.ignored_model)
        self.ignored_edit.setCompleter(self.ignored_completer)
        fmt.addRow("Ignored tags:", self.ignored_edit)
        fmt.addRow(
            "",
            QLabel(
                "Tags never shown in the title — separate with commas. "
                "Type and pick from your collection's tags."
            ),
        )

        self.list_ignored = QListWidget()
        self.list_ignored.setSelectionMode(3)  # QAbstractItemView.ExtendedSelection
        self.list_ignored.setMaximumHeight(110)
        fmt.addRow("Ignoring now:", self.list_ignored)

        row_ignored_buttons = QHBoxLayout()
        self.btn_add_ignored = QPushButton("Add typed tag")
        self.btn_add_ignored.clicked.connect(self._on_add_ignored)
        row_ignored_buttons.addWidget(self.btn_add_ignored)
        self.btn_remove_ignored = QPushButton("Remove selected")
        self.btn_remove_ignored.clicked.connect(self._on_remove_ignored)
        row_ignored_buttons.addWidget(self.btn_remove_ignored)
        btn_refresh_tags = QPushButton("Refresh tag list")
        btn_refresh_tags.clicked.connect(self._load_all_tags)
        row_ignored_buttons.addWidget(btn_refresh_tags)
        fmt.addRow("", row_ignored_buttons)

        self.cb_subdeck = QCheckBox(
            "Show the sub-deck you descended into during review"
        )
        fmt.addRow("", self.cb_subdeck)

        self.edit_subdeck_format = QLineEdit()
        fmt.addRow("Sub-deck format:", self.edit_subdeck_format)

        self.cb_argv0 = QCheckBox('Use the program file name instead of "Anki"')
        fmt.addRow("", self.cb_argv0)

        settings_layout.addWidget(group_fmt)
        settings_layout.addStretch()
        self.tabs.addTab(settings_tab, "Settings")

        # ===== Logs tab =====================================================
        self.tabs.addTab(self._build_logs_tab(), "Logs")

        root.addWidget(self.tabs)

        # --- Buttons ---------------------------------------------------------
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
# ------------------------------------------------------------ Logs tab
    def _build_logs_tab(self) -> QWidget:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Toolbar row
        top = QHBoxLayout()
        top.addWidget(QLabel("Minimum level:"))
        self.combo_log_level = QComboBox()
        for label, lvl in (
            ("DEBUG", logmod.DEBUG),
            ("INFO", logmod.INFO),
            ("WARNING", logmod.WARNING),
            ("ERROR", logmod.ERROR),
        ):
            self.combo_log_level.addItem(label, lvl)
        self.combo_log_level.setCurrentIndex(0)
        self.combo_log_level.currentIndexChanged.connect(self._refresh_logs)
        top.addWidget(self.combo_log_level)
        top.addStretch(1)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh_logs)
        top.addWidget(btn_refresh)

        btn_copy = QPushButton("Copy")
        btn_copy.clicked.connect(self._on_log_copy)
        top.addWidget(btn_copy)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._on_log_clear)
        top.addWidget(btn_clear)

        btn_open = QPushButton("Open log file…")
        btn_open.clicked.connect(self._on_log_open)
        top.addWidget(btn_open)

        lay.addLayout(top)

        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        try:  # monospace helps readability where available
            self.txt_log.setLineWrapMode(0)  # QPlainTextEdit.NoWrap
            font = QFont("monospace")
            font.setPointSize(9)
            self.txt_log.setFont(font)
        except Exception:
            pass
        lay.addWidget(self.txt_log)

        self.lbl_log_path = QLabel("")
        lay.addWidget(self.lbl_log_path)
        return tab

    # ------------------------------------------------------------ log helpers
    def _current_log_level(self) -> int:
        if self.combo_log_level is None:
            return logmod.DEBUG
        lvl = self.combo_log_level.currentData()
        return lvl if isinstance(lvl, int) else logmod.DEBUG

    def _refresh_logs(self) -> None:
        level = self._current_log_level()
        lines = logmod.snapshot(level)
        self.txt_log.setPlainText("\n".join(lines))
        self.lbl_log_path.setText(
            "Log file: {}   |   shown: {}   (in-memory ring: {})".format(
                logmod.log_file_path() or "(none)",
                len(lines),
                logmod.ring_size(),
            )
        )

    def _on_log_copy(self) -> None:
        text = self.txt_log.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def _on_log_clear(self) -> None:
        logmod.clear()
        self._refresh_logs()

    def _on_log_open(self) -> None:
        path = logmod.log_file_path()
        if not path:
            QMessageBox.information(self, "Log file", "No log file is available.")
            return
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc:  # pragma: no cover
            QMessageBox.information(self, "Log file", f"{path}\n\n{exc}")

# ---------------------------------------------------------- load / save
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
        self.edit_subdeck_format.setText(
            str(cfg.get(CFG_SUBDECK_FORMAT, DEFAULTS[CFG_SUBDECK_FORMAT]))
        )
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

    # ------------------------------------------------------------ ignored tags
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
            self,
            "Reset to defaults",
            "Reset all settings to their defaults?",
            yes | no,
            no,
        )
        if result == yes:
            save_config(dict(DEFAULTS))
            refresh_settings()
            self._load_values()


def open_settings(*_args, **_kwargs) -> None:
    """Open the settings dialog (pick compatible exec)."""
    _run_dialog(SettingsDialog(mw))


def register_config_action() -> None:
    """Bind the Config button in the add-ons list to our dialog."""
    # Tolerate 0/1+ positional args across Anki versions.
    try:
        mw.addonManager.setConfigAction(__name__, open_settings)
    except Exception:
        # Fallback: add a Tools menu item if the config-action API is missing.
        from aqt.qt import QAction

        action = QAction("Deck Name & Tags in Title — Settings", mw)
        action.triggered.connect(open_settings)
        mw.form.menuTools.addAction(action)
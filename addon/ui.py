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
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from .config import get_config, save_config, refresh_settings
from .constants import (
    CFG_CONTENT,
    CFG_SEPARATOR,
    CFG_TAG_SEPARATOR,
    CFG_MAX_TAGS,
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
        self.setMinimumWidth(460)
        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

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
                "card being reviewed (tags only appear during review)."
            ),
        )
        root.addWidget(group_content)

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

        self.cb_subdeck = QCheckBox(
            "Show the sub-deck you descended into during review"
        )
        fmt.addRow("", self.cb_subdeck)

        self.edit_subdeck_format = QLineEdit()
        fmt.addRow("Sub-deck format:", self.edit_subdeck_format)

        self.cb_argv0 = QCheckBox('Use the program file name instead of "Anki"')
        fmt.addRow("", self.cb_argv0)

        root.addWidget(group_fmt)

        # --- Buttons ---------------------------------------------------------
        buttons = QHBoxLayout()
        btn_reset = QPushButton("Reset to defaults")
        btn_reset.clicked.connect(self._on_reset)
        buttons.addWidget(btn_reset)
        buttons.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)

        btn_save = QPushButton("Save")
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        buttons.addWidget(btn_save)

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
        cfg[CFG_SHOW_SUBDECK] = bool(self.cb_subdeck.isChecked())
        cfg[CFG_SUBDECK_FORMAT] = self.edit_subdeck_format.text()
        cfg[CFG_USE_ARGV0] = bool(self.cb_argv0.isChecked())
        return cfg

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
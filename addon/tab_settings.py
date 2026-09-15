# -*- mode: python ; coding: utf-8 -*-
"""Settings tab for the config dialog (one tab = one file)."""
from __future__ import annotations
from aqt.qt import (
    QCheckBox, QComboBox, QCompleter, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QSpinBox, QStringListModel,
    QVBoxLayout, QWidget,
)
from .constants import CONTENT_LABELS


class SettingsTabMixin:
    """Builds the Settings tab widgets onto ``self``."""

    def _build_settings_tab(self) -> QWidget:
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(12)
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
        try:
            from aqt.qt import Qt as _Qt

            try:
                _cs = _Qt.CaseSensitivity.CaseInsensitive  # Qt6
            except AttributeError:
                _cs = getattr(_Qt, "CaseInsensitive", None)  # Qt5 fallback
            if _cs is not None:
                self.ignored_completer.setCaseSensitivity(_cs)
        except Exception:
            pass  # keep Qt default (case-sensitive) if enum unavailable
        self.ignored_model = QStringListModel(self)
        self.ignored_completer.setModel(self.ignored_model)
        self.ignored_edit.setCompleter(self.ignored_completer)
        fmt.addRow("Ignored tags:", self.ignored_edit)
        fmt.addRow(
            "",
            QLabel(
                "Tags never shown in the title — separate with commas. "
                "Type and pick from your collection\'s tags."
            ),
        )
        self.list_ignored = QListWidget()
        try:
            try:
                from aqt.qt import QAbstractItemView as _QAbsView
            except ImportError:
                from PyQt6.QtWidgets import QAbstractItemView as _QAbsView  # type: ignore
            try:
                _mode = _QAbsView.SelectionMode.ExtendedSelection  # Qt6
            except AttributeError:
                _mode = getattr(_QAbsView, "ExtendedSelection", None)  # Qt5 fallback
            if _mode is not None:
                self.list_ignored.setSelectionMode(_mode)
        except Exception:
            pass  # keep Qt default selection mode if enum unavailable
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
        return settings_tab

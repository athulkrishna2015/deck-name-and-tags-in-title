# -*- mode: python ; coding: utf-8 -*-
"""Logs tab for the config dialog (one tab = one file)."""
from __future__ import annotations
from aqt.qt import (
    QComboBox, QDesktopServices, QFont, QHBoxLayout, QLabel, QMessageBox,
    QPlainTextEdit, QPushButton, QUrl, QVBoxLayout, QWidget,
)
from . import logging as logmod


class LogsTabMixin:
    """Builds the Logs tab and its helpers onto ``self``."""

    def _build_logs_tab(self) -> QWidget:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
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
        btn_open = QPushButton("Open log file...")
        btn_open.clicked.connect(self._on_log_open)
        top.addWidget(btn_open)
        lay.addLayout(top)
        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        try:
            from aqt.qt import QPlainTextEdit as _QPlainTextEdit

            try:
                _nowrap = _QPlainTextEdit.LineWrapMode.NoWrap  # Qt6
            except AttributeError:
                _nowrap = getattr(_QPlainTextEdit, "NoWrap", None)  # Qt5 fallback
            if _nowrap is not None:
                self.txt_log.setLineWrapMode(_nowrap)
            font = QFont("monospace")
            font.setPointSize(9)
            self.txt_log.setFont(font)
        except Exception:
            pass
        lay.addWidget(self.txt_log)
        self.lbl_log_path = QLabel("")
        lay.addWidget(self.lbl_log_path)
        return tab

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
        from aqt.qt import QApplication
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
        except Exception as exc:
            QMessageBox.information(self, "Log file", f"{path}\n\n{exc}")

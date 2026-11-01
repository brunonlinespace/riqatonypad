#!/usr/bin/env python3
"""Existing RiqatonyPad about dialog presentation methods, relocated unchanged."""
import html
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


def show_about_dialog(self):
    # Keep the Pad-family modeless About presentation used by RiqatonyPad 0.5.x.
    # Avoid QMessageBox.about(): the bespoke dialog is consistent with the
    # sibling Pads and has proven more reliable across packaged Qt themes.
    if self.about_dialog is not None:
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()
        return
    dialog = QDialog(self)
    dialog.setWindowTitle("About — RiqatonyPad")
    dialog.setWindowIcon(self.windowIcon())
    dialog.setModal(False)
    dialog.setMinimumSize(700, 470)
    dialog.resize(700, 470)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(24, 22, 24, 18)
    layout.setSpacing(10)

    icon_path = resource_path("icons", "riqatonypad-about.png")
    if os.path.isfile(icon_path):
        logo = QLabel(dialog)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(
                112, 112,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            layout.addWidget(logo)

    title = QLabel(f"<h2>{APP_NAME}</h2>", dialog)
    title.setTextFormat(Qt.TextFormat.RichText)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    version = QLabel(f"Version {APP_VERSION}", dialog)
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version)
    tagline = QLabel("<b>Friendly. Fast. Focused.</b>", dialog)
    tagline.setTextFormat(Qt.TextFormat.RichText)
    tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(tagline)
    description = QLabel(
        "A lightweight Rich Text Format editor focused on portable, "
        "predictable rich documents.",
        dialog,
    )
    description.setWordWrap(True)
    description.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(description)
    details = QLabel(dialog)
    details.setTextFormat(Qt.TextFormat.RichText)
    details.setWordWrap(True)
    details.setAlignment(Qt.AlignmentFlag.AlignCenter)
    details.setOpenExternalLinks(False)
    details.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    # Match Rico Plus: establish readable link roles before RichText parsing.
    details_palette = details.palette()
    if details_palette.color(QPalette.ColorRole.Window).lightness() >= 140:
        about_link_blue = QColor("#0068A6")
        details_palette.setColor(QPalette.ColorRole.Link, about_link_blue)
        details_palette.setColor(QPalette.ColorRole.LinkVisited, about_link_blue)
        details.setPalette(details_palette)
    configuration_path = html.escape(str(self.config_file)).replace("/", "/&#8203;")
    details.setText(
        f"<a href='{GITHUB_URL}'>{GITHUB_URL}</a><br>"
        "Built on Python, PyQt6, Nuxpad 2, "
        "<a href='https://github.com/59de44955ebd/PyWordpad'>PyWordpad</a> "
        "and Microsoft WordPad-inspired document features.<br>"
        f"<b>Configuration:</b> {configuration_path}<br><br>"
        "Copyright © 2026 Bruno Machado<br>"
        "[<a href='https://github.com/brunonlinespace/'>"
        "https://github.com/brunonlinespace/</a>]<br>"
        "Licensed under the GNU General Public License v3 or later."
    )
    details.linkActivated.connect(lambda href:self._open_host_target(href))
    layout.addWidget(details)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog)
    ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
    if ok_button is not None:
        ok_button.setText("OK")
    buttons.accepted.connect(dialog.close)
    layout.addWidget(buttons)
    dialog.finished.connect(lambda _result: setattr(self, "about_dialog", None))
    self.about_dialog = dialog
    dialog.show()

#!/usr/bin/python3
import sys
import random
import logging
import re
import socket
import ssl
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import locale
import os
import shutil

import requests

from PyQt5.QtCore import QUrl, QTimer, Qt, QSettings, QTime, QEvent, QStandardPaths
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QRadioButton, QButtonGroup, QInputDialog, QCheckBox, QComboBox, QTimeEdit,
    QProgressBar, QDoubleSpinBox, QSpinBox, QFileDialog, QSlider, QSizePolicy,
    QGraphicsOpacityEffect
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QDesktopServices

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)

# Globales Stylesheet
GLOBAL_STYLE = """
QMainWindow { background-color: #ffffff; }
QGroupBox { border: 1px solid #cccccc; border-radius: 5px; margin-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
QLineEdit, QTextEdit, QListWidget { border: 1px solid #cccccc; border-radius: 3px; padding: 2px; }
"""

# Button Styles
DAY_BUTTON_STYLE_GREEN = "background-color: #5cb85c; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;"
DAY_BUTTON_STYLE_RED = "background-color: #d9534f; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;"
DAY_BUTTON_STYLE_DEFAULT = "background-color: #ffd700; color: black; border-radius: 5px; padding: 10px 20px; font-size: 14px;"

NIGHT_BUTTON_STYLE_GREEN = "background-color: #006400; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;"
NIGHT_BUTTON_STYLE_RED = "background-color: #8B0000; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;"
NIGHT_BUTTON_STYLE_DEFAULT = "background-color: #161616; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;"

BLUE_RADIO = "QRadioButton { color: #337ab7; padding: 3px; margin: 2px 0px; }"

# --- Übersetzungsfunktionalität und Wörterbücher
CURRENT_LANG = 'de'
translations = {
    'de': {
        "Ab wann soll das helle Motiv verwendet werden? (Direkte Eingabe möglich)":
            "Ab wann soll das helle Motiv verwendet werden? (Direkte Eingabe möglich)",
        "Tagmodus ab:": "Tagmodus ab:",
        "Ab wann soll das dunkle Motiv verwendet werden? (Direkte Eingabe möglich)":
            "Ab wann soll das dunkle Motiv verwendet werden? (Direkte Eingabe möglich)",
        "Nachtmodus ab:": "Nachtmodus ab:",
        "Tag Theme:": "Tag Theme:",
        "Nacht Theme:": "Nacht Theme:",
        "Tag Modus": "Tag Modus",
        "Nacht Modus": "Nacht Modus",
        "URL Hinzufügen": "URL Hinzufügen",
        "URL Löschen": "URL Löschen",
        "Alle URLs Löschen": "Alle URLs Löschen",
        "URLs": "URLs",
        "Funktionen": "Funktionen",
        "Einmalig": "Einmalig",
        "Sequentiell": "Sequentiell",
        "Zufällig": "Zufällig",
        "Parameter & URL Eingabe": "Parameter & URL Eingabe",
        "Wartezeit URL Aufruf:": "Wartezeit URL Aufruf:",
        "Random Zusatz MIN (ms):": "Random Zusatz MIN (ms):",
        "Random Zusatz MAX (ms):": "Random Zusatz MAX (ms):",
        "Durchlauf Wiederholungen:": "Durchlauf Wiederholungen:",
        "Neue URL eingeben...": "Neue URL eingeben...",
        "Proxy Einstellungen": "Proxy Einstellungen",
        "Proxy verwenden": "Proxy verwenden",
        "Typ:": "Typ:",
        "z.B. proxy.example.com": "z.B. proxy.example.com",
        "z.B. 8080": "z.B. 8080",
        "Aufgerufene Website / Video": "Aufgerufene Website / Video",
        "Protokoll / Live Status": "Protokoll / Live Status",
        "Protokoll löschen": "Protokoll löschen",
        "URL Auswahl": "URL Auswahl",
        "YouTube Kanal Videos abrufen": "YouTube Kanal Videos abrufen",
        "YouTube Kanal-URL, Kanal-ID oder Handle eingeben...":
            "YouTube Kanal-URL, Kanal-ID oder Handle eingeben...",
        "Wert eingeben": "Wert eingeben",
        "Neuen Wert eingeben:": "Neuen Wert eingeben:",
        "Theme gewechselt: Tag Modus (": "Theme gewechselt: Tag Modus (",
        "Theme gewechselt: Nacht Modus (": "Theme gewechselt: Nacht Modus (",
        "Kein YouTube-Kanal angegeben.": "Kein YouTube-Kanal angegeben.",
        "Konnte den Titel nicht laden:": "Konnte den Titel nicht laden:",
        "Keine gültige URL eingegeben.": "Keine gültige URL eingegeben.",
        "Keine URLs in der Liste!": "Keine URLs in der Liste!",
        "Auswahl abgebrochen.": "Auswahl abgebrochen.",
        "Keine URLs ausgewählt!": "Keine URLs ausgewählt!",
        "Ungültige URL-Auswahl.": "Ungültige URL-Auswahl.",
        "Starte Ablauf (zufällig), Wiederholungen:": "Starte Ablauf (zufällig), Wiederholungen:",
        "Starte Ablauf (sequentiell), Wiederholungen:": "Starte Ablauf (sequentiell), Wiederholungen:",
        "Beginne Wiederholung": "Beginne Wiederholung",
        "von": "von",
        "Öffne URL:": "Öffne URL:",
        "Warte": "Warte",
        "Sekunden ...": "Sekunden ...",
        "Ablauf gestoppt.": "Ablauf gestoppt.",
        "Ablauf beendet.": "Ablauf beendet.",
        "Stop-Befehl empfangen. Ablauf abgebrochen.":
            "Stop-Befehl empfangen. Ablauf abgebrochen.",
        "Proxy aktiviert, aber Host oder Port fehlen. URL-Aufruf wird abgebrochen.":
            "Proxy aktiviert, aber Host oder Port fehlen. URL-Aufruf wird abgebrochen.",
        "Lade URL über SOCKS4 Proxy:": "Lade URL über SOCKS4 Proxy:",
        "Lade URL über SOCKS5 Proxy:": "Lade URL über SOCKS5 Proxy:",
        "Lade URL über Proxy:": "Lade URL über Proxy:",
        "Fehler: Status Code": "Fehler: Status Code",
        "Fehler beim Proxy-Aufruf:": "Fehler beim Proxy-Aufruf:",
        "Kein Proxy aktiviert – daher wird die URL direkt geladen.":
            "Kein Proxy aktiviert – daher wird die URL direkt geladen.",
        "Fehler beim Abrufen des YouTube-Titels:": "Fehler beim Abrufen des YouTube-Titels:",
        "Konnte die Channel-ID aus der Handle-Seite nicht extrahieren.":
            "Konnte die Channel-ID aus der Handle-Seite nicht extrahieren.",
        "Fehler beim Abrufen der Handle-Seite: Status Code":
            "Fehler beim Abrufen der Handle-Seite: Status Code",
        "Fehler beim Abrufen der Handle-Seite:":
            "Fehler beim Abrufen der Handle-Seite:",
        "Fehler beim Abrufen des Feeds: Status Code":
            "Fehler beim Abrufen des Feeds: Status Code",
        "Videos vom Kanal hinzugefügt.": "Videos vom Kanal hinzugefügt.",
        "Parameter Aktualisieren": "Parameter Aktualisieren",
        "Funktion": "Funktion",
        "Funkt.:" : "Funkt.:",
        "Wartezeit URL Aufruf:": "Wartezeit URL Aufruf:",
        "Wartezeit": "Wartezeit",
        "Durchlauf Wiederholungen:": "Durchlauf Wiederholungen:",
        "Wiederholungen:": "Wiederholungen:",
        "URL hinzugefügt:": "URL hinzugefügt:",
        "URL gelöscht:": "URL gelöscht:",
        "Alle URLs wurden gelöscht.": "Alle URLs wurden gelöscht.",
        "Keine URL zum Löschen ausgewählt.": "Keine URL zum Löschen ausgewählt.",
        "Einzelne URL auswählen": "Einzelne URL auswählen",
        "Wähle eine URL:": "Wähle eine URL:",
        "Video abdunkeln": "Video abdunkeln",
        "Abdunklungsgrad:": "Abdunklungsgrad:"
    },
    'en': {
        "Ab wann soll das helle Motiv verwendet werden? (Direkte Eingabe möglich)":
            "From when should the light theme be used? (Direct input possible)",
        "Tagmodus ab:": "Day mode from:",
        "Ab wann soll das dunkle Motiv verwendet werden? (Direkte Eingabe möglich)":
            "From when should the dark theme be used? (Direct input possible)",
        "Nachtmodus ab:": "Night mode from:",
        "Tag Theme:": "Day Theme:",
        "Nacht Theme:": "Night Theme:",
        "Tag Modus": "Day Mode",
        "Nacht Modus": "Night Mode",
        "URL Hinzufügen": "Add URL",
        "URL Löschen": "Delete URL",
        "Alle URLs Löschen": "Delete All URLs",
        "URLs": "URLs",
        "Funktionen": "Functions",
        "Einmalig": "Once",
        "Sequentiell": "Sequential",
        "Zufällig": "Random",
        "Parameter & URL Eingabe": "Parameters & URL Input",
        "Wartezeit URL Aufruf:": "Wait time for URL call:",
        "Random Zusatz MIN (ms):": "Random additional MIN (ms):",
        "Random Zusatz MAX (ms):": "Random additional MAX (ms):",
        "Durchlauf Wiederholungen:": "Repetitions:",
        "Neue URL eingeben...": "Enter new URL...",
        "Proxy Einstellungen": "Proxy Settings",
        "Proxy verwenden": "Use Proxy",
        "Typ:": "Type:",
        "z.B. proxy.example.com": "e.g. proxy.example.com",
        "z.B. 8080": "e.g. 8080",
        "Aufgerufene Website / Video": "Loaded Website / Video",
        "Protokoll / Live Status": "Log / Live Status",
        "Protokoll löschen": "Clear Log",
        "URL Auswahl": "URL Selection",
        "YouTube Kanal Videos abrufen": "Fetch YouTube Channel Videos",
        "YouTube Kanal-URL, Kanal-ID oder Handle eingeben...":
            "Enter YouTube Channel URL, Channel ID, or Handle...",
        "Wert eingeben": "Enter value",
        "Neuen Wert eingeben:": "Enter new value:",
        "Theme gewechselt: Tag Modus (": "Theme switched: Day Mode (",
        "Theme gewechselt: Nacht Modus (": "Theme switched: Night Mode (",
        "Kein YouTube-Kanal angegeben.": "No YouTube channel provided.",
        "Konnte den Titel nicht laden:": "Could not load title:",
        "Keine gültige URL eingegeben.": "No valid URL entered.",
        "Keine URLs in der Liste!": "No URLs in the list!",
        "Auswahl abgebrochen.": "Selection cancelled.",
        "Keine URLs ausgewählt!": "No URLs selected!",
        "Ungültige URL-Auswahl.": "Invalid URL selection.",
        "Starte Ablauf (zufällig), Wiederholungen:": "Starting sequence (random), repetitions:",
        "Starte Ablauf (sequentiell), Wiederholungen:": "Starting sequence (sequential), repetitions:",
        "Beginne Wiederholung": "Starting repetition",
        "von": "of",
        "Öffne URL:": "Opening URL:",
        "Warte": "Waiting",
        "Sekunden ...": "seconds ...",
        "Ablauf gestoppt.": "Sequence stopped.",
        "Ablauf beendet.": "Sequence completed.",
        "Stop-Befehl empfangen. Ablauf abgebrochen.":
            "Stop command received. Sequence aborted.",
        "Proxy aktiviert, aber Host oder Port fehlen. URL-Aufruf wird abgebrochen.":
            "Proxy enabled but host or port missing. URL call aborted.",
        "Lade URL über SOCKS4 Proxy:": "Loading URL via SOCKS4 proxy:",
        "Lade URL über SOCKS5 Proxy:": "Loading URL via SOCKS5 proxy:",
        "Lade URL über Proxy:": "Loading URL via proxy:",
        "Fehler: Status Code": "Error: Status Code",
        "Fehler beim Proxy-Aufruf:": "Error during proxy call:",
        "Kein Proxy aktiviert – daher wird die URL direkt geladen.":
            "No proxy enabled – loading URL directly.",
        "Fehler beim Abrufen des YouTube-Titels:": "Error fetching YouTube title:",
        "Konnte die Channel-ID aus der Handle-Seite nicht extrahieren.":
            "Could not extract channel ID from handle page.",
        "Fehler beim Abrufen der Handle-Seite: Status Code":
            "Error fetching handle page: Status Code",
        "Fehler beim Abrufen der Handle-Seite:":
            "Error fetching handle page:",
        "Fehler beim Abrufen des Feeds: Status Code":
            "Error fetching feed: Status Code",
        "Videos vom Kanal hinzugefügt.": "Channel videos added.",
        "Parameter Aktualisieren": "Update Parameters",
        "Funktion": "Function",
        "Funkt.:" : "Funct.:",
        "Wartezeit URL Aufruf:": "Wait time for URL call:",
        "Wartezeit": "Wait time",
        "Durchlauf Wiederholungen:": "Repetitions:",
        "Wiederholungen:": "Repetitions:",
        "URL hinzugefügt:": "URL added:",
        "URL gelöscht:": "URL deleted:",
        "Alle URLs wurden gelöscht.": "All URLs deleted.",
        "Keine URL zum Löschen ausgewählt.": "No URL selected for deletion.",
        "Einzelne URL auswählen": "Select single URL",
        "Wähle eine URL:": "Choose a URL:",
        "Video abdunkeln": "Darken Video",
        "Abdunklungsgrad:": "Darkness Level:"
    }
}

def _tr(text):
    return translations.get(CURRENT_LANG, {}).get(text, text)

def set_language_automatically():
    global CURRENT_LANG
    sys_lang = locale.getdefaultlocale()[0]
    if sys_lang:
        if sys_lang.startswith("en"):
            CURRENT_LANG = "en"
        elif sys_lang.startswith("fr"):
            CURRENT_LANG = "fr"
        elif sys_lang.startswith("es"):
            CURRENT_LANG = "es"
        elif sys_lang.startswith("pl"):
            CURRENT_LANG = "pl"
        else:
            CURRENT_LANG = "de"
    else:
        CURRENT_LANG = "de"

# --- Themes
DAY_THEMES = {
    "Weiß (Standard)": """
        QMainWindow { background-color: #ffffff; }
        QGroupBox { background-color: #f9f9f9; color: #333333; border: 1px solid #cccccc; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #ffd700; color: black; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Grün": """
        QMainWindow { background-color: #f0f0f0; }
        QGroupBox { background-color: #e0e0e0; color: #222222; border: 1px solid #aaaaaa; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #000000; border: 1px solid #aaaaaa; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Blau": """
        QMainWindow { background-color: #e6f7ff; }
        QGroupBox { background-color: #cceeff; color: #003366; border: 1px solid #99ccff; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #003366; border: 1px solid #99ccff; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #3399ff; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Gelb": """
        QMainWindow { background-color: #fffacd; }
        QGroupBox { background-color: #fff8dc; color: #665500; border: 1px solid #ffeb99; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #665500; border: 1px solid #ffeb99; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #ffcc00; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Beige": """
        QMainWindow { background-color: #f5f5dc; }
        QGroupBox { background-color: #fafad2; color: #333300; border: 1px solid #e6e6b3; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #333300; border: 1px solid #e6e6b3; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #b3b300; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Lavendel": """
        QMainWindow { background-color: #e6e6fa; }
        QGroupBox { background-color: #d8bfd8; color: #4b0082; border: 1px solid #c8a2c8; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #4b0082; border: 1px solid #c8a2c8; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #9370db; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Hellgrün": """
        QMainWindow { background-color: #f0fff0; }
        QGroupBox { background-color: #e0ffe0; color: #006400; border: 1px solid #b3ffb3; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #006400; border: 1px solid #b3ffb3; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #32cd32; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Gold": """
        QMainWindow { background-color: #fafad2; }
        QGroupBox { background-color: #fffacd; color: #666600; border: 1px solid #ffff99; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #666600; border: 1px solid #ffff99; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #ffd700; color: black; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Mandel": """
        QMainWindow { background-color: #ffebcd; }
        QGroupBox { background-color: #ffe4c4; color: #663300; border: 1px solid #ffd2a6; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #663300; border: 1px solid #ffd2a6; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #cd853f; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Old Lace": """
        QMainWindow { background-color: #fdf5e6; }
        QGroupBox { background-color: #fffaf0; color: #666633; border: 1px solid #f0e68c; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #666633; border: 1px solid #f0e68c; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #daa520; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Alice Blue": """
        QMainWindow { background-color: #f0f8ff; }
        QGroupBox { background-color: #e6f2ff; color: #003366; border: 1px solid #99ccff; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #003366; border: 1px solid #99ccff; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #6699ff; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """,
    "Misty Rose": """
        QMainWindow { background-color: #ffe4e1; }
        QGroupBox { background-color: #ffdcd1; color: #993333; border: 1px solid #ffb3a7; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #ffffff; color: #993333; border: 1px solid #ffb3a7; border-radius: 3px; padding: 2px; }
        QPushButton { background-color: #ff6666; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QWebEngineView { background-color: #ffffff; }
    """
}

NIGHT_THEMES = {
    "Dunkelgrau (Standard)": """
        QMainWindow { background-color: #2c2c2c; }
        QGroupBox { background-color: #3c3c3c; color: #eeeeee; border: 1px solid #555555; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #2c2c2c; color: #ffffff; border: 1px solid #555555; border-radius: 3px; padding: 2px; }
        QLabel { color: #ffffff; }
        QPushButton { background-color: #161616; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Anthrazit": """
        QMainWindow { background-color: #1a1a1a; }
        QGroupBox { background-color: #2a2a2a; color: #cccccc; border: 1px solid #444444; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #1a1a1a; color: #ffffff; border: 1px solid #444444; border-radius: 3px; padding: 2px; }
        QLabel { color: #ffffff; }
        QPushButton { background-color: #005500; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Blau (Dunkel)": """
        QMainWindow { background-color: #000033; }
        QGroupBox { background-color: #000066; color: #cce6ff; border: 1px solid #000099; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #000033; color: #cce6ff; border: 1px solid #000099; border-radius: 3px; padding: 2px; }
        QLabel { color: #cce6ff; }
        QPushButton { background-color: #0000cc; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Schwarz (Tief)": """
        QMainWindow { background-color: #141414; }
        QGroupBox { background-color: #1e1a1a; color: #d3d3d3; border: 1px solid #333333; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #141414; color: #d3d3d3; border: 1px solid #333333; border-radius: 3px; padding: 2px; }
        QLabel { color: #d3d3d3; }
        QPushButton { background-color: #4f4f4f; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Dunkelgrau": """
        QMainWindow { background-color: #202020; }
        QGroupBox { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444444; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #202020; color: #e0e0e0; border: 1px solid #444444; border-radius: 3px; padding: 2px; }
        QLabel { color: #e0e0e0; }
        QPushButton { background-color: #555555; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Grau": """
        QMainWindow { background-color: #2d2d2d; }
        QGroupBox { background-color: #383838; color: #cccccc; border: 1px solid #555555; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #2d2d2d; color: #cccccc; border: 1px solid #555555; border-radius: 3px; padding: 2px; }
        QLabel { color: #cccccc; }
        QPushButton { background-color: #666666; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Mittelgrau": """
        QMainWindow { background-color: #363636; }
        QGroupBox { background-color: #424242; color: #bfbfbf; border: 1px solid #666666; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #363636; color: #bfbfbf; border: 1px solid #666666; border-radius: 3px; padding: 2px; }
        QLabel { color: #bfbfbf; }
        QPushButton { background-color: #737373; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Grau (Dunkel 2)": """
        QMainWindow { background-color: #585858; }
        QGroupBox { background-color: #636363; color: #7a7a7a; border: 1px solid #888888; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #585858; color: #7a7a7a; border: 1px solid #888888; border-radius: 3px; padding: 2px; }
        QLabel { color: #7a7a7a; }
        QPushButton { background-color: #707070; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """,
    "Hellgrau": """
        QMainWindow { background-color: #606060; }
        QGroupBox { background-color: #6a6a6a; color: #737373; border: 1px solid #888888; border-radius: 5px; margin-top: 10px; }
        QLineEdit, QTextEdit, QListWidget { background-color: #606060; color: #737373; border: 1px solid #888888; border-radius: 3px; padding: 2px; }
        QLabel { color: #737373; }
        QPushButton { background-color: #787878; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px; }
        QScrollBar { background-color: #333333; }
        QWebEngineView { background-color: #000000; }
    """
}

# Subclass für QLineEdit mit Maus-Direkteingabe
class MouseInputLineEdit(QLineEdit):
    def mouseDoubleClickEvent(self, event):
        current = self.text()
        text, ok = QInputDialog.getText(self, _tr("Wert eingeben"), _tr("Neuen Wert eingeben:"), text=current)
        if ok:
            self.setText(text)
        else:
            super().mouseDoubleClickEvent(event)

# -------------------------------------------------------------------
# Minimale SOCKS4-Unterstützung (HTTP und HTTPS)
def socks4_get(url, proxy_host, proxy_port, timeout=10):
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError("SOCKS4-Unterstützung: Nur http:// und https:// URLs werden unterstützt.")
    dest_host = parsed.hostname
    dest_port = parsed.port or (443 if scheme == "https" else 80)
    s = socket.create_connection((proxy_host, int(proxy_port)), timeout=timeout)
    s.settimeout(timeout)
    try:
        try:
            ip = socket.inet_aton(socket.gethostbyname(dest_host))
            use_socks4a = False
        except Exception:
            ip = b'\x00\x00\x00\x01'
            use_socks4a = True
        req = bytearray()
        req.append(0x04)
        req.append(0x01)
        req += dest_port.to_bytes(2, byteorder="big")
        req += ip
        req += b'\x00'
        if use_socks4a:
            req += dest_host.encode() + b'\x00'
        s.sendall(req)
        reply = s.recv(8)
        if len(reply) < 8 or reply[1] != 0x5A:
            s.close()
            raise Exception("SOCKS4-Proxyverbindung fehlgeschlagen.")
        if scheme == "https":
            context = ssl.create_default_context()
            s = context.wrap_socket(s, server_hostname=dest_host)
        path = parsed.path if parsed.path else "/"
        if parsed.query:
            path += "?" + parsed.query
        request_line = f"GET {path} HTTP/1.0\r\nHost: {dest_host}\r\n\r\n"
        s.sendall(request_line.encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        return response
    except Exception as e:
        s.close()
        raise e

# -------------------------------------------------------------------
# Minimale SOCKS5-Unterstützung (HTTP und HTTPS)
def socks5_get(url, proxy_host, proxy_port, timeout=10):
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError("SOCKS5-Unterstützung: Nur http:// und https:// URLs werden unterstützt.")
    dest_host = parsed.hostname
    dest_port = parsed.port or (443 if scheme == "https" else 80)
    s = socket.create_connection((proxy_host, int(proxy_port)), timeout=timeout)
    s.settimeout(timeout)
    try:
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if len(resp) != 2 or resp[0] != 0x05 or resp[1] != 0x00:
            s.close()
            raise Exception("SOCKS5-Proxy-Handshake fehlgeschlagen.")
        dest_host_bytes = dest_host.encode()
        req = bytearray()
        req.append(0x05)
        req.append(0x01)
        req.append(0x00)
        req.append(0x03)
        req.append(len(dest_host_bytes))
        req += dest_host_bytes
        req += dest_port.to_bytes(2, byteorder="big")
        s.sendall(req)
        resp = s.recv(4)
        if len(resp) < 4 or resp[1] != 0x00:
            s.close()
            raise Exception("SOCKS5-Verbindungsanfrage fehlgeschlagen.")
        atyp = resp[3]
        if atyp == 0x01:
            s.recv(6)
        elif atyp == 0x03:
            domain_len = s.recv(1)[0]
            s.recv(domain_len + 2)
        elif atyp == 0x04:
            s.recv(18)
        else:
            s.close()
            raise Exception("Unbekannter ATYP in SOCKS5-Antwort.")
        if scheme == "https":
            context = ssl.create_default_context()
            s = context.wrap_socket(s, server_hostname=dest_host)
        path = parsed.path if parsed.path else "/"
        if parsed.query:
            path += "?" + parsed.query
        request_line = f"GET {path} HTTP/1.0\r\nHost: {dest_host}\r\n\r\n"
        s.sendall(request_line.encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        return response
    except Exception as e:
        s.close()
        raise e

# -------------------------------------------------------------------
# Hauptklasse
# -------------------------------------------------------------------
# Änderungen:
# 1. Zuerst wird die Benutzeroberfläche initialisiert (_setup_ui), bevor auf Widgets zugegriffen wird.
# 2. Anschließend wird geprüft, ob die Config-Datei existiert – falls nicht, wird sie mit Standardwerten erstellt.
# 3. Falls ein Fehler beim Laden der Config auftritt, wird ein Fallback implementiert.
# 4. Die Video-Abdunklungs-Funktion wird so umprogrammiert, dass im Nachtmodus, wenn die Checkbox angehakt ist,
#    der Filter über ein GUI-Overlay angewendet wird.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Programmtitel und Config-Namen anpassen
        self.setWindowTitle("Yc.U - YouClick Ultimate")
        self.resize(2000, 850)
        self._is_running = False
        self._current_timer = None
        self.page_calls_count = 0
        self.video_filter_enabled = False
        self.video_filter_level = 50  # 0-100, Default 50

        # First build the UI components
        self._setup_ui()  # This creates url_list_widget and other widgets

        # Now initialize settings AFTER UI components exist
        config_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation), "YouClick Ultimate")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_file = os.path.join(config_dir, "Yc.U.conf")
        self.settings = QSettings(self.config_file, QSettings.IniFormat)

        # Only create default config if it doesn't exist
        if not os.path.exists(self.config_file):
            self.save_settings()  # Now safe because UI components exist

        # Rest of initialization
        self.log_messages = []
        self.last_wait_time = None
        self.wait_start = None
        self.wait_duration_ms = 0
        self.current_theme = "day"

        self.load_settings()
        self.apply_theme_automatically()
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.apply_theme_automatically)
        self.theme_timer.start(300000)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(1000)
        self.progress_timer = None
        self.web_view.loadFinished.connect(self.handle_video_load)

    def handle_video_load(self, finished):
        # Statt CSS/JS wird nun das Overlay aktualisiert
        self.update_video_filter()

    def update_video_filter(self):
        # Aktualisiert den Overlay-Filter basierend auf Checkbox und Slider
        if self.current_theme == "night" and self.filter_checkbox.isChecked():
            opacity = self.filter_slider.value() / 100.0
            effect = QGraphicsOpacityEffect(self.video_overlay)
            effect.setOpacity(opacity)
            self.video_overlay.setGraphicsEffect(effect)
            # Overlay an die aktuelle Größe der WebView anpassen
            self.video_overlay.setGeometry(0, 0, self.web_view.width(), self.web_view.height())
            self.video_overlay.show()
            self.video_overlay.raise_()
        else:
            self.video_overlay.hide()
        self.video_filter_enabled = self.filter_checkbox.isChecked()
        self.video_filter_level = self.filter_slider.value()

    def save_settings(self):
        urls = []
        for i in range(self.url_list_widget.count()):
            item = self.url_list_widget.item(i)
            real_url = item.data(Qt.UserRole) or item.text()
            display_text = item.text()
            urls.append((real_url, display_text))
        self.settings.setValue("urls", urls)
        self.settings.setValue("wait_time", self.wait_time_spinbox.value())
        self.settings.setValue("min_wait", self.min_wait_spinbox.value())
        self.settings.setValue("max_wait", self.max_wait_spinbox.value())
        self.settings.setValue("repeat", self.repeat_spinbox.value())
        self.settings.setValue("log_messages", self.log_messages)
        if self.radio_url_single.isChecked():
            self.settings.setValue("url_scope", "Einzelne URL")
        elif self.radio_url_multiple.isChecked():
            self.settings.setValue("url_scope", "Mehrere URLs")
        elif self.radio_url_all.isChecked():
            self.settings.setValue("url_scope", "Alle URLs")
        if self.radio_func_once.isChecked():
            self.settings.setValue("func_type", "Einmalig")
        elif self.radio_func_sequential.isChecked():
            self.settings.setValue("func_type", "Sequentiell")
        elif self.radio_func_random.isChecked():
            self.settings.setValue("func_type", "Zufällig")
        self.settings.setValue("proxy_enabled", self.proxy_checkbox.isChecked())
        self.settings.setValue("proxy_type", self.proxy_type_combo.currentText())
        self.settings.setValue("proxy_host", self.proxy_host_edit.text())
        self.settings.setValue("proxy_port", self.proxy_port_edit.text())
        self.settings.setValue("day_time", self.day_time_edit.time().toString("HH:mm"))
        self.settings.setValue("night_time", self.night_time_edit.time().toString("HH:mm"))
        self.settings.setValue("day_theme", self.day_theme_combo.currentText())
        self.settings.setValue("night_theme", self.night_theme_combo.currentText())
        self.settings.setValue("video_filter_enabled", self.filter_checkbox.isChecked())
        self.settings.setValue("video_filter_level", self.filter_slider.value())

    def load_settings(self):
        urls = self.settings.value("urls", [])
        if urls is None:
            urls = []
        if urls and isinstance(urls[0], str):
            urls = [(url, url) for url in urls]
        for real_url, display_text in urls:
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, real_url)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.url_list_widget.addItem(item)
        self.wait_time_spinbox.setValue(float(self.settings.value("wait_time", 1)))
        self.min_wait_spinbox.setValue(int(self.settings.value("min_wait", 100)))
        self.max_wait_spinbox.setValue(int(self.settings.value("max_wait", 500)))
        self.repeat_spinbox.setValue(int(self.settings.value("repeat", 1)))
        self.log_messages = self.settings.value("log_messages", [])
        if isinstance(self.log_messages, str):
            self.log_messages = self.log_messages.splitlines()
        self.status_edit.setPlainText("\n".join(self.log_messages))
        url_scope = self.settings.value("url_scope", "Einzelne URL")
        if url_scope == "Einzelne URL":
            self.radio_url_single.setChecked(True)
        elif url_scope == "Mehrere URLs":
            self.radio_url_multiple.setChecked(True)
        elif url_scope == "Alle URLs":
            self.radio_url_all.setChecked(True)
        func_type = self.settings.value("func_type", "Einmalig")
        if func_type == "Einmalig":
            self.radio_func_once.setChecked(True)
        elif func_type == "Sequentiell":
            self.radio_func_sequential.setChecked(True)
        elif func_type == "Zufällig":
            self.radio_func_random.setChecked(True)
        self.proxy_checkbox.setChecked(self.settings.value("proxy_enabled", False, type=bool))
        proxy_type = self.settings.value("proxy_type", "HTTP")
        index = self.proxy_type_combo.findText(proxy_type)
        if index >= 0:
            self.proxy_type_combo.setCurrentIndex(index)
        self.proxy_host_edit.setText(self.settings.value("proxy_host", ""))
        self.proxy_port_edit.setText(self.settings.value("proxy_port", ""))
        day_time_str = self.settings.value("day_time", "06:00")
        night_time_str = self.settings.value("night_time", "18:00")
        self.day_time_edit.setTime(QTime.fromString(day_time_str, "HH:mm"))
        self.night_time_edit.setTime(QTime.fromString(night_time_str, "HH:mm"))
        day_theme = self.settings.value("day_theme", "Weiß (Standard)")
        night_theme = self.settings.value("night_theme", "Dunkelgrau (Standard)")
        index = self.day_theme_combo.findText(day_theme)
        if index >= 0:
            self.day_theme_combo.setCurrentIndex(index)
        index = self.night_theme_combo.findText(night_theme)
        if index >= 0:
            self.night_theme_combo.setCurrentIndex(index)
        self.filter_checkbox.setChecked(self.settings.value("video_filter_enabled", False, type=bool))
        self.filter_slider.setValue(int(self.settings.value("video_filter_level", 50)))
        self.update_video_filter()
        self.update_status_bar()

    def _setup_ui(self):
        central = QWidget()
        main_v_layout = QVBoxLayout()
        central.setLayout(main_v_layout)
        self.setCentralWidget(central)

        # --- Konfigurationsleiste: Theme-Zeit Einstellungen (immer aktiv)
        theme_time_layout = QHBoxLayout()
        self.day_time_edit = QTimeEdit()
        self.day_time_edit.setDisplayFormat("HH:mm")
        self.day_time_edit.setToolTip(_tr("Ab wann soll das helle Motiv verwendet werden? (Direkte Eingabe möglich)"))
        theme_time_layout.addWidget(QLabel(_tr("Tagmodus ab:")))
        theme_time_layout.addWidget(self.day_time_edit)
        self.night_time_edit = QTimeEdit()
        self.night_time_edit.setDisplayFormat("HH:mm")
        self.night_time_edit.setToolTip(_tr("Ab wann soll das dunkle Motiv verwendet werden? (Direkte Eingabe möglich)"))
        theme_time_layout.addWidget(QLabel(_tr("Nachtmodus ab:")))
        theme_time_layout.addWidget(self.night_time_edit)
        main_v_layout.addLayout(theme_time_layout)

        # --- Theme-Auswahl (immer aktiv)
        theme_select_layout = QHBoxLayout()
        theme_select_layout.addWidget(QLabel(_tr("Tag Theme:")))
        self.day_theme_combo = QComboBox()
        self.day_theme_combo.addItems(list(DAY_THEMES.keys()))
        self.day_theme_combo.currentIndexChanged.connect(lambda: self.toggle_theme("day"))
        theme_select_layout.addWidget(self.day_theme_combo)
        theme_select_layout.addWidget(QLabel(_tr("Nacht Theme:")))
        self.night_theme_combo = QComboBox()
        self.night_theme_combo.addItems(list(NIGHT_THEMES.keys()))
        self.night_theme_combo.currentIndexChanged.connect(lambda: self.toggle_theme("night"))
        theme_select_layout.addWidget(self.night_theme_combo)
        main_v_layout.addLayout(theme_select_layout)

        # --- Mode Buttons: Tag und Nacht
        mode_button_layout = QHBoxLayout()
        self.btn_day_mode = QPushButton(_tr("Tag Modus"))
        self.btn_day_mode.setStyleSheet(DAY_BUTTON_STYLE_DEFAULT)
        self.btn_day_mode.clicked.connect(lambda: self.toggle_theme("day"))
        mode_button_layout.addWidget(self.btn_day_mode)
        self.btn_night_mode = QPushButton(_tr("Nacht Modus"))
        self.btn_night_mode.setStyleSheet(DAY_BUTTON_STYLE_DEFAULT)
        self.btn_night_mode.clicked.connect(lambda: self.toggle_theme("night"))
        mode_button_layout.addWidget(self.btn_night_mode)
        main_v_layout.addLayout(mode_button_layout)

        # --- Linke Spalte: URLs, Funktionen und Parameter
        left_column = QVBoxLayout()
        # Gruppe "URLs"
        self.group_urls = QGroupBox(_tr("URLs"))
        urls_layout = QHBoxLayout()
        self.group_urls.setLayout(urls_layout)
        self.radio_url_single = QRadioButton(_tr("Einzelne URL"))
        self.radio_url_multiple = QRadioButton(_tr("Mehrere URLs"))
        self.radio_url_all = QRadioButton(_tr("Alle URLs"))
        for rb in (self.radio_url_single, self.radio_url_multiple, self.radio_url_all):
            rb.setStyleSheet(BLUE_RADIO)
            urls_layout.addWidget(rb)
        self.url_scope_group = QButtonGroup()
        self.url_scope_group.addButton(self.radio_url_single)
        self.url_scope_group.addButton(self.radio_url_multiple)
        self.url_scope_group.addButton(self.radio_url_all)
        self.radio_url_single.setChecked(True)
        left_column.addWidget(self.group_urls)

        # Gruppe "Funktionen"
        self.group_functions = QGroupBox(_tr("Funktionen"))
        functions_layout = QHBoxLayout()
        self.group_functions.setLayout(functions_layout)
        self.radio_func_once = QRadioButton(_tr("Einmalig"))
        self.radio_func_sequential = QRadioButton(_tr("Sequentiell"))
        self.radio_func_random = QRadioButton(_tr("Zufällig"))
        for rb in (self.radio_func_once, self.radio_func_sequential, self.radio_func_random):
            rb.setStyleSheet(BLUE_RADIO)
            functions_layout.addWidget(rb)
        self.func_group = QButtonGroup()
        self.func_group.addButton(self.radio_func_once)
        self.func_group.addButton(self.radio_func_sequential)
        self.func_group.addButton(self.radio_func_random)
        self.radio_func_once.setChecked(True)
        left_column.addWidget(self.group_functions)

        # Gruppe "Parameter & URL Eingabe"
        self.group_parameter = QGroupBox(_tr("Parameter & URL Eingabe"))
        param_layout = QVBoxLayout()
        self.group_parameter.setLayout(param_layout)
        # Zeile 1: Wartezeit URL Aufruf
        row1 = QHBoxLayout()
        row1.addWidget(QLabel(_tr("Wartezeit")))
        self.wait_time_spinbox = QDoubleSpinBox()
        self.wait_time_spinbox.setDecimals(2)
        self.wait_time_spinbox.setMinimum(0.1)
        self.wait_time_spinbox.setValue(1.0)
        self.wait_time_spinbox.setSingleStep(0.1)
        row1.addWidget(self.wait_time_spinbox)
        param_layout.addLayout(row1)
        # Zeile 2: Random Zusatz MIN (ms)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(_tr("Random Zusatz MIN (ms):")))
        self.min_wait_spinbox = QSpinBox()
        self.min_wait_spinbox.setMinimum(0)
        self.min_wait_spinbox.setMaximum(10000)
        self.min_wait_spinbox.setValue(100)
        row2.addWidget(self.min_wait_spinbox)
        param_layout.addLayout(row2)
        # Zeile 3: Random Zusatz MAX (ms)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel(_tr("Random Zusatz MAX (ms):")))
        self.max_wait_spinbox = QSpinBox()
        self.max_wait_spinbox.setMinimum(0)
        self.max_wait_spinbox.setMaximum(10000)
        self.max_wait_spinbox.setValue(500)
        row3.addWidget(self.max_wait_spinbox)
        param_layout.addLayout(row3)
        # Zeile 4: Durchlauf Wiederholungen -> "Wiederholungen:"
        row4 = QHBoxLayout()
        row4.addWidget(QLabel(_tr("Wiederholungen:")))
        self.repeat_spinbox = QSpinBox()
        self.repeat_spinbox.setMinimum(1)
        self.repeat_spinbox.setMaximum(1000)
        self.repeat_spinbox.setValue(1)
        row4.addWidget(self.repeat_spinbox)
        param_layout.addLayout(row4)
        # URL Eingabe
        self.new_url_edit = QLineEdit()
        self.new_url_edit.setPlaceholderText(_tr("Neue URL eingeben..."))
        self.new_url_edit.installEventFilter(self)
        param_layout.addWidget(self.new_url_edit)
        # Buttons für URL-Eingabe
        url_button_layout = QHBoxLayout()
        self.btn_add_url = QPushButton(_tr("URL Hinzufügen"))
        self.btn_add_url.setStyleSheet(DAY_BUTTON_STYLE_GREEN)
        self.btn_add_url.clicked.connect(self.add_url_to_list)
        url_button_layout.addWidget(self.btn_add_url)
        self.btn_delete_url = QPushButton(_tr("URL Löschen"))
        self.btn_delete_url.setStyleSheet(DAY_BUTTON_STYLE_RED)
        self.btn_delete_url.clicked.connect(self.delete_selected_urls)
        url_button_layout.addWidget(self.btn_delete_url)
        self.btn_delete_all = QPushButton(_tr("Alle URLs Löschen"))
        self.btn_delete_all.setStyleSheet(DAY_BUTTON_STYLE_RED)
        self.btn_delete_all.clicked.connect(self.delete_all_urls)
        url_button_layout.addWidget(self.btn_delete_all)
        param_layout.addLayout(url_button_layout)
        left_column.addWidget(self.group_parameter)

        # --- Proxy Einstellungen (Eingabefelder, die beim Laufen deaktiviert werden sollen)
        self.group_proxy = QGroupBox(_tr("Proxy Einstellungen"))
        proxy_layout = QHBoxLayout()
        self.group_proxy.setLayout(proxy_layout)
        self.proxy_checkbox = QCheckBox(_tr("Proxy verwenden"))
        proxy_layout.addWidget(self.proxy_checkbox)
        proxy_layout.addWidget(QLabel(_tr("Typ:")))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        proxy_layout.addWidget(self.proxy_type_combo)
        proxy_layout.addWidget(QLabel(_tr("Host:")))
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("z.B. proxy.example.com")
        proxy_layout.addWidget(self.proxy_host_edit)
        proxy_layout.addWidget(QLabel(_tr("Port:")))
        self.proxy_port_edit = QLineEdit()
        self.proxy_port_edit.setPlaceholderText("z.B. 8080")
        proxy_layout.addWidget(self.proxy_port_edit)
        left_column.addWidget(self.group_proxy)

        # --- Horizontale Aufteilung: Linke Spalte und Videoanzeige
        content_layout = QHBoxLayout()
        content_layout.addLayout(left_column, stretch=1)
        self.group_website = QGroupBox(_tr("Aufgerufene Website / Video"))
        website_layout = QVBoxLayout()
        self.group_website.setLayout(website_layout)
        self.web_view = QWebEngineView()
        website_layout.addWidget(self.web_view)
        # --- Video Filter für Nachtmodus: Abdunkeln des Video-Bereichs
        # Das Video wird nun nicht über CSS/JS, sondern über ein GUI-Overlay abgedunkelt.
        self.video_overlay = QWidget(self.web_view)
        self.video_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.video_overlay.setStyleSheet("background-color: black;")
        self.video_overlay.hide()
        filter_layout = QHBoxLayout()
        self.filter_checkbox = QCheckBox(_tr("Video abdunkeln"))
        self.filter_slider = QSlider(Qt.Horizontal)
        self.filter_slider.setRange(0, 100)
        self.filter_slider.setValue(self.video_filter_level)
        filter_layout.addWidget(self.filter_checkbox)
        filter_layout.addWidget(QLabel(_tr("Abdunklungsgrad:")))
        filter_layout.addWidget(self.filter_slider)
        website_layout.addLayout(filter_layout)
        self.filter_checkbox.toggled.connect(self.update_video_filter)
        self.filter_slider.valueChanged.connect(self.update_video_filter)
        # --- Livestatus Leiste und Fortschrittsbalken
        self.status_params = QLabel("")
        self.status_params.setStyleSheet("background-color: #d3d3d3; border: 1px solid #cccccc; padding: 3px; font-weight: bold; color: black;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimum(0)
        status_progress_layout = QHBoxLayout()
        status_progress_layout.addWidget(self.status_params)
        status_progress_layout.addWidget(self.progress_bar)
        website_layout.addLayout(status_progress_layout)
        content_layout.addWidget(self.group_website, stretch=1)
        main_v_layout.addLayout(content_layout)

        # --- YouTube Kanal Videos abrufen und Eingabefeld
        self.btn_channel_videos = QPushButton(_tr("YouTube Kanal Videos abrufen"))
        self.btn_channel_videos.setStyleSheet(DAY_BUTTON_STYLE_DEFAULT)
        self.btn_channel_videos.clicked.connect(self.fetch_channel_videos)
        main_v_layout.addWidget(self.btn_channel_videos)
        self.youtube_channel_edit = QLineEdit()
        self.youtube_channel_edit.setPlaceholderText(_tr("YouTube Kanal-URL, Kanal-ID oder Handle eingeben..."))
        main_v_layout.addWidget(self.youtube_channel_edit)

        # --- Gruppe URL Auswahl
        self.group_url_list = QGroupBox(_tr("URL Auswahl"))
        url_list_layout = QVBoxLayout()
        self.group_url_list.setLayout(url_list_layout)
        self.url_list_widget = QListWidget()
        self.url_list_widget.setEnabled(True)
        url_list_layout.addWidget(self.url_list_widget)
        main_v_layout.addWidget(self.group_url_list)

        # --- Start / STOP Buttons (ohne Parameter Aktualisieren)
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet(DAY_BUTTON_STYLE_GREEN)
        self.btn_start.clicked.connect(self.start_running)
        btn_layout.addWidget(self.btn_start)
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setStyleSheet(DAY_BUTTON_STYLE_RED)
        self.btn_stop.clicked.connect(self.stop_running)
        btn_layout.addWidget(self.btn_stop)
        main_v_layout.addLayout(btn_layout)

        # --- Protokoll / Live Status und Config Buttons
        self.group_status = QGroupBox(_tr("Protokoll / Live Status"))
        status_layout = QVBoxLayout()
        self.group_status.setLayout(status_layout)
        self.status_edit = QTextEdit()
        self.status_edit.setReadOnly(True)
        status_layout.addWidget(self.status_edit)
        config_buttons_layout = QHBoxLayout()
        self.btn_clear_log = QPushButton(_tr("Protokoll löschen"))
        self.btn_clear_log.setStyleSheet(DAY_BUTTON_STYLE_RED)
        self.btn_clear_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_config_folder = QPushButton("Config Ordner")
        self.btn_config_folder.clicked.connect(self.open_config_folder)
        self.btn_config_folder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_config_import = QPushButton("Config importieren")
        self.btn_config_import.clicked.connect(self.import_config)
        self.btn_config_import.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_config_export = QPushButton("Config exportieren")
        self.btn_config_export.clicked.connect(self.export_config)
        self.btn_config_export.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Gleicher Anteil für alle vier Buttons
        config_buttons_layout.addWidget(self.btn_clear_log, 1)
        config_buttons_layout.addWidget(self.btn_config_folder, 1)
        config_buttons_layout.addWidget(self.btn_config_import, 1)
        config_buttons_layout.addWidget(self.btn_config_export, 1)
        status_layout.addLayout(config_buttons_layout)
        main_v_layout.addWidget(self.group_status)

        self.update_status_bar()
        self.setStyleSheet(GLOBAL_STYLE)

    def eventFilter(self, obj, event):
        if obj == self.new_url_edit and event.type() == QEvent.Type(77):
            QTimer.singleShot(0, self.add_url_to_list)
            return False
        return super().eventFilter(obj, event)

    def open_config_folder(self):
        config_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation), "YouClick Ultimate")
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(config_path))

    def import_config(self):
        src, _ = QFileDialog.getOpenFileName(self, "Config importieren", "", "CONF Files (*.conf)")
        if src:
            try:
                # Konfigurationsdatei ersetzen
                shutil.copy(src, self.config_file)
                
                # QSettings-Instanz neu initialisieren
                self.settings = QSettings(self.config_file, QSettings.IniFormat)
                
                # Einstellungen komplett neu laden
                self.load_settings()
                
                # UI-Komponenten aktualisieren
                self.update_status_bar()
                self.apply_theme_automatically()  # Theme neu anwenden
                self.log_status("Config importiert und aktiviert: " + src)
                
                # Web-View zurücksetzen
                self.web_view.setHtml("")
                
            except Exception as e:
                self.log_status("Fehler beim Importieren: " + str(e))

    def export_config(self):
        dest = QFileDialog.getExistingDirectory(self, "Config exportieren", "")
        if dest:
            full_dest = os.path.join(dest, "Yc.U.conf")
            try:
                self.settings.sync()
                shutil.copyfile(self.config_file, full_dest)
                self.log_status("Config exportiert: " + full_dest)
            except Exception as e:
                self.log_status("Fehler beim Exportieren: " + str(e))

    def clear_log(self):
        self.log_messages = []
        self.status_edit.clear()

    def apply_theme_automatically(self):
        current_time = QTime.currentTime()
        day_time = self.day_time_edit.time() if self.day_time_edit.time().isValid() else QTime(6, 0)
        night_time = self.night_time_edit.time() if self.night_time_edit.time().isValid() else QTime(18, 0)
        if day_time <= current_time < night_time:
            self.toggle_theme("day")
        else:
            self.toggle_theme("night")

    def update_status_bar(self):
        urls = self.get_checked_urls()
        url_count = len(urls)
        func = _tr("Einmalig") if self.radio_func_once.isChecked() else (_tr("Sequentiell") if self.radio_func_sequential.isChecked() else _tr("Zufällig"))
        _, _, _, repeat = self.get_parameters()
        if self._is_running and hasattr(self, '_repeat_count') and hasattr(self, '_current_repeat') and hasattr(self, '_urls'):
            repetition_status = f"{self._current_repeat + 1} / {self._repeat_count}"
            total_expected = len(self._urls) * self._repeat_count
            page_status = f"{self.page_calls_count} / {total_expected}"
            current_wait = f"{self.last_wait_time:.3f}" if self.last_wait_time is not None else "0.000"
        else:
            repetition_status = f"{repeat} / {repeat}"
            page_status = f"{self.page_calls_count}"
            current_wait = f"{self.get_parameters()[0]:.3f}"
        status_text = (f"URLs: {url_count} | {_tr('Funkt.:')} {func} | {_tr('Wartezeit')} {current_wait} s | "
                       f"{_tr('Wiederholungen:')} {repetition_status} | Seitenaufrufe: {page_status}")
        self.status_params.setText(status_text)

    def get_parameters(self):
        wait_time = self.wait_time_spinbox.value()
        min_wait = self.min_wait_spinbox.value()
        max_wait = self.max_wait_spinbox.value()
        repeat = self.repeat_spinbox.value()
        return wait_time, min_wait, max_wait, repeat

    def add_url_to_list(self):
        url = self.new_url_edit.text().strip()
        if not url:
            self.log_status(_tr("Keine gültige URL eingegeben."))
            return
        if "youtube.com/watch" in url or "youtu.be/" in url:
            title = self.get_youtube_title(url)
            if title:
                item = QListWidgetItem(title)
                item.setData(Qt.UserRole, url)
            else:
                item = QListWidgetItem(url)
                item.setData(Qt.UserRole, url)
                self.log_status(_tr("Konnte den Titel nicht laden:") + " " + url)
        else:
            item = QListWidgetItem(url)
            item.setData(Qt.UserRole, url)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        self.url_list_widget.addItem(item)
        self.new_url_edit.clear()
        self.log_status(_tr("URL hinzugefügt:") + " " + item.text())
        self.save_settings()
        self.update_status_bar()

    def delete_selected_urls(self):
        indices = []
        for i in range(self.url_list_widget.count()):
            item = self.url_list_widget.item(i)
            if item.isSelected():
                indices.append(i)
        for i in reversed(indices):
            removed = self.url_list_widget.takeItem(i)
            self.log_status(_tr("URL gelöscht:") + " " + removed.text())
        if not indices:
            self.log_status(_tr("Keine URL zum Löschen ausgewählt."))
        self.save_settings()
        self.update_status_bar()

    def delete_all_urls(self):
        self.url_list_widget.clear()
        self.log_status(_tr("Alle URLs wurden gelöscht."))
        self.save_settings()
        self.update_status_bar()

    def get_checked_urls(self):
        urls = []
        for i in range(self.url_list_widget.count()):
            item = self.url_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                urls.append(item.data(Qt.UserRole))
        return urls

    def log_status(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_messages.insert(0, f"{timestamp} - {message}")
        self.status_edit.setPlainText("\n".join(self.log_messages))
        self.status_edit.moveCursor(QTextCursor.Start)
        logging.info(message)

    # Sperre veränderbare Eingabefelder (außer Tagzeit und Theme) während des Betriebs.
    def set_controls_enabled(self, enabled):
        self.btn_start.setEnabled(enabled)
        self.btn_stop.setEnabled(not enabled)
        self.btn_add_url.setEnabled(enabled)
        self.btn_delete_url.setEnabled(enabled)
        self.btn_delete_all.setEnabled(enabled)
        self.new_url_edit.setEnabled(enabled)
        self.wait_time_spinbox.setEnabled(enabled)
        self.min_wait_spinbox.setEnabled(enabled)
        self.max_wait_spinbox.setEnabled(enabled)
        self.repeat_spinbox.setEnabled(enabled)
        for rb in self.url_scope_group.buttons():
            rb.setEnabled(enabled)
        for rb in self.func_group.buttons():
            rb.setEnabled(enabled)
        self.proxy_checkbox.setEnabled(enabled)
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_host_edit.setEnabled(enabled and not self._is_running)
        self.proxy_port_edit.setEnabled(enabled and not self._is_running)
        if self.current_theme == "night":
            dark_style = "background-color: #333333; color: white; border: 1px solid #555555;"
            self.day_time_edit.setStyleSheet(dark_style)
            self.night_time_edit.setStyleSheet(dark_style)
            self.day_theme_combo.setStyleSheet(dark_style)
            self.night_theme_combo.setStyleSheet(dark_style)
        else:
            self.day_time_edit.setStyleSheet("")
            self.night_time_edit.setStyleSheet("")
            self.day_theme_combo.setStyleSheet("")
            self.night_theme_combo.setStyleSheet("")

    def compute_total_wait_ms(self, wait_time, min_wait, max_wait):
        return int(wait_time * 1000) + random.randint(min_wait, max_wait)

    def toggle_theme(self, mode):
        self.current_theme = mode
        if mode == "day":
            theme_name = self.day_theme_combo.currentText()
            style = DAY_THEMES.get(theme_name, DAY_THEMES["Weiß (Standard)"])
            self.setStyleSheet(style)
            self.btn_day_mode.setStyleSheet(DAY_BUTTON_STYLE_DEFAULT)
            self.btn_night_mode.setStyleSheet("background-color: #333333; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
            self.btn_add_url.setStyleSheet(DAY_BUTTON_STYLE_GREEN)
            self.btn_delete_url.setStyleSheet(DAY_BUTTON_STYLE_RED)
            self.btn_delete_all.setStyleSheet(DAY_BUTTON_STYLE_RED)
            self.btn_channel_videos.setStyleSheet("background-color: #FF8C00; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
            self.btn_clear_log.setStyleSheet(DAY_BUTTON_STYLE_RED)
            self.btn_start.setStyleSheet(DAY_BUTTON_STYLE_GREEN)
            self.btn_stop.setStyleSheet(DAY_BUTTON_STYLE_RED)
            self.new_url_edit.setStyleSheet("color: blue;")
            self.day_time_edit.setStyleSheet("")
            self.night_time_edit.setStyleSheet("")
            self.day_theme_combo.setStyleSheet("")
            self.night_theme_combo.setStyleSheet("")
            self.proxy_checkbox.setStyleSheet("")
            self.proxy_type_combo.setStyleSheet("")
            self.proxy_host_edit.setStyleSheet("")
            self.proxy_port_edit.setStyleSheet("")
            for rb in self.url_scope_group.buttons():
                rb.setStyleSheet(BLUE_RADIO)
            for rb in self.func_group.buttons():
                rb.setStyleSheet(BLUE_RADIO)
            self.wait_time_spinbox.setStyleSheet("")
            self.min_wait_spinbox.setStyleSheet("")
            self.max_wait_spinbox.setStyleSheet("")
            self.repeat_spinbox.setStyleSheet("")
            self.status_params.setStyleSheet("background-color: #d3d3d3; border: 1px solid #cccccc; padding: 3px; font-weight: bold; color: black;")
            self.url_list_widget.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #cccccc;")
            self.status_edit.setStyleSheet("background-color: #f9f9f9; color: black; border: 1px solid #cccccc;")
            self.progress_bar.setStyleSheet("")
            self.log_status(_tr("Theme gewechselt: Tag Modus (") + theme_name + ")")
            self.filter_checkbox.setEnabled(True)
            self.filter_slider.setEnabled(True)
            self.web_view.setStyleSheet("")
            self.video_overlay.hide()

        elif mode == "night":
            theme_name = self.night_theme_combo.currentText()
            style = NIGHT_THEMES.get(theme_name, NIGHT_THEMES["Dunkelgrau (Standard)"])
            self.setStyleSheet(style)
            dark_style = "background-color: #333333; color: white; border: 1px solid #555555;"
            self.day_time_edit.setStyleSheet(dark_style)
            self.night_time_edit.setStyleSheet(dark_style)
            self.day_theme_combo.setStyleSheet(dark_style)
            self.night_theme_combo.setStyleSheet(dark_style)
            self.proxy_checkbox.setStyleSheet(dark_style)
            self.proxy_type_combo.setStyleSheet(dark_style)
            self.proxy_host_edit.setStyleSheet(dark_style)
            self.proxy_port_edit.setStyleSheet(dark_style)
            self.wait_time_spinbox.setStyleSheet(dark_style)
            self.min_wait_spinbox.setStyleSheet(dark_style)
            self.max_wait_spinbox.setStyleSheet(dark_style)
            self.repeat_spinbox.setStyleSheet(dark_style)
            self.new_url_edit.setStyleSheet("color: #add8e6; background-color: #333333; border: 1px solid #555555;")
            for rb in self.url_scope_group.buttons():
                rb.setStyleSheet(dark_style)
            for rb in self.func_group.buttons():
                rb.setStyleSheet(dark_style)
            self.btn_day_mode.setStyleSheet("background-color: #ccaa00; color: black; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
            self.btn_night_mode.setStyleSheet("background-color: #333333; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
            self.btn_add_url.setStyleSheet(NIGHT_BUTTON_STYLE_GREEN)
            self.btn_delete_url.setStyleSheet(NIGHT_BUTTON_STYLE_RED)
            self.btn_delete_all.setStyleSheet(NIGHT_BUTTON_STYLE_RED)
            self.btn_start.setStyleSheet(NIGHT_BUTTON_STYLE_GREEN)
            self.btn_stop.setStyleSheet(NIGHT_BUTTON_STYLE_RED)
            self.btn_channel_videos.setStyleSheet("background-color: #cc5500; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
            self.btn_clear_log.setStyleSheet(NIGHT_BUTTON_STYLE_RED)
            self.status_params.setStyleSheet("background-color: #444444; border: 1px solid #888888; padding: 3px; font-weight: bold; color: white;")
            self.url_list_widget.setStyleSheet("background-color: #2c2c2c; color: white; border: 1px solid #444444;")
            self.status_edit.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #555555;")
            self.progress_bar.setStyleSheet("QProgressBar {background-color: #444444; color: white; border: 1px solid #888888; text-align: center; } QProgressBar::chunk { background-color: #007700; }")
            self.log_status(_tr("Theme gewechselt: Nacht Modus (") + theme_name + ")")
            self.filter_checkbox.setStyleSheet("color: #add8e6;")
            self.filter_checkbox.setEnabled(True)
            self.filter_slider.setEnabled(True)
            self.web_view.setStyleSheet("QScrollBar:vertical { background: #333333; } QScrollBar:horizontal { background: #333333; }")
            
            # Filter sofort aktivieren bei Nachtmodus
            if self.filter_checkbox.isChecked():
                self.update_video_filter()
                self.video_overlay.show()
            else:
                self.video_overlay.hide()

            self.update_status_bar()

    def get_youtube_title(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                match = re.search(r'<title>(.*?) - YouTube</title>', response.text)
                if match:
                    return match.group(1).strip()
        except Exception as e:
            self.log_status(_tr("Fehler beim Abrufen des YouTube-Titels:") + " " + str(e))
        return None

    def fetch_channel_videos(self):
        channel_input = self.youtube_channel_edit.text().strip()
        if not channel_input:
            self.log_status(_tr("Kein YouTube-Kanal angegeben."))
            return
        channel_id = ""
        feed_url = ""
        if "youtube.com/channel/" in channel_input:
            channel_id = channel_input.split("youtube.com/channel/")[-1].split("/")[0]
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        elif "youtube.com/user/" in channel_input:
            username = channel_input.split("youtube.com/user/")[-1].split("/")[0]
            feed_url = f"https://www.youtube.com/feeds/videos.xml?user={username}"
        elif "/@" in channel_input:
            try:
                resp = requests.get(channel_input, timeout=10)
                if resp.status_code == 200:
                    m = re.search(r'"channelId":"(UC[\w-]+)"', resp.text)
                    if not m:
                        m = re.search(r'<meta\s+(?:itemprop|name)=["\']channelId["\']\s+content=["\'](UC[\w-]+)["\']', resp.text)
                    if m:
                        channel_id = m.group(1)
                        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    else:
                        self.log_status(_tr("Konnte die Channel-ID aus der Handle-Seite nicht extrahieren."))
                        return
                else:
                    self.log_status(_tr("Fehler beim Abrufen der Handle-Seite: Status Code") + " " + str(resp.status_code))
                    return
            except Exception as e:
                self.log_status(_tr("Fehler beim Abrufen der Handle-Seite:") + " " + str(e))
                return
        else:
            channel_id = channel_input
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            resp = requests.get(feed_url, timeout=10)
            if resp.status_code != 200:
                self.log_status(_tr("Fehler beim Abrufen des Feeds: Status Code") + " " + str(resp.status_code))
                return
            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
            count = 0
            for entry in root.findall("atom:entry", ns):
                video_id_elem = entry.find("yt:videoId", ns)
                if video_id_elem is not None:
                    video_url = f"https://www.youtube.com/watch?v={video_id_elem.text}"
                    item = QListWidgetItem(video_url)
                    item.setData(Qt.UserRole, video_url)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Checked)
                    self.url_list_widget.addItem(item)
                    count += 1
            self.log_status(str(count) + " " + _tr("Videos vom Kanal hinzugefügt."))
            self.update_status_bar()
        except Exception as e:
            self.log_status(_tr("Fehler beim Abrufen des YouTube-Kanals:") + " " + str(e))

    def load_url(self, url):
        enforce_dark = ("youtube.com/watch" in url or "youtu.be/" in url) and (self.current_theme == "night")
        if self.proxy_checkbox.isChecked():
            host = self.proxy_host_edit.text().strip()
            port = self.proxy_port_edit.text().strip()
            if not host or not port:
                self.log_status(_tr("Proxy aktiviert, aber Host oder Port fehlen. URL-Aufruf wird abgebrochen."))
                return
            proxy_type = self.proxy_type_combo.currentText().upper()
            try:
                if proxy_type == "SOCKS4":
                    self.log_status(_tr("Lade URL über SOCKS4 Proxy:") + " " + host + ":" + port)
                    response = socks4_get(url, host, port, timeout=10)
                    self.web_view.setHtml(response.decode(errors='ignore'), QUrl(url))
                elif proxy_type == "SOCKS5":
                    self.log_status(_tr("Lade URL über SOCKS5 Proxy:") + " " + host + ":" + port)
                    response = socks5_get(url, host, port, timeout=10)
                    self.web_view.setHtml(response.decode(errors='ignore'), QUrl(url))
                else:
                    proxy_url = f"{proxy_type.lower()}://{host}:{port}"
                    proxies = {"http": proxy_url, "https": proxy_url}
                    self.log_status(_tr("Lade URL über Proxy:") + " " + proxy_url)
                    response = requests.get(url, proxies=proxies, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        self.web_view.setHtml(response.text, QUrl(response.url))
                    else:
                        self.log_status(_tr("Fehler: Status Code") + " " + str(response.status_code))
                        return
            except Exception as e:
                self.log_status(_tr("Fehler beim Proxy-Aufruf:") + " " + str(e))
                return
        else:
            self.log_status(_tr("Kein Proxy aktiviert – daher wird die URL direkt geladen."))
            try:
                self.web_view.loadFinished.disconnect(self.update_video_filter)
            except Exception:
                pass
            if enforce_dark and self.filter_checkbox.isChecked():
                self.update_video_filter()
            self.web_view.load(QUrl(url))
        self.page_calls_count += 1
        self.update_status_bar()

    def enforce_youtube_dark_mode(self, finished=True):
        js = """
        (function() {
          document.cookie = "PREF=dark_mode=1; path=/; domain=.youtube.com";
          var style = document.createElement('style');
          style.innerHTML = 'body, #content, ytd-app { background-color: #181818 !important; color: #e0e0e0 !important; }';
          document.head.appendChild(style);
        })();
        """
        self.web_view.page().runJavaScript(js)
        try:
            self.web_view.loadFinished.disconnect(self.enforce_youtube_dark_mode)
        except Exception:
            pass

    def run_url_sequence(self, urls, repeat_count, random_order=False):
        if not urls:
            self.log_status(_tr("Keine URLs ausgewählt!"))
            self.set_controls_enabled(True)
            self._is_running = False
            return
        if random_order:
            urls = urls.copy()
            random.shuffle(urls)
        mode_text = _tr("Zufällig") if random_order else _tr("Sequentiell")
        self.log_status(_tr("Starte Ablauf (") + mode_text + _tr("), Wiederholungen:") + " " + str(repeat_count))
        self.clear_log()
        self.page_calls_count = 0
        self.last_wait_time = None
        self._current_repeat = 0
        self._urls = urls
        self._current_index = 0
        self._repeat_count = repeat_count
        self._random_order = random_order
        self._is_running = True
        self.set_controls_enabled(False)
        self.btn_stop.setEnabled(True)
        self.process_next_url()

    def process_next_url(self):
        if not self._is_running:
            self.log_status(_tr("Ablauf gestoppt."))
            self.set_controls_enabled(True)
            return
        if self._current_repeat >= self._repeat_count:
            self.log_status(_tr("Ablauf beendet."))
            self.set_controls_enabled(True)
            self._is_running = False
            return
        if self._current_index >= len(self._urls):
            self._current_repeat += 1
            if self._current_repeat >= self._repeat_count:
                self.log_status(_tr("Ablauf beendet."))
                self.set_controls_enabled(True)
                self._is_running = False
                return
            self.log_status(_tr("Beginne Wiederholung") + " " + str(self._current_repeat + 1) + " " + _tr("von") + " " + str(self._repeat_count))
            if self._random_order:
                self._urls = self._urls.copy()
                random.shuffle(self._urls)
            self._current_index = 0
        url = self._urls[self._current_index]
        self.log_status(_tr("Öffne URL:") + " " + url)
        self.load_url(url)
        self._current_index += 1
        wait_time, min_wait, max_wait, _ = self.get_parameters()
        total_wait_ms = self.compute_total_wait_ms(wait_time, min_wait, max_wait)
        self.last_wait_time = total_wait_ms / 1000
        self.log_status(_tr("Warte") + " " + f"{self.last_wait_time:.3f}" + " " + _tr("Sekunden ..."))
        self.wait_start = QTime.currentTime()
        self.wait_duration_ms = total_wait_ms
        self.progress_bar.setMaximum(total_wait_ms)
        self.progress_bar.setValue(0)
        if self.progress_timer is not None:
            self.progress_timer.stop()
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        self.progress_timer.start(50)
        self._current_timer = QTimer.singleShot(total_wait_ms, self.process_next_url)

    def update_progress_bar(self):
        elapsed = self.wait_start.msecsTo(QTime.currentTime())
        if elapsed > self.wait_duration_ms:
            elapsed = self.wait_duration_ms
        self.progress_bar.setValue(elapsed)
        if elapsed >= self.wait_duration_ms:
            if self.progress_timer is not None:
                self.progress_timer.stop()

    def start_running(self):
        if self._is_running:
            return
        wait_time, min_wait, max_wait, repeat = self.get_parameters()
        if self.radio_url_single.isChecked():
            urls_all = self.get_checked_urls()
            if not urls_all:
                self.log_status(_tr("Keine URLs in der Liste!"))
                return
            if len(urls_all) == 1:
                selected = urls_all[0]
            else:
                selected, ok = QInputDialog.getItem(self, _tr("Einzelne URL auswählen"), _tr("Wähle eine URL:"), urls_all, 0, False)
                if not ok or not selected:
                    self.log_status(_tr("Auswahl abgebrochen."))
                    return
            url_list = [selected]
        elif self.radio_url_multiple.isChecked():
            url_list = self.get_checked_urls()
            if not url_list:
                self.log_status(_tr("Keine URLs ausgewählt!"))
                return
        elif self.radio_url_all.isChecked():
            url_list = []
            for i in range(self.url_list_widget.count()):
                item = self.url_list_widget.item(i)
                url_list.append(item.data(Qt.UserRole))
            if not url_list:
                self.log_status(_tr("Keine URLs in der Liste!"))
                return
        else:
            self.log_status(_tr("Ungültige URL-Auswahl."))
            return

        if self.radio_func_once.isChecked():
            effective_repeat = 1
            random_order = False
        elif self.radio_func_sequential.isChecked():
            effective_repeat = repeat
            random_order = False
        elif self.radio_func_random.isChecked():
            effective_repeat = repeat
            random_order = True
        else:
            effective_repeat = repeat
            random_order = False

        self.run_url_sequence(url_list, repeat_count=effective_repeat, random_order=random_order)

    def stop_running(self):
        self._is_running = False
        if self.progress_timer is not None:
            self.progress_timer.stop()
        self.log_status(_tr("Stop-Befehl empfangen. Ablauf abgebrochen."))
        self.set_controls_enabled(True)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

if __name__ == '__main__':
    set_language_automatically()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

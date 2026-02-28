import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import feedparser
from winotify import Notification, audio
import threading
import time
import json
import os
import csv
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from collections import defaultdict
import webbrowser
import urllib.parse
import urllib.request
from io import BytesIO
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Sentiment Analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("TextBlob not installed. Run: pip install textblob")

# --- KONFIGURACJA GLOBALNA ---
PLIK_KONFIGURACJI = "radar_config_v44.json"
PLIK_HISTORII = "radar_historia_v44.json"
MAX_FRAZ = 20
INTERVAL = 600  # 10 minut
BURST_WINDOW = 900  # 15 minut w sekundach
BURST_THRESHOLD = 3  # Minimum newsów do uznania za burst
MAX_FRAZ = 20
INTERVAL = 600  # 10 minut
BURST_WINDOW = 900  # 15 minut w sekundach
BURST_THRESHOLD = 3  # Minimum newsów do uznania za burst
COFFEE_LINK = "https://buymeacoffee.com/kitay"  # Zmień na swój link!

# --- THEME CONFIGURATION (FINANCIAL DARK MODE) ---
THEME = {
    "bg_main": "#f0f0f0",       # Windows/Swing Light Grey (Burp style)
    "bg_panel": "#ffffff",      # White content areas
    "bg_input": "#ffffff",      # White inputs
    "fg_text": "#000000",       # Black text
    "fg_dim": "#666666",        # Dimmed text
    "accent_green": "#2e7d32",  # Standard Green
    "accent_red": "#d32f2f",    # Standard Red
    "accent_blue": "#1976d2",   # Standard Blue
    "accent_gold": "#fbc02d",   # Standard Gold
    "accent_select": "#ff9800", # BURP ORANGE SELECTION
    "font_main": ("Segoe UI", 9),
    "font_mono": ("Consolas", 9),
    "font_header": ("Segoe UI", 11, "bold"),
    "border": "#cccccc"
}

# --- TRANSLATIONS / TŁUMACZENIA ---
TRANSLATIONS = {
    "pl": {
        # Tytuł i główne
        "title": "Radar Inwestora v4.4 PRO - Multi-language",
        "monitoring": "🎯 Monitoring",
        "history": "📊 Historia",
        "sources": "🌐 Źródła",
        "readme": "📖 Instrukcja",
        "support": "☕ Wsparcie",
        
        # Monitoring
        "region_settings": "⚙️ Ustawienia Regionu",
        "search_in": "Szukaj newsów w:",
        "add_phrase": "➕ Dodaj Nową Frazę",
        "phrase": "Fraza:",
        "ticker": "Ticker:",
        "ticker_hint": "(np. AAPL, TSLA)",
        "priority": "Priorytet:",
        "category": "Kategoria:",
        "filters_pos": "Filtry (+):",
        "filters_neg": "Filtry (-):",
        "min_sentiment": "Min Sentiment:",
        "separate_commas": "(oddziel przecinkami)",
        "exclude_words": "(wykluczaj te słowa)",
        "add_phrase_btn": "DODAJ FRAZĘ",
        "counter": "Licznik:",
        "monitored_phrases": "Monitorowane Frazy:",
        "scan_now": "SKANUJ TERAZ",
        "pause": "PAUZA",
        "resume": "WZNÓW",
        "import": "IMPORTUJ",
        "export": "EKSPORTUJ",
        "log": "Log Aplikacji:",
        "status": "Status:",
        "idle": "Oczekiwanie...",
        "scanning": "Skanowanie...",
        
        # Historia
        "statistics": "📊 STATYSTYKI:",
        "total_news": "Wszystkich newsów:",
        "today": "Dzisiaj wykryto:",
        "avg_sentiment": "Średni sentiment:",
        "by_priority": "Po priorytetach:",
        "top_5": "TOP 5 najaktywniejszych:",
        "active_bursts": "🔥 AKTYWNE BURST:",
        "history_100": "Historia (ostatnie 100):",
        "date_time": "Data/Czas",
        "title_col": "Tytuł",
        "source": "Źródło",
        "export_csv": "EKSPORTUJ CSV",
        "clear_history": "WYCZYŚĆ HISTORIĘ",
        
        # Źródła
        "source_stats": "📊 STATYSTYKI ŹRÓDEŁ:",
        "news_count": "Newsów:",
        "enable_all": "WŁĄCZ WSZYSTKIE",
        "disable_all": "WYŁĄCZ WSZYSTKIE",
        
        # README
        "readme_title": "📖 INSTRUKCJA UŻYTKOWNIKA",
        "readme_content": """
╔═══════════════════════════════════════════════════════════╗
║         RADAR INWESTORA v4.3 PRO - INSTRUKCJA            ║
╚═══════════════════════════════════════════════════════════╝

🚀 SZYBKI START
───────────────────────────────────────────────────────────
1. Wybierz region (np. POLSKA, USA, UK)
2. Dodaj frazę do monitorowania (np. "Apple" lub "Tesla")
3. OPCJONALNIE: Dodaj ticker (np. AAPL, TSLA)
   ⚠️ WAŻNE: Ticker jest wymagany dla Yahoo Finance i Seeking Alpha!
   • Google News używa frazy (nazwy firmy)
   • Yahoo Finance i Seeking Alpha używają tickera
4. Ustaw priorytet:
   • CRITICAL - najważniejsze (czerwony, głośny alarm)
   • HIGH - ważne (pomarańczowy)
   • MEDIUM - standardowe (niebieski)
   • LOW - mniej ważne (szary)
5. Wybierz kategorię (Portfolio, Watchlist, Sektor...)
6. Kliknij "DODAJ FRAZĘ"

Aplikacja automatycznie skanuje co 10 minut!

💡 FUNKCJE
───────────────────────────────────────────────────────────
✓ Monitoring newsów z Google News, Yahoo Finance, Seeking Alpha
✓ Analiza sentymentu (pozytywny/negatywny/neutralny)
✓ Powiadomienia Windows przy nowych newsach
✓ Detekcja "burst" - nagłego wzrostu newsów
✓ Filtry pozytywne (+) i negatywne (-)
✓ Eksport historii do CSV
✓ Statystyki i analiza trendów

📈 TICKER vs FRAZA
───────────────────────────────────────────────────────────
• FRAZA: Nazwa firmy (np. "Apple", "Microsoft")
  → Używana przez Google News
  
• TICKER: Symbol giełdowy (np. AAPL, MSFT)
  → Wymagany dla Yahoo Finance i Seeking Alpha
  → Zawsze wielkie litery (automatycznie)
  
Przykład:
  Fraza: "Apple"
  Ticker: AAPL
  
Bez tickera tylko Google News będzie skanowane!

🎯 FILTRY
───────────────────────────────────────────────────────────
• Filtry (+): News MUSI zawierać te słowa
  Przykład: "earnings, revenue, profit"
  
• Filtry (-): News NIE MOŻE zawierać tych słów
  Przykład: "rumor, speculation"
  
• Min Sentiment: Próg sentymentu (-1.0 do 1.0)
  -1.0 = bardzo negatywny
   0.0 = neutralny
  +1.0 = bardzo pozytywny

🔔 POWIADOMIENIA
───────────────────────────────────────────────────────────
Różne dźwięki dla każdego priorytetu:
• CRITICAL - LoopingAlarm (powtarzający się)
• HIGH - Reminder (przypomnienie)
• MEDIUM - Default (standardowy)
• LOW - SMS (cichy)

📊 ZAKŁADKI
───────────────────────────────────────────────────────────
🎯 Monitoring - Dodawanie i zarządzanie frazami
📊 Historia - Statystyki i archiwum wykrytych newsów
🌐 Źródła - Włączanie/wyłączanie źródeł newsów
📖 Instrukcja - Ta instrukcja
☕ Wsparcie - Wesprzyj projekt!

⚙️ WSKAZÓWKI
───────────────────────────────────────────────────────────
• Używaj konkretnych fraz zamiast ogólnych słów
• Dodaj filtry aby zawęzić wyniki
• Możesz monitorować max 20 fraz jednocześnie
• Double-click na newsie w historii otwiera link
• Konfiguracja zapisuje się automatycznie

🐛 PROBLEMY?
───────────────────────────────────────────────────────────
• Brak powiadomień? → Uruchom jako administrator
• Za dużo newsów? → Użyj filtrów negatywnych
• Aplikacja się zawiesza? → Sprawdź połączenie internetowe

═══════════════════════════════════════════════════════════
              Powodzenia w inwestowaniu! 📈
═══════════════════════════════════════════════════════════
        """,
        
        # Wsparcie
        "support_title": "☕ WESPRZYJ PROJEKT",
        "support_content": """
╔═══════════════════════════════════════════════════════════╗
║              DZIĘKUJĘ ZA UŻYWANIE RADARU!                ║
╚═══════════════════════════════════════════════════════════╝

Jeśli Radar Inwestora pomaga Ci w inwestowaniu, rozważ 
wsparcie projektu! 🙏

Twoje wsparcie pozwoli na:
───────────────────────────────────────────────────────────
✓ Dalszy rozwój aplikacji
✓ Dodawanie nowych funkcji
✓ Lepsze źródła newsów
✓ Integracje z brokerami
✓ Wsparcie techniczne

Kliknij przycisk poniżej aby wesprzeć projekt! 💚
        """,
        "coffee_button": "☕ KUP MI KAWĘ",
        "thank_you": "Dziękuję za wsparcie! 💚",
        
        # Komunikaty
        "error": "Błąd",
        "success": "Sukces",
        "warning": "Ostrzeżenie",
        "info": "Info",
        "phrase_added": "Dodano frazę",
        "phrase_exists": "Fraza już istnieje",
        "max_phrases": "Osiągnięto maksimum fraz",
        "phrase_removed": "Usunięto frazę",
        "confirm": "Potwierdzenie",
        "delete_phrase": "Usunąć frazę",
        "import_success": "Zaimportowano",
        "export_success": "Wyeksportowano",
        "history_cleared": "Historia wyczyszczona",
        "confirm_clear": "Usunąć wszystkie newsy starsze niż 30 dni?",
        "scanning_progress": "Skanowanie",
        
        # Kategorie
        "cat_portfolio": "Portfolio",
        "cat_watchlist": "Watchlist",
        "cat_sector": "Sektor",
        "cat_macro": "Makro",
        "cat_competition": "Konkurencja",
        "cat_insider": "Insider",
        "cat_other": "Inne",
    },
    
    "en": {
        # Title and main
        "title": "Investment Radar v4.4 PRO - Multi-language",
        "monitoring": "🎯 Monitoring",
        "history": "📊 History",
        "sources": "🌐 Sources",
        "readme": "📖 User Guide",
        "support": "☕ Support",
        
        # Monitoring
        "region_settings": "⚙️ Region Settings",
        "search_in": "Search news in:",
        "add_phrase": "➕ Add New Phrase",
        "phrase": "Phrase:",
        "ticker": "Ticker:",
        "ticker_hint": "(e.g. AAPL, TSLA)",
        "priority": "Priority:",
        "category": "Category:",
        "filters_pos": "Filters (+):",
        "filters_neg": "Filters (-):",
        "min_sentiment": "Min Sentiment:",
        "separate_commas": "(separate with commas)",
        "exclude_words": "(exclude these words)",
        "add_phrase_btn": "ADD PHRASE",
        "counter": "Counter:",
        "monitored_phrases": "Monitored Phrases:",
        "scan_now": "SCAN NOW",
        "pause": "PAUSE",
        "resume": "RESUME",
        "import": "IMPORT",
        "export": "EXPORT",
        "log": "Application Log:",
        "status": "Status:",
        "idle": "Idle...",
        "scanning": "Scanning...",
        
        # History
        "statistics": "📊 STATISTICS:",
        "total_news": "Total news:",
        "today": "Detected today:",
        "avg_sentiment": "Average sentiment:",
        "by_priority": "By priority:",
        "top_5": "TOP 5 most active:",
        "active_bursts": "🔥 ACTIVE BURSTS:",
        "history_100": "History (last 100):",
        "date_time": "Date/Time",
        "title_col": "Title",
        "source": "Source",
        "export_csv": "EXPORT CSV",
        "clear_history": "CLEAR HISTORY",
        
        # Sources
        "source_stats": "📊 SOURCE STATISTICS:",
        "news_count": "News count:",
        "enable_all": "ENABLE ALL",
        "disable_all": "DISABLE ALL",
        
        # README
        "readme_title": "📖 USER GUIDE",
        "readme_content": """
╔═══════════════════════════════════════════════════════════╗
║        INVESTMENT RADAR v4.3 PRO - USER GUIDE            ║
╚═══════════════════════════════════════════════════════════╝

🚀 QUICK START
───────────────────────────────────────────────────────────
1. Select region (e.g., USA, UK, POLAND)
2. Add a phrase to monitor (e.g., "Apple" or "Tesla")
3. OPTIONAL: Add ticker (e.g., AAPL, TSLA)
   ⚠️ IMPORTANT: Ticker is required for Yahoo Finance and Seeking Alpha!
   • Google News uses phrase (company name)
   • Yahoo Finance and Seeking Alpha use ticker
4. Set priority:
   • CRITICAL - most important (red, loud alarm)
   • HIGH - important (orange)
   • MEDIUM - standard (blue)
   • LOW - less important (gray)
5. Choose category (Portfolio, Watchlist, Sector...)
6. Click "ADD PHRASE"

The app automatically scans every 10 minutes!

💡 FEATURES
───────────────────────────────────────────────────────────
✓ Monitor news from Google News, Yahoo Finance, Seeking Alpha
✓ Sentiment analysis (positive/negative/neutral)
✓ Windows notifications for new articles
✓ "Burst" detection - sudden increase in news
✓ Positive (+) and negative (-) filters
✓ Export history to CSV
✓ Statistics and trend analysis

📈 TICKER vs PHRASE
───────────────────────────────────────────────────────────
• PHRASE: Company name (e.g., "Apple", "Microsoft")
  → Used by Google News
  
• TICKER: Stock symbol (e.g., AAPL, MSFT)
  → Required for Yahoo Finance and Seeking Alpha
  → Always uppercase (automatic)
  
Example:
  Phrase: "Apple"
  Ticker: AAPL
  
Without ticker, only Google News will be scanned!

🎯 FILTERS
───────────────────────────────────────────────────────────
• Filters (+): News MUST contain these words
  Example: "earnings, revenue, profit"
  
• Filters (-): News MUST NOT contain these words
  Example: "rumor, speculation"
  
• Min Sentiment: Sentiment threshold (-1.0 to 1.0)
  -1.0 = very negative
   0.0 = neutral
  +1.0 = very positive

🔔 NOTIFICATIONS
───────────────────────────────────────────────────────────
Different sounds for each priority:
• CRITICAL - LoopingAlarm (repeating)
• HIGH - Reminder
• MEDIUM - Default
• LOW - SMS (quiet)

📊 TABS
───────────────────────────────────────────────────────────
🎯 Monitoring - Add and manage phrases
📊 History - Statistics and archive of detected news
🌐 Sources - Enable/disable news sources
📖 User Guide - This guide
☕ Support - Support the project!

⚙️ TIPS
───────────────────────────────────────────────────────────
• Use specific phrases instead of general words
• Add filters to narrow results
• You can monitor max 20 phrases simultaneously
• Double-click on news in history to open link
• Configuration saves automatically

🐛 PROBLEMS?
───────────────────────────────────────────────────────────
• No notifications? → Run as administrator
• Too many news? → Use negative filters
• App freezing? → Check internet connection

═══════════════════════════════════════════════════════════
                Happy investing! 📈
═══════════════════════════════════════════════════════════
        """,
        
        # Support
        "support_title": "☕ SUPPORT THE PROJECT",
        "support_content": """
╔═══════════════════════════════════════════════════════════╗
║           THANK YOU FOR USING INVESTMENT RADAR!          ║
╚═══════════════════════════════════════════════════════════╝

If Investment Radar helps you in your investing journey,
please consider supporting the project! 🙏

Your support will enable:
───────────────────────────────────────────────────────────
✓ Continued app development
✓ Adding new features
✓ Better news sources
✓ Broker integrations
✓ Technical support

Click the button below to support the project! 💚
        """,
        "coffee_button": "☕ BUY ME A COFFEE",
        "thank_you": "Thank you for your support! 💚",
        
        # Messages
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        "phrase_added": "Phrase added",
        "phrase_exists": "Phrase already exists",
        "max_phrases": "Maximum phrases reached",
        "phrase_removed": "Phrase removed",
        "confirm": "Confirmation",
        "delete_phrase": "Delete phrase",
        "import_success": "Imported",
        "export_success": "Exported",
        "history_cleared": "History cleared",
        "confirm_clear": "Delete all news older than 30 days?",
        "scanning_progress": "Scanning",
        
        # Categories
        "cat_portfolio": "Portfolio",
        "cat_watchlist": "Watchlist",
        "cat_sector": "Sector",
        "cat_macro": "Macro",
        "cat_competition": "Competition",
        "cat_insider": "Insider",
        "cat_other": "Other",
    }
}

# Regiony
REGIONY = {
    "POLSKA (pl)": "hl=pl-PL&gl=PL&ceid=PL:pl",
    "USA (en)": "hl=en-US&gl=US&ceid=US:en",
    "GERMANY (de)": "hl=de-DE&gl=DE&ceid=DE:de",
    "UK (en)": "hl=en-GB&gl=GB&ceid=GB:en",
    "JAPAN (ja)": "hl=ja-JP&gl=JP&ceid=JP:ja",
    "CHINA (zh)": "hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "INDIA (en)": "hl=en-IN&gl=IN&ceid=IN:en",
    "WORLD (en)": "hl=en-US&gl=US&ceid=US:en"
}

# Priorytety
# Priorytety (Dostosowane do Dark Mode)
PRIORYTETY = {
    "CRITICAL": {"kolor": "#FF5252", "bg": "#3e1a1a", "dzwiek": audio.LoopingAlarm},  # Czerwony na ciemnym tle
    "HIGH": {"kolor": "#FFAB40", "bg": "#3e2b1a", "dzwiek": audio.Reminder},      # Pomarańczowy
    "MEDIUM": {"kolor": "#448AFF", "bg": "#1a253e", "dzwiek": audio.Default},      # Niebieski
    "LOW": {"kolor": "#B0BEC5", "bg": "#263238", "dzwiek": audio.SMS}             # Szary
}

# Źródła newsów
SOURCES = {
    "Google News": {
        "enabled": True,
        "type": "google",
        "weight": 1.0
    },
    "Yahoo Finance": {
        "enabled": True,
        "type": "yahoo",
        "weight": 1.2,
        "base_url": "https://finance.yahoo.com/rss/"
    },
    "Seeking Alpha": {
        "enabled": True,
        "type": "seekingalpha",
        "weight": 1.5,
        "base_url": "https://seekingalpha.com/feed.xml"
    },
    "MarketWatch": {
        "enabled": True,
        "type": "general",
        "weight": 1.1,
        "base_url": "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/"
    },
    "CNBC": {
        "enabled": True,
        "type": "general",
        "weight": 1.1,
        "base_url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"
    },
    "Benzinga": {
        "enabled": False,
        "type": "benzinga",
        "weight": 1.3,
        "base_url": "https://www.benzinga.com/stock/{ticker}/feed"  # redirectuje, wyłączone
    },
    "PR Newswire": {
        "enabled": True,
        "type": "prnewswire",
        "weight": 1.2,
        "base_url": "https://www.prnewswire.com/rss/news-releases-list.rss"
    },
    "OpenInsider": {
        "enabled": True,
        "type": "openinsider",
        "weight": 2.0,
        "base_url": "http://openinsider.com/rss?s={ticker}"
    }
}

class RadarApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "pl"  # Domyślny język
        
        # Zmienne
        self.monitorowane_frazy = []
        self.historia_newsow = {}
        self.burst_tracker = defaultdict(list)
        self.skanowanie_aktywne = True
        self.wymuszenie_skanowania = False
        self.wybrany_region_kod = REGIONY["USA (en)"]
        self.sources_config = SOURCES.copy()
        
        # Cache dla duplikatów
        self.known_titles = set()
        
        # Log widget (inicjalizowany w stworz_zakladke_log)
        self.log_text = None

        # Historia sorting & filtering
        self.history_sort_col = "time"
        self.history_sort_reverse = True
        self.history_from_date = None  # datetime object or None
        
        # Wczytaj język z konfiguracji (jeśli istnieje)
        self.wczytaj_konfiguracje()
        
        # Ustaw tytuł
        self.root.title(self.t("title"))
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)
        self.root.configure(bg=THEME["bg_main"])
        
        # Konfiguracja Stylów (Dark Mode)
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam' pozwala na lepszą kontrolę kolorów
        
        self.style.configure(".", 
            background=THEME["bg_main"], 
            foreground=THEME["fg_text"],
            fieldbackground=THEME["bg_input"],
            font=THEME["font_main"]
        )
        
        # TNotebook
        self.style.configure("TNotebook", background=THEME["bg_main"], borderwidth=0)
        self.style.configure("TNotebook.Tab", 
            background=THEME["bg_panel"], 
            foreground=THEME["fg_dim"],
            padding=[15, 5],
            font=("Segoe UI", 9, "bold")
        )
        self.style.map("TNotebook.Tab", 
            background=[("selected", THEME["bg_input"])],
            foreground=[("selected", THEME["accent_blue"])]
        )
        
        # TFrame, TLabel, TButton
        self.style.configure("TFrame", background=THEME["bg_main"])
        self.style.configure("Card.TFrame", background=THEME["bg_panel"], relief="flat")
        
        self.style.configure("TLabel", background=THEME["bg_main"], foreground=THEME["fg_text"])
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=THEME["accent_blue"])
        
        self.style.configure("TButton", 
            background=THEME["bg_panel"], 
            foreground=THEME["fg_text"],
            borderwidth=1,
            focuscolor=THEME["accent_blue"]
        )
        self.style.map("TButton", 
            background=[('active', THEME["bg_input"])], 
            foreground=[('active', THEME["accent_blue"])]
        )
        
        # Action Button (Accent)
        self.style.configure("Action.TButton", 
            background=THEME["accent_blue"], 
            foreground="white",
            font=("Segoe UI", 9, "bold")
        )
        
        # Treeview (Financial Grid Look)
        self.style.configure("Treeview", 
            background=THEME["bg_main"],
            foreground=THEME["fg_text"],
            fieldbackground=THEME["bg_main"],
            rowheight=25,
            font=THEME["font_mono"],
            borderwidth=0
        )
        self.style.configure("Treeview.Heading", 
            background=THEME["bg_panel"], 
            foreground=THEME["fg_dim"],
            font=("Segoe UI", 8, "bold"),
            borderwidth=1,
            relief="flat"
        )
        self.style.map("Treeview", background=[('selected', THEME["bg_input"])], foreground=[('selected', THEME["accent_blue"])])

        # TCombobox (Naprawa widoczności)
        self.style.map('TCombobox', fieldbackground=[('readonly', THEME["bg_input"])])
        self.style.map('TCombobox', selectbackground=[('readonly', THEME["accent_select"])]) # Orange
        self.style.map('TCombobox', selectforeground=[('readonly', "black")])
        self.style.configure("TCombobox", 
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_panel"], 
            foreground=THEME["fg_text"],
            arrowcolor=THEME["fg_text"]
        )
        
        # TEntry
        self.style.configure("TEntry", 
            fieldbackground=THEME["bg_input"],
            foreground=THEME["fg_text"],
            insertcolor="black"
        )

        
        # Tworzenie GUI
        self.stworz_gui()
        
        # Logika
        self.wczytaj_historie()
        self.odswiez_liste_gui()
        self.odswiez_statystyki()
        
        # Info o sentiment
        if not SENTIMENT_AVAILABLE:
            self.log("⚠️ TextBlob not installed - sentiment analysis disabled")
            self.log("Install: pip install textblob")
        else:
            self.log("✅ Sentiment Analysis active")
        
        # Wątki
        self.next_scan_time = None  # dla countdown w status bar
        self.thread = threading.Thread(target=self.petla_radaru, daemon=True)
        self.thread.start()
        
        self.burst_thread = threading.Thread(target=self.monitoruj_burst, daemon=True)
        self.burst_thread.start()
        
        self.countdown_thread = threading.Thread(target=self.petla_countdown, daemon=True)
        self.countdown_thread.start()
    
    def t(self, key):
        """Pobierz tłumaczenie dla klucza"""
        return TRANSLATIONS[self.current_lang].get(key, key)
    
    def get_categories(self):
        """Pobierz listę kategorii w aktualnym języku"""
        return [
            self.t("cat_portfolio"),
            self.t("cat_watchlist"),
            self.t("cat_sector"),
            self.t("cat_macro"),
            self.t("cat_competition"),
            self.t("cat_insider"),
            self.t("cat_other")
        ]
    
    def switch_language(self):
        """Przełącz język"""
        self.current_lang = "en" if self.current_lang == "pl" else "pl"
        self.zapisz_konfiguracje()
        
        # Odśwież GUI
        messagebox.showinfo(
            "Language Changed" if self.current_lang == "en" else "Zmieniono język",
            "Please restart the application for changes to take effect.\n\nProszę zrestartować aplikację aby zobaczyć zmiany." if self.current_lang == "en" 
            else "Proszę zrestartować aplikację aby zobaczyć zmiany.\n\nPlease restart the application for changes to take effect."
        )
    
    def stworz_gui(self):
        # Top bar z przyciskiem języka
        top_frame = tk.Frame(self.root, bg=THEME["bg_panel"], height=40)
        top_frame.pack(fill='x', side='top')
        top_frame.pack_propagate(False)
        
        lang_btn = tk.Button(
            top_frame, 
            text=f"🌐 {'EN' if self.current_lang == 'pl' else 'PL'}",
            command=self.switch_language,
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_blue"],
            fg="white",
            activebackground=THEME["accent_green"], # Highlight
            padx=15,
            pady=0,
            bd=0
        )
        lang_btn.pack(side='right', padx=10, pady=5)
        
        ttk.Label(
            top_frame, 
            text="Investment Radar v4.4 PRO",
            style="Header.TLabel",
            background=THEME["bg_panel"]
        ).pack(side='left', padx=10)
        
        # Główny kontener poziomy: notebook + sidebar
        main_container = tk.Frame(self.root, bg=THEME["bg_main"])
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Notebook dla zakładek (lewa strona)
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True, side='left')

        # Sidebar (prawa strona)
        self.stworz_sidebar(main_container)
        
        # Zakładka 1: Monitoring
        tab_monitor = tk.Frame(notebook)
        notebook.add(tab_monitor, text=self.t("monitoring"))
        self.stworz_zakladke_monitoring(tab_monitor)
        
        # Zakładka 2: Historia
        tab_historia = tk.Frame(notebook)
        notebook.add(tab_historia, text=self.t("history"))
        self.stworz_zakladke_historia(tab_historia)
        
        # Zakładka 3: Źródła
        tab_sources = tk.Frame(notebook)
        notebook.add(tab_sources, text=self.t("sources"))
        self.stworz_zakladke_zrodla(tab_sources)
        
        # Zakładka 4: README
        tab_readme = tk.Frame(notebook)
        notebook.add(tab_readme, text=self.t("readme"))
        self.stworz_zakladke_readme(tab_readme)
        
        # Zakładka 5: Wsparcie
        tab_support = tk.Frame(notebook)
        notebook.add(tab_support, text=self.t("support"))
        self.stworz_zakladke_wsparcie(tab_support)
        
        # Zakładka 6: Log aplikacji
        tab_log = tk.Frame(notebook, bg=THEME["bg_main"])
        notebook.add(tab_log, text="📋 Log")
        self.stworz_zakladke_log(tab_log)

    def stworz_zakladke_monitoring(self, parent):
        # Ustawienia regionu
        frame_settings = tk.LabelFrame(parent, text=self.t("region_settings"), padx=10, pady=5, 
                                      bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_header"])
        frame_settings.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_settings, text=self.t("search_in"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).pack(side='left')
        
        self.combo_region = ttk.Combobox(frame_settings, values=list(REGIONY.keys()), 
                                         state="readonly", width=20)
        self.combo_region.current(1)  # USA domyślnie
        self.combo_region.pack(side='left', padx=10)
        self.combo_region.bind("<<ComboboxSelected>>", self.zmien_region)

        # Dodawanie frazy
        frame_input = tk.LabelFrame(parent, text=self.t("add_phrase"), padx=10, pady=5,
                                   bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_header"])
        frame_input.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_input, text=self.t("phrase"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_fraza = ttk.Entry(frame_input, width=25)
        self.entry_fraza.grid(row=0, column=1, padx=5, pady=2)
        self.entry_fraza.bind('<Return>', lambda e: self.dodaj_fraze())
        
        tk.Label(frame_input, text=self.t("ticker"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_ticker = ttk.Entry(frame_input, width=10)
        self.entry_ticker.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        tk.Label(frame_input, text=self.t("ticker_hint"), font=("Segoe UI", 8), bg=THEME["bg_panel"], fg=THEME["fg_dim"]).grid(row=1, column=1, sticky='e', padx=5)
        
        tk.Label(frame_input, text=self.t("priority"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=0, column=2, sticky='w', padx=5)
        self.combo_priorytet = ttk.Combobox(frame_input, values=list(PRIORYTETY.keys()), 
                                            state="readonly", width=10)
        self.combo_priorytet.current(2)  # MEDIUM
        self.combo_priorytet.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_input, text=self.t("category"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=0, column=4, sticky='w', padx=5)
        self.combo_kategoria = ttk.Combobox(frame_input, values=self.get_categories(), 
                                            state="readonly", width=12)
        self.combo_kategoria.current(0)
        self.combo_kategoria.grid(row=0, column=5, padx=5)
        
        # Filtry
        tk.Label(frame_input, text=self.t("filters_pos"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_filtry_poz = ttk.Entry(frame_input, width=25)
        self.entry_filtry_poz.grid(row=2, column=1, padx=5, pady=2)
        tk.Label(frame_input, text=self.t("separate_commas"), bg=THEME["bg_panel"], fg=THEME["fg_dim"]).grid(row=2, column=2, columnspan=2, sticky='w')
        
        tk.Label(frame_input, text=self.t("filters_neg"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.entry_filtry_neg = ttk.Entry(frame_input, width=25)
        self.entry_filtry_neg.grid(row=3, column=1, padx=5, pady=2)
        tk.Label(frame_input, text=self.t("exclude_words"), bg=THEME["bg_panel"], fg=THEME["fg_dim"]).grid(row=3, column=2, columnspan=2, sticky='w')
        
        tk.Label(frame_input, text=self.t("min_sentiment"), bg=THEME["bg_panel"], fg=THEME["fg_text"]).grid(row=3, column=4, sticky='w', padx=5)
        self.entry_min_sentiment = ttk.Entry(frame_input, width=8)
        self.entry_min_sentiment.insert(0, "-1.0")
        self.entry_min_sentiment.grid(row=3, column=5, padx=5)
        tk.Label(frame_input, text="(-1.0 to 1.0)", bg=THEME["bg_panel"], fg=THEME["fg_dim"]).grid(row=3, column=6, sticky='w')
        
        btn_dodaj = tk.Button(frame_input, text=self.t("add_phrase_btn"), command=self.dodaj_fraze, 
                             bg=THEME["accent_blue"], fg="white", font=THEME["font_header"], bd=0, padx=10)
        btn_dodaj.grid(row=0, column=6, rowspan=3, padx=10, pady=5)

        # Licznik
        self.label_licznik = tk.Label(parent, text=f"{self.t('counter')} 0/{MAX_FRAZ}", 
                                     font=THEME["font_header"], bg=THEME["bg_main"], fg=THEME["fg_text"])
        self.label_licznik.pack(pady=5)

        # Lista monitorowanych (Treeview zamiast Listbox)
        tk.Label(parent, text=self.t("monitored_phrases"), font=THEME["font_header"], bg=THEME["bg_main"], fg=THEME["fg_text"]).pack(pady=(10, 5))
        
        frame_list = tk.Frame(parent, bg=THEME["bg_main"])
        frame_list.pack(fill='both', expand=True, padx=10)
        
        list_container = tk.Frame(frame_list, bg=THEME["bg_main"])
        list_container.pack(side='left', fill='both', expand=True)
        
        columns = ("priority", "category", "ticker", "phrase")
        self.lista_frazy = ttk.Treeview(list_container, columns=columns, show='headings', height=10)
        
        self.lista_frazy.heading("priority", text=self.t("priority"))
        self.lista_frazy.heading("category", text=self.t("category"))
        self.lista_frazy.heading("ticker", text=self.t("ticker"))
        self.lista_frazy.heading("phrase", text=self.t("phrase"))
        
        self.lista_frazy.column("priority", width=80, anchor='center')
        self.lista_frazy.column("category", width=100, anchor='center')
        self.lista_frazy.column("ticker", width=80, anchor='center')
        self.lista_frazy.column("phrase", width=200, anchor='w')
        
        scroll_list = ttk.Scrollbar(list_container, command=self.lista_frazy.yview)
        scroll_list.pack(side='right', fill='y')
        
        self.lista_frazy.config(yscrollcommand=scroll_list.set)
        self.lista_frazy.config(yscrollcommand=scroll_list.set)
        self.lista_frazy.pack(fill='both', expand=True)
        self.lista_frazy.bind('<<TreeviewSelect>>', self.pokaz_newsy_dla_frazy)
        
        # Przyciski zarządzania (Bitogenic Style - Subtle)
        btn_frame = tk.Frame(frame_list, bg=THEME["bg_main"])
        btn_frame.pack(side='right', fill='y', padx=(10, 0))
        
        def create_pro_btn(text, command, accent_color=None):
            # Default style: Dark Grey bg, Text color white/grey
            # Active style: Accent Color
            
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=THEME["bg_panel"], fg=THEME["fg_text"],
                           activebackground=accent_color if accent_color else THEME["bg_input"], 
                           activeforeground="white",
                           width=14, bd=0, font=("Segoe UI", 9), pady=5)
            
            # Hover effect
            def on_enter(e):
                btn['bg'] = THEME["bg_input"]
            def on_leave(e):
                btn['bg'] = THEME["bg_panel"]
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            return btn

        # Scan Button (Highlighted)
        btn_scan = tk.Button(btn_frame, text="🔍 "+self.t("scan_now"), command=self.wymusz_skanowanie,
                            bg=THEME["accent_blue"], fg="white", 
                            activebackground="#1976d2", activeforeground="white",
                            width=14, bd=0, font=("Segoe UI", 9, "bold"), pady=6)
        btn_scan.pack(pady=5)
        
        create_pro_btn("❌ "+self.t("delete_phrase"), self.usun_fraze, THEME["accent_red"]).pack(pady=5)
        create_pro_btn("⏸ "+self.t("pause"), self.pauza_skanowania, THEME["accent_gold"]).pack(pady=5)
        create_pro_btn("▶ "+self.t("resume"), self.wznow_skanowania, THEME["accent_green"]).pack(pady=5)
        create_pro_btn("📥 "+self.t("import"), self.importuj_frazy).pack(pady=5)
        create_pro_btn("📤 "+self.t("export"), self.eksportuj_frazy).pack(pady=5)

        # Sekcja Newsów (Zamiast Logów) -> Burp Style Listener
        tk.Label(parent, text="News Preview (Last 5)", font=THEME["font_header"], bg=THEME["bg_main"], fg=THEME["fg_text"]).pack(pady=(10, 5))
        
        preview_frame = tk.Frame(parent, bg=THEME["bg_main"])
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols_news = ("time", "title", "source", "sentiment")
        self.preview_news = ttk.Treeview(preview_frame, columns=cols_news, show='headings', height=8)
        
        self.preview_news.heading("time", text="Time")
        self.preview_news.heading("title", text="Title")
        self.preview_news.heading("source", text="Source")
        self.preview_news.heading("sentiment", text="Sent")
        
        self.preview_news.column("time", width=100, anchor='center')
        self.preview_news.column("title", width=400, anchor='w')
        self.preview_news.column("source", width=100, anchor='center')
        self.preview_news.column("sentiment", width=80, anchor='center')
        
        scroll_prev = ttk.Scrollbar(preview_frame, command=self.preview_news.yview)
        scroll_prev.pack(side='right', fill='y')
        self.preview_news.config(yscrollcommand=scroll_prev.set)
        self.preview_news.pack(fill='both', expand=True)
        
        self.preview_news.bind('<Double-1>', self.otworz_link_z_preview)

        # Status bar
        self.status_bar = tk.Label(parent, text=f"{self.t('status')} {self.t('idle')}", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def stworz_sidebar(self, parent):
        """Boczny panel reklamowy — Agrojelonki"""
        FB_PAGE = "https://www.facebook.com/AgroturystykaAgrojelonki"
        FB_PHOTO_URL = "https://graph.facebook.com/AgroturystykaAgrojelonki/picture?type=large"

        sidebar = tk.Frame(parent, bg=THEME["bg_panel"], width=160, relief="flat", bd=1)
        sidebar.pack(side='right', fill='y', padx=(4, 0))
        sidebar.pack_propagate(False)

        # Tytuł
        tk.Label(
            sidebar, text="🌿 Odwiedź nas",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_panel"], fg=THEME["accent_green"]
        ).pack(pady=(12, 4))

        # Ramka na zdjęcie
        self._sidebar_photo_frame = tk.Label(
            sidebar, bg=THEME["bg_panel"], cursor="hand2"
        )
        self._sidebar_photo_frame.pack(pady=4)
        self._sidebar_photo_frame.bind("<Button-1>", lambda e: webbrowser.open(FB_PAGE))

        # Placeholder jeśli PIL niedostępny
        self._sidebar_photo_ref = None

        # Nazwa strony
        tk.Label(
            sidebar, text="Agroturystyka\nAgrojelonki",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_panel"], fg=THEME["fg_text"],
            justify="center", cursor="hand2"
        ).pack(pady=(2, 0))

        # Przycisk Facebook
        btn_fb = tk.Button(
            sidebar,
            text="👍 Facebook",
            font=("Segoe UI", 8, "bold"),
            bg="#1877F2", fg="white",
            activebackground="#145db2",
            bd=0, pady=5, padx=10, cursor="hand2",
            command=lambda: webbrowser.open(FB_PAGE)
        )
        btn_fb.pack(pady=8, padx=10, fill='x')

        # Tagi / opis
        tk.Label(
            sidebar,
            text="🏡 Agroturystyka\n🧀 Serowarnia\n🌾 Rolnictwo\n🐄 Hodowla",
            font=("Segoe UI", 8),
            bg=THEME["bg_panel"], fg=THEME["fg_dim"],
            justify="center"
        ).pack(pady=4)

        # Separator
        tk.Frame(sidebar, bg=THEME["fg_dim"], height=1).pack(fill='x', padx=10, pady=8)

        # Link do serowarni
        tk.Label(
            sidebar, text="mojaserowarnia.pl",
            font=("Segoe UI", 8, "underline"),
            bg=THEME["bg_panel"], fg=THEME["accent_blue"],
            cursor="hand2"
        ).pack()
        tk.Label(
            sidebar, text="🧀 Sklep online",
            font=("Segoe UI", 8),
            bg=THEME["bg_panel"], fg=THEME["fg_dim"]
        ).pack(pady=(0, 8))

        # Bind link serowarni
        sidebar.winfo_children()[-2].bind(
            "<Button-1>", lambda e: webbrowser.open("https://mojaserowarnia.pl")
        )

        # Załaduj zdjęcie profilowe (w tle)
        def laduj_zdjecie():
            if not PIL_AVAILABLE:
                return
            try:
                req = urllib.request.Request(
                    FB_PHOTO_URL,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                img = Image.open(BytesIO(data))
                img = img.resize((130, 130), Image.LANCZOS)
                # Okrągłe przycinanie
                mask = Image.new("L", (130, 130), 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 130, 130), fill=255)
                img_rgba = img.convert("RGBA")
                img_rgba.putalpha(mask)
                photo = ImageTk.PhotoImage(img_rgba)
                self._sidebar_photo_ref = photo
                self._sidebar_photo_frame.config(image=photo)
                self.log("🌿 Sidebar: zdjęcie Agrojelonek załadowane")
            except Exception as ex:
                self.log(f"⚠️ Sidebar: nie można załadować zdjęcia — {ex}")
                self._sidebar_photo_frame.config(text="🏡", font=("Segoe UI", 40))

        threading.Thread(target=laduj_zdjecie, daemon=True).start()

    def stworz_zakladke_log(self, parent):
        """Zakładka z logiem aplikacji w czasie rzeczywistym"""
        header_frame = tk.Frame(parent, bg=THEME["bg_main"])
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="📋 Application Log", font=THEME["font_header"],
                 bg=THEME["bg_main"], fg=THEME["fg_text"]).pack(side='left')
        
        tk.Button(header_frame, text="🗑 CLEAR LOG", 
                  command=self.clear_log,
                  bg=THEME["accent_red"], fg="white", bd=0, padx=10, pady=3).pack(side='right', padx=5)
        
        log_frame = tk.Frame(parent, bg=THEME["bg_main"])
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=THEME["font_mono"],
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            state='disabled',
            height=30
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Kolorowanie składni logu
        self.log_text.tag_configure("error", foreground="#ff5252")
        self.log_text.tag_configure("success", foreground="#69ff47")
        self.log_text.tag_configure("warning", foreground="#ffab40")
        self.log_text.tag_configure("info", foreground="#448aff")

    def clear_log(self):
        """Czyści log"""
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', 'end')
            self.log_text.config(state='disabled')

    def usun_fraze(self):
        selected_item = self.lista_frazy.selection()
        if not selected_item:
            return
        
        item = self.lista_frazy.item(selected_item)
        values = item['values']
        if not values: 
            return
            
        fraza = values[3] # Index 3 is phrase
        
        # Find index in list
        idx = -1
        for i, obj in enumerate(self.monitorowane_frazy):
            if obj['fraza'] == fraza:
                idx = i
                break
        
        if idx == -1: return

        if messagebox.askyesno(self.t("confirm"), f"{self.t('delete_phrase')}: {fraza}?"):
            del self.monitorowane_frazy[idx]
            self.zapisz_konfiguracje()
            self.odswiez_liste_gui()
            self.log(f"❌ {self.t('phrase_removed')}: {fraza}")

    def odswiez_liste_gui(self):
        # Clear tree
        for item in self.lista_frazy.get_children():
            self.lista_frazy.delete(item)
        
        for fraza_obj in self.monitorowane_frazy:
            prio = fraza_obj['priorytet']
            kat = fraza_obj.get('kategoria', 'Other')
            fraza = fraza_obj['fraza']
            ticker = fraza_obj.get('ticker', '')
            
            # Insert into tree
            self.lista_frazy.insert('', 'end', values=(prio, kat, ticker, fraza))
        
        self.label_licznik.config(text=f"{self.t('counter')} {len(self.monitorowane_frazy)}/{MAX_FRAZ}")

    def stworz_zakladke_zrodla(self, parent):
        # Statystyki źródeł
        stats_frame = tk.LabelFrame(parent, text=self.t("source_stats"), padx=10, pady=10,
                                   bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_header"])
        stats_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        self.label_source_stats = tk.Label(stats_frame, text="", justify='left',
                                           font=THEME["font_mono"], anchor='nw', bg=THEME["bg_panel"], fg=THEME["fg_text"])
        self.label_source_stats.pack(fill='both', expand=True)
        
        # Kontrolki źródeł
        controls_frame = tk.LabelFrame(parent, text=self.t("sources"), padx=10, pady=10,
                                      bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_header"])
        controls_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.source_vars = {}
        self.source_weight_entries = {}
        
        for source_name, source_config in self.sources_config.items():
            frame = tk.Frame(controls_frame, bg=THEME["bg_panel"])
            frame.pack(fill='x', pady=5)
            
            var = tk.BooleanVar(value=source_config['enabled'])
            self.source_vars[source_name] = var
            
            chk = tk.Checkbutton(frame, text=source_name, variable=var,
                                font=("Segoe UI", 10), bg=THEME["bg_panel"], fg=THEME["fg_text"], 
                                selectcolor=THEME["bg_input"], activebackground=THEME["bg_panel"])
            chk.pack(side='left')
            
            tk.Label(frame, text="Weight:", bg=THEME["bg_panel"], fg=THEME["fg_dim"]).pack(side='left', padx=(20, 5))
            entry = tk.Entry(frame, width=5, bg=THEME["bg_input"], fg=THEME["fg_text"], insertbackground="white")
            entry.insert(0, str(source_config['weight']))
            entry.pack(side='left')
            self.source_weight_entries[source_name] = entry
        
        # Przyciski
        btn_frame = tk.Frame(controls_frame, bg=THEME["bg_panel"])
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text=self.t("enable_all"), command=self.enable_all_sources,
                 bg=THEME["bg_panel"], fg=THEME["fg_text"], bd=0, padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text=self.t("disable_all"), command=self.disable_all_sources,
                 bg=THEME["bg_panel"], fg=THEME["fg_text"], bd=0, padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="💾 SAVE", command=self.save_sources_config,
                 bg=THEME["accent_blue"], fg="white", bd=0, padx=10).pack(side='left', padx=5)

    def stworz_zakladke_readme(self, parent):
        """Zakładka z instrukcją"""
        # Tytuł
        title_label = tk.Label(
            parent,
            text=self.t("readme_title"),
            font=THEME["font_header"],
            bg=THEME["bg_main"],
            fg=THEME["accent_blue"]
        )
        title_label.pack(pady=10)
        
        # Tekst instrukcji
        text_widget = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=THEME["font_mono"],
            bg=THEME["bg_panel"],
            fg=THEME["fg_text"],
            padx=10,
            pady=10,
            borderwidth=0
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', self.t("readme_content"))
        text_widget.config(state='disabled')  # Read-only

    def stworz_zakladke_wsparcie(self, parent):
        """Zakładka wsparcia projektu"""
        # Container centralny
        container = tk.Frame(parent, bg=THEME["bg_main"])
        container.pack(expand=True, fill='both')
        
        # Tytuł
        title_label = tk.Label(
            container,
            text=self.t("support_title"),
            font=("Segoe UI", 18, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["accent_gold"]
        )
        title_label.pack(pady=20)
        
        # Tekst wsparcia
        text_widget = tk.Text(
            container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg=THEME["bg_panel"],
            fg=THEME["fg_text"],
            height=15,
            width=60,
            padx=20,
            pady=20,
            relief=tk.FLAT,
            borderwidth=0
        )
        text_widget.pack(pady=10)
        text_widget.insert('1.0', self.t("support_content"))
        text_widget.config(state='disabled')
        
        # Przycisk "Kup mi kawę"
        coffee_btn = tk.Button(
            container,
            text=self.t("coffee_button"),
            command=self.open_coffee_link,
            font=("Segoe UI", 14, "bold"),
            bg="#FFDD00",
            fg="black",
            padx=30,
            pady=15,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        )
        coffee_btn.pack(pady=20)
        
        # Animacja hover
        def on_enter(e):
            coffee_btn['bg'] = '#FFE54C'
        
        def on_leave(e):
            coffee_btn['bg'] = '#FFDD00'
        
        coffee_btn.bind("<Enter>", on_enter)
        coffee_btn.bind("<Leave>", on_leave)
        
        # Dodatkowa informacja
        info_label = tk.Label(
            container,
            text="💚 " + self.t("thank_you") + " 💚",
            font=("Segoe UI", 10, "italic"),
            bg=THEME["bg_main"],
            fg=THEME["accent_green"]
        )
        info_label.pack(pady=10)

    def open_coffee_link(self):
        """Otwórz link do wsparcia"""
        webbrowser.open(COFFEE_LINK)
        self.log(f"☕ {self.t('coffee_button')} - {self.t('thank_you')}")

    def zmien_region(self, event=None):
        wybrana_nazwa = self.combo_region.get()
        self.wybrany_region_kod = REGIONY[wybrana_nazwa]
        self.log(f"Region changed to: {wybrana_nazwa}")

    def dodaj_fraze(self):
        fraza = self.entry_fraza.get().strip()
        if not fraza:
            return
        
        if len(self.monitorowane_frazy) >= MAX_FRAZ:
            messagebox.showwarning(self.t("warning"), self.t("max_phrases"))
            return
        
        if any(f['fraza'].lower() == fraza.lower() for f in self.monitorowane_frazy):
            messagebox.showwarning(self.t("warning"), self.t("phrase_exists"))
            return
        
        priorytet = self.combo_priorytet.get()
        kategoria = self.combo_kategoria.get()
        ticker = self.entry_ticker.get().strip().upper()  # Ticker zawsze uppercase
        
        filtry_poz = [f.strip() for f in self.entry_filtry_poz.get().split(',') if f.strip()]
        filtry_neg = [f.strip() for f in self.entry_filtry_neg.get().split(',') if f.strip()]
        
        try:
            min_sent = float(self.entry_min_sentiment.get())
            min_sent = max(-1.0, min(1.0, min_sent))
        except:
            min_sent = -1.0
        
        fraza_obj = {
            'fraza': fraza,
            'ticker': ticker,  # Dodany ticker
            'priorytet': priorytet,
            'kategoria': kategoria,
            'filtry_pozytywne': filtry_poz,
            'filtry_negatywne': filtry_neg,
            'min_sentiment': min_sent
        }
        
        self.monitorowane_frazy.append(fraza_obj)
        self.zapisz_konfiguracje()
        self.odswiez_liste_gui()
        
        self.entry_fraza.delete(0, tk.END)
        self.entry_ticker.delete(0, tk.END)
        self.entry_filtry_poz.delete(0, tk.END)
        self.entry_filtry_neg.delete(0, tk.END)
        
        self.log(f"✅ {self.t('phrase_added')}: {fraza} [{priorytet}]")

    def wymusz_skanowanie(self):
        self.wymuszenie_skanowania = True
        self.log(f"🔍 {self.t('scan_now')}...")

    def pauza_skanowania(self):
        self.skanowanie_aktywne = False
        self.log(f"⏸ {self.t('pause')}")

    def wznow_skanowania(self):
        self.skanowanie_aktywne = True
        self.log(f"▶ {self.t('resume')}")

    def importuj_frazy(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'frazy' in data:
                    self.monitorowane_frazy = data['frazy'][:MAX_FRAZ]
                    self.zapisz_konfiguracje()
                    self.odswiez_liste_gui()
                    messagebox.showinfo(self.t("success"), f"{self.t('import_success')}: {len(self.monitorowane_frazy)}")
                    self.log(f"📥 {self.t('import_success')}: {filepath}")
        except Exception as e:
            messagebox.showerror(self.t("error"), str(e))

    def eksportuj_frazy(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"radar_phrases_{datetime.now().strftime('%Y%m%d')}.json"
        )
        if not filepath:
            return
        
        try:
            data = {'frazy': self.monitorowane_frazy}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo(self.t("success"), f"{self.t('export_success')}: {filepath}")
            self.log(f"📤 {self.t('export_success')}: {filepath}")
        except Exception as e:
            messagebox.showerror(self.t("error"), str(e))

    def enable_all_sources(self):
        for var in self.source_vars.values():
            var.set(True)

    def disable_all_sources(self):
        for var in self.source_vars.values():
            var.set(False)

    def save_sources_config(self):
        for source_name, var in self.source_vars.items():
            self.sources_config[source_name]['enabled'] = var.get()
            try:
                weight = float(self.source_weight_entries[source_name].get())
                self.sources_config[source_name]['weight'] = max(0.1, min(10.0, weight))
            except:
                pass
        
        self.zapisz_konfiguracje()
        messagebox.showinfo(self.t("success"), "Sources configuration saved!")
        self.log("💾 Sources config saved")

    def log(self, message):
        """Log do GUI (ScrolledText) i konsoli"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted = f"[{timestamp}] {message}\n"
        print(formatted, end="")
        # Zapisz do GUI log widget jeśli istnieje
        try:
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.config(state='normal')
                self.log_text.insert('end', formatted)
                self.log_text.see('end')  # Auto-scroll do końca
                self.log_text.config(state='disabled')
                # Ogranicz do 500 linii żeby nie puchnąć
                lines = int(self.log_text.index('end-1c').split('.')[0])
                if lines > 500:
                    self.log_text.config(state='normal')
                    self.log_text.delete('1.0', f'{lines-400}.0')
                    self.log_text.config(state='disabled')
        except Exception:
            pass


    def log_status(self, message):
        """Log noise/status updates to status bar only"""
        self.status_bar.config(text=str(message))
        self.root.update_idletasks()

    def wczytaj_konfiguracje(self):
        if os.path.exists(PLIK_KONFIGURACJI):
            try:
                with open(PLIK_KONFIGURACJI, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.monitorowane_frazy = data.get('frazy', [])
                    
                    # Merge loaded sources with defaults to ensure new sources appear
                    loaded_sources = data.get('sources', {})
                    # Start with defaults
                    self.sources_config = SOURCES.copy()
                    # Update with loaded values where they exist
                    for name, config in loaded_sources.items():
                        if name in self.sources_config:
                            self.sources_config[name].update(config)
                        else:
                             # Optionally keep old sources that are not in defaults anymore?
                             # For now, let's keep strictly what's in defaults + user settings for them.
                             # If user had custom source structure, it might be lost if we only use keys from SOURCES.
                             # But this app doesn't allow adding custom source definitions in UI, only enabling/disabling defined ones.
                             pass
                             
                    self.current_lang = data.get('language', 'pl')
            except Exception as e:
                print(f"Config load error: {e}")

    def zapisz_konfiguracje(self):
        data = {
            'frazy': self.monitorowane_frazy,
            'sources': self.sources_config,
            'language': self.current_lang
        }
        try:
            with open(PLIK_KONFIGURACJI, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")

    def wczytaj_historie(self):
        if os.path.exists(PLIK_HISTORII):
            try:
                with open(PLIK_HISTORII, 'r', encoding='utf-8') as f:
                    self.historia_newsow = json.load(f)
            except Exception as e:
                print(f"History load error: {e}")
        
        # Zbuduj cache tytułów
        self.known_titles = {dane['tytul'] for dane in self.historia_newsow.values()}

    def zapisz_historie(self):
        try:
            with open(PLIK_HISTORII, 'w', encoding='utf-8') as f:
                json.dump(self.historia_newsow, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"History save error: {e}")

    def dodaj_do_historii(self, link, tytul, fraza_obj, sentiment_polarity, sentiment_label, source):
        if link not in self.historia_newsow:
            self.historia_newsow[link] = {
                'tytul': tytul,
                'fraza': fraza_obj['fraza'],
                'priorytet': fraza_obj['priorytet'],
                'kategoria': fraza_obj['kategoria'],
                'timestamp': datetime.now().isoformat(),
                'sentiment_polarity': sentiment_polarity,
                'sentiment_label': sentiment_label,
                'source': source,
                'region': self.combo_region.get()
            }
            self.known_titles.add(tytul)
            self.zapisz_historie()
            
            # Odśwież preview jeśli dodano newsa do aktualnie wybranej frazy
            selected = self.lista_frazy.selection()
            if selected:
                item = self.lista_frazy.item(selected)
                curr_fraza = item['values'][3]
                if curr_fraza == fraza_obj['fraza']:
                    self.pokaz_newsy_dla_frazy(None)

    def pokaz_newsy_dla_frazy(self, event):
        selected = self.lista_frazy.selection()
        if not selected:
            return
            
        item = self.lista_frazy.item(selected)
        values = item['values']
        if not values: return
        
        fraza = values[3]
        
        # Wyczyść
        for row in self.preview_news.get_children():
            self.preview_news.delete(row)
            
        # Znajdź newsy dla tej frazy
        newsy = []
        for link, dane in self.historia_newsow.items():
            if dane.get('fraza') == fraza:
                newsy.append((link, dane))
        
        # Sortuj (najnowsze)
        newsy.sort(key=lambda x: x[1]['timestamp'], reverse=True)
        
        # Pokaż top 5
        for link, dane in newsy[:5]:
            dt = dane['timestamp'][:16].replace('T', ' ')
            sent = dane.get('sentiment_label', 'N/A')
            src = dane.get('source', '?')
            title = dane['tytul']
            self.preview_news.insert('', 'end', values=(dt, title, src, sent), tags=(link,))

    def otworz_link_z_preview(self, event):
        selected = self.preview_news.selection()
        if not selected:
            return
        item = self.preview_news.item(selected)
        link = item['tags'][0]
        webbrowser.open(link)

    def wyslij_powiadomienie(self, link, tytul, tresc, priorytet, sentiment_polarity, sentiment_label, source):
        # CRITICAL i HIGH zawsze powiadamiają - złe newsy też są ważne!
        # MEDIUM i LOW tylko dla POSITIVE sentiment (żeby nie zalewać alertami)
        if not SENTIMENT_AVAILABLE:
            # Bez sentymentu - powiadamiaj tylko CRITICAL i HIGH
            if priorytet not in ("CRITICAL", "HIGH"):
                return
        else:
            if priorytet in ("MEDIUM", "LOW") and sentiment_label != "POSITIVE":
                return

        try:
            dzwiek = PRIORYTETY[priorytet]['dzwiek']
            
            if sentiment_label == "POSITIVE":
                sent_emoji = "📈"
            elif sentiment_label == "NEGATIVE":
                sent_emoji = "📉"
            else:
                sent_emoji = "📰"
            
            notification = Notification(
                app_id="Investment Radar",
                title=f"{priorytet} | {source}",
                msg=f"{sent_emoji} {sentiment_label} ({sentiment_polarity:+.2f})\n\n{tytul}\n\n{tresc}",
                duration="long",
                launch=link,
                icon=""
            )
            notification.add_actions(label="Open News", launch=link)
            
            notification.set_audio(dzwiek, loop=False)
            notification.show()
        except Exception as e:
            self.log(f"Notification error: {e}")

    def monitoruj_burst(self):
        """Monitoruj burst detection"""
        while True:
            time.sleep(60)
            
            if not self.skanowanie_aktywne:
                continue
            
            teraz = datetime.now()
            
            for fraza_obj in self.monitorowane_frazy:
                fraza = fraza_obj['fraza']
                events = self.burst_tracker.get(fraza, [])
                
                # Usuń stare eventy
                recent_events = [e for e in events if (teraz - e['timestamp']).total_seconds() < BURST_WINDOW]
                self.burst_tracker[fraza] = recent_events
                
                # Sprawdź burst
                if len(recent_events) >= BURST_THRESHOLD:
                    # Sprawdź czy już było powiadomienie o burst
                    last_burst = fraza_obj.get('last_burst_notification')
                    if not last_burst or (teraz - datetime.fromisoformat(last_burst)).total_seconds() > 3600:
                        msg = f"🔥 BURST: {fraza} — {len(recent_events)} newsów w {BURST_WINDOW//60} min!"
                        self.log(msg)
                        fraza_obj['last_burst_notification'] = teraz.isoformat()
                        # Windows toast dla burstu
                        try:
                            notif = Notification(
                                app_id="Investment Radar",
                                title=f"🔥 BURST ALERT — {fraza}",
                                msg=f"{len(recent_events)} newsów w ostatnich {BURST_WINDOW//60} minutach!",
                                duration="long"
                            )
                            notif.set_audio(audio.Reminder, loop=False)
                            notif.show()
                        except Exception as e:
                            self.log(f"Burst notification error: {e}")

    def petla_countdown(self):
        """Aktualizuje status bar z countdown do następnego skanu"""
        while True:
            try:
                if self.next_scan_time and self.skanowanie_aktywne:
                    remaining = self.next_scan_time - datetime.now().timestamp()
                    if remaining > 0:
                        mins = int(remaining // 60)
                        secs = int(remaining % 60)
                        self.status_bar.config(
                            text=f"{self.t('status')} {self.t('idle')} | ⏱ Następny skan za: {mins:02d}:{secs:02d}"
                        )
            except Exception:
                pass
            time.sleep(1)

    def petla_radaru(self):
        """Główna pętla skanowania"""
        while True:
            try:
                if not self.skanowanie_aktywne:
                    time.sleep(5)
                    continue
                
                start_time = datetime.now().timestamp()
                self.status_bar.config(text=f"{self.t('status')} {self.t('scanning')}...")
                
                # --- PRE-FETCH GENERAL FEEDS ---
                general_feeds_cache = {}
                for source_name, config in self.sources_config.items():
                    if not config['enabled']: continue
                    if config['type'] in ['prnewswire', 'general']:
                        try:
                            self.log(f"  → Pre-fetching {source_name}...")
                            feed = feedparser.parse(config['base_url'])
                            status = getattr(feed, 'status', 0)
                            if status and status not in (200, 301, 302):
                                self.log(f"  ⚠️ {source_name}: HTTP {status}")
                                general_feeds_cache[source_name] = []
                            elif feed.bozo and not feed.entries:
                                self.log(f"  ⚠️ {source_name}: Feed error — {getattr(feed, 'bozo_exception', 'unknown')}")
                                general_feeds_cache[source_name] = []
                            else:
                                general_feeds_cache[source_name] = feed.entries
                                self.log(f"  ✅ {source_name}: pobrano {len(feed.entries)} artykułów")
                        except Exception as e:
                            self.log(f"❌ Error pre-fetching {source_name}: {e}")
                            general_feeds_cache[source_name] = []

                for idx, fraza_obj in enumerate(self.monitorowane_frazy):
                    if not self.skanowanie_aktywne:
                        break
                    
                    fraza = fraza_obj['fraza']
                    ticker = fraza_obj.get('ticker', '')
                    priorytet = fraza_obj['priorytet']
                    
                    self.log_status(f"🔍 {self.t('scanning_progress')}: {fraza} [{priorytet}]")
                    source_hits = {}  # źródło -> liczba nowych newsów
                    
                    # Scan z różnych źródeł
                    for source_name, source_config in self.sources_config.items():
                        if not source_config['enabled']:
                            continue
                        
                        entries_to_process = []
                        
                        # --- 1. SEARCH-BASED SOURCES (Google, Yahoo, SA) ---
                        if source_config['type'] in ['google', 'yahoo', 'seekingalpha']:
                            url = None
                            
                            if source_config['type'] == 'google':
                                fraza_encoded = urllib.parse.quote_plus(fraza)
                                url = f"https://news.google.com/rss/search?q={fraza_encoded}&{self.wybrany_region_kod}"
                            elif source_config['type'] == 'yahoo':
                                if not ticker: continue
                                url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
                            elif source_config['type'] == 'seekingalpha':
                                if not ticker: continue
                                url = f"https://seekingalpha.com/symbol/{ticker}.xml"
                            
                            if url:
                                try:
                                    self.log_status(f"  → Scanning {source_name} [{fraza}]...")
                                    feed = feedparser.parse(url)
                                    status = getattr(feed, 'status', 0)
                                    if status and status not in (200, 301, 302):
                                        self.log(f"  ⚠️ {source_name} [{fraza}]: HTTP {status} — zablokowany lub niedostępny")
                                        entries_to_process = []
                                    elif feed.bozo and not feed.entries:
                                        self.log(f"  ⚠️ {source_name} [{fraza}]: Feed error — {getattr(feed, 'bozo_exception', 'unknown')}")
                                        entries_to_process = []
                                    else:
                                        entries_to_process = feed.entries[:5]
                                except Exception as e:
                                    self.log(f"❌ Error scanning {source_name}: {e}")
                        
                        # --- 2. GENERAL FEEDS (PR Newswire, MarketWatch, CNBC - phrase matching) ---
                        elif source_config['type'] in ['prnewswire', 'general']:
                            cached_entries = general_feeds_cache.get(source_name, [])
                            no_match_titles = []
                            for news in cached_entries:
                                content_to_check = (news.title + " " + news.get('summary', '')).lower()
                                match = fraza.lower() in content_to_check
                                if not match and ticker:
                                    match = bool(re.search(r'\b' + re.escape(ticker.lower()) + r'\b', content_to_check))
                                if match:
                                    entries_to_process.append(news)
                                else:
                                    no_match_titles.append(news.title[:50])
                            
                            if not entries_to_process and cached_entries:
                                # Diagnostic: pokaż sample co jest w feedzie
                                sample = " | ".join(no_match_titles[:3])
                                self.log(f"  ○ {source_name} [{fraza}]: brak matchów w {len(cached_entries)} art. Sample: {sample}")
                        
                        # --- 3. OPENINSIDER (insider trading RSS) ---
                        elif source_config['type'] == 'openinsider':
                            if not ticker:
                                continue
                            try:
                                url = source_config['base_url'].format(ticker=ticker)
                                self.log_status(f"  → Scanning OpenInsider ({ticker})...")
                                feed = feedparser.parse(url)
                                status = getattr(feed, 'status', 0)
                                if status and status not in (200, 301, 302):
                                    self.log(f"  ⚠️ OpenInsider [{ticker}]: HTTP {status}")
                                    entries_to_process = []
                                else:
                                    entries_to_process = feed.entries[:10]
                                    if entries_to_process:
                                        self.log(f"  📊 OpenInsider [{ticker}]: {len(entries_to_process)} transakcji insiderów")
                            except Exception as e:
                                self.log(f"❌ Error scanning OpenInsider: {e}")
                        
                        # --- PROCESS FOUND ENTRIES ---
                        if entries_to_process:
                             # Limit processing if too many matches from general feed? 
                             # Let's verify up to 10 latest matches
                             for news in entries_to_process[:10]:
                                # Sprawdź duplikaty (link lub tytuł)
                                if news.link in self.historia_newsow:
                                    continue
                                
                                if news.title in self.known_titles:
                                    continue
                                
                                # Filtry pozytywne
                                if fraza_obj.get('filtry_pozytywne'):
                                    if not any(filtr.lower() in news.title.lower() or filtr.lower() in news.get('summary', '').lower()
                                             for filtr in fraza_obj['filtry_pozytywne']):
                                        continue
                                
                                # Filtry negatywne
                                if fraza_obj.get('filtry_negatywne'):
                                    if any(filtr.lower() in news.title.lower() or filtr.lower() in news.get('summary', '').lower()
                                          for filtr in fraza_obj['filtry_negatywne']):
                                        continue
                                
                                # Sentiment
                                sentiment_polarity = 0.0
                                sentiment_label = "NEUTRAL"
                                
                                if SENTIMENT_AVAILABLE:
                                    try:
                                        blob = TextBlob(news.title + " " + news.get('summary', ''))
                                        sentiment_polarity = blob.sentiment.polarity
                                        
                                        if sentiment_polarity > 0.1:
                                            sentiment_label = "POSITIVE"
                                        elif sentiment_polarity < -0.1:
                                            sentiment_label = "NEGATIVE"
                                        
                                        # Sprawdź min sentiment
                                        if sentiment_polarity < fraza_obj.get('min_sentiment', -1.0):
                                            continue
                                    except:
                                        pass
                                
                                # Burst tracking
                                self.burst_tracker[fraza].append({
                                    'timestamp': datetime.now(),
                                    'link': news.link
                                })
                                
                                # Powiadomienie
                                self.log(f"📰 NEW [{source_name}]: {news.title[:60]}... [{sentiment_label}]")
                                source_hits[source_name] = source_hits.get(source_name, 0) + 1
                                
                                # Pass Link to notification
                                self.wyslij_powiadomienie(news.link, news.title, news.get('summary', '')[:200],
                                                         priorytet, sentiment_polarity, sentiment_label, source_name)
                                
                                self.dodaj_do_historii(news.link, news.title, fraza_obj,
                                                      sentiment_polarity, sentiment_label, source_name)
                    
                    # Podsumowanie frazy
                    if source_hits:
                        summary = " | ".join(f"{src}: {n}" for src, n in source_hits.items())
                        self.log(f"  📊 [{fraza}] nowe newsy → {summary}")
                    else:
                        self.log(f"  ○ [{fraza}] brak nowych newsów")
                    
                    time.sleep(1) # Small delay between phrases
                
                self.log(f"✅ Scan cycle complete. Waiting 10 min...")
                self.odswiez_statystyki()
                self.status_bar.config(text=f"{self.t('status')} {self.t('idle')}")
                
                # Czekaj na następny cykl
                next_scan = start_time + INTERVAL
                self.next_scan_time = next_scan  # dla countdown
                while datetime.now().timestamp() < next_scan:
                    if self.wymuszenie_skanowania:
                        self.wymuszenie_skanowania = False
                        break
                    time.sleep(1)
                    if not self.skanowanie_aktywne:
                        break
            
            except Exception as e:
                self.log(f"❌ Loop error: {e}")
                time.sleep(60)

    def stworz_zakladke_historia(self, parent):
        # Statystyki
        stats_frame = tk.LabelFrame(parent, text=self.t("statistics"), padx=10, pady=10,
                                   bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_header"])
        stats_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        self.label_stats = tk.Label(stats_frame, text="", justify='left', 
                                    font=THEME["font_mono"], anchor='nw', bg=THEME["bg_panel"], fg=THEME["fg_text"])
        self.label_stats.pack(fill='both', expand=True)
        
        # Tree historia
        tree_frame = tk.Frame(parent, bg=THEME["bg_main"])
        tree_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # --- Date Filter UI ---
        filter_frame = tk.Frame(tree_frame, bg=THEME["bg_main"])
        filter_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(filter_frame, text="From Date (YYYY-MM-DD):", bg=THEME["bg_main"], fg=THEME["fg_text"]).pack(side='left', padx=5)
        self.entry_history_from_date = tk.Entry(filter_frame, width=12)
        self.entry_history_from_date.pack(side='left', padx=5)
        
        tk.Button(filter_frame, text="FILTER", command=self.filter_history,
                 bg=THEME["accent_blue"], fg="white", bd=0, padx=10).pack(side='left', padx=5)
        tk.Button(filter_frame, text="CLEAR", command=self.clear_filter,
                 bg=THEME["bg_panel"], fg=THEME["fg_text"], bd=0, padx=10).pack(side='left', padx=5)
        # ----------------------

        tk.Label(tree_frame, text=self.t("history_100"), font=THEME["font_header"], 
                 bg=THEME["bg_main"], fg=THEME["fg_text"]).pack()
        
        self.tree_historia = ttk.Treeview(tree_frame, columns=(
            "time", "priority", "phrase", "sentiment", "source", "title"
        ), show='headings', height=25)
        
        # Bind headings for sorting
        for col in ["time", "priority", "phrase", "sentiment", "source", "title"]:
            self.tree_historia.heading(col, text=col.capitalize(), 
                command=lambda c=col: self.sort_treeview(c))
        
        self.tree_historia.heading("time", text=self.t("date_time"))
        self.tree_historia.heading("priority", text=self.t("priority"))
        self.tree_historia.heading("phrase", text=self.t("phrase"))
        self.tree_historia.heading("sentiment", text="Sentiment")
        self.tree_historia.heading("source", text=self.t("source"))
        self.tree_historia.heading("title", text=self.t("title_col"))
        
        self.tree_historia.column("time", width=130)
        self.tree_historia.column("priority", width=80)
        self.tree_historia.column("phrase", width=120)
        self.tree_historia.column("sentiment", width=70)
        self.tree_historia.column("source", width=120)
        self.tree_historia.column("title", width=300)
        
        scroll_tree = ttk.Scrollbar(tree_frame, command=self.tree_historia.yview)
        scroll_tree.pack(side='right', fill='y')
        self.tree_historia.config(yscrollcommand=scroll_tree.set)
        self.tree_historia.pack(fill='both', expand=True)
        
        self.tree_historia.bind('<Double-1>', self.otworz_link_z_historii)
        
        # Przyciski
        btn_frame = tk.Frame(tree_frame, bg=THEME["bg_main"])
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text=self.t("export_csv"), command=self.eksport_csv,
                 bg=THEME["bg_panel"], fg=THEME["fg_text"], bd=0, padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text=self.t("clear_history"), command=self.czyszcz_historie,
                 bg=THEME["accent_red"], fg="white", bd=0, padx=10).pack(side='left', padx=5)

    def sort_treeview(self, col):
        """Sortuje historię po kliknięciu w kolumnę"""
        if self.history_sort_col == col:
            self.history_sort_reverse = not self.history_sort_reverse
        else:
            self.history_sort_col = col
            self.history_sort_reverse = False  # Default asc for new col? Or desc? Let's say asc.
            
        self.odswiez_statystyki()

    def filter_history(self):
        """Filtruje historię po dacie"""
        date_str = self.entry_history_from_date.get().strip()
        if not date_str:
            return

        try:
            # Parse YYYY-MM-DD
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            self.history_from_date = dt
            self.odswiez_statystyki()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")

    def clear_filter(self):
        """Czyści filtr daty"""
        self.entry_history_from_date.delete(0, tk.END)
        self.history_from_date = None
        self.odswiez_statystyki()

    def odswiez_statystyki(self):
        """Odświeża statystyki"""
        total = len(self.historia_newsow)
        
        dzisiaj = datetime.now().date()
        dzis_count = sum(1 for dane in self.historia_newsow.values()
                        if datetime.fromisoformat(dane['timestamp']).date() == dzisiaj)
        
        # Po priorytetach
        prio_counts = {}
        for dane in self.historia_newsow.values():
            prio = dane['priorytet']
            prio_counts[prio] = prio_counts.get(prio, 0) + 1
        
        # TOP frazy
        fraza_counts = {}
        for dane in self.historia_newsow.values():
            fraza = dane['fraza']
            fraza_counts[fraza] = fraza_counts.get(fraza, 0) + 1
        
        top_frazy = sorted(fraza_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Średni sentiment
        sentiments = [dane.get('sentiment_polarity', 0) for dane in self.historia_newsow.values()]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        # Burst info
        active_bursts = []
        teraz = datetime.now()
        for fraza, events in self.burst_tracker.items():
            recent = [e for e in events if (teraz - e['timestamp']).total_seconds() < BURST_WINDOW]
            if len(recent) >= BURST_THRESHOLD:
                active_bursts.append(f"{fraza} ({len(recent)})")
        
        # Formatowanie
        tekst = f"{self.t('statistics')}\n\n"
        tekst += f"• {self.t('total_news')} {total}\n"
        tekst += f"• {self.t('today')} {dzis_count}\n"
        tekst += f"• {self.t('avg_sentiment')} {avg_sentiment:+.2f}\n\n"
        
        tekst += f"{self.t('by_priority')}\n"
        for prio in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = prio_counts.get(prio, 0)
            tekst += f"  • {prio}: {count}\n"
        
        tekst += f"\n{self.t('top_5')}\n"
        for fraza, count in top_frazy:
            tekst += f"  • {fraza}: {count}\n"
        
        if active_bursts:
            tekst += f"\n{self.t('active_bursts')}\n"
            for burst in active_bursts:
                tekst += f"  • {burst}\n"
        
        self.label_stats.config(text=tekst)
        
        # Odśwież tree
        self.tree_historia.delete(*self.tree_historia.get_children())
        
        # Przygotuj listę do wyświetlenia
        display_items = []
        for link, dane in self.historia_newsow.items():
            # Filtr daty
            if self.history_from_date:
                item_dt = datetime.fromisoformat(dane['timestamp'])
                if item_dt < self.history_from_date:
                    continue
            
            display_items.append((link, dane))
            
        # Sortowanie
        # map column name to sort key
        key_map = {
            "time": lambda x: x[1]['timestamp'],
            "priority": lambda x: x[1]['priorytet'],
            "phrase": lambda x: x[1]['fraza'],
            "sentiment": lambda x: x[1].get('sentiment_polarity', 0.0),
            "source": lambda x: x[1].get('source', ''),
            "title": lambda x: x[1]['title'] # bug fix below: tytul vs title? In dict it is 'tytul'
        }
        
        # Fix sort key for title because dict key is 'tytul' but col is 'title'
        # Also handle potential missing keys safely
        def get_sort_key(item):
            link, dane = item
            col = self.history_sort_col
            if col == 'time': return dane.get('timestamp', '')
            if col == 'priority': return dane.get('priorytet', '')
            if col == 'phrase': return dane.get('fraza', '')
            if col == 'sentiment': return dane.get('sentiment_polarity', 0.0)
            if col == 'source': return dane.get('source', '')
            if col == 'title': return dane.get('tytul', '')
            return ''

        historia_sorted = sorted(display_items, key=get_sort_key, reverse=self.history_sort_reverse)
        
        # Show all items respecting filter (or maybe limit to match previous logic? Requirement says "filter records", likely implies showing all that match)
        # But previous code had [:100]. Let's keep a reasonable limit or show all? 
        # User requirement: "History: sort ... filter ... limit results" not explicitly stated 100 limit, but generally good practice.
        # But if filtering, user probably wants to see older stuff. Let's increase limit or remove it for filtered view.
        # Let's show max 500 to prevent ui lag if list is huge.
        
        for link, dane in historia_sorted[:500]:
            czas = datetime.fromisoformat(dane['timestamp']).strftime('%Y-%m-%d %H:%M')
            sent = dane.get('sentiment_polarity', 0.0)
            sent_str = f"{sent:+.2f}"
            
            self.tree_historia.insert('', 'end', values=(
                czas,
                dane['priorytet'],
                dane['fraza'][:20],
                sent_str,
                dane.get('source', 'N/A')[:15],
                dane['tytul'][:50]
            ), tags=(link,))
        
        # Odśwież statystyki źródeł
        self.odswiez_statystyki_zrodel()

    def odswiez_statystyki_zrodel(self):
        """Odświeża statystyki źródeł"""
        source_counts = defaultdict(int)
        source_sentiments = defaultdict(list)
        
        for dane in self.historia_newsow.values():
            source = dane.get('source', 'Unknown')
            source_counts[source] += 1
            source_sentiments[source].append(dane.get('sentiment_polarity', 0.0))
        
        tekst = f"{self.t('source_stats')}\n\n"
        
        for source in ["Google News", "Yahoo Finance", "Seeking Alpha", "PR Newswire", "OpenInsider", "Unknown"]:
            count = source_counts.get(source, 0)
            sentiments = source_sentiments.get(source, [])
            avg_sent = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            tekst += f"• {source}:\n"
            tekst += f"  - {self.t('news_count')} {count}\n"
            tekst += f"  - {self.t('avg_sentiment')} {avg_sent:+.2f}\n\n"
        
        self.label_source_stats.config(text=tekst)

    def otworz_link_z_historii(self, event):
        """Otwórz link po double-click"""
        selected = self.tree_historia.selection()
        if selected:
            item = self.tree_historia.item(selected[0])
            link = item['tags'][0]
            webbrowser.open(link)

    def eksport_csv(self):
        """Eksportuj historię do CSV"""
        if not self.historia_newsow:
            messagebox.showinfo(self.t("info"), "History is empty")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"radar_history_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([self.t("date_time"), self.t("priority"), self.t("category"), 
                               self.t("phrase"), "Sentiment", "Sentiment_Label", self.t("source"),
                               self.t("title_col"), "Link", "Region"])
                
                for link, dane in self.historia_newsow.items():
                    writer.writerow([
                        dane['timestamp'],
                        dane['priorytet'],
                        dane['kategoria'],
                        dane['fraza'],
                        dane.get('sentiment_polarity', 0.0),
                        dane.get('sentiment_label', 'NEUTRAL'),
                        dane.get('source', 'N/A'),
                        dane['tytul'],
                        link,
                        dane.get('region', 'N/A')
                    ])
            
            messagebox.showinfo(self.t("success"), f"{self.t('export_success')}: {len(self.historia_newsow)}")
            self.log(f"💾 CSV export: {filepath}")
            
        except Exception as e:
            messagebox.showerror(self.t("error"), f"Export failed:\n{e}")

    def czyszcz_historie(self):
        """Usuń newsy starsze niż 30 dni"""
        if not self.historia_newsow:
            messagebox.showinfo(self.t("info"), "History is empty")
            return
        
        if not messagebox.askyesno(self.t("confirm"), self.t("confirm_clear")):
            return
        
        granica = datetime.now() - timedelta(days=30)
        przed = len(self.historia_newsow)
        
        self.historia_newsow = {
            link: dane for link, dane in self.historia_newsow.items()
            if datetime.fromisoformat(dane['timestamp']) > granica
        }
        
        po = len(self.historia_newsow)
        usuniete = przed - po
        
        self.zapisz_historie()
        
        # Odbuduj cache tytułów
        self.known_titles = {dane['tytul'] for dane in self.historia_newsow.values()}
        
        self.odswiez_statystyki()
        
        messagebox.showinfo(self.t("info"), f"{self.t('history_cleared')}: {usuniete}")
        self.log(f"🗑️ Cleaned: {usuniete} entries")

if __name__ == "__main__":
    root = tk.Tk()
    app = RadarApp(root)
    root.mainloop()


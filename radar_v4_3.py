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

# Sentiment Analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("TextBlob not installed. Run: pip install textblob")

# --- KONFIGURACJA GLOBALNA ---
PLIK_KONFIGURACJI = "radar_config_v43.json"
PLIK_HISTORII = "radar_historia_v43.json"
MAX_FRAZ = 20
INTERVAL = 600  # 10 minut
BURST_WINDOW = 900  # 15 minut w sekundach
BURST_THRESHOLD = 3  # Minimum newsów do uznania za burst
COFFEE_LINK = "https://buymeacoffee.com/kitay"  # Zmień na swój link!

# --- TRANSLATIONS / TŁUMACZENIA ---
TRANSLATIONS = {
    "pl": {
        # Tytuł i główne
        "title": "Radar Inwestora v4.3 PRO - Multi-language",
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
        "title": "Investment Radar v4.3 PRO - Multi-language",
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
PRIORYTETY = {
    "CRITICAL": {"kolor": "#ff0000", "bg": "#ffe6e6", "dzwiek": audio.LoopingAlarm},
    "HIGH": {"kolor": "#ff6600", "bg": "#fff0e6", "dzwiek": audio.Reminder},
    "MEDIUM": {"kolor": "#0066cc", "bg": "#e6f2ff", "dzwiek": audio.Default},
    "LOW": {"kolor": "#666666", "bg": "#f5f5f5", "dzwiek": audio.SMS}
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
        
        # Wczytaj język z konfiguracji (jeśli istnieje)
        self.wczytaj_konfiguracje()
        
        # Ustaw tytuł
        self.root.title(self.t("title"))
        self.root.geometry("1000x950")
        
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
        self.thread = threading.Thread(target=self.petla_radaru, daemon=True)
        self.thread.start()
        
        self.burst_thread = threading.Thread(target=self.monitoruj_burst, daemon=True)
        self.burst_thread.start()
    
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
        top_frame = tk.Frame(self.root, bg="#f0f0f0", height=40)
        top_frame.pack(fill='x', side='top')
        top_frame.pack_propagate(False)
        
        lang_btn = tk.Button(
            top_frame, 
            text=f"🌐 {'EN' if self.current_lang == 'pl' else 'PL'}",
            command=self.switch_language,
            font=("Arial", 9, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        )
        lang_btn.pack(side='right', padx=10, pady=5)
        
        tk.Label(
            top_frame, 
            text="Investment Radar v4.3 PRO",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        ).pack(side='left', padx=10)
        
        # Notebook dla zakładek
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
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

    def stworz_zakladke_monitoring(self, parent):
        # Ustawienia regionu
        frame_settings = tk.LabelFrame(parent, text=self.t("region_settings"), padx=10, pady=5)
        frame_settings.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_settings, text=self.t("search_in")).pack(side='left')
        
        self.combo_region = ttk.Combobox(frame_settings, values=list(REGIONY.keys()), 
                                         state="readonly", width=20)
        self.combo_region.current(1)  # USA domyślnie
        self.combo_region.pack(side='left', padx=10)
        self.combo_region.bind("<<ComboboxSelected>>", self.zmien_region)

        # Dodawanie frazy
        frame_input = tk.LabelFrame(parent, text=self.t("add_phrase"), padx=10, pady=5)
        frame_input.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_input, text=self.t("phrase")).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_fraza = tk.Entry(frame_input, width=25)
        self.entry_fraza.grid(row=0, column=1, padx=5, pady=2)
        self.entry_fraza.bind('<Return>', lambda e: self.dodaj_fraze())
        
        tk.Label(frame_input, text=self.t("ticker")).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_ticker = tk.Entry(frame_input, width=10)
        self.entry_ticker.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        tk.Label(frame_input, text=self.t("ticker_hint"), font=("Arial", 8)).grid(row=1, column=1, sticky='e', padx=5)
        
        tk.Label(frame_input, text=self.t("priority")).grid(row=0, column=2, sticky='w', padx=5)
        self.combo_priorytet = ttk.Combobox(frame_input, values=list(PRIORYTETY.keys()), 
                                            state="readonly", width=10)
        self.combo_priorytet.current(2)  # MEDIUM
        self.combo_priorytet.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_input, text=self.t("category")).grid(row=0, column=4, sticky='w', padx=5)
        self.combo_kategoria = ttk.Combobox(frame_input, values=self.get_categories(), 
                                            state="readonly", width=12)
        self.combo_kategoria.current(0)
        self.combo_kategoria.grid(row=0, column=5, padx=5)
        
        # Filtry
        tk.Label(frame_input, text=self.t("filters_pos")).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_filtry_poz = tk.Entry(frame_input, width=25)
        self.entry_filtry_poz.grid(row=2, column=1, padx=5, pady=2)
        tk.Label(frame_input, text=self.t("separate_commas")).grid(row=2, column=2, columnspan=2, sticky='w')
        
        tk.Label(frame_input, text=self.t("filters_neg")).grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.entry_filtry_neg = tk.Entry(frame_input, width=25)
        self.entry_filtry_neg.grid(row=3, column=1, padx=5, pady=2)
        tk.Label(frame_input, text=self.t("exclude_words")).grid(row=3, column=2, columnspan=2, sticky='w')
        
        tk.Label(frame_input, text=self.t("min_sentiment")).grid(row=3, column=4, sticky='w', padx=5)
        self.entry_min_sentiment = tk.Entry(frame_input, width=8)
        self.entry_min_sentiment.insert(0, "-1.0")
        self.entry_min_sentiment.grid(row=3, column=5, padx=5)
        tk.Label(frame_input, text="(-1.0 to 1.0)").grid(row=3, column=6, sticky='w')
        
        btn_dodaj = tk.Button(frame_input, text=self.t("add_phrase_btn"), command=self.dodaj_fraze, 
                             bg="#90EE90", font=("Arial", 9, "bold"))
        btn_dodaj.grid(row=0, column=6, rowspan=3, padx=10, pady=5)

        # Licznik
        self.label_licznik = tk.Label(parent, text=f"{self.t('counter')} 0/{MAX_FRAZ}", 
                                     font=("Arial", 10, "bold"))
        self.label_licznik.pack(pady=5)

        # Lista monitorowanych
        frame_list = tk.Frame(parent)
        frame_list.pack(fill='both', expand=True, padx=10)
        
        list_container = tk.Frame(frame_list)
        list_container.pack(side='left', fill='both', expand=True)
        
        tk.Label(list_container, text=self.t("monitored_phrases"), font=("Arial", 10, "bold")).pack()
        
        self.lista_box = tk.Listbox(list_container, height=12, font=("Consolas", 9))
        self.lista_box.pack(side='left', fill='both', expand=True)
        
        scroll_list = tk.Scrollbar(list_container, command=self.lista_box.yview)
        scroll_list.pack(side='right', fill='y')
        self.lista_box.config(yscrollcommand=scroll_list.set)
        
        # Przyciski zarządzania
        btn_frame = tk.Frame(frame_list)
        btn_frame.pack(side='right', fill='y', padx=10)
        
        tk.Button(btn_frame, text="❌\n"+self.t("delete_phrase").upper(), command=self.usun_fraze,
                 bg="#ff6666", width=12).pack(pady=5)
        tk.Button(btn_frame, text="🔍\n"+self.t("scan_now"), command=self.wymusz_skanowanie,
                 bg="#66ccff", width=12).pack(pady=5)
        tk.Button(btn_frame, text="⏸\n"+self.t("pause"), command=self.pauza_skanowania,
                 bg="#ffcc66", width=12).pack(pady=5)
        tk.Button(btn_frame, text="▶\n"+self.t("resume"), command=self.wznow_skanowania,
                 bg="#66ff66", width=12).pack(pady=5)
        tk.Button(btn_frame, text="📥\n"+self.t("import"), command=self.importuj_frazy,
                 bg="#cc99ff", width=12).pack(pady=5)
        tk.Button(btn_frame, text="📤\n"+self.t("export"), command=self.eksportuj_frazy,
                 bg="#ff99cc", width=12).pack(pady=5)

        # Log
        tk.Label(parent, text=self.t("log"), font=("Arial", 10, "bold")).pack(pady=5)
        
        self.log_text = scrolledtext.ScrolledText(parent, height=8, font=("Consolas", 8))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Status bar
        self.status_bar = tk.Label(parent, text=f"{self.t('status')} {self.t('idle')}", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def stworz_zakladke_historia(self, parent):
        # Statystyki
        stats_frame = tk.Frame(parent)
        stats_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        self.label_stats = tk.Label(stats_frame, text="", justify='left', 
                                    font=("Consolas", 9), anchor='nw')
        self.label_stats.pack(fill='both', expand=True)
        
        # Tree historia
        tree_frame = tk.Frame(parent)
        tree_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(tree_frame, text=self.t("history_100"), font=("Arial", 10, "bold")).pack()
        
        self.tree_historia = ttk.Treeview(tree_frame, columns=(
            "time", "priority", "phrase", "sentiment", "source", "title"
        ), show='headings', height=25)
        
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
        
        scroll_tree = tk.Scrollbar(tree_frame, command=self.tree_historia.yview)
        scroll_tree.pack(side='right', fill='y')
        self.tree_historia.config(yscrollcommand=scroll_tree.set)
        self.tree_historia.pack(fill='both', expand=True)
        
        self.tree_historia.bind('<Double-1>', self.otworz_link_z_historii)
        
        # Przyciski
        btn_frame = tk.Frame(tree_frame)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text=self.t("export_csv"), command=self.eksport_csv,
                 bg="#90EE90").pack(side='left', padx=5)
        tk.Button(btn_frame, text=self.t("clear_history"), command=self.czyszcz_historie,
                 bg="#ff6666").pack(side='left', padx=5)

    def stworz_zakladke_zrodla(self, parent):
        # Statystyki źródeł
        stats_frame = tk.Frame(parent)
        stats_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        self.label_source_stats = tk.Label(stats_frame, text="", justify='left',
                                           font=("Consolas", 9), anchor='nw')
        self.label_source_stats.pack(fill='both', expand=True)
        
        # Kontrolki źródeł
        controls_frame = tk.LabelFrame(parent, text=self.t("sources"), padx=10, pady=10)
        controls_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.source_vars = {}
        self.source_weight_entries = {}
        
        for source_name, source_config in self.sources_config.items():
            frame = tk.Frame(controls_frame)
            frame.pack(fill='x', pady=5)
            
            var = tk.BooleanVar(value=source_config['enabled'])
            self.source_vars[source_name] = var
            
            chk = tk.Checkbutton(frame, text=source_name, variable=var,
                                font=("Arial", 10))
            chk.pack(side='left')
            
            tk.Label(frame, text="Weight:").pack(side='left', padx=(20, 5))
            entry = tk.Entry(frame, width=5)
            entry.insert(0, str(source_config['weight']))
            entry.pack(side='left')
            self.source_weight_entries[source_name] = entry
        
        # Przyciski
        btn_frame = tk.Frame(controls_frame)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text=self.t("enable_all"), command=self.enable_all_sources,
                 bg="#90EE90").pack(side='left', padx=5)
        tk.Button(btn_frame, text=self.t("disable_all"), command=self.disable_all_sources,
                 bg="#ff6666").pack(side='left', padx=5)
        tk.Button(btn_frame, text="💾 SAVE", command=self.save_sources_config,
                 bg="#66ccff").pack(side='left', padx=5)

    def stworz_zakladke_readme(self, parent):
        """Zakładka z instrukcją"""
        # Tytuł
        title_label = tk.Label(
            parent,
            text=self.t("readme_title"),
            font=("Arial", 16, "bold"),
            fg="#0066cc"
        )
        title_label.pack(pady=10)
        
        # Tekst instrukcji
        text_widget = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f9f9f9",
            padx=10,
            pady=10
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', self.t("readme_content"))
        text_widget.config(state='disabled')  # Read-only

    def stworz_zakladke_wsparcie(self, parent):
        """Zakładka wsparcia projektu"""
        # Container centralny
        container = tk.Frame(parent)
        container.pack(expand=True)
        
        # Tytuł
        title_label = tk.Label(
            container,
            text=self.t("support_title"),
            font=("Arial", 18, "bold"),
            fg="#FF6B35"
        )
        title_label.pack(pady=20)
        
        # Tekst wsparcia
        text_widget = tk.Text(
            container,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#f9f9f9",
            height=15,
            width=60,
            padx=20,
            pady=20,
            relief=tk.FLAT
        )
        text_widget.pack(pady=10)
        text_widget.insert('1.0', self.t("support_content"))
        text_widget.config(state='disabled')
        
        # Przycisk "Kup mi kawę"
        coffee_btn = tk.Button(
            container,
            text=self.t("coffee_button"),
            command=self.open_coffee_link,
            font=("Arial", 14, "bold"),
            bg="#FFDD00",
            fg="#000000",
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3,
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
            font=("Arial", 10, "italic"),
            fg="#666666"
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

    def usun_fraze(self):
        selected = self.lista_box.curselection()
        if not selected:
            return
        
        idx = selected[0]
        fraza = self.monitorowane_frazy[idx]['fraza']
        
        if messagebox.askyesno(self.t("confirm"), f"{self.t('delete_phrase')}: {fraza}?"):
            del self.monitorowane_frazy[idx]
            self.zapisz_konfiguracje()
            self.odswiez_liste_gui()
            self.log(f"❌ {self.t('phrase_removed')}: {fraza}")

    def odswiez_liste_gui(self):
        self.lista_box.delete(0, tk.END)
        
        for fraza_obj in self.monitorowane_frazy:
            prio = fraza_obj['priorytet']
            kat = fraza_obj['kategoria']
            fraza = fraza_obj['fraza']
            ticker = fraza_obj.get('ticker', '')
            
            # Dodaj ticker do wyświetlania jeśli istnieje
            if ticker:
                tekst = f"[{prio}] [{kat}] {fraza} (${ticker})"
            else:
                tekst = f"[{prio}] [{kat}] {fraza}"
            
            if fraza_obj.get('filtry_pozytywne'):
                tekst += f" +({','.join(fraza_obj['filtry_pozytywne'])})"
            if fraza_obj.get('filtry_negatywne'):
                tekst += f" -({','.join(fraza_obj['filtry_negatywne'])})"
            
            self.lista_box.insert(tk.END, tekst)
            
            # Kolorowanie
            idx = self.lista_box.size() - 1
            kolor = PRIORYTETY[prio]['kolor']
            bg = PRIORYTETY[prio]['bg']
            self.lista_box.itemconfig(idx, fg=kolor, bg=bg)
        
        self.label_licznik.config(text=f"{self.t('counter')} {len(self.monitorowane_frazy)}/{MAX_FRAZ}")

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
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def wczytaj_konfiguracje(self):
        if os.path.exists(PLIK_KONFIGURACJI):
            try:
                with open(PLIK_KONFIGURACJI, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.monitorowane_frazy = data.get('frazy', [])
                    self.sources_config = data.get('sources', SOURCES.copy())
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
            self.zapisz_historie()

    def wyslij_powiadomienie(self, tytul, tresc, priorytet, sentiment_polarity, sentiment_label, source):
        try:
            dzwiek = PRIORYTETY[priorytet]['dzwiek']
            
            sent_emoji = "😐"
            if sentiment_polarity > 0.1:
                sent_emoji = "😊"
            elif sentiment_polarity < -0.1:
                sent_emoji = "😟"
            
            notification = Notification(
                app_id="Investment Radar",
                title=f"{priorytet} | {source}",
                msg=f"{sent_emoji} {sentiment_label} ({sentiment_polarity:+.2f})\n\n{tytul}\n\n{tresc}",
                duration="long",
                icon=""
            )
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
                        self.log(f"🔥 BURST detected for: {fraza} ({len(recent_events)} news in {BURST_WINDOW/60:.0f} min)")
                        fraza_obj['last_burst_notification'] = teraz.isoformat()

    def petla_radaru(self):
        """Główna pętla skanowania"""
        while True:
            try:
                if not self.skanowanie_aktywne:
                    time.sleep(5)
                    continue
                
                start_time = datetime.now().timestamp()
                self.status_bar.config(text=f"{self.t('status')} {self.t('scanning')}...")
                
                for idx, fraza_obj in enumerate(self.monitorowane_frazy):
                    if not self.skanowanie_aktywne:
                        break
                    
                    fraza = fraza_obj['fraza']
                    ticker = fraza_obj.get('ticker', '')  # Pobierz ticker
                    priorytet = fraza_obj['priorytet']
                    
                    self.log(f"🔍 {self.t('scanning_progress')}: {fraza} [{priorytet}]")
                    
                    # Scan z różnych źródeł
                    for source_name, source_config in self.sources_config.items():
                        if not source_config['enabled']:
                            continue
                        
                        url = None
                        
                        # Google News - używa frazy (nazwy firmy)
                        if source_config['type'] == 'google':
                            fraza_encoded = urllib.parse.quote_plus(fraza)
                            url = f"https://news.google.com/rss/search?q={fraza_encoded}&{self.wybrany_region_kod}"
                        
                        # Yahoo Finance - używa tickera
                        elif source_config['type'] == 'yahoo':
                            if not ticker:
                                continue  # Pomiń jeśli brak tickera
                            url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
                        
                        # Seeking Alpha - używa tickera
                        elif source_config['type'] == 'seekingalpha':
                            if not ticker:
                                continue  # Pomiń jeśli brak tickera
                            url = f"https://seekingalpha.com/symbol/{ticker}.xml"
                        
                        if not url:
                            continue
                        
                        try:
                            self.log(f"  → Scanning {source_name}...")
                            feed = feedparser.parse(url)
                            
                            news_count = len(feed.entries[:5])
                            if news_count > 0:
                                self.log(f"  ✓ Found {news_count} articles from {source_name}")
                            
                            for news in feed.entries[:5]:
                                # Sprawdź duplikaty
                                if news.link in self.historia_newsow:
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
                                self.log(f"📰 NEW: {news.title[:60]}... [{sentiment_label}]")
                                self.wyslij_powiadomienie(news.title, news.get('summary', '')[:200],
                                                         priorytet, sentiment_polarity, sentiment_label, source_name)
                                self.dodaj_do_historii(news.link, news.title, fraza_obj,
                                                      sentiment_polarity, sentiment_label, source_name)
                        
                        except Exception as e:
                            self.log(f"❌ Error scanning {source_name}: {e}")
                    
                    time.sleep(2)
                
                self.log(f"✅ Scan cycle complete. Waiting 10 min...")
                self.odswiez_statystyki()
                self.status_bar.config(text=f"{self.t('status')} {self.t('idle')}")
                
                # Czekaj na następny cykl
                next_scan = start_time + INTERVAL
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
        
        historia_sorted = sorted(self.historia_newsow.items(),
                                key=lambda x: x[1]['timestamp'], reverse=True)
        
        for link, dane in historia_sorted[:100]:
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
        
        for source in ["Google News", "Yahoo Finance", "Seeking Alpha", "Unknown"]:
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
        self.odswiez_statystyki()
        
        messagebox.showinfo(self.t("info"), f"{self.t('history_cleared')}: {usuniete}")
        self.log(f"🗑️ Cleaned: {usuniete} entries")

if __name__ == "__main__":
    root = tk.Tk()
    app = RadarApp(root)
    root.mainloop()


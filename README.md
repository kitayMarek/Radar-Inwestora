[README.md](https://github.com/user-attachments/files/24356249/README.md)
# 📊 Radar Inwestora v4.2 PRO 


## 🎯 Co to jest?

Radar Inwestora to zaawansowane narzędzie do monitorowania newsów finansowych z wielu źródeł, z analizą sentymentu i systemem powiadomień. 

## ✨ Funkcje aplikacji

- 🌐 **Multi-source**: Google News, Yahoo Finance, Seeking Alpha
- 📊 **Analiza sentymentu**: Automatyczna ocena tonu newsów (pozytywny/negatywny/neutralny)
- 🔔 **Powiadomienia Windows**: Różne dźwięki dla różnych priorytetów
- 🔥 **Burst detection**: Wykrywanie nagłych wzrostów aktywności newsowej
- 🎯 **Filtry**: Pozytywne i negatywne słowa kluczowe
- 📈 **Statystyki**: Historia, wykresy i analiza trendów
- 💾 **Eksport**: CSV z pełnymi danymi

## 🚀 Szybki start

### Wymagania
- Windows 7/8/10/11
- Python 3.8 lub nowszy (tylko do budowania!)
- ~500 MB wolnego miejsca
- Połączenie internetowe

### Budowanie w 3 krokach

1. **Zainstaluj Python**
   ```bash
   # Pobierz z https://www.python.org/downloads/
   # WAŻNE: Zaznacz "Add Python to PATH"!
   ```


```
Fraza: "Apple earnings"
Priorytet: HIGH
Kategoria: Portfolio
Filtry (+): revenue, profit
Filtry (-): rumor
```

### Analiza sektora
```
Fraza: "semiconductor shortage"
Priorytet: MEDIUM
Kategoria: Sektor
Min Sentiment: -0.5
```

### Tracking konkurencji
```
Fraza: "Tesla production"
Priorytet: MEDIUM
Kategoria: Konkurencja
Źródło: Yahoo Finance (weight: 1.2)
```

## 🔧 Troubleshooting

### Problem: "Python not found"
**Rozwiązanie**: Zainstaluj Python i upewnij się że zaznaczyłeś "Add to PATH"

### Problem: Brak powiadomień
**Rozwiązanie**:
1. Uruchom jako administrator
2. Sprawdź ustawienia Windows Notifications
3. Sprawdź czy winotify jest zainstalowany

Więcej rozwiązań: `FAQ.txt`

## 📈 Statystyki projektu

- **Wersja**: 4.2 PRO
- **Języki**: Python, Tkinter
- **Zależności**: feedparser, winotify, textblob
- **Rozmiar .exe**: ~40-60 MB
- **Platformy**: Windows 7/8/10/11

## 🛠️ Dla deweloperów

### Budowanie z linii poleceń
```bash
# Instalacja zależności
pip install -r requirements.txt

# Budowanie
pyinstaller --clean --noconfirm radar_installer.spec

# Wersja debug (z konsolą)
pyinstaller --clean --noconfirm radar_installer_debug.spec

# Wersja portable
pyinstaller --onedir radar_v4_2_pro.py
```

### Zaawansowane opcje
```bash
# Z szyfrowaniem
pyinstaller --key=YOUR_KEY_16_CHARS radar_installer.spec

# Bez UPX compression
pyinstaller --noupx radar_installer.spec

# Z własną ikoną
pyinstaller --icon=icon.ico radar_installer.spec
```

## 📄 Licencje

- **Aplikacja**: Do ustalenia przez autora
- **Zależności**:
  - feedparser: BSD License
  - winotify: MIT License
  - textblob: MIT License
  - Python: PSF License

## 🤝 Wkład w projekt

Sugestie i zgłoszenia błędów mile widziane! 


## 🎓 Dodatkowe zasoby

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Python Documentation](https://docs.python.org/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)


### v4.2 PRO (25.12.2024)
- ✨ Dodano sentiment analysis
- ✨ Multi-source support
- ✨ Burst detection
- 🔧 Optymalizacja wydajności
- 📦 Kompletny pakiet buildera



*Powodzenia w inwestowaniu!* 📈

<img width="987" height="1080" alt="Radar1" src="https://github.com/user-attachments/assets/0224e208-3e37-49fb-a157-3eaf556b3a19" />
<img width="1163" height="1080" alt="Radar2" src="https://github.com/user-attachments/assets/1f0884d6-3d4e-4362-b7cc-8f56ec2b2bf9" />
<img width="1163" height="1080" alt="Radar3" src="https://github.com/user-attachments/assets/e202ef12-48e5-4665-93e1-28ca6e1a3fc2" />
<img width="1162" height="1080" alt="Radar4" src="https://github.com/user-attachments/assets/2f924f22-cfb5-4060-b89a-55b6b616a04e" />
<img width="1166" height="1080" alt="Radar5" src="https://github.com/user-attachments/assets/4c19b78a-2b9b-46ab-a2e0-c023d6052eaf" />





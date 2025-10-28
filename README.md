# AI Test Automation Framework

Framework unificato per test automation con AI agents, supporta sia test **mobile** (iOS/Android) che **web** (browser).

## 🚀 Features

- ✨ **Unified Runner**: Gestione unificata di test mobile e web
- 🤖 **AI-Powered**: Usa LLM (Gemini, OpenAI, Ollama) per interpretare task in linguaggio naturale
- 📱 **Mobile Testing**: Supporto completo per iOS e Android via Appium
- 🌐 **Web Testing**: Automazione browser con Browser-Use
- 📊 **HTML Reports**: Report interattivi con screenshot e GIF animate
- ☁️ **Cloud Support**: Integrazione con LambdaTest per testing su cloud
- 🔄 **Excel Configuration**: Configurazione test tramite file Excel

## 📋 Requisiti

### Software
- Python 3.11+
- Node.js (per Appium)
- Appium Server
- Browser Chromium/Chrome

### Installazione Dipendenze

```bash
# Crea ambiente virtuale
python -m venv .venv

# Attiva ambiente
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Installa dipendenze Python
pip install -r requirements.txt

# Installa Appium (per test mobile)
npm install -g appium
appium driver install uiautomator2  # Android
appium driver install xcuitest      # iOS

# Installa Playwright (per test web)
playwright install chromium --with-deps
```

## ⚙️ Configurazione

### 1. File .env

Crea un file `.env` nella root del progetto:

```bash
# === LLM Configuration ===
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_google_api_key

# OpenAI (opzionale)
OPENAI_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your_openai_key

# Local LLM con Ollama (opzionale)
USE_LOCAL_LLM=false
LOCAL_LLM=llava:13b

# LLM per test web
WEB_LLM_PROVIDER=gemini  # gemini|openai|ollama

# === Mobile Testing (LambdaTest) ===
LT_USERNAME=your_lambdatest_username
LT_ACCESS_KEY=your_lambdatest_access_key

# === Misc ===
ANONYMIZED_TELEMETRY=false
BROWSER_HEADLESS=false
```

### 2. File Excel

Il file `dati_test.xlsx` deve contenere le seguenti colonne:

#### Colonne Obbligatorie (per tutti i test)
- `TestID`: Identificatore univoco (es: WEB_001, MOB_001)
- `Descrizione`: Descrizione human-readable del test
- `Task`: Task in linguaggio naturale per l'AI agent
- `Execution`: `True`/`False` per eseguire o saltare il test
- **`Device`**: `mobile` o `web` ← **NUOVO CAMPO CHIAVE**

#### Colonne per Test Mobile (required solo se Device="mobile")
- `Platform`: `Android` o `iOS`
- `DeviceName`: Nome del dispositivo (es: Pixel 6, iPhone 14)
- `UDID`: Device ID per esecuzione locale
- `AppPackage`: Package name Android (es: com.example.app)
- `AppActivity`: Activity Android (es: .MainActivity)
- `AppID`: App ID per LambdaTest (es: lt://APP123456)

#### Esempio Excel

| TestID | Descrizione | Task | Execution | Device | Platform | DeviceName | AppPackage |
|--------|-------------|------|-----------|--------|----------|------------|------------|
| WEB_001 | Google Search | Search for "AI agents" on google.com | True | web | - | - | - |
| MOB_001 | Android Login | Open app and login | True | mobile | Android | Pixel 6 | com.app |

## 🎯 Utilizzo

### Esecuzione Standard

```bash
# Esegui tutti i test con Execution=True
python main_runner.py
```

Il sistema:
1. Legge `dati_test.xlsx`
2. Filtra test con `Execution=True`
3. Instradrà automaticamente verso:
   - `MobileTestExecutor` se `Device=mobile`
   - `WebTestExecutor` se `Device=web`
4. Genera report HTML unificato
5. Apre report nel browser

### Debug

```bash
# Abilita logging dettagliato
export BROWSER_USE_LOGGING_LEVEL=debug  # Linux/Mac
set BROWSER_USE_LOGGING_LEVEL=debug    # Windows

# Esegui con debug
python main_runner.py
```

## 📁 Struttura Progetto

```
aitestautomation/
├── main_runner.py              # 🆕 Entry point principale (USA QUESTO)
├── dati_test.xlsx              # File Excel unificato
├── .env                        # Configurazione (GIT IGNORED)
├── system_prompt.txt           # System prompt custom per web tests
│
├── tests/
│   ├── mobile_test_executor.py # 🆕 Executor test mobile
│   ├── web_test_executor.py    # 🆕 Executor test web
│   ├── mobile_AI_test.py       # ⚠️ DEPRECATED (ma ancora funzionante)
│   └── web_AI_test.py          # ⚠️ DEPRECATED (ma ancora funzionante)
│
├── utilities/
│   ├── excel_utils.py          # Lettura Excel
│   ├── report_utils.py         # Generazione report HTML
│   ├── set_capabilities.py     # Configurazione Appium
│   └── utils.py                # Utility functions
│
├── screen/
│   ├── mobile/                 # Screenshot test mobile
│   └── web/                    # Screenshot test web
│
├── reports/
│   └── unified/                # 🆕 Report unificati
│       └── YYYYMMDD_HHMMSS/
│           └── test_report_*.html
│
├── app_class.py                # Wrapper Appium per test mobile
└── app_use/                    # Package Browser-Use agent per mobile
```

## 📊 Report

Il report HTML include:

- 📈 **Summary Dashboard**: Totale / Passati / Falliti
- 🖼️ **Screenshots interattivi**: Click per ingrandire
- 🎬 **GIF Animata**: Replay completo dell'esecuzione
- ✅❌ **Status Colorati**: Verde (pass) / Rosso (fail)
- 🔍 **Step-by-Step**: Espandi/Collassa ogni step
- 📱🌐 **Mixed Tests**: Test mobile e web nello stesso report

Location: `reports/unified/YYYYMMDD_HHMMSS/test_report_*.html`

## 🔧 Troubleshooting

### Problema: "Campo obbligatorio mancante: Device"

**Soluzione**: Aggiungi colonna `Device` nel file Excel con valori `mobile` o `web`

### Problema: Test mobile non parte

**Checklist**:
1. ✅ Appium server in esecuzione: `appium`
2. ✅ Device connesso: `adb devices` (Android) o `xcrun simctl list` (iOS)
3. ✅ UDID corretto nel file Excel
4. ✅ App installata sul device
5. ✅ Variabili `.env` configurate

### Problema: Test web non parte

**Checklist**:
1. ✅ Browser-Use installato: `pip install browser-use`
2. ✅ Chromium installato: `playwright install chromium --with-deps`
3. ✅ API key configurata in `.env`
4. ✅ File `system_prompt.txt` presente (opzionale)

### Problema: "No module named 'app_use'"

**Soluzione**:
```bash
# Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

## 🆕 What's New

### v2.0 - Unified Runner (Attuale)

- ✨ Single entry point (`main_runner.py`) per tutti i test
- 🔄 Routing automatico basato su colonna `Device`
- 📊 Report unificati per mobile + web
- 📚 Documentazione completa

### v1.0 - Dual System (Deprecato)

- File separati: `mobile_AI_test.py` + `web_AI_test.py`
- Excel separati: `dati_test_app.xlsx` + `dati_test.xlsx`
- Report separati

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join Server]
- 📖 Docs: [Full Documentation](./docs/)

## 📄 License

MIT License - vedi file LICENSE per dettagli

## 🤝 Contributing

Pull requests are welcome! Per cambiamenti maggiori, apri prima un issue per discutere cosa vorresti modificare.

## 🙏 Credits

- [Browser-Use](https://github.com/browser-use/browser-use) - Web automation framework
- [App-Use](https://github.com/erickjtorres/app-use) - Web automation framework
- [Appium](https://appium.io/) - Mobile automation
- [LambdaTest](https://www.lambdatest.com/) - Cloud testing platform

---

**Made with ❤️ by Pasquale Delli Bergoli**
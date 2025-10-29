# AI Test Automation Framework

Framework unificato per test automation con AI agents, supporta sia test **mobile** (iOS/Android) che **web** (browser).

## 🚀 Features

- ✨ **Unified Runner**: Gestione unificata di test mobile e web.
- 🤖 **AI-Powered**: Usa LLM (Gemini, OpenAI, Ollama) per interpretare task in linguaggio naturale.
- 📱 **Mobile Testing**: Supporto completo per iOS e Android via Appium.
- 🌐 **Web Testing**: Automazione browser con Browser-Use.
- 📊 **HTML Reports**: Report interattivi con screenshot e GIF animate.
- ☁️ **Cloud Support**: Integrazione con LambdaTest per testing su cloud.
- 📝 **Web Editor**: Interfaccia web per gestire i file Excel dei test case (aggiungere, modificare, eliminare righe, avviare esecuzioni).
- 🔄 **Excel Configuration**: Configurazione test tramite file Excel.

## 📋 Requisiti

### Software
- Python 3.11+.
- Node.js (per Appium).
- Appium Server.
- Browser Chromium/Chrome.
- Flask (per l'editor web).

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

⚙️ Configurazione
1. File .env
Crea un file .env nella root del progetto copiando .env.example. Modifica almeno una API key per un provider LLM (es. GOOGLE_API_KEY).

Bash

# Esempio minimo
# === LLM Configuration ===
GOOGLE_API_KEY=your_google_api_key

# === Mobile Testing (LambdaTest - Opzionale) ===
LT_USERNAME=your_lambdatest_username
LT_ACCESS_KEY=your_lambdatest_access_key

# === Misc ===
ANONYMIZED_TELEMETRY=false
BROWSER_HEADLESS=false

2. File Excel
Il file dati_test.xlsx (o un altro file .xlsx nella root) contiene i test case. Puoi gestirlo manualmente o usare l'editor web.

Colonne Obbligatorie (per tutti i test)
TestID: Identificatore univoco (es: WEB_001, MOB_001).

Descrizione: Descrizione human-readable del test.

Task: Task in linguaggio naturale per l'AI agent.

Active: True/False per eseguire o saltare il test.

Device: mobile o web.

Colonne per Test Mobile (solo se Device="mobile")
Execution: local o cloud.

Platform: Android o iOS.

DeviceName: Nome del dispositivo.

UDID: Device ID per esecuzione locale.

AppPackage: Package name Android.

AppActivity: Activity Android.

AppID: App ID per LambdaTest (solo con Execution = 'cloud').

🎯 Utilizzo
Opzione 1: Esecuzione Standard da Terminale
Bash

# Esegui tutti i test attivi dal file di default (dati_test.xlsx)
python main_runner.py

# Esegui test da un file specifico
python main_runner.py --file nome_altro_file.xlsx
Il sistema legge l'Excel, filtra i test attivi, li instrada all'executor corretto (mobile/web) e genera/apre il report HTML.

Opzione 2: Gestione ed Esecuzione tramite Web Editor
Avvia l'Editor Web:

Bash

python web_editor.py
Il browser si aprirà automaticamente su http://127.0.0.1:5000.

Usa l'Interfaccia:

Seleziona il file Excel dal menu a tendina.

Carica nuovi file .xlsx dal tuo disco.

Modifica i dati nelle celle (doppio click o seleziona e scrivi).

Attiva/Disattiva test con le checkbox.

Aggiungi/Elimina righe.

Espandi righe con task lunghi.

Salva le modifiche (il pulsante appare solo se ci sono modifiche).

Avvia Test: Clicca sul pulsante <i class="bi bi-play-fill"></i> per eseguire i test attivi nel file attualmente visualizzato. L'output apparirà in una finestra modale.

Visualizza Report: Clicca su "Vedi Report" per accedere all'elenco delle esecuzioni passate e aprirle o eliminarle.

Ferma l'Editor: Premi CTRL+C nel terminale dove hai avviato web_editor.py.

Debug
Bash

# Abilita logging dettagliato (imposta nel .env o come variabile d'ambiente)
# BROWSER_USE_LOGGING_LEVEL=DEBUG
# DEBUG_MODE=true

# Esegui con encoding forzato (per Windows, se hai problemi con caratteri speciali)
python -X utf8 main_runner.py
python -X utf8 web_editor.py

📁 Struttura Progetto (Aggiornata)
aitestautomation/
├── main_runner.py              # Entry point esecuzione test
├── web_editor.py               # NUOVO: Entry point editor web
├── dati_test.xlsx              # File Excel di default
├── .env                        # Configurazione (GIT IGNORED)
├── requirements.txt            # Dipendenze Python
├── system_prompt.txt           # System prompt custom per web tests
│
├── templates/                  # NUOVO: File HTML per l'editor web
│   ├── index.html
│   └── reports.html
│
├── tests/
│   ├── mobile_test_executor.py # Executor test mobile
│   ├── web_test_executor.py    # Executor test web
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
│   └── unified/                # Report unificati
│       └── YYYYMMDD_HHMMSS/
│           └── test_report_*.html
│
├── app_class.py                # Wrapper Appium per test mobile
└── app_use/                    # Package App-Use agent per mobile

📊 Report
Il report HTML generato da main_runner.py include:

Summary Dashboard

Screenshot interattivi

GIF Animata (se abilitata)

Status Colorati

Step-by-Step

Location: reports/unified/YYYYMMDD_HHMMSS/test_report_*.html. Puoi accedere all'elenco tramite il link "Vedi Report" nell'editor web.

🔧 Troubleshooting
Problema: Web Editor non trova index.html (TemplateNotFound)
Soluzione: Assicurati che i file index.html e reports.html siano dentro una cartella chiamata templates allo stesso livello di web_editor.py. Verifica che .gitignore non stia ignorando i file .html.

Problema: ModuleNotFoundError: No module named 'pandas' (o altre librerie)
Soluzione: Assicurati che l'ambiente virtuale .venv sia attivo ((.venv) visibile nel terminale) e reinstalla le dipendenze: pip install -r requirements.txt.

Problema: Caratteri speciali/Emoji non visibili nel terminale (UnicodeEncodeError)
Soluzione: Esegui gli script con -X utf8 (python -X utf8 web_editor.py) o rimuovi/sostituisci i caratteri problematici (come nel banner di main_runner.py o le emoji in config_manager.py).

Problema: Test mobile non parte
Checklist: Appium server in esecuzione (appium)? Device connesso/emulatore avviato (adb devices)? UDID corretto? App installata? Variabili .env (per cloud) corrette?

Problema: Test web non parte
Checklist: Browser-Use installato? Chromium installato (playwright install chromium --with-deps)? API key LLM configurata in .env?

📞 Support
📧 Email: pasquale.dellibergoli91@gmail.com

📖 Docs: Vedi cartella docs/.

📄 License
MIT License

🤝 Contributing
Pull requests are welcome!

🙏 Credits
Browser-Use

App-Use

Appium

LambdaTest

Flask

Pandas

Made with ❤️ by Pasquale Delli Bergoli
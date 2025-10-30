# AI Test Automation Framework

Framework unificato per test automation con AI agents, che supporta sia test **mobile** (iOS/Android) che **web** (browser).

Ora include una **interfaccia web completa** per la gestione, l'esecuzione e la generazione di test case.

## 🚀 Features Principali

- ✨ **Web UI Integrata**: Una pagina Home per navigare tra le funzionalità principali.
- 📝 **Editor Test Case Web**: Un editor visuale per creare, modificare, eliminare e gestire i test case nei tuoi file Excel.
- 🤖 **Generatore Test Case AI**: Una pagina dedicata per caricare file di requisiti e generare automaticamente nuovi test case usando l'AI.
- ▶️ **Esecuzione Web**: Avvia e ferma le esecuzioni dei test direttamente dal browser, visualizzando i log in tempo reale.
- 📊 **Visualizzatore Report**: Sfoglia, apri ed elimina i report HTML delle esecuzioni passate.
- 📱 **Test Mobili**: Supporto completo per iOS e Android tramite Appium.
- 🌐 **Test Web**: Automazione browser tramite Browser-Use.
- ☁️ **Cloud Support**: Integrazione con LambdaTest per testing su cloud.

## 📋 Requisiti

### Software
- Python 3.11+
- Node.js (per Appium, se si eseguono test mobile)
- Appium Server (se si eseguono test mobile locali)
- Browser Chromium/Chrome

### Installazione Dipendenze

1.  **Crea Ambiente Virtuale**
    ```bash
    python -m venv .venv
    ```

2.  **Attiva Ambiente**
    ```bash
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Installa Dipendenze Python**
    (Include `Flask`, `pandas`, `langchain`, `google-generativeai`, `appium-python-client`, ecc.)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Installa Dipendenze Web/Mobile (Necessarie per `main_runner.py`)**
    ```bash
    # Installa Playwright (per test web)
    playwright install chromium --with-deps

    # Installa Appium (per test mobile)
    npm install -g appium
    appium driver install uiautomator2  # Android
    # appium driver install xcuitest      # iOS
    ```

## ⚙️ Configurazione

### 1. File .env

Crea un file `.env` nella root del progetto copiando `.env.example`.

**L'unica variabile obbligatoria per iniziare è una chiave API per l'IA:**

```bash
# Esempio minimo per Google Gemini (raccomandato)
GOOGLE_API_KEY=your_google_api_key

# ---
# Puoi configurare quale LLM usare per l'esecuzione E la generazione
# Opzioni: "gemini", "openai", "ollama"
WEB_LLM_PROVIDER=gemini
Assicurati che l'API key corrispondente (es. OPENAI_API_KEY se usi "openai") sia configurata.

2. File Excel
L'editor web gestirà automaticamente la creazione e la modifica dei file .xlsx nella cartella principale. La struttura richiesta è: TestID, Descrizione, Task, Active, Device, Execution, Platform, DeviceName, UDID, AppID, AppPackage, AppActivity

🎯 Utilizzo (Metodo Consigliato: Interfaccia Web)
Avvia l'interfaccia web completa con un singolo comando.

1. Avvia il Web Server
Bash

# Assicurati che il tuo ambiente .venv sia attivo
python web_editor.py
Il tuo browser si aprirà automaticamente su http://127.0.0.1:5000.

2. Pagina Home
Verrai accolto da una pagina iniziale dove potrai scegliere tra:

Editor Test Case: Per gestire ed eseguire i test.

Genera Test Case: Per creare nuovi test da requisiti.

Vedi Report Esecuzioni: Per visualizzare lo storico dei report.

3. Editor Test Case (/editor)
Gestisci File: Seleziona file .xlsx esistenti o carica nuovi file dal tuo computer.

Modifica Live: Clicca su qualsiasi cella per modificarne il contenuto. Il testo lungo è gestito correttamente.

Attiva/Disattiva: Usa le checkbox Active per decidere quali test eseguire.

Aggiungi/Elimina: Aggiungi nuove righe o eliminale con le icone <i class="bi bi-trash-fill"></i> e <i class="bi bi-plus-lg"></i>.

Esegui Test:

Clicca <i class="bi bi-play-fill"></i> Avvia Test.

Se hai modifiche non salvate, ti verrà chiesto di salvarle.

L'output del terminale apparirà in una finestra modale.

Puoi fermare l'esecuzione in qualsiasi momento con il pulsante STOP.

4. Generatore di Test (/generate)
Carica Input: Carica un file di requisiti (es. requisiti.txt) e un file di prompt (es. prompt_costruisci_test.txt).

Seleziona: I file caricati appaiono nei menu a tendina (l'ultimo prompt usato viene memorizzato).

Genera: Clicca <i class="bi bi-magic"></i> Genera Test Case.

Log in Tempo Reale: Vedrai i log dell'IA mentre lavora.

Interrompi: Puoi fermare la generazione con il pulsante STOP.

Scarica: I risultati appaiono in una tabella, pronti per essere scaricati come file .csv.

📁 Struttura Progetto (Aggiornata)
aitestautomation/
│
├── 🚀 CORE FILES
│   ├── web_editor.py             # Entry point NUOVO (Avvia server web)
│   ├── main_runner.py            # Entry point Esecuzione Test (usato da web_editor)
│   ├── dati_test.xlsx            # File Excel di default
│   ├── .env                      # Configurazione (GIT IGNORED)
│   └── requirements.txt          # Dipendenze Python
│
├── 📁 templates/                
│   ├── home.html                 # Pagina iniziale
│   ├── index.html                # Editor Test Case
│   ├── generate_tests.html       # Pagina Generazione Test
│   └── reports.html              # Pagina Elenco Report
│
├── 🧪 tests/
│   ├── test_generator.py         # Classe per generare test da AI
│   ├── mobile_test_executor.py   # Executor test mobile
│   └── web_test_executor.py      # Executor test web
│
├── 🛠️ utilities/
│   ├── excel_utils.py            # Lettura Excel
│   ├── report_utils.py           # Generazione report HTML
│   └── ...                       # Altre utility
│
├── 📊 reports/
│   └── unified/                  # Report HTML generati
│
└── 🖼️ screen/                   # Screenshot dei test
🔧 Troubleshooting
Problema: ModuleNotFoundError: No module named 'pandas' (o flask)
Soluzione: L'ambiente virtuale non è attivo.

Ferma il server (CTRL+C).

Attiva l'ambiente: .venv\Scripts\activate (Windows) o source .venv/bin/activate (Mac/Linux).

Installa le dipendenze: pip install -r requirements.txt.

Riavvia il server: python web_editor.py.

Problema: TemplateNotFound: home.html (o index.html)
Soluzione: Il server non trova i file HTML. Assicurati che i file home.html, index.html, generate_tests.html, e reports.html si trovino in una cartella chiamata templates allo stesso livello di web_editor.py.

Problema: L'interfaccia web non si aggiorna dopo le modifiche al codice
Soluzione: Il tuo browser sta usando una vecchia versione in cache.

Assicurati che il server web_editor.py sia in esecuzione (l'ultima versione disabilita la cache).

Svuota la cache del browser o fai un Hard Refresh (Ctrl+Shift+R su Windows, Cmd+Shift+R su Mac).

Prova in una finestra di navigazione in incognito.

Problema: UnicodeEncodeError (caratteri strani nel terminale)
Soluzione: (Solo per Windows) Il terminale non gestisce i caratteri UTF-8.

Azione: Rimuovi i caratteri speciali (come emoji ✅ o banner ╔═══╗) dai file Python (config_manager.py, main_runner.py).

Alternativa: Avvia python con il flag -X utf8: python -X utf8 web_editor.py.

📞 Supporto
📧 Email: pasquale.dellibergoli91@gmail.com

📖 Docs: Vedi cartella docs/.

📄 Licenza
MIT License

🙏 Riconoscimenti
Browser-Use

App-Use

Appium

Flask

Pandas

Made with ❤️ by Pasquale Delli Bergoli
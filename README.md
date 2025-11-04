# 🤖 AI Test Automation Framework

<div align="center">

**Framework unificato di test automation powered by AI**  
Supporto completo per test **Mobile** (iOS/Android) e **Web** (Browser)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Appium](https://img.shields.io/badge/Appium-Ready-purple.svg)](http://appium.io/)
[![Browser-Use](https://img.shields.io/badge/Browser--Use-Integrated-orange.svg)](https://github.com/browser-use/browser-use)
[![App-Use](https://img.shields.io/badge/App--Use-Integrated-red.svg)](https://github.com/app-use/app-use)

</div>

---

## ✨ Caratteristiche Principali

<table>
<tr>
<td width="50%">

### 🎨 Interfaccia Web Completa
- **Home Dashboard** intuitiva
- **Editor Visuale** per test case
- **Generatore AI** integrato
- **Configurazione LLM** centralizzata
- **Esecuzione in tempo reale**
- **Report interattivi**

</td>
<td width="50%">

### 🚀 Testing Avanzato
- **Test Mobile** iOS & Android
- **Test Web** multi-browser
- **Cloud Testing** con LambdaTest
- **Log in tempo reale**
- **Screenshot automatici**
- **Multi-LLM Support**

</td>
</tr>
</table>

---

## 📸 Screenshots

```
┌──────────────────────────────────────────────────────┐
│  🏠 Home  →  📝 Editor  →  🤖 Generator  →  ⚙️ Config │
│            ↓                                         │
│         ▶️ Execute  →  📊 Reports                     │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Start

### 1️⃣ Setup Ambiente

```bash
# Clona il repository
git clone https://github.com/pdellibergoli/ai-test-automation.git
cd aitestautomation

# Crea e attiva ambiente virtuale
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2️⃣ Configura API Keys

**Metodo 1: Tramite Web UI (Raccomandato)**

```bash
# Avvia il framework
python web_editor.py

# Nel browser:
# 1. Vai su http://127.0.0.1:5000
# 2. Clicca su "Configurazione"
# 3. Seleziona il provider LLM (Gemini, OpenAI, Ollama)
# 4. Inserisci la tua API key
# 5. Salva
```

**Metodo 2: Manualmente via .env**

Crea un file `.env` nella root del progetto:

```bash
# Gemini (Raccomandato - Free Tier disponibile)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Opzionale: Altri provider
# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini

# Ollama (Locale)
USE_LOCAL_LLM=false
LOCAL_LLM=llava:13b
OLLAMA_BASE_URL=http://localhost:11434

# Provider attivo
WEB_LLM_PROVIDER=gemini  # Opzioni: gemini, openai, ollama
```

### 3️⃣ Installa Driver (per test mobile/web)

```bash
# Browser automation
playwright install chromium --with-deps

# Mobile automation (se necessario)
npm install -g appium
appium driver install uiautomator2  # Android
appium driver install xcuitest      # iOS (solo su Mac)
```

### 4️⃣ Avvia il Framework! 🎉

```bash
python web_editor.py
```

Il browser si aprirà automaticamente su `http://127.0.0.1:5000`

---

## 🎨 Interfaccia Web

### 🏠 Home Dashboard
Punto di partenza per tutte le operazioni:
- **Editor Test Case**: Gestisci i tuoi test
- **Genera Test Case**: Crea test con l'AI
- **Configurazione**: Imposta provider LLM e API keys
- **Vedi Report**: Analizza le esecuzioni

### 📝 Editor Test Case (`/editor`)

| Feature | Descrizione |
|---------|-------------|
| **Gestione File** | Carica, crea, e seleziona file Excel |
| **Modifica Live** | Click su cella per editing immediato |
| **Toggle Active** | Checkbox per abilitare/disabilitare test |
| **Aggiungi/Rimuovi** | Icone intuitive per gestire righe |
| **Esecuzione** | Avvia test con log in tempo reale |
| **Stop Immediato** | Interrompi esecuzione in qualsiasi momento |

### 🤖 Generatore AI (`/generate`)

```
1. Carica file requisiti   →  2. Seleziona prompt
                ↓
3. Clicca "Genera"  →  4. Monitora progresso
                ↓
5. Scarica CSV      →  6. Importa nell'editor
```

**Features**:
- Log in tempo reale della generazione
- Interruzione sicura del processo
- Export diretto in formato CSV
- Memorizzazione ultimo prompt usato
- Configurazione LLM dinamica

### ⚙️ Configurazione LLM (`/config`) **NUOVO!**

Gestione centralizzata dei provider LLM:

**Supported Providers:**
- **Google Gemini** (Free tier disponibile, raccomandato per iniziare)
- **OpenAI** (GPT-4, GPT-4.1-mini, etc.)
- **Ollama** (LLM locali, privacy totale)

**Features:**
- 🔄 Cambio provider senza riavvio
- 🔑 Gestione sicura delle API keys
- 📝 Configurazione modelli specifici
- 💾 Salvataggio automatico in `.env`
- ✅ Validazione real-time delle impostazioni

**Guida Rapida:**
1. Seleziona il provider dal menu dropdown
2. Inserisci l'API key (recuperala dai link forniti)
3. (Opzionale) Personalizza il nome del modello
4. Clicca "Salva Configurazione"
5. La nuova configurazione è immediatamente attiva

### 📊 Report Viewer (`/reports`)
- Lista cronologica di tutte le esecuzioni
- Apertura diretta dei report HTML
- Eliminazione report obsoleti
- Filtri e ricerca integrati

---

## 📁 Struttura Progetto

```
aitestautomation/
│
├── 🚀 CORE
│   ├── web_editor.py           # ⭐ Entry point principale
│   ├── main_runner.py          # Test execution engine
│   ├── config_manager.py       # Gestione configurazione dinamica
│   ├── dati_test.xlsx          # Template file Excel
│   ├── llm_models.json         # Definizione provider LLM
│   ├── .env                    # Configurazione (gitignored)
│   └── requirements.txt        # Dipendenze Python
│
├── 🎨 FRONTEND
│   └── templates/
│       ├── home.html           # Dashboard principale
│       ├── index.html          # Editor test case
│       ├── generate_tests.html # Generatore AI
│       ├── config.html         # ⭐ Configurazione LLM (NUOVO)
│       └── reports.html        # Viewer report
│
├── 🧪 TEST ENGINE
│   └── tests/
│       ├── test_generator.py       # AI test generation
│       ├── mobile_test_executor.py # Mobile automation
│       └── web_test_executor.py    # Web automation
│
├── 🛠️ UTILITIES
│   └── utilities/
│       ├── excel_utils.py      # Excel I/O operations
│       ├── report_utils.py     # HTML report generation
│       └── ...                 # Altri helper
│
├── 📊 OUTPUT
│   ├── reports/unified/        # Report HTML generati
│   └── screen/                 # Screenshot test failures
│
└── 📚 DOCS
    └── docs/                   # Documentazione aggiuntiva
```

---

## 📋 Requisiti Sistema

### Software Necessario

| Component | Versione | Scopo |
|-----------|----------|-------|
| **Python** | 3.11+ | Runtime principale |
| **Node.js** | Latest LTS | Appium Server |
| **Chromium** | Latest | Web testing |
| **Appium** | 2.0+ | Mobile testing |

### File Excel - Struttura Colonne

```
TestID | Descrizione | Task | Active | Device | Execution | Platform
DeviceName | UDID | AppID | AppPackage | AppActivity
```

> 💡 **Tip**: L'editor web crea automaticamente la struttura corretta!

---

## 🎓 Guida d'Uso

### Esempio: Creare un Test da Zero

1. **Configura il tuo LLM** (prima volta):
   - Vai su "Configurazione"
   - Seleziona il provider (es. Gemini)
   - Inserisci l'API key
   - Salva

2. **Genera con AI**:
   - Vai su "Genera Test Case"
   - Carica `requisiti.txt`
   - Seleziona `prompt_costruisci_test.txt`
   - Click "Genera" e attendi

3. **Modifica nell'Editor**:
   - Apri il CSV generato
   - Affina le descrizioni
   - Imposta `Active=TRUE`

4. **Esegui**:
   - Click "Avvia Test"
   - Monitora log in tempo reale
   - Controlla screenshot in caso di errori

5. **Analizza Report**:
   - Vai su "Vedi Report"
   - Apri il report HTML
   - Analizza metriche e failures

---

## 🤖 Configurazione Multi-LLM

### Provider Supportati

<details>
<summary><b>🌟 Google Gemini (Raccomandato)</b></summary>

**Pro:**
- ✅ Free tier generoso
- ✅ Ottima qualità/prezzo
- ✅ Veloce e affidabile
- ✅ Modelli vision inclusi

**Setup:**
```bash
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash  # o gemini-2.0-pro
WEB_LLM_PROVIDER=gemini
```

**Ottieni la key:** [Google AI Studio](https://makersuite.google.com/app/apikey)
</details>

<details>
<summary><b>🔵 OpenAI</b></summary>

**Pro:**
- ✅ Modelli più avanzati (GPT-4)
- ✅ Documentazione eccellente
- ✅ Supporto enterprise

**Setup:**
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini  # o gpt-4
WEB_LLM_PROVIDER=openai
```

**Ottieni la key:** [OpenAI Platform](https://platform.openai.com/api-keys)
</details>

<details>
<summary><b>🏠 Ollama (Locale)</b></summary>

**Pro:**
- ✅ Gratuito al 100%
- ✅ Privacy totale
- ✅ Nessun rate limit
- ✅ Offline

**Setup:**
```bash
# 1. Installa Ollama: https://ollama.ai/
# 2. Scarica un modello: ollama pull llava:13b

# In .env:
USE_LOCAL_LLM=true
LOCAL_LLM=llava:13b
OLLAMA_BASE_URL=http://localhost:11434
WEB_LLM_PROVIDER=ollama
```

**Note:** Richiede GPU per prestazioni ottimali.
</details>

### Cambio Provider al Volo

Non serve riavviare l'applicazione:
1. Vai su `/config`
2. Seleziona nuovo provider
3. Inserisci credenziali
4. Salva → Configurazione attiva immediatamente

---

## 🔧 Troubleshooting

<details>
<summary><b>❌ ModuleNotFoundError: No module named 'pandas'</b></summary>

**Causa**: Ambiente virtuale non attivo

**Soluzione**:
```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
python web_editor.py
```
</details>

<details>
<summary><b>❌ TemplateNotFound: config.html</b></summary>

**Causa**: File template mancante

**Soluzione**:
Verifica che la cartella `templates/` esista e contenga:
- `home.html`
- `index.html`
- `generate_tests.html`
- `config.html` ← **nuovo**
- `reports.html`
</details>

<details>
<summary><b>❌ API Key non valida o missing</b></summary>

**Soluzione:**
1. Vai su `/config` nell'interfaccia web
2. Verifica di aver inserito la key corretta
3. Clicca "Salva Configurazione"
4. Prova nuovamente l'esecuzione

**Debug manuale .env:**
```bash
# Verifica .env esiste
ls -la .env              # Mac/Linux
dir .env                 # Windows

# Controlla contenuto
cat .env                 # Mac/Linux
type .env                # Windows
```
</details>

<details>
<summary><b>❌ Cache browser non aggiorna l'interfaccia</b></summary>

**Soluzione**:
```
1. Hard Refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
2. Oppure: Apri finestra in incognito
3. Oppure: Svuota cache browser
```
</details>

<details>
<summary><b>❌ UnicodeEncodeError su Windows</b></summary>

**Soluzione**:
```bash
# Opzione 1: Avvia con UTF-8
python -X utf8 web_editor.py

# Opzione 2: Rimuovi emoji dai file .py
# (cerca caratteri come ✅ 🚀 nei file config_manager.py, main_runner.py)
```
</details>

<details>
<summary><b>❌ llm_models.json non trovato</b></summary>

**Causa**: File di configurazione LLM mancante

**Soluzione**:
Crea il file `llm_models.json` nella root del progetto con questo contenuto:
```json
{
    "gemini": {
        "name": "Google Gemini",
        "fields": [
            { "id": "GOOGLE_API_KEY", "label": "API Key", "type": "password" },
            { "id": "GEMINI_MODEL", "label": "Model Name", "type": "text", "default": "gemini-2.5-flash" }
        ],
        "env_to_set": { "WEB_LLM_PROVIDER": "gemini", "USE_LOCAL_LLM": "false" }
    },
    "openai": {
        "name": "OpenAI",
        "fields": [
            { "id": "OPENAI_API_KEY", "label": "API Key", "type": "password" },
            { "id": "OPENAI_MODEL", "label": "Model Name", "type": "text", "default": "gpt-4.1-mini" }
        ],
        "env_to_set": { "WEB_LLM_PROVIDER": "openai", "USE_LOCAL_LLM": "false" }
    },
    "ollama": {
        "name": "Ollama (Locale)",
        "fields": [
            { "id": "LOCAL_LLM", "label": "Model Name", "type": "text", "default": "llava:13b" },
            { "id": "OLLAMA_BASE_URL", "label": "Base URL", "type": "text", "default": "http://localhost:11434" }
        ],
        "env_to_set": { "WEB_LLM_PROVIDER": "ollama", "USE_LOCAL_LLM": "true" }
    }
}
```
</details>

---

## 🤝 Contribuire

Contributi benvenuti! Per contribuire:

1. Fork del repository
2. Crea un branch (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push del branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

---

## 📚 Risorse

- 📖 **Documentazione Completa**: Vedi cartella [`docs/`](docs/)
- 🎥 **Video Tutorial**: [Coming Soon]
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/pdellibergoli/ai-test-automation/issues)

---

## 🛠️ Stack Tecnologico

| Categoria | Tecnologie |
|-----------|------------|
| **Backend** | Python, Flask |
| **Testing** | Appium, Playwright, Browser-Use |
| **AI/ML** | LangChain, Google Gemini, OpenAI, Ollama |
| **Data** | Pandas, Excel |
| **Frontend** | Bootstrap 5, JavaScript |
| **Cloud** | LambdaTest Integration |

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **MIT License** - vedi il file [LICENSE](LICENSE) per dettagli.

---

## 🙏 Ringraziamenti

Un grazie speciale a:

- [**Browser-Use**](https://github.com/browser-use/browser-use) - Web automation framework
- [**App-Use**](https://github.com/app-use/app-use) - Mobile automation utilities
- [**Appium**](https://appium.io/) - Cross-platform mobile testing
- [**Flask**](https://flask.palletsprojects.com/) - Web framework
- [**Pandas**](https://pandas.pydata.org/) - Data manipulation
- [**LangChain**](https://www.langchain.com/) - AI orchestration

---

<div align="center">

### Made with ❤️ by [Pasquale Delli Bergoli](mailto:pasquale.dellibergoli91@gmail.com)

[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/pdellibergoli)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/pasquale-delli-bergoli/)

**⭐ Se ti piace questo progetto, lascia una star!**

</div>
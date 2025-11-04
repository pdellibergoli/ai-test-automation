"""
Configuration Manager - Gestione centralizzata della configurazione
Carica e valida tutte le impostazioni da .env e fornisce accesso type-safe
"""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Definisci il percorso del file .env nella root del progetto
ENV_PATH = Path(__file__).parent / '.env'

class ConfigurationError(Exception):
    """Eccezione custom per errori di configurazione."""
    pass

class Config:
    """
    Classe per gestire la configurazione dell'applicazione.
    NON è più un singleton. Carica i valori da .env ogni volta che viene istanziata.
    """
    
    def __init__(self):
        # Carica (o ricarica) le variabili da .env
        # override=True assicura che le variabili già presenti in os.environ vengano aggiornate
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        self._load_config()
    
    def _load_config(self):
        """Carica la configurazione dalle variabili d'ambiente."""
        # ===== LLM Configuration =====
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        self.use_local_llm = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.local_llm_model = os.getenv("LOCAL_LLM", "llava:13b")
        # Aggiungiamo OLLAMA_BASE_URL se non presente
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.web_llm_provider = os.getenv("WEB_LLM_PROVIDER", "gemini").lower()
        
        # ===== Mobile Testing =====
        self.lt_username = os.getenv("LT_USERNAME", "")
        self.lt_access_key = os.getenv("LT_ACCESS_KEY", "")
        
        # ===== Browser Configuration =====
        self.browser_headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
        self.browser_logging_level = os.getenv("BROWSER_USE_LOGGING_LEVEL", "info").upper()
        
        # ===== Appium Configuration =====
        self.appium_server_url = os.getenv("APPIUM_SERVER_URL", "http://localhost:4723")
        
        # ===== Paths =====
        self.project_root = Path(__file__).parent
        self.report_dir = Path(os.getenv("REPORT_DIR", self.project_root / "reports" / "unified"))
        self.screen_dir = self.project_root / "screen"
        
        # ===== Misc =====
        self.anonymized_telemetry = os.getenv("ANONYMIZED_TELEMETRY", "false").lower() == "true"
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # ... (tutte le altre funzioni della classe Config rimangono invariate) ...
    def validate_mobile_config(self, execution_mode: str = "local") -> tuple[bool, str]:
        if execution_mode.lower() == "cloud":
            if not self.lt_username or not self.lt_access_key:
                return False, "LambdaTest credentials missing: set LT_USERNAME and LT_ACCESS_KEY in .env"
        return True, ""
    
    def validate_web_config(self) -> tuple[bool, str]:
        provider = self.web_llm_provider
        
        if provider == "gemini":
            if not self.google_api_key:
                return False, "Google API key missing: set GOOGLE_API_KEY in .env"
        elif provider == "openai":
            if not self.openai_api_key:
                return False, "OpenAI API key missing: set OPENAI_API_KEY in .env"
        elif provider == "ollama":
            if not self.local_llm_model:
                return False, "Ollama model not specified: set LOCAL_LLM in .env"
        else:
            return False, f"Invalid WEB_LLM_PROVIDER: {provider}. Use 'gemini', 'openai', or 'ollama'"
        return True, ""
    
    def get_lambdatest_url(self) -> str:
        if not self.lt_username or not self.lt_access_key:
            raise ConfigurationError("LambdaTest credentials not configured")
        return f"https://{self.lt_username}:{self.lt_access_key}@mobile-hub.lambdatest.com/wd/hub"
    
    def print_config_summary(self):
        print("\n" + "="*70); print("⚙️  CONFIGURATION SUMMARY"); print("="*70)
        print("\n📱 Mobile Testing:")
        print(f"   Appium Server: {self.appium_server_url}")
        print(f"   LambdaTest: {'✅ Configured (' + self.lt_username + ')' if self.lt_username else '❌ Not configured'}")
        print("\n🌐 Web Testing:")
        print(f"   LLM Provider: {self.web_llm_provider}")
        print(f"   Browser Headless: {self.browser_headless}")
        print("\n🤖 LLM Configuration:")
        if self.use_local_llm:
            print(f"   Mode: Local (Ollama)")
            print(f"   Model: {self.local_llm_model}")
            print(f"   Base URL: {self.ollama_base_url}")
        elif self.web_llm_provider == "gemini":
            print(f"   Provider: Google Gemini"); print(f"   Model: {self.gemini_model}")
            print(f"   API Key: {'✅ Set' if self.google_api_key else '❌ Missing'}")
        elif self.web_llm_provider == "openai":
            print(f"   Provider: OpenAI"); print(f"   Model: {self.openai_model}")
            print(f"   API Key: {'✅ Set' if self.openai_api_key else '❌ Missing'}")
        print("\n📁 Paths:"); print(f"   Project Root: {self.project_root}"); print(f"   Reports: {self.report_dir}"); print(f"   Screenshots: {self.screen_dir}")
        print("\n🔧 Other:"); print(f"   Debug Mode: {self.debug_mode}"); print(f"   Logging Level: {self.browser_logging_level}")
        print("\n" + "="*70 + "\n")
    
    def check_required_env_vars(self) -> list[str]:
        missing = []
        if self.web_llm_provider == "gemini" and not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        elif self.web_llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        return missing

# ===== Helper Functions =====

def get_config() -> Config:
    """
    Ottiene una NUOVA istanza della configurazione, ricaricando da .env.
    
    Returns:
        Nuova istanza Config
    """
    # Rimuovendo il singleton, ogni chiamata ricarica le impostazioni da .env
    return Config() 

# ... (il resto delle funzioni 'validate_environment', 'setup_logging', e il blocco __main__ rimangono invariati) ...
def validate_environment() -> bool:
    config = get_config()
    missing = config.check_required_env_vars()
    if missing:
        print("❌ Variabili d'ambiente mancanti:"); [print(f"   - {var}") for var in missing]
        print("\n💡 Aggiungi queste variabili al file .env o salvale nella pagina di Configurazione.")
        return False
    print("✅ Configurazione ambiente validata con successo")
    return True

def setup_logging():
    import logging
    config = get_config()
    level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
    log_level = level_map.get(config.browser_logging_level, logging.INFO)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if config.debug_mode:
        logging.getLogger().setLevel(logging.DEBUG); print("🐛 Debug mode enabled")

if __name__ == "__main__":
    print("Test Gestore Configurazione...")
    config = get_config()
    config.print_config_summary()
    validate_environment()
    print("\n✅ Configuration test completed!")
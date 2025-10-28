"""
Configuration Manager - Gestione centralizzata della configurazione
Carica e valida tutte le impostazioni da .env e fornisce accesso type-safe
"""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Eccezione custom per errori di configurazione."""
    pass


class Config:
    """
    Classe singleton per gestire la configurazione dell'applicazione.
    Carica variabili da .env e fornisce accesso type-safe.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_config()
            self._initialized = True
    
    def _load_config(self):
        """Carica la configurazione dal file .env"""
        # Load .env file
        load_dotenv()
        
        # ===== LLM Configuration =====
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        self.use_local_llm = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.local_llm_model = os.getenv("LOCAL_LLM", "llava:13b")
        
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
    
    # ===== Validation Methods =====
    
    def validate_mobile_config(self, execution_mode: str = "local") -> tuple[bool, str]:
        """
        Valida la configurazione per test mobile.
        
        Args:
            execution_mode: "local" o "cloud"
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if execution_mode.lower() == "cloud":
            if not self.lt_username or not self.lt_access_key:
                return False, "LambdaTest credentials missing: set LT_USERNAME and LT_ACCESS_KEY in .env"
        
        return True, ""
    
    def validate_web_config(self) -> tuple[bool, str]:
        """
        Valida la configurazione per test web.
        
        Returns:
            Tuple (is_valid, error_message)
        """
        provider = self.web_llm_provider
        
        if provider == "gemini":
            if not self.google_api_key:
                return False, "Google API key missing: set GOOGLE_API_KEY in .env"
        elif provider == "openai":
            if not self.openai_api_key:
                return False, "OpenAI API key missing: set OPENAI_API_KEY in .env"
        elif provider == "ollama":
            # Ollama doesn't need API key, but check if model is specified
            if not self.local_llm_model:
                return False, "Ollama model not specified: set LOCAL_LLM in .env"
        else:
            return False, f"Invalid WEB_LLM_PROVIDER: {provider}. Use 'gemini', 'openai', or 'ollama'"
        
        return True, ""
    
    def get_lambdatest_url(self) -> str:
        """
        Costruisce l'URL completo per LambdaTest.
        
        Returns:
            URL formattato per LambdaTest
        """
        if not self.lt_username or not self.lt_access_key:
            raise ConfigurationError("LambdaTest credentials not configured")
        
        return f"https://{self.lt_username}:{self.lt_access_key}@mobile-hub.lambdatest.com/wd/hub"
    
    # ===== Display Methods =====
    
    def print_config_summary(self):
        """Stampa un summary della configurazione attuale."""
        print("\n" + "="*70)
        print("⚙️  CONFIGURATION SUMMARY")
        print("="*70)
        
        print("\n📱 Mobile Testing:")
        print(f"   Appium Server: {self.appium_server_url}")
        if self.lt_username:
            print(f"   LambdaTest: ✅ Configured ({self.lt_username})")
        else:
            print(f"   LambdaTest: ❌ Not configured")
        
        print("\n🌐 Web Testing:")
        print(f"   LLM Provider: {self.web_llm_provider}")
        print(f"   Browser Headless: {self.browser_headless}")
        
        print("\n🤖 LLM Configuration:")
        if self.use_local_llm:
            print(f"   Mode: Local (Ollama)")
            print(f"   Model: {self.local_llm_model}")
        else:
            if self.web_llm_provider == "gemini":
                print(f"   Provider: Google Gemini")
                print(f"   Model: {self.gemini_model}")
                print(f"   API Key: {'✅ Set' if self.google_api_key else '❌ Missing'}")
            elif self.web_llm_provider == "openai":
                print(f"   Provider: OpenAI")
                print(f"   Model: {self.openai_model}")
                print(f"   API Key: {'✅ Set' if self.openai_api_key else '❌ Missing'}")
        
        print("\n📁 Paths:")
        print(f"   Project Root: {self.project_root}")
        print(f"   Reports: {self.report_dir}")
        print(f"   Screenshots: {self.screen_dir}")
        
        print("\n🔧 Other:")
        print(f"   Debug Mode: {self.debug_mode}")
        print(f"   Telemetry: {'Enabled' if self.anonymized_telemetry else 'Disabled'}")
        print(f"   Logging Level: {self.browser_logging_level}")
        
        print("\n" + "="*70 + "\n")
    
    def check_required_env_vars(self) -> list[str]:
        """
        Controlla quali variabili d'ambiente richieste sono mancanti.
        
        Returns:
            Lista di nomi delle variabili mancanti
        """
        missing = []
        
        # Check LLM credentials based on provider
        if self.web_llm_provider == "gemini" and not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        elif self.web_llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        
        return missing


# ===== Helper Functions =====

def get_config() -> Config:
    """
    Ottiene l'istanza singleton della configurazione.
    
    Returns:
        Istanza Config
    """
    return Config()


def validate_environment() -> bool:
    """
    Valida che tutte le variabili d'ambiente necessarie siano presenti.
    
    Returns:
        True se la configurazione è valida, False altrimenti
    """
    config = get_config()
    missing = config.check_required_env_vars()
    
    if missing:
        print("❌ Variabili d'ambiente mancanti:")
        for var in missing:
            print(f"   - {var}")
        print("\n💡 Aggiungi queste variabili al file .env")
        return False
    
    print("✅ Configurazione ambiente validata con successo")
    return True


def setup_logging():
    """
    Configura il logging in base alle impostazioni di configurazione.
    """
    import logging
    
    config = get_config()
    
    # Map string level to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level = level_map.get(config.browser_logging_level, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if config.debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug mode enabled")


# ===== Example Usage =====

if __name__ == "__main__":
    """
    Test della configurazione - esegui questo script per verificare le impostazioni
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║            CONFIGURATION MANAGER - Test                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Load configuration
    config = get_config()
    
    # Print summary
    config.print_config_summary()
    
    # Validate environment
    print("🔍 Validating environment...")
    is_valid = validate_environment()
    
    if not is_valid:
        print("\n❌ Configurazione non valida - correggere gli errori nel file .env")
        exit(1)
    
    # Test mobile config validation
    print("\n🧪 Testing mobile configuration validation...")
    is_valid, msg = config.validate_mobile_config("local")
    print(f"   Local mode: {'✅' if is_valid else '❌'} {msg if msg else ''}")
    
    is_valid, msg = config.validate_mobile_config("cloud")
    print(f"   Cloud mode: {'✅' if is_valid else '❌'} {msg if msg else ''}")
    
    # Test web config validation
    print("\n🧪 Testing web configuration validation...")
    is_valid, msg = config.validate_web_config()
    print(f"   Web config: {'✅' if is_valid else '❌'} {msg if msg else ''}")
    
    print("\n✅ Configuration test completed!")
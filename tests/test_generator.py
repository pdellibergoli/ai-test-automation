import sys
from pathlib import Path
import os
import re
import argparse  # Aggiunto per gli argomenti da riga di comando
import json      # Aggiunto per stampare l'output JSON

# Aggiungi la root del progetto al sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from config_manager import get_config
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    from langchain_community.chat_models import ChatOllama
    from langchain.schema import HumanMessage, SystemMessage
except ImportError as e:
    print(f"Errore: Manca una libreria necessaria: {e}", file=sys.stderr)
    print("Esegui 'pip install -r requirements.txt' per installare le dipendenze mancanti.")
    ChatGoogleGenerativeAI = None; ChatOpenAI = None; ChatOllama = None

class TestGenerator:
    """
    Utilizza un LLM per generare casi di test strutturati basati sul contenuto
    testuale dei requisiti e di un prompt.
    """
    
    def __init__(self):
        if not all([ChatGoogleGenerativeAI, ChatOpenAI, ChatOllama]):
            raise ImportError("Alcune librerie LLM non sono state caricate. Controlla l'installazione.")
        self.config = get_config()
        self.llm = self._setup_llm()

    def _setup_llm(self):
        """ Configura l'LLM in base a .env """
        provider = self.config.web_llm_provider
        
        if self.config.use_local_llm or provider == "ollama":
            model = self.config.local_llm_model or "llava:13b"
            print(f"🤖 [TestGenerator] Usando Ollama locale: {model}", file=sys.stderr)
            return ChatOllama(model=model, temperature=0.2)
        elif provider == "openai":
            if not self.config.openai_api_key:
                raise ValueError("Provider 'openai' selezionato, ma OPENAI_API_KEY non trovato in .env")
            model = self.config.openai_model or "gpt-4.1-mini"
            print(f"🤖 [TestGenerator] Usando OpenAI: {model}", file=sys.stderr)
            return ChatOpenAI(model=model, api_key=self.config.openai_api_key, temperature=0.2)
        elif provider == "gemini":
            if not self.config.google_api_key:
                raise ValueError("Provider 'gemini' selezionato, ma GOOGLE_API_KEY non trovato in .env")
            model = self.config.gemini_model or "gemini-2.5-flash"
            print(f"🤖 [TestGenerator] Usando Google Gemini: {model}", file=sys.stderr)
            return ChatGoogleGenerativeAI(model=model, google_api_key=self.config.google_api_key, temperature=0.2)
        else:
            raise ValueError(f"Provider LLM '{provider}' non supportato. Controlla WEB_LLM_PROVIDER in .env.")

    def _read_file_content(self, file_path: Path):
        """Legge il contenuto di un file di testo."""
        if not file_path.exists():
            raise FileNotFoundError(f"File non trovato: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Errore durante la lettura di {file_path}: {e}")

    def _parse_ai_output(self, raw_text: str) -> list[dict]:
        """ Converte l'output testuale dell'AI in un elenco strutturato. """
        test_cases = []
        pattern = re.compile(r"Descrizione:\s*(.*?)\s*Task:\s*(.*?)(?=\nDescrizione:|\Z)", re.DOTALL)
        matches = pattern.findall(raw_text)
        
        if not matches:
            parts = raw_text.split("Descrizione:")[1:]
            for part in parts:
                if "Task:" in part:
                    try:
                        desc, task = part.split("Task:", 1)
                        desc = desc.strip().lstrip("- .1234567890")
                        task = task.strip()
                        if desc and task: test_cases.append({"Descrizione": desc, "Task": task})
                    except ValueError: continue
        else:
            for desc, task in matches:
                desc = desc.strip().lstrip("- .1234567890")
                task = task.strip()
                if desc and task: test_cases.append({"Descrizione": desc, "Task": task})
        return test_cases

    def generate_tests(self, requirements_path_str: str, additional_prompt_path_str: str) -> list[dict]:
        """ Genera i casi di test leggendo i due file di input (come percorsi). """
        requirements_file = project_root / requirements_path_str
        additional_prompt_file = project_root / additional_prompt_path_str

        requirements_content = self._read_file_content(requirements_file)
        additional_prompt_content = self._read_file_content(additional_prompt_file)
        
        system_message = SystemMessage(content="Sei un esperto Analista QA...") # Prompt abbreviato per brevità
        user_prompt = f"""
        --- REQUISITI DEL SOFTWARE ---
        {requirements_content}
        --- ISTRUZIONI AGGIUNTIVE (PROMPT) ---
        {additional_prompt_content}
        ---
        Basandoti su ENTRAMBI i documenti, genera la lista dei casi di test:
        """
        user_message = HumanMessage(content=user_prompt)

        print(f"🧠 Chiamata all'LLM per la generazione dei test...", file=sys.stderr) # Stampa su stderr per i log

        try:
            response = self.llm.invoke([system_message, user_message])
            raw_text = response.content
            structured_tests = self._parse_ai_output(raw_text)
            
            if not structured_tests and raw_text:
                print("ATTENZIONE: Parsing dell'output AI fallito.", file=sys.stderr)
                return [{"Descrizione": "Errore di Parsing - Output Grezzo", "Task": raw_text}]
                
            return structured_tests
            
        except Exception as e:
            print(f"❌ Errore durante la chiamata all'LLM: {e}", file=sys.stderr)
            raise

# --- BLOCCO DI ESECUZIONE (NUOVO) ---
if __name__ == "__main__":
    """
    Questo blocco viene eseguito quando si lancia:
    > python tests/test_generator.py --req-file ... --prompt-file ...
    """
    parser = argparse.ArgumentParser(description="Generatore di Test Case AI")
    parser.add_argument('--req-file', type=str, required=True, help='Nome file requisiti')
    parser.add_argument('--prompt-file', type=str, required=True, help='Nome file prompt')
    args = parser.parse_args()

    try:
        # 1. Avvia il generatore
        generator = TestGenerator()
        
        # 2. Genera i test
        test_cases = generator.generate_tests(args.req_file, args.prompt_file)
        
        # 3. Stampa un marcatore speciale
        print("---JSON_RESULT_START---", file=sys.stderr) # Log per il server
        
        # 4. Stampa il JSON finale su STDOUT
        # Questo è l'unico output che il frontend leggerà come "dati"
        print(json.dumps(test_cases)) 
        
    except Exception as e:
        # Stampa l'errore su STDERR in modo che appaia nei log
        print(f"ERRORE_GENERAZIONE: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
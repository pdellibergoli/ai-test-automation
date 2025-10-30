import sys
from pathlib import Path
import os
import re # Importa il modulo per le espressioni regolari

# Aggiungi la root del progetto al sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from config_manager import get_config
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
except ImportError as e:
    print(f"Errore: Manca una libreria necessaria: {e}", file=sys.stderr)
    # Non usiamo sys.exit() per permettere al server web di gestire l'errore
    ChatGoogleGenerativeAI = None # Imposta a None se l'import fallisce

class TestGenerator:
    """
    Utilizza un LLM per generare casi di test strutturati basati sul contenuto
    testuale dei requisiti e di un prompt.
    """
    
    def __init__(self):
        if ChatGoogleGenerativeAI is None:
            raise ImportError("Librerie LLM non trovate. Esegui 'pip install langchain-google-genai'")
            
        self.config = get_config()
        self.llm = self._setup_llm()

    def _setup_llm(self):
        if self.config.google_api_key:
            model_name = self.config.gemini_model or "gemini-2.5-flash"
            return ChatGoogleGenerativeAI(
                model=model_name, 
                google_api_key=self.config.google_api_key,
                temperature=0.2
            )
        raise ValueError("Nessun provider LLM (es. GOOGLE_API_KEY) configurato in .env.")

    def _parse_ai_output(self, raw_text: str) -> list[dict]:
        """
        Converte l'output testuale dell'AI in un elenco strutturato di dizionari.
        Si aspetta un formato "Descrizione: ... Task: ..."
        """
        test_cases = []
        
        # Pattern Regex per cercare "Descrizione: [contenuto] Task: [contenuto]"
        # re.DOTALL fa sì che '.' includa anche i caratteri "a capo"
        pattern = re.compile(r"Descrizione:\s*(.*?)\s*Task:\s*(.*?)(?=\nDescrizione:|\Z)", re.DOTALL)
        
        matches = pattern.findall(raw_text)
        
        if not matches:
            # Fallback se il pattern principale non funziona
            parts = raw_text.split("Descrizione:")[1:]
            for part in parts:
                if "Task:" in part:
                    try:
                        desc, task = part.split("Task:", 1)
                        # Pulisce gli spazi e i numeri/punti iniziali
                        desc = desc.strip().lstrip("- .1234567890")
                        task = task.strip()
                        if desc and task:
                            test_cases.append({"Descrizione": desc, "Task": task})
                    except ValueError:
                        continue # Ignora parti malformate
        else:
            for desc, task in matches:
                desc = desc.strip().lstrip("- .1234567890")
                task = task.strip()
                if desc and task:
                    test_cases.append({"Descrizione": desc, "Task": task})
                    
        return test_cases

    def generate_tests(self, requirements_content: str, additional_prompt_content: str) -> list[dict]:
        """
        Genera i casi di test basandosi sul *contenuto* testuale dei file.
        
        Args:
            requirements_content (str): Il testo completo del file dei requisiti.
            additional_prompt_content (str): Il testo completo del file prompt aggiuntivo.
            
        Returns:
            list[dict]: Una lista di dizionari {"Descrizione": "...", "Task": "..."}
        """
        
        system_message = SystemMessage(
            content=(
                "Sei un esperto Analista QA. Il tuo compito è generare una lista di casi di test (positivi, negativi, edge-case) "
                "basandoti sui requisiti e sulle istruzioni aggiuntive. "
                "Per ogni test, fornisci una 'Descrizione:' e un 'Task:'. "
                "Il 'Task' deve essere una istruzione chiara in linguaggio naturale per un AI agent."
                "IMPORTANTE: Separa ogni caso di test iniziando con 'Descrizione:' seguito da 'Task:'."
            )
        )
        user_prompt = f"""
        --- REQUISITI DEL SOFTWARE ---
        {requirements_content}
        
        --- ISTRUZIONI AGGIUNTIVE (PROMPT) ---
        {additional_prompt_content}
        
        ---
        Basandoti su ENTRAMBI i documenti, genera la lista dei casi di test:
        """
        user_message = HumanMessage(content=user_prompt)

        print(f"🧠 Chiamata all'LLM per la generazione dei test...")

        try:
            response = self.llm.invoke([system_message, user_message])
            raw_text = response.content
            
            # Parsifichiamo l'output
            structured_tests = self._parse_ai_output(raw_text)
            
            if not structured_tests and raw_text:
                # Se il parsing fallisce ma abbiamo testo, restituiscilo in un formato di emergenza
                print("ATTENZIONE: Parsing dell'output AI fallito. Restituisco output grezzo.")
                return [{"Descrizione": "Errore di Parsing - Output Grezzo", "Task": raw_text}]
                
            return structured_tests
            
        except Exception as e:
            print(f"❌ Errore durante la chiamata all'LLM: {e}", file=sys.stderr)
            raise # Rilancia l'eccezione così l'API può gestirla
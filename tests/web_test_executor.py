"""
Web Test Executor - Gestisce l'esecuzione dei test web
Estratto e refactorizzato da web_AI_test.py
"""
import os
import sys
from pathlib import Path
import asyncio
import logging
import traceback
from PIL import Image

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from browser_use import Agent, Browser, ChatOllama, ChatOpenAI, ChatGoogle
from browser_use.browser.events import ScreenshotEvent
from utilities import utils
from utilities.report_utils import TestCase
from dotenv import load_dotenv


class WebTestExecutor:
    """
    Executor per test web su browser.
    Gestisce la configurazione Browser-Use e l'esecuzione degli agenti AI.
    """
    
    def __init__(self, report_generator, output_dir):
        """
        Inizializza l'executor web.
        
        Args:
            report_generator: Istanza di HTMLReportGenerator
            output_dir: Directory per output e screenshot
        """
        load_dotenv()
        self.report = report_generator
        self.output_dir = Path(output_dir)
        self.project_root = project_root
        self.execution_step_gif = self.project_root / 'agent_history.gif'
        
        # Load system prompt
        self.system_prompt = self.load_system_prompt()
        
        # Optimization prompt for faster execution
        self.optimization_prompt = """
        - Convert prompt into Playwright concise commands
        - Get to the goal as quickly as possible
        """
        
        # Initialize browser instance (reused across tests)
        self.browser = None
        
        logging.basicConfig(level=logging.INFO)
    
    def load_system_prompt(self) -> str:
        """
        Carica il system prompt dal file se disponibile.
        
        Returns:
            Contenuto del system prompt o stringa vuota
        """
        prompt_file = self.project_root / "system_prompt.txt"
        
        if prompt_file.exists():
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                print("✅ System prompt caricato dal file")
                return content
            except Exception as e:
                print(f"⚠️  Impossibile leggere system_prompt.txt: {e}")
                return ""
        else:
            print("ℹ️  File system_prompt.txt non trovato, uso prompt di default")
            return ""
    
    def get_browser_instance(self) -> Browser:
        """
        Ottiene o crea l'istanza del browser.
        Il browser viene riutilizzato tra i test per efficienza.
        
        Returns:
            Istanza Browser configurata
        """
        if self.browser is None:
            self.browser = Browser(
                minimum_wait_page_load_time=0.1,
                wait_between_actions=0.1,
                enable_default_extensions=True,
                headless=False  # Set to True for headless mode
            )
            print("🌐 Browser instance creata")
        
        return self.browser
    
    def create_llm_instance(self):
        """
        Crea l'istanza del modello LLM per l'agente.
        
        Returns:
            Istanza del modello LLM configurato
        """
        # You can switch between different LLM providers
        llm_provider = os.getenv("WEB_LLM_PROVIDER", "gemini").lower()
        
        if llm_provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            print(f"🤖 Usando OpenAI: {model}")
            return ChatOpenAI(model=model)
            
        elif llm_provider == "ollama":
            model = os.getenv("LOCAL_LLM", "gemma3:4b")
            print(f"🤖 Usando Ollama locale: {model}")
            return ChatOllama(model=model)
            
        else:  # default to Gemini
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            print(f"🤖 Usando Google Gemini: {model}")
            return ChatGoogle(model=model)
    
    async def execute(self, data: dict):
        """
        Esegue un test web completo.
        
        Args:
            data: Dizionario con tutti i parametri del test
        """
        test_id = data['TestID']
        descrizione = data['Descrizione']
        task = data['Task']
        
        print(f"🌐 Inizializzazione test web: {test_id}")
        
        # Setup
        step_counter = {"i": 0}
        current_test = TestCase(test_id, descrizione)
        
        # Clean screenshots folder
        screen_dir = self.project_root / "screen/web"
        screen_dir.mkdir(parents=True, exist_ok=True)
        utils.clean_img_folder(screen_dir)
        
        # Get browser and LLM
        browser = self.get_browser_instance()
        llm = self.create_llm_instance()
        
        try:
            # Create Agent
            agent = Agent(
                task,
                browser=browser,
                llm=llm,
                use_vision=True,
                file_system_path=str(self.project_root),
                generate_gif=True,
                extend_system_message=self.optimization_prompt,
                temperature=0.1
            )
            
            # Define step hook for screenshots
            async def step_hook(agent: Agent):
                try:
                    # Take screenshot using Browser-Use event system
                    screenshot_event = agent.browser_session.event_bus.dispatch(
                        ScreenshotEvent(full_page=False)
                    )
                    await screenshot_event
                    result = await screenshot_event.event_result(
                        raise_if_any=True, 
                        raise_if_none=True
                    )
                    
                    # Convert base64 to image file
                    img_path = utils.base64_to_image(
                        base64_string=str(result),
                        output_filename=screen_dir / f"step_{step_counter['i']}.jpg"
                    )
                    
                    # Resize image for report
                    with Image.open(img_path) as img:
                        img_resized = img.resize((1200, 675), Image.Resampling.HAMMING)
                        img_resized.save(img_path)
                    
                    # Add step to test case
                    current_test.add_step(
                        f"Step - {step_counter['i']}", 
                        img_path, 
                        False
                    )
                    step_counter["i"] += 1
                    
                except Exception as e:
                    print(f'❌ Error in step hook: {e}')
                    traceback.print_exc()
            
            # Run agent
            print(f"🚀 Esecuzione agente per task: {task[:50]}...")
            history = await agent.run(on_step_start=step_hook)
            
            # Check result
            if history.is_successful():
                print(f'✅ Test {test_id} completato con successo')
            else:
                print(f"⚠️  Test {test_id} non completato")
                step_counter["i"] -= 1
                screen_path = screen_dir / f"step_{step_counter['i']}.jpg"
                current_test.add_step("Step - FAILED", screen_path, True)
            
            # Add execution GIF
            if self.execution_step_gif.exists():
                current_test.add_step("Execution steps", self.execution_step_gif, False)
            
            # Add to report
            self.report.add_test_case_result(current_test)
            
            print(f'📊 Final result: {history.final_result()}')
            
        except Exception as e:
            print(f'❌ Errore durante esecuzione test {test_id}: {e}')
            traceback.print_exc()
            
            # Add failure to report
            current_test.add_step("EXECUTION ERROR", None, True)
            self.report.add_test_case_result(current_test)
    
    async def cleanup(self):
        """
        Cleanup delle risorse del browser.
        Da chiamare alla fine di tutti i test.
        """
        if self.browser is not None:
            try:
                print("🧹 Chiusura browser...")
                await self.browser.stop()
                self.browser = None
            except Exception as e:
                print(f"⚠️  Errore durante chiusura browser: {e}")
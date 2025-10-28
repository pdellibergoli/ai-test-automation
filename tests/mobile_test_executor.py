"""
Mobile Test Executor - Gestisce l'esecuzione dei test mobile
Estratto e refactorizzato da mobile_AI_test.py
"""
import os
import sys
from pathlib import Path
import asyncio
import logging
import traceback
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app_use import Agent
from app_class import App
from utilities import utils, set_capabilities
from utilities.report_utils import TestCase
from dotenv import load_dotenv
from browser_use import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

# Carica il .env nella shell
load_dotenv() 

class MobileTestExecutor:
    """
    Executor per test mobile su dispositivi iOS/Android.
    Gestisce la configurazione Appium e l'esecuzione degli agenti AI.
    """
    
    def __init__(self, report_generator, output_dir):
        """
        Inizializza l'executor mobile.
        
        Args:
            report_generator: Istanza di HTMLReportGenerator
            output_dir: Directory per output e screenshot
        """
        load_dotenv()
        self.report = report_generator
        self.output_dir = Path(output_dir)
        self.project_root = project_root
        self.execution_step_gif = self.project_root / 'agent_history.gif'
        
        logging.basicConfig(level=logging.INFO)
        
    def setup_app_instance(self, data: dict) -> tuple[App, dict]:
        """
        Configura l'istanza App con le capabilities appropriate.
        
        Args:
            data: Dizionario con i dati di configurazione del test
            
        Returns:
            Tupla (app_instance, driver)
        """
        try:
            execution = data.get('Execution', '').lower()
            platform = data['Platform']
            device_name = data['DeviceName']
            udid = data.get('UDID', '')
            app_id = data.get('AppID', '')
            app_package = data.get('AppPackage', '')
            app_activity = data.get('AppActivity', '')
            test_id = data['TestID']
            descrizione = data['Descrizione']
        except KeyError as e:
            raise ValueError(f"Missing required test configuration parameter: {e}")
        
        
        # Determine execution mode (local or cloud)
        if execution == 'local':
            custom_caps = set_capabilities.set_appium_caps(
                platform, device_name, udid, app_package, app_activity
            )
            appium_server_url = 'http://localhost:4723'
            print(f"🖥️  Configurazione LOCALE - Appium: {appium_server_url}")
            
        else:
            # Cloud execution (LambdaTest)
            custom_caps = set_capabilities.set_mobile_cloud_caps(
                platform, device_name, app_id, test_id, descrizione
            )
            lt_username = os.getenv("LT_USERNAME")
            lt_access_key = os.getenv("LT_ACCESS_KEY")
            appium_server_url = f'https://{lt_username}:{lt_access_key}@mobile-hub.lambdatest.com/wd/hub'
            print(f"☁️  Configurazione CLOUD - LambdaTest")
        
        # Create App instance
        app = App(
            appium_server_url=appium_server_url,
            **custom_caps
        )
        
        return app, app.driver
    
    def create_llm_instance(self):
        """
        Crea l'istanza del modello LLM per l'agente.
        
        Returns:
            Istanza del modello LLM configurato
        """
        # You can switch between different LLM providers
        use_local_llm = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        
        if use_local_llm:
            model = os.getenv("LOCAL_LLM", "llava:13b")
            print(f"🤖 Usando LLM locale: {model}")
            return ChatOllama(model=model)
        else:
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            print(f"🤖 Usando Google Gemini: {model}")
            return ChatGoogleGenerativeAI(model=model)
    
    async def execute(self, data: dict):
        """
        Esegue un test mobile completo.
        
        Args:
            data: Dizionario con tutti i parametri del test
        """
        test_id = data['TestID']
        descrizione = data['Descrizione']
        task = data['Task']
        
        print(f"📱 Inizializzazione test mobile: {test_id}")
        
        # Setup
        step_counter = {"i": 0}
        current_test = TestCase(test_id, descrizione)
        
        # Clean screenshots folder
        screen_dir = self.project_root / "screen/mobile"
        screen_dir.mkdir(parents=True, exist_ok=True)
        utils.clean_img_folder(screen_dir)
        
        # Setup App
        app, driver = self.setup_app_instance(data)
        
        # Setup LLM
        llm = self.create_llm_instance()
        
        try:
            # Create Agent
            agent = Agent(
                task,
                llm=llm,
                app=app,
                generate_gif=True,
            )
            
            # Define step hook for screenshots
            async def step_hook(agent: Agent):
                try:
                    screen_path = screen_dir / f"step_{step_counter['i']}.jpg"
                    driver.save_screenshot(screen_path)
                    current_test.add_step(
                        f"Step - {step_counter['i']}", 
                        screen_path, 
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
            
        finally:
            # Cleanup
            print(f"🧹 Cleanup risorse per test {test_id}")
            try:
                await agent.close()
            except:
                pass
            
            try:
                app.close()
            except:
                pass
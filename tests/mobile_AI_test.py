import sys
from pathlib import Path

from browser_use import ChatOllama

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import asyncio
import logging
import pathlib
import os
import traceback
import datetime
import webbrowser

from utilities import set_capabilities
from utilities import utils
from utilities import excel_utils
from utilities.report_utils import HTMLReportGenerator, TestCase
from langchain_google_genai import ChatGoogleGenerativeAI
from app_use import Agent
from app_class import App
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent

class AIAgentMobileTest:
    # Read GOOGLE_API_KEY into env
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    execution_step_gif = project_root / 'agent_history.gif'
    # Crea il generatore di report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / f"reports/mobile/{timestamp}"
    report = HTMLReportGenerator(output_dir)
    report.start_suite("Suite Test")
    excel_file_path = project_root / 'dati_test_app.xlsx'
    list_data = excel_utils.excel_read_data(excel_file_path, 'Foglio1')

    for data in list_data:
        if data['Execution']:
            test_id = data['TestID']
            execution = data['Execution']
            platform = data['Platform']
            device_name = data['DeviceName']
            udid = data['UDID']
            app_id = data['AppID']
            app_package = data['AppPackage']
            app_activity = data['AppActivity']
            descrizione = data['Descrizione']

            if execution.lower() == 'local':
                custom_caps = set_capabilities.set_appium_caps(platform, device_name, udid, app_package, app_activity)
                appium_server_url = 'http://localhost:4723'
            else:
                custom_caps = set_capabilities.set_mobile_cloud_caps(platform, device_name, app_id, test_id, descrizione)
                appium_server_url = f'https://{os.getenv("LT_USERNAME")}:{os.getenv("LT_ACCESS_KEY")}@mobile-hub.lambdatest.com/wd/hub'

            app = App(
                appium_server_url=appium_server_url,
                **custom_caps  # Questo passa tutte le chiavi e i valori del dizionario
            )
            driver = app.driver
            step_counter = {"i": 0}
            current_test = TestCase(data['TestID'], data['Descrizione'])
        
            # Clean di tutte le .jpg
            utils.clean_img_folder(project_root / "screen/mobile")
            # Get command task
            task = data['Task']

            async def Validation(task, app, driver, current_test, step_counter, data, descrizione, execution_step_gif, report):     
                # Create agent with the model
                agent = Agent(
                    task,
                    #llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL")),
                    llm = ChatOllama(model=os.getenv("LOCAL_LLM")),
                    app=app,
                    generate_gif=True,  # Enable GIF generation for actions
                )
                # Define the hook function
                async def my_step_hook(agent: Agent):
                    try:
                        screen_path = project_root / f"screen/mobile/step_{step_counter['i']}.jpg"
                        driver.save_screenshot(screen_path)
                        current_test.add_step(f"Step - {step_counter['i']}", screen_path, False)
                        step_counter["i"] += 1
                    except Exception as e:
                        print(f'❌ Error: {e}')
                        traceback.print_exc()  
                try:
                    history = await agent.run(on_step_start=my_step_hook)
                    if history.is_successful():
                        print(f'✅ Agent successfully completed the {data['TestID']} - {descrizione}')
                    else:
                        print("⚠️ Agent couldn't complete the task.")
                        step_counter["i"] -= 1
                        screen_path = project_root / f"screen/mobile/step_{step_counter['i']}.jpg"
                        current_test.add_step(f"Step - FAILED", screen_path, True)
                    #utils.copy_agent_history(SCRIPT_DIR, output_dir, descrizione.replace(" ", "_").lower() + ".gif")
                    current_test.add_step(f"Execution steps", execution_step_gif, False)
                    report.add_test_case_result(current_test)
                    print(f'Final result: {history.final_result()}')
                except Exception as e:
                    print(f'❌ Error: {e}')
                finally:
                    await agent.close()
                    app.close()

        asyncio.run(Validation(task, app, driver, current_test, step_counter, data, descrizione, execution_step_gif, report))
    #Finalizza il report e ottieni il percorso del file
    final_report_path = report.finalize_report()
    #Apri il file nel browser predefinito
    webbrowser.open_new_tab(final_report_path.as_uri())
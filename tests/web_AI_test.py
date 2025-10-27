import asyncio
import datetime
import pathlib
import os
import sys
import webbrowser
from PIL import Image

project_root = pathlib.Path(__file__).parent.parent
sys.path.append(str(project_root))

from utilities import utils
from utilities import excel_utils
from utilities.report_utils import HTMLReportGenerator, TestCase

from browser_use import Agent, ChatGoogle, Browser, ChatOllama, ChatOpenAI
from dotenv import load_dotenv
from browser_use.browser.events import ScreenshotEvent

project_root = pathlib.Path(__file__).parent.parent

try:
    with open(project_root / "system_prompt.txt", "r", encoding="utf-8") as f:
        llm_prompt = f.read()
    print("✅ System prompt caricato con successo dal file.")
except FileNotFoundError:
    print("❌ Errore: File 'system_prompt.txt' non trovato. Assicurati che sia nella stessa cartella.")
    exit()

class AIAgentWebTest:
    # Read GOOGLE_API_KEY into env
    load_dotenv()
    execution_step_gif = project_root / 'agent_history.gif'
    # Crea il generatore di report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / f"reports/web/{timestamp}"
    report = HTMLReportGenerator(output_dir)
    report.start_suite("Suite Test")
    excel_file_path = project_root / 'dati_test.xlsx'
    list_data = excel_utils.excel_read_data(excel_file_path, 'Foglio1')

    OPTIMIZATION_PROMPT = """
    - Convert prompt into Playwright concise commands
    - Get to the goal as quickly as possible
    """

    browser = Browser(
        minimum_wait_page_load_time=0.1,    # Reduce wait time
        wait_between_actions=0.1,
        enable_default_extensions=True
    )

    for data in list_data:
        if data['Execution']:
            step_counter = {"i": 0}
            current_test = TestCase(data['TestID'], data['Descrizione'])
            descrizione = data['Descrizione']
            
            # Clean di tutte le .jpg
            utils.clean_img_folder(project_root / "screen/web")
            # Get command task
            task = data['Task']

            async def Validation(task, browser, step_counter, current_test, descrizione, execution_step_gif, report, OPTIMIZATION_PROMPT):
                # Create agent with the model
                agent = Agent(
                    task,
                    browser = browser,
                    #llm = ChatGoogle(model=os.getenv("GEMINI_MODEL")),
                    llm = ChatOllama(model="gemma3:4b"),
                    use_vision=True,
                    file_system_path=str(project_root),
                    generate_gif=True,  # Enable GIF generation for actions
                    extend_system_message=OPTIMIZATION_PROMPT,
                    temperature=0.1
                )
                # Define the hook function
                async def my_step_hook(agent: Agent):
                    try:
                        screenshot_event = agent.browser_session.event_bus.dispatch(ScreenshotEvent(full_page=False))
                        await screenshot_event
                        result = await screenshot_event.event_result(raise_if_any=True, raise_if_none=True)
                        img_path = utils.base64_to_image(
                            base64_string = str(result),
                            output_filename = project_root / f"screen/web/step_{step_counter['i']}.jpg"
                        )
                        with Image.open(img_path) as img:
                            img_ridimensionata = img.resize((1200, 675), Image.Resampling.HAMMING)
                            img_ridimensionata.save(img_path)
                        current_test.add_step(f"Step - {step_counter['i']}", img_path, False)

                        step_counter["i"] += 1
                    except Exception as e:
                        print(f'❌ Error: {e}')
                        import traceback

                        traceback.print_exc()

                try:
                    history = await agent.run(on_step_start=my_step_hook)
                    if history.is_successful():
                        print(f'✅ Agent successfully completed the {current_test.test_id} - {descrizione}')
                    else:
                        print("⚠️ Agent couldn't complete the task.")
                        step_counter["i"] -= 1
                        screen_path = project_root / f"screen/web/step_{step_counter['i']}.jpg"
                        current_test.add_step(f"Step - FAILED", screen_path, True)
                    current_test.add_step(f"Execution steps", execution_step_gif, False)
                    report.add_test_case_result(current_test)
                    print(f'Final result: {history.final_result()}')
                except Exception as e:
                    print(f'❌ Error: {e}')

            asyncio.run(Validation(task, browser, step_counter, current_test, descrizione, execution_step_gif, report, OPTIMIZATION_PROMPT))
    #Finalizza il report e ottieni il percorso del file
    final_report_path = report.finalize_report()
    #Apri il file nel browser predefinito
    webbrowser.open_new_tab(final_report_path.as_uri())
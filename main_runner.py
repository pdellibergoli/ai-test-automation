"""
Main Test Runner - Gestisce l'esecuzione unificata di test mobile e web
Legge il parametro 'Device' dal foglio Excel e instrada verso il test appropriato
"""
import sys
from pathlib import Path
import asyncio
import logging
import datetime
import webbrowser

# Setup project root
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utilities import excel_utils
from utilities.report_utils import HTMLReportGenerator
from tests.mobile_test_executor import MobileTestExecutor
from tests.web_test_executor import WebTestExecutor
from config_manager import get_config, validate_environment, setup_logging

# Setup configuration and logging
config = get_config()
setup_logging()


class UnifiedTestRunner:
    """
    Classe principale che gestisce l'esecuzione dei test in base al tipo di device.
    Supporta sia test mobile che web attraverso un'interfaccia unificata.
    """
    
    def __init__(self, excel_file: str, sheet_name: str = 'Foglio1'):
        """
        Inizializza il test runner.
        
        Args:
            excel_file: Path al file Excel con i dati di test
            sheet_name: Nome del foglio Excel da leggere
        """
        self.excel_file = Path(excel_file)
        self.sheet_name = sheet_name
        self.project_root = project_root
        
        # Setup report directory
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.project_root / f"reports/unified/{self.timestamp}"
        
        # Initialize HTML report generator
        self.report = HTMLReportGenerator(self.output_dir)
        
        # Initialize executors
        self.mobile_executor = MobileTestExecutor(self.report, self.output_dir)
        self.web_executor = WebTestExecutor(self.report, self.output_dir)
        
    def read_test_data(self):
        """
        Legge i dati di test dal file Excel.
        
        Returns:
            Lista di dizionari con i dati di test
        """
        print(f"📖 Lettura dati da: {self.excel_file}")
        test_data = excel_utils.excel_read_data(self.excel_file, self.sheet_name)
        
        if not test_data:
            raise ValueError(f"❌ Nessun dato trovato nel file {self.excel_file}")
            
        print(f"✅ Letti {len(test_data)} test case dal file Excel")
        return test_data
    
    def validate_test_data(self, data: dict) -> tuple[bool, str]:
        """
        Valida che i dati del test case siano completi.
        
        Args:
            data: Dizionario con i dati del test case
            
        Returns:
            Tupla (is_valid, error_message)
        """
        required_fields = ['TestID', 'Task', 'Descrizione', 'Execution', 'Device']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Campo obbligatorio mancante: {field}"
        
        # Validate Device field
        device = str(data['Device']).lower()
        if device not in ['mobile', 'web']:
            return False, f"Device deve essere 'mobile' o 'web', ricevuto: {data['Device']}"
        
        return True, ""
    
    async def execute_test_case(self, data: dict):
        """
        Esegue un singolo test case instradandolo al giusto executor.
        
        Args:
            data: Dizionario con i dati del test case
        """
        # Validate test data
        is_valid, error_msg = self.validate_test_data(data)
        if not is_valid:
            print(f"⚠️  Test {data.get('TestID', 'UNKNOWN')} - Validazione fallita: {error_msg}")
            return
        
        device_type = str(data['Device']).lower()
        test_id = data['TestID']
        
        print(f"\n{'='*80}")
        print(f"🚀 Esecuzione Test: {test_id} - {data['Descrizione']}")
        print(f"📱 Device Type: {device_type.upper()}")
        print(f"{'='*80}\n")
        
        try:
            if device_type == 'mobile':
                await self.mobile_executor.execute(data)
            elif device_type == 'web':
                await self.web_executor.execute(data)
            else:
                print(f"❌ Device type non supportato: {device_type}")
                
        except Exception as e:
            print(f"❌ Errore durante l'esecuzione del test {test_id}: {e}")
            import traceback
            traceback.print_exc()
    
    async def run_all_tests(self):
        """
        Esegue tutti i test dal file Excel.
        Filtra automaticamente i test con Execution = True/Yes/Si/1
        """
        # Read test data
        test_data_list = self.read_test_data()
        
        # Start test suite
        self.report.start_suite("Suite Test Automatici - Unified Runner")
        
        # Count tests to execute
        executable_tests = [
            data for data in test_data_list 
            if str(data.get('Execution', '')).lower() in ['true', 'yes', 'si', '1']
        ]
        
        print(f"\n📊 Test da eseguire: {len(executable_tests)} su {len(test_data_list)} totali\n")
        
        # Execute each test
        for idx, data in enumerate(executable_tests, 1):
            print(f"\n[{idx}/{len(executable_tests)}] Processing test...")
            await self.execute_test_case(data)
        
        # Finalize report
        print(f"\n{'='*80}")
        print("📝 Finalizzazione report...")
        final_report_path = self.report.finalize_report()
        
        print(f"✅ Report generato: {final_report_path}")
        print(f"{'='*80}\n")
        
        # Open report in browser
        webbrowser.open_new_tab(final_report_path.as_uri())
        
        return final_report_path


def main():
    """
    Entry point principale dell'applicazione.
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        UNIFIED TEST AUTOMATION RUNNER                     ║
    ║        Mobile & Web Test Execution Framework              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Determine which Excel file to use based on test type
    # You can modify this logic to accept command line arguments
    excel_file = project_root / 'dati_test.xlsx'  # Unified file for both mobile and web
    
    if not excel_file.exists():
        print(f"❌ File Excel non trovato: {excel_file}")
        print(f"💡 Assicurati che il file esista nella directory del progetto")
        sys.exit(1)
    
    # Create runner and execute tests
    runner = UnifiedTestRunner(excel_file=excel_file)
    
    try:
        asyncio.run(runner.run_all_tests())
        print("\n✅ Esecuzione completata con successo!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Esecuzione interrotta dall'utente")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
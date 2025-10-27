import pandas as pd

import tests.mobile_AI_test as mobile_AI_test
import tests.web_AI_test as web_AI_test

class TestRunner:
    def __init__(self, config_file):
        self.config_file = config_file
        
        # --- MAPPA DELLE CLASSI ---
        # Questo dizionario collega la stringa dal file Excel alla classe Python reale.
        # È il modo più sicuro per chiamare classi dinamicamente.
        

    def _read_config(self):
        """Legge il file Excel e lo restituisce come DataFrame."""
        try:
            df = pd.read_excel(self.config_file)
            # Normalizza la colonna 'Execution' per gestire 'Yes', 'si', 'TRUE', ecc.
            df['Execution'] = df['Execution'].astype(str).str.lower().isin(['true', 'yes', 'si', '1'])
            return df
        except FileNotFoundError:
            print(f"❌ ERRORE: File di configurazione non trovato: '{self.config_file}'")
            return None
        except Exception as e:
            print(f"❌ ERRORE: Impossibile leggere il file Excel. Dettagli: {e}")
            return None
        
    def run_tests(self):
        """Esegue i test in base alla configurazione."""
        config_df = self._read_config()
        if config_df is None:
            print("Esecuzione interrotta a causa di un errore.")
            return

        print("--- Inizio della suite di test ---\n")

        for index, row in config_df.iterrows():
            if row['Execution']:
                class_name = row['Class test']
                
                # Cerca la classe corrispondente nella nostra mappa
                test_class = self.CLASS_MAP.get(class_name)

                if test_class:
                    try:
                        # Crea un'istanza della classe trovata, passando i dati della riga
                        test_instance = test_class(row)
                        # Esegue il test
                        test_instance.run()
                    except Exception as e:
                        print(f"❌ ERRORE durante l'esecuzione di '{class_name}': {e}\n")
                else:
                    print(f"⚠️  ATTENZIONE: Classe '{class_name}' definita in Excel ma non trovata nel codice. Salto il test.\n")
        
        print("--- Fine della suite di test ---")

if __name__ == "__main__":
    excel_file = 'config_tests.xlsx'
    runner = TestRunner(config_file=excel_file)
    runner.run_tests()
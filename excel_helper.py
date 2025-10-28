"""
Excel Helper - Script per supporto file excel
"""
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.append(str(project_root))

def validate_unified_file(excel_file: str = "dati_test.xlsx", sheet_name: str = "Foglio1"):
    """
    Valida il file Excel unificato.
    
    Args:
        excel_file: Path al file da validare
        sheet_name: Nome del foglio da validare
    """
    print("\n🔍 Validazione file unificato...")
    
    file_path = project_root / excel_file
    
    if not file_path.exists():
        print(f"❌ File non trovato: {file_path}")
        return False
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Required columns
        required_cols = ['TestID', 'Descrizione', 'Task', 'Execution', 'Device']
        
        print("\n📋 Verifica colonne obbligatorie:")
        for col in required_cols:
            if col in df.columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - MANCANTE!")
                return False
        
        # Validate Device values
        print("\n📱 Verifica valori Device:")
        device_values = df['Device'].dropna().unique()
        valid_devices = ['mobile', 'web']
        
        for device in device_values:
            device_lower = str(device).lower()
            if device_lower in valid_devices:
                count = len(df[df['Device'].str.lower() == device_lower])
                print(f"   ✅ {device}: {count} test")
            else:
                print(f"   ⚠️  Valore non valido: {device}")
        
        # Check for empty required fields
        print("\n🔍 Verifica campi vuoti:")
        for col in required_cols:
            empty_count = df[col].isna().sum()
            if empty_count > 0:
                print(f"   ⚠️  {col}: {empty_count} righe vuote")
            else:
                print(f"   ✅ {col}: OK")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Totale righe: {len(df)}")
        print(f"   Test da eseguire: {len(df[df['Execution'].isin(['True', 'true', 'Yes', 'yes', 'Si', 'si', True, 1])])}")
        
        print("\n✅ Validazione completata!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante validazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_sample_unified_excel(output_file: str = "dati_test_sample.xlsx"):
    """
    Crea un file Excel di esempio con la struttura corretta.
    
    Args:
        output_file: Nome del file di esempio da creare
    """
    print("\n📝 Creazione file Excel di esempio...")
    
    sample_data = {
        'TestID': [
            'WEB_001', 'WEB_002', 'WEB_003',
            'MOB_001', 'MOB_002'
        ],
        'Descrizione': [
            'Google Search Test',
            'Wikipedia Navigation',
            'Form Submission Test',
            'Android App Login',
            'iOS App Navigation'
        ],
        'Task': [
            'Navigate to google.com and search for "AI agents"',
            'Go to wikipedia.org and search for "Browser automation"',
            'Fill the contact form with test data and submit',
            'Open the app and login with credentials',
            'Navigate through app sections and verify content'
        ],
        'Execution': [True, True, False, True, False],
        'Device': ['web', 'web', 'web', 'mobile', 'mobile'],
        'Platform': ['', '', '', 'Android', 'iOS'],
        'DeviceName': ['', '', '', 'Pixel 6', 'iPhone 14'],
        'UDID': ['', '', '', 'emulator-5554', '00008030-xxxxx'],
        'AppID': ['', '', '', '', ''],
        'AppPackage': ['', '', '', 'com.example.app', 'com.example.app'],
        'AppActivity': ['', '', '', '.MainActivity', ''],
    }
    
    df_sample = pd.DataFrame(sample_data)
    
    output_path = project_root / output_file
    df_sample.to_excel(output_path, sheet_name='Foglio1', index=False)
    
    print(f"✅ File di esempio creato: {output_path}")
    print(f"\n💡 Usa questo file come riferimento per la struttura corretta")
    
    return True


def main():
    """
    Main function con menu interattivo.
    """
    print("""
    ╔═════════════════════════════════════════╗
    ║                                         ║
    ║              EXCEL HELPER               ║
    ║                                         ║
    ╚═════════════════════════════════════════╝
    """)
    
    print("Seleziona un'opzione:")
    print("  1. Valida file esistente")
    print("  2. Crea file di esempio")
    print("  3. Esci")
    
    choice = input("\nScelta (1-3): ").strip()
    
    if choice == '1':
        print("\n" + "="*60)
        file_to_validate = input("Nome file da validare [dati_test.xlsx]: ").strip() or "dati_test.xlsx"
        validate_unified_file(file_to_validate)
        
    elif choice == '2':
        print("\n" + "="*60)
        sample_file = input("Nome file di esempio [dati_test_sample.xlsx]: ").strip() or "dati_test_sample.xlsx"
        create_sample_unified_excel(sample_file)
        
    elif choice == '3':
        print("\n👋 Arrivederci!")
        return
        
    else:
        print("\n❌ Scelta non valida")


if __name__ == "__main__":
    main()
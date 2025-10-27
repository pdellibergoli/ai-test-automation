import pandas as pd
import pprint

def excel_read_data(nome_file_excel, nome_foglio_excel):
    # La lista dati viene ora definita dentro la funzione per evitare che 
    # i dati di esecuzioni precedenti rimangano in memoria.
    lista_dati = []
    
    try:
        # --- PASSO 1: Leggiamo solo l'intestazione per trovare i nomi delle colonne ---
        df_header = pd.read_excel(nome_file_excel, sheet_name=nome_foglio_excel, nrows=0)
        
        # --- PASSO 2: Creiamo la lista di colonne valide dinamicamente ---
        colonne_valide = []
        for colonna in df_header.columns:
            # Pandas nomina le colonne vuote 'Unnamed: X'. Ci fermiamo alla prima.
            if 'Unnamed:' in str(colonna):
                break
            colonne_valide.append(colonna)

        if not colonne_valide:
            print("❌ ERRORE: Nessuna colonna valida trovata nel file Excel.")
            return []

        print(f"✅ Colonne identificate dinamicamente: {colonne_valide}")

        # --- PASSO 3: Ora leggiamo il file usando solo le colonne valide ---
        df = pd.read_excel(nome_file_excel, sheet_name=nome_foglio_excel, usecols=colonne_valide)
        print(f"✅ Dati letti con successo dal file '{nome_file_excel}'. Elaborazione...")

        # --- PASSO 4: Convertiamo l'intero DataFrame in una lista di dizionari ---
        # Il metodo to_dict('records') è più diretto e pulito del ciclo for.
        lista_dati = df.to_dict('records')

        print("✅ Elaborazione completata.")
        print("\n--- Contenuto dell'oggetto finale (lista di dizionari) ---")
        pprint.pprint(lista_dati)

    except FileNotFoundError:
        print(f"❌ ERRORE: Il file '{nome_file_excel}' non è stato trovato.")
    except Exception as e:
        print(f"❌ Si è verificato un errore imprevisto: {e}")

    return lista_dati


'''import pandas as pd
import pprint # Usiamo pprint per una stampa più leggibile dell'output finale

# --- Configurazione ---
nome_foglio_excel = 'Foglio1'
colonne_da_leggere = ['TestID', 'Task', 'Descrizione','Execution','Platform','DeviceName','UDID','AppID','AppPackage','AppActivity']

# Inizializziamo una lista vuota che conterrà i nostri dati
lista_dati = []

def excel_read_data(nome_file_excel):
    try:
        df = pd.read_excel(nome_file_excel, sheet_name=nome_foglio_excel, usecols=colonne_da_leggere)
        print(f"✅ Dati letti con successo dal file '{nome_file_excel}'. Elaborazione...")

        for indice, riga in df.iterrows():
            # Per ogni riga, creiamo un dizionario
            riga_come_oggetto = {
                'TestID': riga['TestID'],
                'Task': riga['Task'],
                'Descrizione': riga['Descrizione'],
                'Execution': riga['Execution'],
                'Platform': riga['Platform'],
                'DeviceName': riga['DeviceName'],
                'UDID': riga['UDID'],
                'AppID': riga['AppID'],
                'AppPackage': riga['AppPackage'],
                'AppActivity': riga['AppActivity']
                
            }
            # Aggiungiamo il dizionario appena creato alla nostra lista
            lista_dati.append(riga_come_oggetto)

        print("✅ Elaborazione completata. I dati sono stati salvati in una lista.")
        
        # Ora la variabile 'lista_dati' contiene tutti i tuoi dati.
        # Possiamo stamparla per verificare il risultato.
        print("\n--- Contenuto dell'oggetto finale (lista di dizionari) ---")
        pprint.pprint(lista_dati)

    except FileNotFoundError:
        print(f"❌ ERRORE: Il file '{nome_file_excel}' non è stato trovato.")
    except ValueError as e:
        print(f"❌ ERRORE: Colonne non trovate. Controlla che '{colonne_da_leggere}' esistano. Dettagli: {e}")
    except Exception as e:
        print(f"❌ Si è verificato un errore imprevisto: {e}")

    if lista_dati:
        return lista_dati'''
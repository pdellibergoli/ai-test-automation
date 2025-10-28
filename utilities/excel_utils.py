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
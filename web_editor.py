import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory, abort, Response, stream_with_context
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import webbrowser
import threading
import glob
import subprocess
import sys
import time
from io import BytesIO
import shutil # <-- AGGIUNGI QUESTO IMPORT

# --- Configurazione ---
app = Flask(__name__)
project_root = Path(__file__).parent
REPORTS_DIR = project_root / "reports" / "unified"
SHEET_NAME = 'Foglio1'

ALL_COLUMNS = [
    'TestID', 'Descrizione', 'Task', 'Active', 'Execution', 'Device',
    'Platform', 'DeviceName', 'UDID', 'AppID', 'AppPackage', 'AppActivity'
]

# --- Gestione Processo di Test (Globale) ---
test_process = None

def get_excel_file_path(filename: str) -> Path:
    if not filename:
        filename = "dati_test.xlsx"
    safe_filename = secure_filename(filename)
    if not safe_filename:
        abort(400, "Nome file non valido.")
    file_path = (project_root / safe_filename).resolve()
    if project_root != file_path.parent or file_path.suffix != '.xlsx':
        abort(400, "Nome file non valido o non consentito.")
    return file_path

def check_excel_file(file_path: Path):
    if not file_path.exists():
        print(f"⚠️  Creazione file vuoto locale: {file_path.name}")
        df_empty = pd.DataFrame(columns=ALL_COLUMNS)
        try:
            df_empty.to_excel(file_path, sheet_name=SHEET_NAME, index=False)
        except Exception as e:
            print(f"❌ Impossibile creare il file Excel locale: {e}")

# --- Route per le Pagine HTML ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/reports/view/<path:filepath>')
def serve_report(filepath):
    try:
        safe_path = REPORTS_DIR.joinpath(filepath).resolve()
        if not safe_path.is_file() or REPORTS_DIR not in safe_path.parents:
            abort(404, "Report non trovato o accesso negato.")
        directory = safe_path.parent
        filename = safe_path.name
        return send_from_directory(directory, filename)
    except Exception:
        abort(404, "Report non trovato.")

# --- API (Dati JSON) ---

@app.route('/api/excel-files', methods=['GET'])
def get_excel_files():
    files = [f.name for f in project_root.glob('*.xlsx') if not f.name.startswith('~$')]
    files.sort()
    return jsonify(files)

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file inviato"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "File non selezionato"}), 400
    if file and file.filename.endswith('.xlsx'):
        try:
            filename = secure_filename(file.filename)
            save_path = project_root / filename
            file.save(save_path)
            print(f"✅ File caricato localmente: {filename}")
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File non valido. Seleziona un file .xlsx"}), 400

@app.route('/api/reports', methods=['GET'])
def get_reports_list():
    report_list = []
    if not REPORTS_DIR.exists():
        return jsonify([])
    for dir_path in REPORTS_DIR.iterdir():
        if dir_path.is_dir():
            report_files = list(dir_path.glob('test_report_*.html'))
            if report_files:
                relative_path = report_files[0].relative_to(REPORTS_DIR).as_posix()
                report_list.append({"name": dir_path.name, "path": relative_path})
    report_list.sort(key=lambda x: x['name'], reverse=True)
    return jsonify(report_list)

# --- NUOVA ROUTE PER ELIMINARE REPORT ---
@app.route('/api/reports/<folder_name>', methods=['DELETE'])
def delete_report_folder(folder_name):
    """Elimina una cartella specifica all'interno di REPORTS_DIR."""
    try:
        # Sanifica il nome della cartella per evitare attacchi (es. ../../)
        safe_folder_name = secure_filename(folder_name)
        if not safe_folder_name or safe_folder_name != folder_name:
             # Se secure_filename cambia il nome, potrebbe contenere caratteri non sicuri
             abort(400, "Nome cartella non valido.")

        folder_path = (REPORTS_DIR / safe_folder_name).resolve()

        # --- Sicurezza ---
        # Verifica che la cartella sia direttamente dentro REPORTS_DIR
        if not folder_path.is_dir() or folder_path.parent != REPORTS_DIR.resolve():
            abort(404, "Cartella report non trovata o accesso non consentito.")

        # Elimina l'intera cartella e il suo contenuto
        shutil.rmtree(folder_path)

        print(f"✅ Cartella report eliminata: {safe_folder_name}")
        return jsonify({"success": True, "message": f"Report '{safe_folder_name}' eliminato."})

    except FileNotFoundError:
        abort(404, "Cartella report non trovata.")
    except Exception as e:
        print(f"❌ Errore eliminazione report '{folder_name}': {e}")
        return jsonify({"error": str(e)}), 500
# --- FINE NUOVA ROUTE ---


@app.route('/api/tests', methods=['GET'])
def get_tests():
    """Legge un file Excel locale e gestisce errori di colonna."""
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    check_excel_file(file_path) # Assicura che esista localmente
    try:
        # Legge il file locale con pandas
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME).fillna('')

        # --- GESTIONE ERRORI COLONNE INIZIA QUI ---
        
        # 1. Controlla quali colonne MANCANO rispetto a quelle attese
        missing_cols = [col for col in ALL_COLUMNS if col not in df.columns]
        if missing_cols:
            error_message = f"Colonne mancanti nel file '{filename}': {', '.join(missing_cols)}. Assicurati che il file abbia tutte le colonne richieste."
            print(f"❌ {error_message}")
            # Restituisce un errore 400 (Bad Request) con un messaggio chiaro
            return jsonify({"error": error_message}), 400 
            
        # 2. Se tutte le colonne ci sono, aggiungi eventuali colonne extra trovate
        #    e poi riordina secondo ALL_COLUMNS per coerenza.
        #    Questo previene errori se ci sono colonne *in più* nel file.
        #    Prendi tutte le colonne esistenti + quelle definite
        current_columns_ordered = [col for col in ALL_COLUMNS if col in df.columns]
        # Aggiungi colonne extra trovate nel file che non sono in ALL_COLUMNS
        extra_cols = [col for col in df.columns if col not in ALL_COLUMNS]
        final_columns = current_columns_ordered + extra_cols
        
        df = df[final_columns] # Usa l'ordine corretto + colonne extra
        
        # --- FINE GESTIONE ERRORI COLONNE ---

        df['Active'] = df['Active'].apply(lambda x: str(x).lower() in ['true', '1', 'yes', 'si', 'vero'])
        
        # Assicura che TUTTE le colonne di ALL_COLUMNS siano presenti (aggiunge quelle mancanti se non lo erano prima del controllo)
        # Questo serve più che altro per il frontend, il controllo precedente ha già validato
        for col in ALL_COLUMNS:
             if col not in df.columns:
                 df[col] = ''
        
        # Ora riordina definitivamente secondo ALL_COLUMNS per la visualizzazione
        df_display = df[ALL_COLUMNS]
        tests = df_display.to_dict('records')
        return jsonify(tests)
        
    except pd.errors.EmptyDataError:
        # File Excel vuoto o illeggibile
        error_message = f"Il file '{filename}' è vuoto o non è un file Excel valido."
        print(f"❌ {error_message}")
        return jsonify({"error": error_message}), 400
    except Exception as e:
        # Cattura altri errori generici di lettura
        error_message = f"Errore durante la lettura del file '{filename}': {e}"
        print(f"❌ {error_message}")
        # Restituisce 500 per errori imprevisti
        return jsonify({"error": error_message}), 500

@app.route('/api/tests', methods=['POST'])
def save_tests():
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    try:
        data = request.json
        df = pd.DataFrame(data, columns=ALL_COLUMNS) if data else pd.DataFrame(columns=ALL_COLUMNS)
        df.to_excel(file_path, sheet_name=SHEET_NAME, index=False)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API PER ESECUZIONE TEST ---
@app.route('/api/test-status', methods=['GET'])
def get_test_status():
    global test_process
    if test_process and test_process.poll() is None:
        return jsonify({"status": "running"})
    return jsonify({"status": "idle"})

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    global test_process
    if test_process and test_process.poll() is None:
        return Response("Un processo di test è già in esecuzione.", status=409)
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    if not file_path.exists():
        return Response(f"File locale {filename} non trovato.", status=404)
    python_exe = sys.executable
    main_runner_script = str(project_root / 'main_runner.py')
    cmd = [python_exe, main_runner_script, '--file', file_path.name]
    def generate_output():
        global test_process
        try:
            test_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', bufsize=1, cwd=project_root
            )
            yield "--- 🚀 Avvio dei test (usando file locale)... ---\n\n"
            for line in iter(test_process.stdout.readline, ''):
                yield line; time.sleep(0.01)
            test_process.stdout.close()
            return_code = test_process.wait()
            yield f"\n\n--- ✅ Esecuzione terminata (Codice: {return_code}) ---"
        except Exception as e:
            yield f"\n\n--- ❌ ERRORE: Impossibile avviare il processo: {e} ---"
        finally: test_process = None
    return Response(stream_with_context(generate_output()), mimetype='text/plain')

# --- Avvio del Server ---
def open_browser():
    def _open(): webbrowser.open_new("http://127.0.0.1:5000/")
    t = threading.Timer(1.0, _open); t.daemon = True; t.start()

if __name__ == '__main__':
    Path('templates').mkdir(exist_ok=True)
    print(f"\n🚀 Avvio Test Editor su http://127.0.0.1:5000")
    print("   L'editor ora legge e scrive file locali.")
    print("   Premi CTRL+C per fermare il server.")
    open_browser()
    app.run(host='127.0.0.1', port=5000, debug=False)
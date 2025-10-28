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
from io import BytesIO # Necessario per gestire file in memoria
from dotenv import load_dotenv # Necessario per caricare il token

# --- NUOVI IMPORT PER VERCEL BLOB ---
try:
    from vercel_blob import put, get, delete, list_blobs, download
except ImportError:
    print("ERRORE: Libreria 'vercel-blob' non trovata. Esegui: pip install vercel-blob")
    sys.exit(1)

# --- Configurazione ---
app = Flask(__name__)
project_root = Path(__file__).parent
REPORTS_DIR = project_root / "reports" / "unified"
SHEET_NAME = 'Foglio1'

# Carica .env per trovare il aiTestAuto_READ_WRITE_TOKEN
load_dotenv() 
BLOB_TOKEN = os.getenv('aiTestAuto_READ_WRITE_TOKEN')
if not BLOB_TOKEN:
    print("ATTENZIONE: aiTestAuto_READ_WRITE_TOKEN non trovato nel file .env. Le operazioni sui file falliranno.")

ALL_COLUMNS = [
    'TestID', 'Descrizione', 'Task', 'Active', 'Execution', 'Device',
    'Platform', 'DeviceName', 'UDID', 'AppID', 'AppPackage', 'AppActivity'
]

test_process = None

def get_safe_filename(filename: str) -> str:
    """Pulisce il nome del file e valida il suffisso."""
    if not filename:
        filename = "dati_test.xlsx"
    safe_filename = secure_filename(filename)
    if not safe_filename.endswith('.xlsx'):
        abort(400, "Nome file non valido. Accettati solo .xlsx")
    return safe_filename

def check_excel_file_blob(filename: str):
    """Controlla se il file esiste su Blob, altrimenti lo crea."""
    try:
        # Controlla se il file esiste
        get(filename, token=BLOB_TOKEN)
        # print(f"File {filename} trovato su Vercel Blob.")
    except Exception as e:
        # Se '404: Not Found', il file non esiste e lo creiamo
        if '404' in str(e):
            print(f"⚠️  File {filename} non trovato. Creazione su Vercel Blob...")
            df_empty = pd.DataFrame(columns=ALL_COLUMNS)
            output = BytesIO()
            df_empty.to_excel(output, sheet_name=SHEET_NAME, index=False)
            output.seek(0)
            put(filename, output, token=BLOB_TOKEN)
            print(f"✅ File {filename} creato su Vercel Blob.")
        else:
            # Altro errore (es. token non valido)
            print(f"❌ Errore controllo file su Blob: {e}")
            raise

# --- Route per le Pagine HTML ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/reports/view/<path:filepath>')
def serve_report(filepath):
    # NOTA: I report sono ancora serviti localmente.
    # Per Vercel, dovresti caricare anche questi su Vercel Blob
    # e fare un redirect, ma per ora lo lasciamo così.
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
    """Elenca i file .xlsx da Vercel Blob."""
    try:
        blobs = list_blobs(token=BLOB_TOKEN)
        files = [b.pathname for b in blobs if b.pathname.endswith('.xlsx')]
        files.sort()
        return jsonify(files)
    except Exception as e:
        print(f"❌ Errore elenco file da Blob: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Carica un file Excel direttamente su Vercel Blob."""
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file inviato"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "File non selezionato"}), 400
        
    if file and file.filename.endswith('.xlsx'):
        try:
            filename = secure_filename(file.filename)
            # Carica il file in memoria su Vercel Blob
            put(filename, file.stream, token=BLOB_TOKEN)
            print(f"✅ File caricato su Blob: {filename}")
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            print(f"❌ Errore durante l'upload su Blob: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File non valido. Seleziona un file .xlsx"}), 400

@app.route('/api/reports', methods=['GET'])
def get_reports_list():
    # Questa funzione rimane invariata, legge i report locali
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

@app.route('/api/tests', methods=['GET'])
def get_tests():
    """Legge un file Excel da Vercel Blob."""
    filename = get_safe_filename(request.args.get('file'))
    try:
        check_excel_file_blob(filename) # Assicura che esista
        # Scarica il file da Vercel Blob
        blob = get(filename, token=BLOB_TOKEN)
        
        # Leggi il file scaricato (che è in bytes) con pandas
        df = pd.read_excel(BytesIO(blob.read()), sheet_name=SHEET_NAME).fillna('')
        
        df['Active'] = df['Active'].apply(lambda x: str(x).lower() in ['true', '1', 'yes', 'si', 'vero'])
        for col in ALL_COLUMNS:
            if col not in df.columns:
                df[col] = ''
        df = df[ALL_COLUMNS]
        tests = df.to_dict('records')
        return jsonify(tests)
    except Exception as e:
        print(f"❌ Errore lettura da Blob ({filename}): {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tests', methods=['POST'])
def save_tests():
    """Salva un file Excel su Vercel Blob."""
    filename = get_safe_filename(request.args.get('file'))
    try:
        data = request.json
        df = pd.DataFrame(data, columns=ALL_COLUMNS) if data else pd.DataFrame(columns=ALL_COLUMNS)
        
        # Crea un file Excel in memoria
        output = BytesIO()
        df.to_excel(output, sheet_name=SHEET_NAME, index=False)
        output.seek(0) # Riavvolgi il buffer
        
        # Carica il file in memoria su Vercel Blob
        put(filename, output, token=BLOB_TOKEN)
        
        print(f"✅ File {filename} salvato su Vercel Blob.")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Errore salvataggio su Blob: {e}")
        return jsonify({"error": str(e)}), 500

# --- API PER ESECUZIONE TEST ---
# NOTA: L'esecuzione dei test non funzionerà su Vercel,
# ma funzionerà se esegui 'web_editor.py' localmente.

@app.route('/api/test-status', methods=['GET'])
def get_test_status():
    global test_process
    if test_process and test_process.poll() is None:
        return jsonify({"status": "running"})
    return jsonify({"status": "idle"})

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Avvia main_runner.py (localmente)."""
    global test_process
    
    if test_process and test_process.poll() is None:
        return Response("Un processo di test è già in esecuzione.", status=409)

    filename = get_safe_filename(request.args.get('file'))
    
    # NOTA: L'esecuzione scaricherà il file da Blob (vedi Modifica 4)
    python_exe = sys.executable
    main_runner_script = str(project_root / 'main_runner.py')
    cmd = [python_exe, main_runner_script, '--file', filename]

    def generate_output():
        global test_process
        try:
            test_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', bufsize=1, cwd=project_root
            )
            yield "--- 🚀 Avvio dei test... (Il runner scaricherà il file da Vercel Blob) ---\n\n"
            for line in iter(test_process.stdout.readline, ''):
                yield line
                time.sleep(0.01)
            test_process.stdout.close()
            return_code = test_process.wait()
            yield f"\n\n--- ✅ Esecuzione terminata (Codice: {return_code}) ---"
        except Exception as e:
            yield f"\n\n--- ❌ ERRORE: Impossibile avviare il processo: {e} ---"
        finally:
            test_process = None
            
    return Response(stream_with_context(generate_output()), mimetype='text/plain')

# --- Avvio del Server ---
def open_browser():
    def _open():
        webbrowser.open_new("http://127.0.0.1:5000/")
    t = threading.Timer(1.0, _open)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    if not BLOB_TOKEN:
        print("="*60)
        print("ERRORE FATALE: aiTestAuto_READ_WRITE_TOKEN non trovato.")
        print("1. Esegui 'vercel blob add' per creare uno store.")
        print("2. Copia il token dalla dashboard di Vercel.")
        print("3. Aggiungilo al tuo file .env: aiTestAuto_READ_WRITE_TOKEN=...")
        print("="*60)
        sys.exit(1)
        
    Path('templates').mkdir(exist_ok=True)
    print(f"\n🚀 Avvio Test Editor su http://127.0.0.1:5000")
    print("   L'editor ora legge e scrive da Vercel Blob.")
    print("   Premi CTRL+C per fermare il server.")
    
    open_browser()
    app.run(host='127.0.0.1', port=5000, debug=False)
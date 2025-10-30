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
import shutil

# --- Configurazione ---
app = Flask(__name__, template_folder='templates')
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
    if not filename: filename = "dati_test.xlsx"
    safe_filename = secure_filename(filename)
    if not safe_filename: abort(400, "Nome file non valido.")
    file_path = (project_root / safe_filename).resolve()
    if project_root != file_path.parent or file_path.suffix != '.xlsx':
        abort(400, "Nome file non valido o non consentito.")
    return file_path

def check_excel_file(file_path: Path):
    if not file_path.exists():
        print(f"⚠️  Creazione file vuoto locale: {file_path.name}")
        df_empty = pd.DataFrame(columns=ALL_COLUMNS)
        try: df_empty.to_excel(file_path, sheet_name=SHEET_NAME, index=False)
        except Exception as e: print(f"❌ Impossibile creare il file Excel locale: {e}")

# --- Route per le Pagine HTML ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/reports')
def reports_page(): return render_template('reports.html')

@app.route('/reports/view/<path:filepath>')
def serve_report(filepath):
    try:
        safe_path = REPORTS_DIR.joinpath(filepath).resolve()
        if not safe_path.is_file() or REPORTS_DIR not in safe_path.parents:
            abort(404, "Report non trovato o accesso negato.")
        directory, filename = safe_path.parent, safe_path.name
        return send_from_directory(directory, filename)
    except Exception: abort(404, "Report non trovato.")

# --- API (Dati JSON) ---

@app.route('/api/excel-files', methods=['GET'])
def get_excel_files():
    files = [f.name for f in project_root.glob('*.xlsx') if not f.name.startswith('~$')]
    files.sort(); return jsonify(files)

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files: return jsonify({"error": "Nessun file inviato"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "File non selezionato"}), 400
    if file and file.filename.endswith('.xlsx'):
        try:
            filename = secure_filename(file.filename)
            file.save(project_root / filename)
            print(f"✅ File caricato localmente: {filename}")
            return jsonify({"success": True, "filename": filename})
        except Exception as e: return jsonify({"error": str(e)}), 500
    else: return jsonify({"error": "File non valido. Seleziona un file .xlsx"}), 400

@app.route('/api/reports', methods=['GET'])
def get_reports_list():
    report_list = []
    if not REPORTS_DIR.exists(): return jsonify([])
    for dir_path in REPORTS_DIR.iterdir():
        if dir_path.is_dir():
            report_files = list(dir_path.glob('test_report_*.html'))
            if report_files:
                relative_path = report_files[0].relative_to(REPORTS_DIR).as_posix()
                report_list.append({"name": dir_path.name, "path": relative_path})
    report_list.sort(key=lambda x: x['name'], reverse=True); return jsonify(report_list)

@app.route('/api/reports/<folder_name>', methods=['DELETE'])
def delete_report_folder(folder_name):
    try:
        safe_folder_name = secure_filename(folder_name)
        if not safe_folder_name or safe_folder_name != folder_name: abort(400, "Nome cartella non valido.")
        folder_path = (REPORTS_DIR / safe_folder_name).resolve()
        if not folder_path.is_dir() or folder_path.parent != REPORTS_DIR.resolve():
            abort(404, "Cartella report non trovata o accesso non consentito.")
        shutil.rmtree(folder_path)
        print(f"✅ Cartella report eliminata: {safe_folder_name}")
        return jsonify({"success": True, "message": f"Report '{safe_folder_name}' eliminato."})
    except FileNotFoundError: abort(404, "Cartella report non trovata.")
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/tests', methods=['GET'])
def get_tests():
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    check_excel_file(file_path)
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME).fillna('')
        missing_cols = [col for col in ALL_COLUMNS if col not in df.columns]
        if missing_cols:
            error_message = f"Colonne mancanti in '{filename}': {', '.join(missing_cols)}."
            print(f"❌ {error_message}"); return jsonify({"error": error_message}), 400
        current_columns_ordered = [col for col in ALL_COLUMNS if col in df.columns]
        extra_cols = [col for col in df.columns if col not in ALL_COLUMNS]
        df = df[current_columns_ordered + extra_cols]
        df['Active'] = df['Active'].apply(lambda x: str(x).lower() in ['true', '1', 'yes', 'si', 'vero'])
        for col in ALL_COLUMNS:
             if col not in df.columns: df[col] = ''
        df_display = df[ALL_COLUMNS]
        tests = df_display.to_dict('records')
        return jsonify(tests)
    except pd.errors.EmptyDataError:
        error_message = f"Il file '{filename}' è vuoto o non valido."
        print(f"❌ {error_message}"); return jsonify({"error": error_message}), 400
    except Exception as e:
        error_message = f"Errore lettura file '{filename}': {e}"
        print(f"❌ {error_message}"); return jsonify({"error": error_message}), 500

@app.route('/api/tests', methods=['POST'])
def save_tests():
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    try:
        data = request.json
        df = pd.DataFrame(data, columns=ALL_COLUMNS) if data else pd.DataFrame(columns=ALL_COLUMNS)
        df.to_excel(file_path, sheet_name=SHEET_NAME, index=False)
        print(f"✅ File {file_path.name} salvato localmente.")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Errore salvataggio file locale: {e}"); return jsonify({"error": str(e)}), 500

# --- API PER ESECUZIONE TEST ---
@app.route('/api/test-status', methods=['GET'])
def get_test_status():
    global test_process
    if test_process and test_process.poll() is None: return jsonify({"status": "running"})
    return jsonify({"status": "idle"})

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    global test_process
    if test_process and test_process.poll() is None: return Response("Un processo di test è già in esecuzione.", status=409)
    filename = request.args.get('file', 'dati_test.xlsx')
    file_path = get_excel_file_path(filename)
    if not file_path.exists(): return Response(f"File locale {filename} non trovato.", status=404)
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
        except Exception as e: yield f"\n\n--- ❌ ERRORE: Impossibile avviare il processo: {e} ---"
        finally: test_process = None
    return Response(stream_with_context(generate_output()), mimetype='text/plain')

# --- NUOVA ROUTE PER FERMARE I TEST ---
@app.route('/api/stop-tests', methods=['POST'])
def stop_tests():
    """Termina il processo di test in esecuzione."""
    global test_process
    if test_process and test_process.poll() is None:
        try:
            test_process.terminate() # Invia SIGTERM (più pulito)
            # Attendi un breve momento per assicurarti che termini
            test_process.wait(timeout=2) 
            print("⛔ Processo di test terminato dall'utente.")
            return jsonify({"success": True, "message": "Processo terminato."})
        except subprocess.TimeoutExpired:
            test_process.kill() # Forza la chiusura (SIGKILL)
            print("⛔ Processo di test forzato a terminare (kill).")
            return jsonify({"success": True, "message": "Processo terminato forzatamente."})
        except Exception as e:
            print(f"❌ Errore durante l'interruzione del processo: {e}")
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Nessun processo in esecuzione."}), 404
# --- FINE NUOVA ROUTE ---

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
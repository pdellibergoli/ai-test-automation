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
import json
# Importa le funzioni per leggere/scrivere .env
from dotenv import load_dotenv, set_key, find_dotenv 

# Importa il TestGenerator
try:
    from tests.test_generator import TestGenerator
except ImportError:
    print("ATTENZIONE: Impossibile importare TestGenerator. La funzione di generazione non sarà disponibile.", file=sys.stderr)
    TestGenerator = None 

# --- Configurazione ---
app = Flask(__name__, template_folder='templates')
project_root = Path(__file__).parent
REPORTS_DIR = project_root / "reports" / "unified"
SHEET_NAME = 'Foglio1'
# Trova il file .env o imposta il percorso di default
ENV_FILE_PATH = find_dotenv()
if not ENV_FILE_PATH:
    ENV_FILE_PATH = str(project_root / '.env')
    Path(ENV_FILE_PATH).touch() # Crealo se non esiste

ALL_COLUMNS = [
    'TestID', 'Descrizione', 'Task', 'Active', 'Execution', 'Device',
    'Platform', 'DeviceName', 'UDID', 'AppID', 'AppPackage', 'AppActivity'
]
test_process = None
generation_process = None

# --- Funzioni di Utility (invariate) ---
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

# --- Route per le Pagine HTML (MODIFICATE) ---
@app.route('/')
def index(): 
    """Serve la pagina Home (Dashboard)."""
    return render_template('home.html')

@app.route('/editor')
def editor_page():
    """Serve la pagina principale dell'editor."""
    return render_template('index.html')

@app.route('/reports')
def reports_page(): 
    """Serve la pagina di elenco dei report."""
    return render_template('reports.html')

@app.route('/generate')
def generate_page():
    """Serve la pagina di generazione test."""
    return render_template('generate_tests.html')

# --- NUOVA ROUTE PER CONFIGURAZIONE ---
@app.route('/config')
def config_page():
    """Serve la pagina di configurazione LLM."""
    return render_template('config.html')

@app.route('/reports/view/<path:filepath>')
def serve_report(filepath):
    """Serve i file di report locali."""
    try:
        safe_path = REPORTS_DIR.joinpath(filepath).resolve()
        if not safe_path.is_file() or REPORTS_DIR not in safe_path.parents:
            abort(404, "Report non trovato.")
        directory, filename = safe_path.parent, safe_path.name
        return send_from_directory(directory, filename)
    except Exception: abort(404, "Report non trovato.")

# --- API (Dati JSON) ---

# --- NUOVE API PER CONFIGURAZIONE LLM ---
@app.route('/api/llm-models', methods=['GET'])
def get_llm_models():
    """Serve il file di configurazione JSON dei modelli."""
    try:
        models_path = project_root / 'llm_models.json'
        if not models_path.exists():
            return jsonify({"error": "File 'llm_models.json' non trovato."}), 404
        with open(models_path, 'r', encoding='utf-8') as f:
            models = json.load(f)
        return jsonify(models)
    except Exception as e:
        return jsonify({"error": f"Impossibile leggere llm_models.json: {e}"}), 500

@app.route('/api/get-env', methods=['GET'])
def get_env():
    """Legge i valori attuali dal file .env."""
    try:
        # Assicura che il file esista
        if not os.path.exists(ENV_FILE_PATH):
            Path(ENV_FILE_PATH).touch()
            
        # Leggi i valori
        load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
        env_values = {
            "WEB_LLM_PROVIDER": os.getenv("WEB_LLM_PROVIDER", "gemini"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
            "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            "LOCAL_LLM": os.getenv("LOCAL_LLM", "llava:13b"),
            "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "USE_LOCAL_LLM": os.getenv("USE_LOCAL_LLM", "false"),
        }
        return jsonify(env_values)
    except Exception as e:
        return jsonify({"error": f"Impossibile leggere il file .env: {e}"}), 500

@app.route('/api/save-env', methods=['POST'])
def save_env():
    """Salva le impostazioni ricevute nel file .env."""
    data = request.json
    try:
        print(f"ℹ️  Salvataggio configurazione in {ENV_FILE_PATH}...")
        for key, value in data.items():
            # Usa set_key per aggiornare o aggiungere la variabile nel file .env
            set_key(ENV_FILE_PATH, key, str(value)) # Converte in stringa per sicurezza
        
        print("✅ Configurazione .env salvata.")
        return jsonify({"success": True, "message": "Configurazione salvata."})
    except Exception as e:
        print(f"❌ Errore salvataggio .env: {e}")
        return jsonify({"error": f"Impossibile salvare il file .env: {e}"}), 500
# --- FINE NUOVE API ---


@app.route('/api/excel-files', methods=['GET'])
def get_excel_files():
    files = [f.name for f in project_root.glob('*.xlsx') if not f.name.startswith('~$')]
    files.sort(); return jsonify(files)

@app.route('/api/input-files', methods=['GET'])
def get_input_files():
    files = []
    for ext in ('*.txt', '*.md', '*.req', '*.prompt'):
        files.extend(project_root.glob(ext))
    file_names = sorted([f.name for f in files if not f.name.startswith('~$')])
    return jsonify(file_names)

@app.route('/api/upload-input-file', methods=['POST'])
def upload_input_file():
    if 'file' not in request.files: return jsonify({"error": "Nessun file inviato"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "File non selezionato"}), 400
    filename = secure_filename(file.filename)
    if not filename.endswith(('.txt', '.md', '.req', '.prompt')):
        return jsonify({"error": "File non valido."}), 400
    try:
        file_path = (project_root / filename).resolve()
        if file_path.parent != project_root: abort(400, "Percorso file non valido.")
        file.save(file_path)
        print(f"✅ File di input caricato localmente: {filename}")
        return jsonify({"success": True, "filename": filename})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/generate-tests', methods=['POST'])
def api_generate_tests():
    global generation_process
    if generation_process and generation_process.poll() is None:
        return Response("Una generazione è già in corso.", status=409)
    data = request.json
    req_file_name = data.get('requirements_file')
    prompt_file_name = data.get('prompt_file')
    if not req_file_name or not prompt_file_name:
        return Response("File requisiti e file prompt sono necessari.", status=400)
    try:
        req_file_safe = secure_filename(req_file_name)
        prompt_file_safe = secure_filename(prompt_file_name)
        if not (project_root / req_file_safe).exists():
             return Response(f"File requisiti non trovato: {req_file_safe}", status=404)
        if not (project_root / prompt_file_safe).exists():
             return Response(f"File prompt non trovato: {prompt_file_safe}", status=404)
        
        python_exe = sys.executable
        generator_script = str(project_root / 'tests' / 'test_generator.py')
        cmd = [python_exe, generator_script, '--req-file', req_file_safe, '--prompt-file', prompt_file_safe]
        
        print(f"🤖 Avvio subprocess TestGenerator: {' '.join(cmd)}")
        def generate_output():
            global generation_process
            try:
                generation_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding='utf-8', bufsize=1, cwd=project_root
                )
                yield "--- 🚀 Avvio generazione... (L'output JSON apparirà alla fine) ---\n\n"
                for line in iter(generation_process.stdout.readline, ''):
                    yield line; time.sleep(0.01)
                generation_process.stdout.close()
                return_code = generation_process.wait()
                if return_code == 0: yield f"\n\n--- ✅ Generazione terminata ---"
                else: yield f"\n\n--- ❌ Generazione fallita (Codice: {return_code}) ---"
            except Exception as e: yield f"\n\n--- ❌ ERRORE: Impossibile avviare il processo: {e} ---"
            finally: generation_process = None
        return Response(stream_with_context(generate_output()), mimetype='text/plain')
    except Exception as e:
        print(f"❌ Errore avvio generazione: {e}", file=sys.stderr)
        return Response(f"Errore interno: {e}", status=500)

@app.route('/api/stop-generation', methods=['POST'])
def stop_generation():
    global generation_process
    if generation_process and generation_process.poll() is None:
        try:
            generation_process.terminate(); generation_process.wait(timeout=2) 
            print("⛔ Processo di generazione terminato dall'utente.")
            return jsonify({"success": True, "message": "Processo terminato."})
        except subprocess.TimeoutExpired:
            generation_process.kill()
            print("⛔ Processo di generazione forzato a terminare (kill).")
            return jsonify({"success": True, "message": "Processo terminato forzatamente."})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Nessun processo in esecuzione."}), 404

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
            abort(404, "Cartella report non trovata.")
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
@app.route('/api/test-status', methods=['GET'])
def get_test_status():
    global test_process
    if test_process and test_process.poll() is None: return jsonify({"status": "running"})
    return jsonify({"status": "idle"})
@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    global test_process
    if test_process and test_process.poll() is None: return Response("Un processo di test è già in esecuzione.", status=409)
    
    # NOTA: Ora che la config è dinamica,
    # i subprocess (main_runner, test_generator) leggeranno
    # automaticamente il file .env aggiornato quando partono.
    # Non serve più passare --llm come argomento.
    
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
            yield "--- 🚀 Avvio dei test (usando config da .env)... ---\n\n"
            for line in iter(test_process.stdout.readline, ''):
                yield line; time.sleep(0.01)
            test_process.stdout.close()
            return_code = test_process.wait()
            yield f"\n\n--- ✅ Esecuzione terminata (Codice: {return_code}) ---"
        except Exception as e: yield f"\n\n--- ❌ ERRORE: Impossibile avviare il processo: {e} ---"
        finally: test_process = None
    return Response(stream_with_context(generate_output()), mimetype='text/plain')
@app.route('/api/stop-tests', methods=['POST'])
def stop_tests():
    global test_process
    if test_process and test_process.poll() is None:
        try:
            test_process.terminate(); test_process.wait(timeout=2) 
            print("⛔ Processo di test terminato dall'utente.")
            return jsonify({"success": True, "message": "Processo terminato."})
        except subprocess.TimeoutExpired:
            test_process.kill()
            print("⛔ Processo di test forzato a terminare (kill).")
            return jsonify({"success": True, "message": "Processo terminato forzatamente."})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Nessun processo in esecuzione."}), 404

# --- Cache Busting ---
@app.after_request
def add_cache_busting_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# --- Avvio del Server ---
def open_browser():
    def _open(): webbrowser.open_new("http://127.0.0.1:5000/")
    t = threading.Timer(1.0, _open); t.daemon = True; t.start()

if __name__ == '__main__':
    Path('templates').mkdir(exist_ok=True)
    if not (project_root / 'llm_models.json').exists():
        print("ATTENZIONE: File 'llm_models.json' mancante. Creane uno per la pagina di configurazione.")
        
    print(f"\n🚀 Avvio Test Editor su http://127.0.0.1:5000")
    print("   Premi CTRL+C per fermare il server.")
    open_browser()
    app.run(host='127.0.0.1', port=5000, debug=False)
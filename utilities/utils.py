import glob
import os
import base64
import shutil
import os
import mimetypes

def base64_to_image(base64_string: str, output_filename: str):
        """Convert base64 string to image."""
        import base64
        import os

        if not os.path.exists(os.path.dirname(output_filename)):
            os.makedirs(os.path.dirname(output_filename))

        img_data = base64.b64decode(base64_string)
        with open(output_filename, "wb") as f:
            f.write(img_data)
        return output_filename

def clean_img_folder(dir):
    for file in glob.glob(f"{dir}/*.*"):
        os.remove(file)
    print(f"Clean successfull!")

def image_to_base64(file_path):
    """Converte un file immagine in una stringa Base64 per l'embedding in HTML."""
    try:
        # Controlla se il file esiste e non è vuoto
        if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream' # Tipo generico se non riconosciuto
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_string}"
        else:
            # Ritorna un'immagine 'placeholder' se il file non esiste o è vuoto
            # Questo è un pixel 1x1 trasparente
            return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    except Exception as e:
        print(f"⚠️  Attenzione: Impossibile leggere lo screenshot '{file_path}'. Errore: {e}")
        return "" # Ritorna una stringa vuota in caso di errore

def copy_agent_history(source_directory, destination_directory, new_file_name): 
    file_name = 'agent_history.gif'
    source_path = os.path.join(source_directory, file_name)
    destination_path = os.path.join(destination_directory, new_file_name)
    try:
        # Assicura che la cartella di destinazione esista, altrimenti la crea
        os.makedirs(destination_directory, exist_ok=True)

        # Copia il file. shutil.copy2 tenta di preservare anche i metadati del file.
        shutil.copy2(source_path, destination_path)
        
        print(f"✅ File copiato con successo da '{source_path}' a '{destination_path}'")

    except FileNotFoundError:
        print(f"❌ ERRORE: Il file di origine '{source_path}' non è stato trovato.")
    except PermissionError:
        print(f"❌ ERRORE: Permesso negato. Prova a eseguire lo script con i privilegi di amministratore (es. con 'sudo').")
    except Exception as e:
        print(f" si è verificato un errore imprevisto: {e}")
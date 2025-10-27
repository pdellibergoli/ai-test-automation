import datetime
from pathlib import Path
import base64
import os

# La classe TestCase rimane invariata
class TestCase:
    def __init__(self, test_id, description):
        self.test_id = test_id
        self.description = description
        self.steps = []
        self.status = "Passato"
    def add_step(self, action, screenshot_path, is_failure=False):
        self.steps.append({ "action": action, "screenshot": screenshot_path })
        if is_failure:
            self.status = "Fallito"

class HTMLReportGenerator:
    """Genera un report HTML con thumbnail e modale per l'ingrandimento."""

    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = self.output_dir / f"test_report_{timestamp}.html"
        self.filename = self.report_file
        self.total_tests, self.passed_count, self.failed_count = 0, 0, 0

    def start_suite(self, suite_title="Report Test Automatici"):
        report_date = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
        html_head = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{suite_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f7f9; color: #333; }}
        .report-container {{ max-width: 1000px; margin: auto; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .report-header {{ padding: 20px; background-color: #2c3e50; color: #ecf0f1; border-bottom: 4px solid #3498db; }}
        .report-header h1 {{ margin: 0; font-size: 24px; }}
        .report-header p {{ margin: 5px 0 0; opacity: 0.9; }}
        .summary {{ display: flex; justify-content: space-around; padding: 20px; border-bottom: 1px solid #e1e1e1; }}
        .summary-item {{ text-align: center; }} .summary-item .count {{ font-size: 22px; font-weight: bold; }} .summary-item .label {{ font-size: 14px; color: #777; }}
        .summary-item.passed .count {{ color: #2ecc71; }} .summary-item.failed .count {{ color: #e74c3c; }}
        .test-case {{ border-bottom: 1px solid #e1e1e1; }}
        .test-header {{ padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }}
        .test-info h3 {{ margin: 0; font-size: 18px; }}
        .status {{ padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 14px; color: #fff; }}
        .status.passed {{ background-color: #2ecc71; }} .status.failed {{ background-color: #e74c3c; }}
        .steps-container {{ padding: 0 20px 20px 20px; }}
        .step {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 8px; overflow: hidden; }}
        .step-header {{ background-color: #f9f9f9; padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
        .step-header::after {{ content: '+'; font-size: 20px; font-weight: bold; color: #3498db; }} .step.active .step-header::after {{ content: '−'; }}
        
        /* --- CSS CORRETTO --- */
        .screenshot-container {{ 
            max-height: 0; 
            overflow: hidden; 
            transition: max-height 0.3s ease-out;
        }}
        .step.active .screenshot-container {{ 
            max-height: 1000px; 
            transition: max-height 0.4s ease-in; 
            padding: 10px; 
            box-sizing: border-box; 
        }}
        /* --- FINE CORREZIONE --- */

        .screenshot-container img {{ max-height: 200px; width: auto; display: block; margin: auto; border-radius: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s ease-in-out; }}
        .screenshot-container img:hover {{ transform: scale(1.03); }}
        .modal {{ display: none; position: fixed; z-index: 1001; padding-top: 50px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.85); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90vh; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; transition: color 0.3s; }}
        .modal-close:hover, .modal-close:focus {{ color: #bbb; text-decoration: none; }}
        #caption {{ margin: auto; display: block; width: 80%; max-width: 700px; text-align: center; color: #ccc; padding: 10px 0; height: 150px; }}
    </style>
</head>
<body>
<div class="report-container">
    <header class="report-header"><h1>{suite_title}</h1><p>Data Inizio: {report_date}</p></header>
    <section class="summary">
        <div class="summary-item total"><div class="count">__TOTAL__</div><div class="label">Test Totali</div></div>
        <div class="summary-item passed"><div class="count">__PASSED__</div><div class="label">Passati</div></div>
        <div class="summary-item failed"><div class="count">__FAILED__</div><div class="label">Falliti</div></div>
    </section>
    <section class="test-list">
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(html_head)

    def _image_to_base64(self, file_path):
        try:
            if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, "rb") as image_file:
                    return f"data:image/png;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
            return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        except Exception as e:
            print(f"⚠️  Attenzione: Impossibile leggere lo screenshot '{file_path}'. Errore: {e}")
            return ""

    def add_test_case_result(self, test_case: TestCase):
        self.total_tests += 1
        if test_case.status.lower() == "passato": self.passed_count += 1
        else: self.failed_count += 1
        
        steps_html_parts = []
        for step in test_case.steps:
            base64_image_src = self._image_to_base64(step['screenshot'])
            step_html = f"""
            <div class="step">
                <div class="step-header">{step['action']}</div>
                <div class="screenshot-container">
                    <img src="{base64_image_src}" alt="Screenshot per: {step['action']}" loading="lazy"
                         title="Clicca per ingrandire l'immagine">
                </div>
            </div>"""
            steps_html_parts.append(step_html)
        
        steps_html = "".join(steps_html_parts)
        status_class = "passed" if test_case.status.lower() == "passato" else "failed"
        test_case_html = f"""
        <div class="test-case">
            <div class="test-header">
                <div class.test-info"><h3>{test_case.test_id}: {test_case.description}</h3></div>
                <div class="status {status_class}">{test_case.status.upper()}</div>
            </div>
            <div class="steps-container">{steps_html}</div>
        </div>"""
        
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(test_case_html)

    def finalize_report(self):
        html_footer = """
            </section>
        </div>
        <div id="imageModal" class="modal">
            <span class="modal-close">&times;</span>
            <img class="modal-content" id="modalImage">
            <div id="caption"></div>
        </div>
        <script>
            document.addEventListener('click', function (event) {
                const header = event.target.closest('.step-header');
                if (header) {
                    event.preventDefault();
                    header.parentElement.classList.toggle('active');
                }
            });
            const modal = document.getElementById('imageModal'), modalImg = document.getElementById('modalImage'), captionText = document.getElementById('caption'), closeBtn = document.querySelector('.modal-close');
            document.querySelector('.test-list').addEventListener('click', function(event) {
                if (event.target.tagName === 'IMG' && event.target.closest('.screenshot-container')) {
                    modal.style.display = "block";
                    modalImg.src = event.target.src;
                    captionText.innerHTML = event.target.alt;
                }
            });
            function closeModal() { modal.style.display = "none"; }
            closeBtn.onclick = closeModal;
            modal.onclick = function(event) { if (event.target === modal) closeModal(); }
        </script>
        </body>
        </html>"""
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(html_footer)
        with open(self.filename, "r", encoding="utf-8") as f: content = f.read()
        content = content.replace("__TOTAL__", str(self.total_tests)).replace("__PASSED__", str(self.passed_count)).replace("__FAILED__", str(self.failed_count))
        with open(self.filename, "w", encoding="utf-8") as f: f.write(content)
        print(f"✅ Report finalizzato: {self.filename}")
        return self.filename
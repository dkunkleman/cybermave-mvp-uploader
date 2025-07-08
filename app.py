from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
from flask import jsonify
import json
import requests
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

MEMORY_FOLDER = 'vault/memory/'
REGISTRY_FILE = 'vault/memory_registry.json'

os.makedirs(MEMORY_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return redirect(url_for('memory_upload'))

@app.route('/admin/memory-upload', methods=['GET', 'POST'])
def memory_upload():
    os.makedirs(MEMORY_FOLDER, exist_ok=True)

    if request.method == 'POST':
        if 'memoryfiles' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('memoryfiles')

        if not files or files[0].filename == '':
            flash('No files selected')
            return redirect(request.url)

        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(MEMORY_FOLDER, filename)
            file.save(filepath)

            # Trigger external AI sync webhook
            try:
                requests.post("https://cybermave-sync.onrender.com/file-received", json={
                    "filename": filename,
                    "path": filepath,
                    "timestamp": str(datetime.datetime.now())
                })
            except Exception as e:
                print(f"Webhook failed: {e}")

            # Log to registry
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, 'r') as f:
                    registry = json.load(f)
            else:
                registry = []

            registry.append({
                'filename': filename,
                'status': 'uploaded'
            })

            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)

            flash(f'{filename} uploaded successfully.')

    return render_template('admin/memory_upload.html')
@app.route('/admin/memory-index', methods=['GET'])
def index_vault_memory():
    files = []
    vault_path = 'vault/memory/'

    for root, dirs, filenames in os.walk(vault_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            try:
                files.append({
                    'filename': filename,
                    'relative_path': filepath,
                    'timestamp': time.ctime(os.path.getmtime(filepath)),
                    'ext': os.path.splitext(filename)[-1].lower()
                })
            except Exception as e:
                files.append({
                    'filename': filename,
                    'relative_path': filepath,
                    'error': str(e)
                })

    return jsonify({
        'total_files': len(files),
        'files': files
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)

"""
Minimal static file server for the AI Driver Monitor PWA.
All AI detection runs in the browser (MediaPipe) — this server
just serves static HTML/JS/CSS files.
"""
import os
from flask import Flask, send_from_directory, send_file

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'[INFO] Serving on port {port}')
    app.run(host='0.0.0.0', port=port)

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.routes.admin import admin_bp
from src.routes.quality import quality_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'ion_regressivos_secret_key_2025'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(quality_bp, url_prefix='/api/quality')

@app.route('/health')
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {'status': 'healthy', 'service': 'Ion Regressivos API'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "API Ion Regressivos - Backend funcionando", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


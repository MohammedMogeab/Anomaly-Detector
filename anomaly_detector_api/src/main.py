import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.routes.flows import flows_bp
from src.routes.recording import recording_bp
from src.routes.payloads import payloads_bp
from src.routes.replay import replay_bp
from src.routes.analysis import analysis_bp
from src.routes.reports import reports_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'anomaly_detector_secret_key_2024'

# Enable CORS for all routes
CORS(app)

# Register API blueprints
app.register_blueprint(flows_bp, url_prefix='/api')
app.register_blueprint(recording_bp, url_prefix='/api')
app.register_blueprint(payloads_bp, url_prefix='/api')
app.register_blueprint(replay_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
from flask import Response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    full_path = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(full_path):
        if path.endswith('.js'):
            with open(full_path, 'rb') as f:
                content = f.read()
            return Response(content, mimetype='application/javascript')
        else:
            return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

import mimetypes
mimetypes.add_type("application/javascript", ".js")

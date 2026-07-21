import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from data_validation import generate_report, DEFAULT_EXPECTED_COLS

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

UPLOAD_DIR = "data/raw/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/validate', methods=['POST'])
def api_validate():
    expected_cols = request.form.get('expected_cols')
    if expected_cols:
        expected_cols = [c.strip() for c in expected_cols.split(',') if c.strip()]
    else:
        expected_cols = DEFAULT_EXPECTED_COLS

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
    else:
        filepath = request.form.get('filepath', 'data/raw/sales.csv')

    report = generate_report(filepath, expected_cols=expected_cols)
    return jsonify(report)

@app.route('/api/report', methods=['GET'])
def get_latest_report():
    report_path = "output/intake_report.json"
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({'status': 'ERROR', 'message': 'No report found'}), 404

@app.route('/api/sample/<sample_name>', methods=['POST'])
def run_sample(sample_name):
    os.makedirs("data/raw/samples", exist_ok=True)
    
    if sample_name == 'valid':
        target = "data/raw/sales.csv"
        cols = DEFAULT_EXPECTED_COLS
    elif sample_name == 'invalid_schema':
        target = "data/raw/samples/invalid_schema.csv"
        with open(target, 'w', encoding='utf-8') as f:
            f.write("customer_code,transaction_amount,transaction_ts\n101,150.0,2025-01-01\n")
        cols = DEFAULT_EXPECTED_COLS
    elif sample_name == 'latin1':
        target = "data/raw/samples/latin1_sample.csv"
        with open(target, 'wb') as f:
            f.write("transaction_id,customer_id,transaction_date,amount\n1,101,2025-01-01,150.00 €\n".encode('latin-1'))
        cols = DEFAULT_EXPECTED_COLS
    elif sample_name == 'unsupported_format':
        target = "data/raw/samples/data.txt"
        with open(target, 'w', encoding='utf-8') as f:
            f.write("some raw text data")
        cols = DEFAULT_EXPECTED_COLS
    else:
        return jsonify({'status': 'ERROR', 'message': 'Invalid sample name'}), 400

    report = generate_report(target, expected_cols=cols)
    return jsonify(report)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Data Validation Firewall API & Web Dashboard on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

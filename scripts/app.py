import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from data_validation import generate_report, DEFAULT_EXPECTED_COLS
from data_ingestion import ingest_dataset

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

    delimiter = request.form.get('delimiter', ',')
    encoding = request.form.get('encoding', 'utf-8')
    is_nested = request.form.get('is_nested', 'false').lower() == 'true'

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
    else:
        filepath = request.form.get('filepath', 'data/raw/sales.csv')

    val_report = generate_report(filepath, expected_cols=expected_cols)
    
    ingest_report = None
    if val_report['status'] == 'PASSED' or filepath.endswith('.json') or filepath.endswith('.csv'):
        try:
            _, ingest_report = ingest_dataset(
                filepath, 
                delimiter=delimiter, 
                encoding=encoding, 
                is_nested=is_nested
            )
        except Exception as e:
            ingest_report = {'error': str(e)}

    return jsonify({
        'validation': val_report,
        'ingestion': ingest_report
    })

@app.route('/api/sample/<sample_name>', methods=['POST'])
def run_sample(sample_name):
    os.makedirs("data/raw/samples", exist_ok=True)
    
    delimiter = ','
    encoding = 'utf-8'
    is_nested = False
    cols = DEFAULT_EXPECTED_COLS

    if sample_name == 'valid':
        target = "data/raw/sales.csv"
    elif sample_name == 'semicolon':
        target = "data/raw/samples/sales_semicolon.csv"
        delimiter = ';'
    elif sample_name == 'nested_json':
        target = "data/raw/samples/nested_customers.json"
        is_nested = True
        cols = ["id", "transaction_date", "amount", "customer.id", "customer.name", "customer.location.city", "customer.location.country"]
    elif sample_name == 'invalid_schema':
        target = "data/raw/samples/invalid_schema.csv"
        with open(target, 'w', encoding='utf-8') as f:
            f.write("customer_code,transaction_amount,transaction_ts\n101,150.0,2025-01-01\n")
    elif sample_name == 'latin1':
        target = "data/raw/samples/latin1_sample.csv"
        encoding = 'latin-1'
        with open(target, 'wb') as f:
            f.write("transaction_id,customer_id,transaction_date,amount\n1,101,2025-01-01,150.00 €\n".encode('latin-1'))
    elif sample_name == 'unsupported_format':
        target = "data/raw/samples/data.txt"
        with open(target, 'w', encoding='utf-8') as f:
            f.write("some raw text data")
    else:
        return jsonify({'status': 'ERROR', 'message': 'Invalid sample name'}), 400

    val_report = generate_report(target, expected_cols=cols)
    try:
        _, ingest_report = ingest_dataset(target, delimiter=delimiter, encoding=encoding, is_nested=is_nested)
    except Exception as e:
        ingest_report = {'error': str(e)}

    return jsonify({
        'validation': val_report,
        'ingestion': ingest_report
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Multi-Format Data Ingestion & Firewall API on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

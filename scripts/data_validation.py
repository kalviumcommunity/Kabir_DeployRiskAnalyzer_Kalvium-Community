import os
import json
import logging
from datetime import datetime
import pandas as pd
import chardet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_EXPECTED_COLS = ["transaction_id", "customer_id", "transaction_date", "amount"]
DEFAULT_ALLOWED_FORMATS = ["csv", "json", "xlsx", "parquet"]

def validate_file_exists(filepath):
    """
    Check 1: File Existence
    Verifies if file exists on disk and has non-zero size.
    """
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    if os.path.getsize(filepath) == 0:
        return False, "File is empty (0 bytes)"
    return True, "File exists and has content"

def validate_file_format(filepath, allowed=None):
    """
    Check 2: Format Validation
    Verifies file extension matches allowed extensions list.
    """
    if allowed is None:
        allowed = DEFAULT_ALLOWED_FORMATS
    ext = filepath.split('.')[-1].lower()
    if ext not in allowed:
        return False, f"Unsupported format '.{ext}'. Allowed: {', '.join(allowed)}"
    return True, f"Format valid: '.{ext}'"

def detect_encoding(filepath):
    """
    Check 4: Encoding Detection
    Detects file encoding using chardet and reports confidence level.
    """
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read(10000)
        if not raw_data:
            return "unknown", "File is empty"
        result = chardet.detect(raw_data)
        enc = result.get('encoding', 'unknown') or 'unknown'
        conf = result.get('confidence', 0.0) or 0.0
        return enc, f"Detected: {enc} ({conf:.0%})"
    except Exception as e:
        return "unknown", f"Error detecting encoding: {str(e)}"

def validate_schema(df, expected_cols):
    """
    Check 3: Schema Validation
    Compares DataFrame columns against expected schema list.
    """
    missing = set(expected_cols) - set(df.columns)
    extra = set(df.columns) - set(expected_cols)
    if missing or extra:
        msg_parts = []
        if missing:
            msg_parts.append(f"Missing required columns: {sorted(list(missing))}")
        if extra:
            msg_parts.append(f"Unexpected extra columns: {sorted(list(extra))}")
        return False, " | ".join(msg_parts)
    return True, "Schema valid"

def capture_stats(filepath, df):
    """
    Check 5: Dimensions & File Stats
    Captures baseline statistics (row count, col count, file size).
    """
    return {
        'rows': int(len(df)),
        'columns': int(len(df.columns)),
        'column_names': list(df.columns),
        'file_size_bytes': os.path.getsize(filepath),
        'file_size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 4)
    }

def generate_report(filepath, expected_cols=None, allowed_formats=None, output_path="output/intake_report.json"):
    """
    Combines all 5 validation gates into a single detailed report.
    Implements fail-fast logic at each critical gate.
    """
    if expected_cols is None:
        expected_cols = DEFAULT_EXPECTED_COLS
    if allowed_formats is None:
        allowed_formats = DEFAULT_ALLOWED_FORMATS

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report = {
        'timestamp': datetime.now().isoformat(),
        'filepath': filepath,
        'status': 'PASSED',
        'checks': {},
        'statistics': None
    }

    # Gate 1: Existence
    file_ok, msg = validate_file_exists(filepath)
    report['checks']['file_exists'] = {'passed': file_ok, 'message': msg}
    if not file_ok:
        report['status'] = 'FAILED'
        _save_report(report, output_path)
        logging.error(f"Validation failed [file_exists]: {msg}")
        return report

    # Gate 2: Format
    format_ok, msg = validate_file_format(filepath, allowed_formats)
    report['checks']['format'] = {'passed': format_ok, 'message': msg}
    if not format_ok:
        report['status'] = 'FAILED'
        _save_report(report, output_path)
        logging.error(f"Validation failed [format]: {msg}")
        return report

    # Gate 4: Encoding (run before reading to report encoding)
    enc, msg = detect_encoding(filepath)
    report['checks']['encoding'] = {'passed': True, 'encoding': enc, 'message': msg}

    # Load file
    ext = filepath.split('.')[-1].lower()
    try:
        if ext == 'csv':
            df = pd.read_csv(filepath, encoding=enc if enc and enc.lower() != 'unknown' else 'utf-8')
        elif ext == 'json':
            df = pd.read_json(filepath)
        elif ext == 'xlsx':
            df = pd.read_excel(filepath)
        elif ext == 'parquet':
            df = pd.read_parquet(filepath)
        else:
            df = pd.read_csv(filepath)
    except Exception as e:
        err_msg = f"Failed to parse file: {str(e)}"
        report['checks']['parse'] = {'passed': False, 'message': err_msg}
        report['status'] = 'FAILED'
        _save_report(report, output_path)
        logging.error(f"Validation failed [parse]: {err_msg}")
        return report

    # Gate 3: Schema
    schema_ok, msg = validate_schema(df, expected_cols)
    report['checks']['schema'] = {'passed': schema_ok, 'message': msg}
    if not schema_ok:
        report['status'] = 'FAILED'

    # Gate 5: Dimensions
    stats = capture_stats(filepath, df)
    report['statistics'] = stats
    report['checks']['dimensions'] = {
        'passed': True,
        'message': f"{stats['rows']} rows x {stats['columns']} columns ({stats['file_size_mb']} MB)"
    }

    _save_report(report, output_path)

    if report['status'] == 'PASSED':
        logging.info(f"Validation PASSED for {filepath}")
    else:
        logging.warning(f"Validation FAILED for {filepath}")

    return report

def _save_report(report, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

def validate_raw_data(file_path, expected_cols=None):
    """
    Backward-compatible wrapper function.
    """
    report = generate_report(file_path, expected_cols=expected_cols)
    return report['status'] == 'PASSED'

if __name__ == "__main__":
    target = "data/raw/sales.csv"
    print(f"--- Running Intake Data Validation Firewall on '{target}' ---")
    rep = generate_report(target)
    print(json.dumps(rep, indent=2))

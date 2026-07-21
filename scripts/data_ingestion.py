import os
import json
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_csv(filepath, delimiter=',', encoding='utf-8'):
    """
    Load CSV with explicit parameters. Avoids dangerous default assumptions.
    """
    try:
        df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
        logging.info(f"Loaded CSV '{filepath}' (delimiter='{delimiter}', encoding='{encoding}') - Shape: {df.shape}")
        return df
    except UnicodeDecodeError:
        logging.warning(f"Cannot decode '{filepath}' with encoding '{encoding}'. Candidate encodings: latin-1, iso-8859-1, cp1252")
        raise

def ingest_csv_with_fallback(filepath, candidate_encodings=None, candidate_delimiters=None):
    """
    Tries multiple encodings and delimiters if primary fails, preventing pipeline crashes.
    """
    if candidate_encodings is None:
        candidate_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    if candidate_delimiters is None:
        candidate_delimiters = [',', ';', '\t', '|']

    last_error = None
    for enc in candidate_encodings:
        for sep in candidate_delimiters:
            try:
                df = pd.read_csv(filepath, delimiter=sep, encoding=enc)
                # Ensure it didn't parse as a single giant column due to wrong delimiter
                if df.shape[1] > 1 or len(candidate_delimiters) == 1:
                    logging.info(f"Fallback SUCCESS for '{filepath}': encoding='{enc}', delimiter='{sep}' - Shape: {df.shape}")
                    return df, enc, sep
            except Exception as e:
                last_error = e
                continue

    raise ValueError(f"Could not load file '{filepath}' with any candidate encoding/delimiter combination. Last error: {last_error}")

def ingest_json(filepath, is_nested=False, record_path=None):
    """
    Ingest JSON data. If is_nested is True, flattens hierarchical structures using pd.json_normalize().
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if is_nested:
            if isinstance(raw_data, dict) and record_path and record_path in raw_data:
                df = pd.json_normalize(raw_data[record_path])
            elif isinstance(raw_data, list):
                df = pd.json_normalize(raw_data)
            elif isinstance(raw_data, dict):
                df = pd.json_normalize([raw_data])
            else:
                df = pd.read_json(filepath)
            logging.info(f"Flattened nested JSON '{filepath}' - Shape: {df.shape}")
        else:
            df = pd.read_json(filepath)
            logging.info(f"Loaded JSON '{filepath}' - Shape: {df.shape}")

        return df
    except Exception as e:
        logging.error(f"Error ingesting JSON '{filepath}': {str(e)}")
        raise

def document_ingestion(df, source):
    """
    Generates a detailed audit trail report of loaded dataset.
    """
    report = {
        'source': source,
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'null_counts': {col: int(df[col].isnull().sum()) for col in df.columns},
        'first_3_rows': df.head(3).to_dict(orient='records')
    }

    print(f"\n=================== INGESTION REPORT: {source} ===================")
    print(f"Shape: {report['rows']} Rows x {report['columns']} Columns")
    print("\nColumn Data Types:")
    for col, dtype in report['column_types'].items():
        null_count = report['null_counts'][col]
        print(f"  - {col}: {dtype} (Nulls: {null_count})")
    print("\nSample Data (First 3 Rows):")
    print(df.head(3))
    print("==================================================================\n")

    return report

def ingest_dataset(filepath, format_type='auto', delimiter=',', encoding='utf-8', is_nested=False):
    """
    Unified, explicit multi-format data ingestion handler.
    """
    ext = filepath.split('.')[-1].lower() if format_type == 'auto' else format_type.lower()
    
    if ext == 'json':
        df = ingest_json(filepath, is_nested=is_nested)
        used_enc, used_sep = 'utf-8', 'N/A'
    elif ext == 'csv':
        try:
            df = ingest_csv(filepath, delimiter=delimiter, encoding=encoding)
            used_enc, used_sep = encoding, delimiter
        except Exception:
            logging.info(f"Primary CSV load failed for '{filepath}'. Initiating encoding/delimiter fallback...")
            df, used_enc, used_sep = ingest_csv_with_fallback(filepath)
    else:
        df = pd.read_csv(filepath)
        used_enc, used_sep = encoding, delimiter

    report = document_ingestion(df, source=filepath)
    report['used_encoding'] = used_enc
    report['used_delimiter'] = used_sep

    return df, report

if __name__ == "__main__":
    test_csv = "data/raw/sales.csv"
    if os.path.exists(test_csv):
        print("--- Testing CSV Ingestion ---")
        df_csv, rep_csv = ingest_dataset(test_csv, delimiter=',', encoding='utf-8')

import pandas as pd
import numpy as np
import logging
import os
import json
from data_validation import generate_report
from data_ingestion import ingest_dataset

INPUT_FILE = "data/raw/sales.csv"
OUTPUT_FILE = "output/processed_sales.csv"
LOG_FILE = "logs/workflow.log"
MIN_AMOUNT = 0

os.makedirs("output", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ingest_data(filepath, delimiter=',', encoding='utf-8'):
    """
    Read CSV file into a Pandas DataFrame after validating through quality firewall
    and using explicit ingestion parameters with audit reporting.
    """
    logging.info(f"Running data validation gate on {filepath}...")
    report = generate_report(filepath)
    if report['status'] != 'PASSED':
        err_msg = f"Data Quality Gate FAILED for {filepath}: {json.dumps(report['checks'])}"
        logging.error(err_msg)
        raise ValueError(err_msg)

    try:
        df, audit_rep = ingest_dataset(filepath, delimiter=delimiter, encoding=encoding)
        logging.info(f"Ingested {len(df)} rows from {filepath} (used encoding: {audit_rep['used_encoding']}, delimiter: {audit_rep['used_delimiter']})")
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise

def process_data(df, min_amount=0):
    """
    Apply business rules and transformations to the raw data.
    
    Filters out invalid amounts, removes duplicates, and imputes missing values.
    
    Args:
        df (pd.DataFrame): Raw transaction history.
        min_amount (float): Minimum valid transaction amount (default: 0).
        
    Returns:
        pd.DataFrame: The cleaned and transformed dataset.
    """
    rows_before = len(df)
    
    df = df.drop_duplicates()
    
    df = df[df['amount'] >= min_amount]
    
    if not df['amount'].isnull().all():
        fill_value = df['amount'].median()
        df.fillna({'amount': fill_value}, inplace=True)
    
    rows_after = len(df)
    logging.info(f"Processing: {rows_before} rows -> {rows_after} rows")
    return df

def output_results(df, filepath):
    """
    Write the processed DataFrame to a target destination.
    
    Args:
        df (pd.DataFrame): The processed dataset to output.
        filepath (str): Destination path for the CSV output.
    """
    df.to_csv(filepath, index=False)
    logging.info(f"Output saved: {filepath}")
    print(f"[SUCCESS] Processed {len(df)} records")

if __name__ == "__main__":
    try:
        print("Starting workflow...")
        
        data = ingest_data(INPUT_FILE)
        
        clean_data = process_data(data, min_amount=MIN_AMOUNT)
        
        output_results(clean_data, OUTPUT_FILE)
        
        print("[SUCCESS] Workflow completed successfully")
        
    except Exception as e:
        logging.error(f"Workflow failed: {str(e)}")
        print(f"Error: {str(e)}")
        exit(1)


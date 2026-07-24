"""
String Cleaning Pipeline (Assignment 11)
Standardizes customer database fields from inconsistent data sources.

Features & Tasks Implemented:
1. Strip Whitespace Consistently (.str.strip)
2. Normalize Casing to Consistent Standard (.str.lower)
3. Remove Special Characters Using Regex ([^a-zA-Z0-9 ])
4. Standardize Categorical Labels Using Mapping Dictionary (.map / .replace)
5. Reusable String Cleaning Function (`clean_text_column`)
"""

import sys
import os
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def strip_all_strings(df):
    """Strip whitespace from all string columns."""
    string_cols = df.select_dtypes(include=['object']).columns
    print("\n--- Task 1: Stripping Whitespace ---")
    for col in string_cols:
        before = df[col].nunique()
        df[col] = df[col].str.strip()
        after = df[col].nunique()
        print(f"{col}: {before} -> {after} unique values")
    return df


def normalize_casing(df, columns_to_lower):
    """Normalize casing for specified columns."""
    print("\n--- Task 2: Normalizing Casing ---")
    for col in columns_to_lower:
        if col in df.columns:
            df[col] = df[col].str.lower()
            print(f"Normalized {col} to lowercase")
    return df


def remove_special_characters(df, columns):
    """Remove special characters from specified columns."""
    print("\n--- Task 3: Removing Special Characters ---")
    for col in columns:
        if col in df.columns:
            # Matches any character that is NOT alphanumeric or a standard space
            df[col] = df[col].str.replace('[^a-zA-Z0-9 ]', '', regex=True)
            print(f"Removed special characters from {col}")
    return df


# Mapping dictionary for Task 4
segment_map = {
    'b2b': 'B2B',
    'b 2 b': 'B2B',
    'b2 b': 'B2B',
    'business-to-business': 'B2B',
    'sme': 'SMB',
    'small medium enterprise': 'SMB',
    'smb': 'SMB',
    'enterprise': 'Enterprise',
    'ent': 'Enterprise'
}


def clean_text_column(series, lowercase=True, strip=True, 
                     remove_special=False, mapping=None):
    """
    Reusable text cleaning function for any string column.
    
    Parameters:
    - series (pd.Series): Input text column.
    - lowercase (bool): If True, converts strings to lower case.
    - strip (bool): If True, strips leading and trailing whitespace.
    - remove_special (bool): If True, removes non-alphanumeric characters except spaces.
    - mapping (dict): Optional dictionary mapping values to canonical labels.
    """
    result = series.copy()
    
    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values in column '{series.name}'")
    
    if strip:
        result = result.astype(str).str.strip()
        result = result.mask(series.isna(), np.nan)
        
    if lowercase:
        result = result.str.lower()
        
    if remove_special:
        result = result.str.replace('[^a-zA-Z0-9 ]', '', regex=True)
        
    if mapping:
        result = result.map(lambda x: mapping.get(x, mapping.get(str(x).lower(), x)) if pd.notna(x) else x)
        
    return result


def generate_sample_dataset():
    """Generates synthetic messy customer dataset with multi-source inconsistencies."""
    data = {
        'customer_id': [101, 102, 103, 104, 105, 106, 107, 108],
        'name': [' JOHN ', 'john', 'John', ' Alice ', 'ALICE', 'Bob ', 'Carol', '  São Paulo User  '],
        'product_name': [' Electronics ', 'electronics', 'ELECTRONICS', ' Laptops ', 'laptops', 'Smartphones ', '  Home Appliances  ', 'Gaming Gear'],
        'segment': ['b2b', 'b 2 b', 'B2B', 'business-to-business', 'sme', 'small medium enterprise', 'enterprise', 'ent'],
        'location': ['São Paulo', 'Montréal', ' São Paulo ', 'New York!', 'San José', 'Montréal ', 'Zürich', 'Tokyo@Japan']
    }
    return pd.DataFrame(data)


def main():
    print("==================================================")
    print("       CUSTOMER DATASET STRING CLEANING PIPELINE  ")
    print("==================================================")
    
    # 1. Load messy synthetic dataset
    df = generate_sample_dataset()
    print("\n--- Raw Sample Dataset ---")
    print(df)
    
    # Task 1 Demonstration
    print("\n[Before Task 1 Value Counts for product_name]")
    print(df['product_name'].value_counts())
    df = strip_all_strings(df)
    print("\n[After Task 1 Value Counts for product_name]")
    print(df['product_name'].value_counts())
    
    # Task 2 Demonstration
    print("\n[Before Task 2 Casing Normalization (name & product_name)]")
    print(df[['name', 'product_name']].head())
    df = normalize_casing(df, columns_to_lower=['name', 'product_name', 'location'])
    print("\n[After Task 2 Casing Normalization]")
    print(df[['name', 'product_name']].head())
    
    # Task 3 Demonstration
    print("\n[Before Task 3 Special Character Removal (location)]")
    print(df['location'].tolist())
    df = remove_special_characters(df, columns=['location', 'name'])
    print("\n[After Task 3 Special Character Removal (location)]")
    print(df['location'].tolist())
    
    # Task 4 Demonstration
    print("\n[Before Task 4 Segment Mapping]")
    print(df['segment'].value_counts())
    df['segment'] = df['segment'].map(lambda x: segment_map.get(x.lower(), x) if pd.notna(x) else x)
    print("\n[After Task 4 Segment Mapping]")
    print(df['segment'].value_counts())

    # Task 5 Reusable Function Demonstration & Edge Case Testing
    print("\n--- Task 5: Testing Reusable clean_text_column with Edge Cases ---")
    test_cases = [
        '  Product A  ',      # Leading/trailing spaces
        'PRODUCT B',         # All caps
        'Product_C',         # Special char
        None,                # Null value
        ''                   # Empty string
    ]
    test_series = pd.Series(test_cases, name='test_column')
    test_result = clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)
    print("\nTest Inputs:\n", test_series)
    print("\nCleaned Outputs:\n", test_result)
    
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/cleaned_customer_data.csv', index=False)
    print("\nCleaned data successfully written to 'data/processed/cleaned_customer_data.csv'.")


if __name__ == '__main__':
    main()

"""
Datetime Feature Engineering Pipeline (Assignment 12)
Parses raw transaction timestamp strings and extracts temporal features for engagement & churn analysis.

Features & Tasks Implemented:
1. Parse Timestamp Strings with Explicit Format (`pd.to_datetime` with explicit `%Y-%m-%d %H:%M:%S`)
2. Extract Day-of-Week and Hour-of-Day (`.dt.day_name()`, `.dt.hour`)
3. Compute Week Number and Resample Data (`.dt.isocalendar().week`, `.resample('W')`)
4. Compute Days-Since-Event Metric (`(today - max_date).dt.days` recency)
5. Build Time-Indexed Aggregation (Multi-level groupby & pivot table)
"""

import sys
import os
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def generate_sample_transactions():
    """Generates synthetic transaction dataset with raw datetime strings."""
    data = {
        'transaction_id': range(1001, 1021),
        'customer_id': [101, 102, 101, 103, 104, 102, 105, 101, 106, 103,
                        104, 105, 102, 107, 101, 108, 103, 106, 105, 104],
        'transaction_date': [
            "2025-01-05 09:15:30", "2025-01-06 14:30:45", "2025-01-12 18:22:10",
            "2025-01-15 10:45:00", "2025-01-18 21:05:15", "2025-01-20 11:12:00",
            "2025-01-25 15:50:20", "2025-02-01 08:30:00", "2025-02-03 16:40:10",
            "2025-02-10 13:00:00", "2025-02-14 19:25:35", "2025-02-18 12:10:50",
            "2025-02-22 17:45:00", "2025-03-01 10:00:00", "2025-03-05 14:15:20",
            "2025-03-10 09:05:00", "2025-03-15 20:30:40", "2025-03-18 11:40:00",
            "2025-03-22 16:20:15", "2025-03-25 13:10:00"
        ],
        'amount': [150.0, 299.5, 45.0, 899.0, 120.0, 350.0, 60.0, 210.0, 450.0, 1100.0,
                   75.0, 520.0, 310.0, 85.0, 640.0, 1250.0, 340.0, 95.0, 410.0, 180.0]
    }
    return pd.DataFrame(data)


def parse_timestamps(df, col='transaction_date', fmt='%Y-%m-%d %H:%M:%S'):
    """Task 1: Parse string timestamps into datetime64 using explicit format string."""
    print("\n--- Task 1: Parsing Timestamps with Explicit Format ---")
    print(f"Format String Specified: '{fmt}'")
    df[col] = pd.to_datetime(df[col], format=fmt)
    print(f"Verified Dtype: {df[col].dtype}")
    return df


def extract_temporal_features(df, col='transaction_date'):
    """Task 2: Extract day of week and hour of day."""
    print("\n--- Task 2: Extracting Day-of-Week and Hour-of-Day ---")
    df['day_of_week'] = df[col].dt.day_name()
    df['hour'] = df[col].dt.hour
    
    print("\nHourly Transaction Volume:")
    hourly_volume = df.groupby('hour').size()
    print(hourly_volume)
    return df


def compute_weekly_resample(df, date_col='transaction_date', amount_col='amount'):
    """Task 3: Compute week number and resample weekly totals."""
    print("\n--- Task 3: Computing Week Number & Resampling Data ---")
    df['week_num'] = df[date_col].dt.isocalendar().week
    
    df_ts = df.set_index(date_col)
    weekly_summary = df_ts[amount_col].resample('W').agg(['sum', 'count', 'mean'])
    print("\nWeekly Revenue and Transaction Summary:")
    print(weekly_summary)
    return df, weekly_summary


def compute_customer_recency(df, customer_id_col='customer_id', date_col='transaction_date'):
    """Task 4: Calculate days since last purchase per customer for recency/churn analysis."""
    print("\n--- Task 4: Computing Days-Since-Event Recency Metric ---")
    # Reference snapshot date for simulation/testing (e.g. 2025-04-01)
    snapshot_date = pd.Timestamp('2025-04-01')
    
    customer_last_purchase = df.groupby(customer_id_col)[date_col].max().reset_index()
    customer_last_purchase['days_since_last_purchase'] = (snapshot_date - customer_last_purchase[date_col]).dt.days
    
    # Merge recency back into original dataframe
    df = df.merge(customer_last_purchase[[customer_id_col, 'days_since_last_purchase']], on=customer_id_col, how='left')
    
    print("\nRecency Summary (Days Since Last Purchase as of Snapshot Date 2025-04-01):")
    print(customer_last_purchase[['customer_id', date_col, 'days_since_last_purchase']])
    print("\nRecency Statistics:")
    print(df['days_since_last_purchase'].describe())
    return df


def time_indexed_aggregations(df, amount_col='amount'):
    """Task 5: Perform multi-dimension aggregations and hour x day-of-week pivot table."""
    print("\n--- Task 5: Time-Indexed Aggregation & Heatmap Pivot Table ---")
    hourly_daily = df.groupby(['day_of_week', 'hour'])[amount_col].agg(['sum', 'count', 'mean'])
    print("\nMulti-level Groupby (Day of Week & Hour):")
    print(hourly_daily.head(10))
    
    pivot_table = pd.pivot_table(
        df,
        values=amount_col,
        index='hour',
        columns='day_of_week',
        aggfunc='sum',
        fill_value=0
    )
    print("\nPivot Table (Hour vs Day of Week Total Revenue):")
    print(pivot_table)
    return pivot_table


def main():
    print("==================================================")
    print("   DATETIME FEATURE ENGINEERING PIPELINE (ASSIGNMENT 12)")
    print("==================================================")
    
    df = generate_sample_transactions()
    print("\n--- Raw Input Transactions ---")
    print(df.head())
    print(f"Raw Date Column Dtype: {df['transaction_date'].dtype}")
    
    # Task 1: Parse timestamps
    df = parse_timestamps(df)
    
    # Task 2: Extract day name and hour
    df = extract_temporal_features(df)
    
    # Task 3: Week number and resampling
    df, weekly_summary = compute_weekly_resample(df)
    
    # Task 4: Recency (days since last purchase)
    df = compute_customer_recency(df)
    
    # Task 5: Time-indexed aggregations & pivot table
    pivot = time_indexed_aggregations(df)
    
    # Testing & Verification Assertions
    print("\n--- Verification & Validation Metrics ---")
    print(f"Min date: {df['transaction_date'].min()}")
    print(f"Max date: {df['transaction_date'].max()}")
    print(f"Days in dataset span: {(df['transaction_date'].max() - df['transaction_date'].min()).days} days")
    print(f"Hours with data: {sorted(df['hour'].unique())}")
    print(f"Weeks in dataset: {df['week_num'].nunique()}")
    print(f"Min days since purchase: {df['days_since_last_purchase'].min()}")
    print(f"Max days since purchase: {df['days_since_last_purchase'].max()}")
    
    # Save output dataset to data/processed
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/datetime_features_transactions.csv', index=False)
    print("\nProcessed feature dataset successfully saved to 'data/processed/datetime_features_transactions.csv'.")


if __name__ == '__main__':
    main()

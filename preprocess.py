"""
========================================================================
   EDUSHIELD: DATA PREPROCESSING PIPELINE
   preprocess.py: Clean, transform, scale and split the cohort data.
========================================================================
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def load_data(filepath):
    """Loads dataset from a CSV file."""
    print(f"[*] Loading dataset from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset CSV file not found at {filepath}")
    
    # Read the dataset (automatically separates comma values)
    df = pd.read_csv(filepath)
    return df

def explore_dataset(df):
    """Performs initial dataset inspection."""
    print("\n" + "="*50)
    print("      EXPLORATORY DATA INSPECTION SUMMARY")
    print("="*50)
    print(f"[*] Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    print("\n[*] Data Types and Sample Values:")
    print(df.dtypes.to_string())
    
    print("\n[*] Checking for Missing Values:")
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()
    if total_missing > 0:
        print(missing_counts[missing_counts > 0].to_string())
    else:
        print("    No missing values detected.")
        
    print("\n[*] Checking for Duplicate Rows:")
    duplicate_count = df.duplicated().sum()
    print(f"    Found {duplicate_count} duplicate rows.")
    return duplicate_count

def clean_data(df):
    """Cleans duplicates and handles missing values."""
    # Remove duplicate rows
    initial_shape = df.shape
    df_cleaned = df.drop_duplicates().copy()
    if df_cleaned.shape != initial_shape:
        print(f"[+] Removed {initial_shape[0] - df_cleaned.shape[0]} duplicate rows.")
    else:
        print("[*] No duplicate rows to remove.")
        
    # Handle missing values if any (none expected in this dataset)
    if df_cleaned.isnull().sum().sum() > 0:
        print("[!] Warning: Missing values detected post-deduplication, imputing with median/mode...")
        for col in df_cleaned.columns:
            if df_cleaned[col].isnull().sum() > 0:
                if df_cleaned[col].dtype in ['int64', 'float64']:
                    df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
                else:
                    df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
                    
    return df_cleaned

def transform_target(df):
    """Maps the multi-class Target column into binary classification:
       Dropout -> 1 (At Risk)
       Graduate / Enrolled -> 0 (Not At Risk)
    """
    print("\n[*] Target Value Counts Before Transformation:")
    print(df['Target'].value_counts().to_string())
    
    # Map target values
    # Graduate -> 0, Enrolled -> 0, Dropout -> 1
    df['Target'] = df['Target'].map({
        'Dropout': 1,
        'Graduate': 0,
        'Enrolled': 0
    })
    
    print("\n[+] Target Value Counts After Transformation (0: Safe/Graduated, 1: At Risk):")
    print(df['Target'].value_counts().to_string())
    return df

def scale_and_split(df, target_col='Target', random_state=42):
    """Scales numerical features and splits data into 80% train / 20% test."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Scale features using StandardScaler
    print("\n[*] Fitting StandardScaler on features...")
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # Save the fitted scaler
    os.makedirs('models', exist_ok=True)
    scaler_path = os.path.join('models', 'scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"[+] Serialized scaler saved to: {scaler_path}")
    
    # Split into 80% training / 20% testing
    print("[*] Splitting dataset into 80% Training and 20% Testing...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.20, random_state=random_state, stratify=y
    )
    
    # Reset indices to align rows before concatenation
    X_train = X_train.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)
    
    # Re-assemble dataframes for model training script
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    return train_df, test_df

def main():
    dataset_path = os.path.join('dataset', 'student_dropout_data.csv')
    
    # 1. Load Data
    df = load_data(dataset_path)
    
    # 2. Explore Data
    explore_dataset(df)
    
    # 3. Clean duplicates & missing values
    df_cleaned = clean_data(df)
    
    # 4. Transform Target to binary
    df_transformed = transform_target(df_cleaned)
    
    # 5. Scale and Split
    train_df, test_df = scale_and_split(df_transformed)
    
    # 6. Save split datasets
    train_output_path = os.path.join('dataset', 'train_processed.csv')
    test_output_path = os.path.join('dataset', 'test_processed.csv')
    
    train_df.to_csv(train_output_path, index=False)
    test_df.to_csv(test_output_path, index=False)
    
    print(f"\n[+] Preprocessing Complete!")
    print(f"    - Processed Train Split saved to: {train_output_path} (Shape: {train_df.shape})")
    print(f"    - Processed Test Split saved to: {test_output_path} (Shape: {test_df.shape})")

if __name__ == "__main__":
    main()

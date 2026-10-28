"""
========================================================================
   EDUSHIELD: MACHINE LEARNING TRAINING & EVALUATION PIPELINE
   train_model.py: Train, evaluate, benchmark, and export the best model.
========================================================================
"""

import os
import json
import pandas as pd
import numpy as np
import joblib

# Sklearn Classifiers & Metrics
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)

# Plotting Feature Importance
import matplotlib.pyplot as plt
import seaborn as sns

# Try importing XGBoost
try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

def load_processed_data():
    """Loads preprocessed train and test data."""
    train_path = os.path.join('dataset', 'train_processed.csv')
    test_path = os.path.join('dataset', 'test_processed.csv')
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Processed split CSV files not found. Run preprocess.py first.")
        
    print("[*] Loading train split from:", train_path)
    train_df = pd.read_csv(train_path)
    print("[*] Loading test split from:", test_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df.drop(columns=['Target'])
    y_train = train_df['Target']
    X_test = test_df.drop(columns=['Target'])
    y_test = test_df['Target']
    
    return X_train, X_test, y_train, y_test

def get_models_dict():
    """Returns a dictionary of initialized models to evaluate."""
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree Classifier": DecisionTreeClassifier(random_state=42),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=100, random_state=42),
        "Support Vector Machine (SVM)": SVC(probability=True, random_state=42),
        "K-Nearest Neighbors (KNN)": KNeighborsClassifier(),
        "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42)
    }
    
    if XGB_AVAILABLE:
        # Use simple parameter mapping for binary classification
        models["XGBoost Classifier"] = XGBClassifier(
            eval_metric='logloss', random_state=42
        )
    else:
        print("[!] XGBoost is not available. Skipping XGBoost from classification evaluation.")
        
    return models

def evaluate_models(models, X_train, X_test, y_train, y_test):
    """Trains each classifier, evaluates metrics, and returns summaries."""
    print("\n" + "="*80)
    print("      TRAINING AND EVALUATING ML CLASSIFIERS")
    print("="*80)
    
    metrics_summary = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"[*] Training model: {name}...")
        # Fit the model
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Predict values and probabilities
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Compute metrics
        acc = accuracy_score(y_test, y_pred) * 100
        prec = precision_score(y_test, y_pred, zero_division=0) * 100
        rec = recall_score(y_test, y_pred) * 100
        f1 = f1_score(y_test, y_pred) * 100
        auc = roc_auc_score(y_test, y_prob) * 100
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        metrics_summary[name] = {
            "accuracy": round(acc, 2),
            "precision": round(prec, 2),
            "recall": round(rec, 2),
            "f1_score": round(f1, 2),
            "roc_auc": round(auc, 2),
            "confusion_matrix": cm
        }
        
        print(f"    - Accuracy: {acc:.2f}% | F1 Score: {f1:.2f}% | ROC-AUC: {auc:.2f}%")
        
    return trained_models, metrics_summary

def print_comparison_grid(metrics):
    """Prints a clean ASCII comparison table to the logs."""
    print("\n" + "="*80)
    print("                MODEL PERFORMANCE COMPARISON BENCHMARKS")
    print("="*80)
    print(f"{'Model Name':<30} | {'Accuracy (%)':<12} | {'Precision (%)':<13} | {'Recall (%)':<10} | {'F1 (%)':<8} | {'ROC-AUC (%)':<11}")
    print("-"*80)
    for name, m in sorted(metrics.items(), key=lambda x: x[1]['f1_score'], reverse=True):
        print(f"{name:<30} | {m['accuracy']:<12.2f} | {m['precision']:<13.2f} | {m['recall']:<10.2f} | {m['f1_score']:<8.2f} | {m['roc_auc']:<11.2f}")
    print("="*80)

def select_best_model(metrics):
    """Selects the best model based primarily on F1 score."""
    best_name = None
    best_f1 = -1
    
    for name, m in metrics.items():
        if m['f1_score'] > best_f1:
            best_f1 = m['f1_score']
            best_name = name
            
    print(f"\n[+] Selected Best Model: {best_name} (F1 Score: {best_f1:.2f}%)")
    return best_name

def handle_feature_importance(best_model, model_name, feature_names):
    """Plots and returns top 15 feature importances if supported."""
    importance_list = []
    
    # Check if model has feature importance coefficients
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Build feature importance list
        for i in indices:
            importance_list.append({
                "feature": feature_names[i],
                "importance": float(importances[i])
            })
            
        # Plot top 15 feature importances
        top_n = min(15, len(feature_names))
        top_features = [feature_names[idx] for idx in indices[:top_n]]
        top_importances = importances[indices[:top_n]]
        
        print(f"\n[*] Generating Feature Importance visualization for {model_name}...")
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        # Draw horizontal bar chart
        ax = sns.barplot(x=top_importances, y=top_features, hue=top_features, palette="viridis", legend=False)
        plt.title(f"Top {top_n} Important Features - {model_name}", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Importance score", fontsize=12, labelpad=10)
        plt.ylabel("Student variables", fontsize=12)
        plt.tight_layout()
        
        # Save visualization to static assets directory
        os.makedirs(os.path.join('static', 'images'), exist_ok=True)
        img_path = os.path.join('static', 'images', 'feature_importance.png')
        plt.savefig(img_path, dpi=150)
        plt.close()
        print(f"[+] Saved feature importance plot to: {img_path}")
        
    elif hasattr(best_model, 'coef_'):
        # For linear models like Logistic Regression
        coefficients = best_model.coef_[0]
        abs_coefficients = np.abs(coefficients)
        indices = np.argsort(abs_coefficients)[::-1]
        
        for i in indices:
            importance_list.append({
                "feature": feature_names[i],
                "importance": float(coefficients[i])
            })
            
        # Plot top 15 linear weights
        top_n = min(15, len(feature_names))
        top_features = [feature_names[idx] for idx in indices[:top_n]]
        top_coefs = coefficients[indices[:top_n]]
        
        print(f"\n[*] Generating Linear Weight coefficients plot for {model_name}...")
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        # Color based on sign (positive = high dropout risk, negative = safe retention)
        colors = ['#dc2626' if w > 0 else '#2563eb' for w in top_coefs]
        
        sns.barplot(x=top_coefs, y=top_features, palette=colors)
        plt.title(f"Top {top_n} Model Coefficients - {model_name}", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Coefficient weight (Red: Risk factor, Blue: Retention factor)", fontsize=11, labelpad=10)
        plt.ylabel("Student variables", fontsize=12)
        plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
        plt.tight_layout()
        
        os.makedirs(os.path.join('static', 'images'), exist_ok=True)
        img_path = os.path.join('static', 'images', 'feature_importance.png')
        plt.savefig(img_path, dpi=150)
        plt.close()
        print(f"[+] Saved coefficients weight plot to: {img_path}")
        
    else:
        print(f"[*] Note: Model {model_name} does not support feature coefficients directly.")
        
    return importance_list

def main():
    # 1. Load Data
    X_train, X_test, y_train, y_test = load_processed_data()
    feature_names = list(X_train.columns)
    
    # 2. Get evaluation list
    models = get_models_dict()
    
    # 3. Train & Evaluate
    trained_models, metrics = evaluate_models(models, X_train, X_test, y_train, y_test)
    
    # 4. Print Benchmarks Table
    print_comparison_grid(metrics)
    
    # 5. Select Best Classifier
    best_name = select_best_model(metrics)
    best_model = trained_models[best_name]
    
    # 6. Extract Feature Importance / Weights
    importance_data = handle_feature_importance(best_model, best_name, feature_names)
    
    # 7. Save output files
    os.makedirs('models', exist_ok=True)
    
    # Save the selected best model
    model_output_path = os.path.join('models', 'student_dropout_model.pkl')
    joblib.dump(best_model, model_output_path)
    print(f"\n[+] Saved best model file to: {model_output_path}")
    
    # Save all benchmarking and feature stats to JSON
    json_output_path = os.path.join('models', 'model_metrics.json')
    metrics_payload = {
        "best_model_name": best_name,
        "models": metrics,
        "feature_importance": importance_data
    }
    
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_payload, f, indent=4)
    print(f"[+] Saved metrics json to: {json_output_path}")
    print("[*] Pipeline complete!")

if __name__ == "__main__":
    main()

# EduShield: AI-Powered Student Retention Analytics Platform

EduShield is an end-to-end Machine Learning web application designed to predict whether higher-education students are at risk of dropping out before completing their courses. By providing early predictions based on demographics, academic credit completion, financial statuses, and macroeconomic indicators, EduShield helps universities coordinate timely counseling and financial interventions.

---

## 🚀 Key Features

* **Institutional Analytics Dashboard**: Monitor student retention rates, course-specific attrition risk, scholarship correlations, and credit-completion trends.
* **Dataset & EDA Overview**: Inspect feature attributes, schemas, missing value summaries, cohort age profiles, and raw dataset samples.
* **Classifier Model Benchmarking**: Benchmark multiple classifiers (Logistic Regression, Decision Trees, K-Nearest Neighbors, SVMs, Random Forests, Gradient Boosting, and XGBoost) and view model accuracies, precisions, recalls, F1 scores, and ROC-AUC metrics.
* **Profile-based Risk Assessment Form**: Enter demographic, background, and credit profiles to receive real-time risk predictions, probability dials, confidence statistics, and personalized intervention action lists.
* **SQLite Ingestion & Logs**: Integration-ready SQLite database infrastructure to audit incoming profiles and store historical cohort profiles.

---

## 🛠️ Technology Stack

* **Backend Framework**: Python 3, Flask, SQLite3
* **Frontend styling & libraries**: HTML5, CSS3 (Custom Glassmorphism design system), JavaScript, Bootstrap 5, FontAwesome Icons, Google Fonts (Outfit & Inter)
* **Data Science & ML Libraries**: Pandas, NumPy, Scikit-Learn, Joblib, Plotly.js (Client-side interactive charting)

---

## 📂 Project Structure

```
EduShield/
│
├── dataset/                     # For storing UCI CSV datasets
├── models/                      # For storing serialized model files (.pkl)
├── static/                      # Static assets served by Flask
│   ├── css/
│   │   └── style.css            # Custom Design system, variables, components & grids
│   ├── js/
│   │   └── main.js              # Sidebar logic, AJAX predict API, Plotly configurations
│   └── images/                  # Workspace image assets
│
├── templates/                   # Reusable HTML layouts with Jinja inheritance
│   ├── base.html                # Sidebar container, CDNs, header banner blocks
│   ├── dashboard.html           # KPI metrics, institutional Plotly widgets & insights
│   ├── dataset.html             # Attributes description, data previews & EDA plots
│   ├── model_comparison.html    # Algorithms performance tables & plots
│   ├── prediction.html          # Profile intake form, risk gauge & recommendations
│   └── about.html               # Project details, outcomes, pipeline & stack descriptions
│
├── app.py                       # Main Flask server entrypoint, routes, SQLite helper, mock API
├── config.py                    # Server config, base directories, SQLite database paths
├── requirements.txt             # Declared Python libraries dependencies
└── README.md                    # Platform documentation
```

---

## 💻 Installation & Setup

1. **Verify Python Setup**: Ensure you have Python 3 and the Windows python launcher `py` installed.
2. **Install Dependencies**:
   ```bash
   py -m pip install -r requirements.txt
   ```
3. **Run the Flask Server**:
   ```bash
   py app.py
   ```
4. **Access the Platform**:
   Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📈 Machine Learning Workflow

```
[ Cohort Dataset CSV ]
          │
          ▼
[ Preprocessing & SQLite Ingestion ]
          │
          ▼
[ Exploratory Data Analysis (EDA) ]
          │
          ▼
[ Feature Engineering & Split (80:20) ]
          │
          ▼
[ Benchmark 7 Classifier Algorithms ]
          │
          ▼
[ Export Best Performing Classifier Model (.pkl) ]
          │
          ▼
[ Production Inference API & DB Audit ]
```

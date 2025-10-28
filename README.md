# 🚛 Air Pressure System (APS) Failure Prediction – End-to-End MLOps Production Grade Project

## 🧠 Overview

This project is a **production-grade MLOps pipeline** for predicting failures in the **Air Pressure System (APS)** of heavy-duty trucks.  
The APS supplies pressurized air used in braking, gear shifting, and other critical functions. The objective is to minimize operational costs by **reducing false predictions** — especially **false negatives**, which represent undetected APS failures and can cause expensive breakdowns.

---
> ⚙️ This project is built with a complete **MLOps production pipeline** using **Docker**, **AWS S3**, **AWS EC2**, **AWS ECR**, and **GitHub Actions** for automated **CI/CD deployment**.  
It ensures continuous integration, continuous training, and continuous deployment with containerized builds and cloud-based orchestration.

---
## 🧩 Problem Statement

The APS dataset contains **sensor readings** from the truck’s air pressure system.

- **Positive Class (1):** Trucks with APS component failure.  
- **Negative Class (0):** Trucks with failures unrelated to APS.  

### 🎯 Business Objective

Misclassification costs are **asymmetric**:

- **Cost_1 (False Positive)** = 10 (unnecessary mechanic check/repair)  
- **Cost_2 (False Negative)** = 500 (missed APS failure → possible breakdown)

**Total Cost formula:**

\[
\text{Total Cost} = (10 \times \text{False Positives}) + (500 \times \text{False Negatives})
\]

Because `Cost_2` is 50× `Cost_1`, the pipeline is optimized to **minimize false negatives** first and then reduce false positives.

---

## 🏗️ Folder Structure

## 📁 Project Structure

```bash
sensor_project/
│
├── .github/
│   └── workflows/
│       └── main.yaml
│
├── sensor/
│   ├── cloud_storage/
│   │   └── s3_syncer.py
│   │
│   ├── components/
│   │   └── __init__.py
│   │
│   ├── configuration/
│   │   ├── __init__.py
│   │   └── mongo_db_connection.py
│   │
│   ├── constant/
│   │   ├── __init__.py
│   │   ├── application.py
│   │   ├── database.py
│   │   ├── env_variable.py
│   │   ├── s3_bucket.py
│   │   └── training_pipeline/
│   │       └── __init__.py
│   │
│   ├── data_access/
│   │   └── __init__.py
│   │
│   ├── entity/
│   │   ├── __init__.py
│   │   └── artifact_entity.py
│   │
│   ├── ml/
│   │   ├── metric/
│   │   │   ├── __init__.py
│   │   │   └── classification_metric.py
│   │   │
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── estimator.py
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── training_pipeline.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── main_utils.py
│   │
│   └── __init__.py
│
├── main.py
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

---
## ⚡ FastAPI Integration – Real-Time Inference API

To serve predictions via REST, this project integrates **FastAPI** for scalable, low-latency inference.


---
## 🔄 CI/CD Pipeline (GitHub Actions + AWS)

**Workflow:** `.github/workflows/main.yaml`

**Pipeline stages:**
1. **Build & Lint**
   - Install dependencies from `requirements.txt`
   - Run linters and static checks (flake8/black)
2. **Test**
   - Run unit tests and integration tests
3. **Train** (optional / conditional)
   - Execute training pipeline (if data or code changes warrant retraining)
   - Generate artifacts under `artifact/`
4. **Evaluation & Validation**
   - Run evaluation scripts to compute metrics and custom cost
   - Validate model meets thresholds (e.g., total cost < threshold OR FN rate <= limit)
5. **Sync & Deploy**
   - Upload model, transformer, and artifacts to **AWS S3**
   - (Optional) Trigger deployment to EC2 / Lambda / SageMaker


**Note:** Secure secrets using GitHub Secrets (e.g., `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `MONGO_DB_URL`).

---

## ☁️ AWS Integration

- **S3** — primary artifact/model storage (trained models, transformers, metrics, logs)  
- **IAM** — least-privilege roles for CI/CD and runtime access  
- **EC2** — optional model serving options (batch/real-time)  
- **CloudWatch / S3 Events** — optional monitoring + retrain triggers

Common pattern:
- CI pipeline builds and tests → artifacts saved to `artifact/` → `s3_syncer.py` uploads artifacts to `s3://<bucket>/models/<run-id>/`

---

## 🧮 Schema Configuration

**File:** `config/schema.yaml` — controls ingestion + validation

Contents include:
- `columns` — list of all columns with types
- `numerical_columns` — features used for transformation/scaling
- `drop_columns` — columns to remove before training
- (Optional) `target_column` — explicit target column (e.g., `class`)

**Usage:**
- `Data Ingestion` reads schema and validates incoming data shape & dtypes.
- `Data Validation` will fail the pipeline if required columns missing or unexpected types present.

---

## 🧠 Machine Learning Pipeline (Detailed Steps)

### 1️⃣ Data Ingestion
- Read raw sensor data from **MongoDB** (via `mongo_db_connection.py`)
- Export collection to CSV / DataFrame
- Save raw artifact to `artifact/raw/` and optionally to **AWS S3**
- Split into train/test according to configuration (e.g., 80/20)

---

### 2️⃣ Data Transformation
- Handle missing values (impute or fill)
- Scale numeric features using **RobustScaler / StandardScaler**
- Encode categorical variables if present
- Save transformer object (`transformer.pkl`) to `artifact/` and **S3**

---

### 3️⃣ Model Training
- Train multiple candidate models (e.g., **LogisticRegression**, **RandomForest**, **XGBoost**)
- Train models on transformed training data
- Save the best-performing model wrapped in a **SensorModel** class (includes both model and preprocessor)
- Generate `model.pkl` under `artifact/model/` and optionally sync to **S3**

---

### 4️⃣ Evaluation
- Combine train & test data or evaluate on a dedicated holdout test set
- Compute model predictions and classic metrics: **Precision**, **Recall**, **F1-Score**
- **Compute custom cost:**
  \[
  \text{Total Cost} = (10 \times \text{False Positives}) + (500 \times \text{False Negatives})
  \]
- Select the model with **minimum total cost** and acceptable recall threshold

---

### 5️⃣ Model Pushing
- Once the model passes all evaluation checks:
  - Push the trained model (`model.pkl`), transformer (`transformer.pkl`), and metrics to **AWS S3** under a versioned directory (e.g., `s3://<bucket>/models/<timestamp>/`)
  - Containerize the inference environment using **Docker**
  - Build and push the Docker image to **AWS ECR (Elastic Container Registry)**
  - Deploy the containerized model to **AWS EC2** or other compute service for real-time inference
- The model version and metadata are tracked for reproducibility and rollback


# SugarSense AI: A Secure Local-First Medical Report Management and Machine Learning Analytics System for Diabetes-Related Health Monitoring

## Abstract

The increasing availability of digital medical reports creates opportunities to improve personal health-data management and longitudinal health monitoring. However, manually maintaining laboratory records can be inconvenient, and extracting useful information from historical medical reports often requires considerable effort. This project proposes **SugarSense AI**, a local-first health-data management and machine-learning analytics system designed to organize diabetes-related laboratory reports and glucose measurements.

The proposed system will accept PDF documents and image-based medical reports, extract relevant text using document-processing and optical character recognition (OCR) techniques, and identify candidate measurements such as fasting blood glucose, post-meal glucose, and glycated hemoglobin (HbA1c). Extracted information will be presented to the user for verification before being stored in a structured SQLite database. The application will support historical record retrieval, trend visualization, and basic statistical analysis using Python.

A separate machine-learning module will explore diabetes-related classification using an appropriate labeled dataset. Logistic Regression and Decision Tree classifiers will be evaluated using suitable validation procedures and performance metrics. The project will also explore MLOps practices, including experiment tracking, model versioning, automated testing, and reproducible training workflows.

The system will prioritize local data processing, restricted file access, and explicit user verification. It is intended as an educational prototype for personal health-record organization and ML experimentation, not as a diagnostic system or a substitute for professional medical advice.

**Keywords:** Diabetes monitoring, medical report extraction, OCR, Python, SQLite, machine learning, Logistic Regression, Decision Tree, MLOps, data privacy.

---

## 1. Introduction

Medical laboratory reports contain valuable information about a person's health, but these records are frequently distributed across paper documents, scanned images, and digital files. Reviewing changes over time can become difficult when previous results are not organized in a consistent format.

SugarSense AI proposes a unified application for collecting, organizing, and analyzing diabetes-related health information. The system will combine document processing, relational database management, data visualization, and machine learning within a single Python-based application.

Unlike a conventional diabetes prediction project that focuses exclusively on training a classifier, SugarSense AI will emphasize the complete data workflow: acquiring information from reports, validating extracted measurements, storing historical records, analyzing trends, and managing the machine-learning lifecycle.

## 2. Problem Statement

Individuals managing elevated blood glucose levels may have difficulty maintaining an organized history of laboratory measurements. Manual data entry can be time-consuming, while automated extraction from scanned documents can introduce errors involving numerical values, units, and dates.

Furthermore, a machine-learning prediction based on an isolated measurement may not adequately represent a person's longitudinal health history. Small educational ML projects also frequently omit important engineering practices, such as data validation, experiment tracking, model versioning, and secure handling of sensitive records.

Therefore, this project aims to develop a local-first system that simplifies medical-report organization, supports verified extraction of structured measurements, enables historical analysis, and provides a separate, reproducible environment for diabetes-related machine-learning experiments.

## 3. Objectives

The primary objectives are:

1. Develop a Python application that accepts PDF and image-based laboratory reports.
2. Extract text locally using PDF parsing and OCR technologies.
3. Identify candidate glucose and HbA1c measurements, including their dates and units where available.
4. Introduce a user-verification stage before saving extracted measurements.
5. Design a relational SQLite database for patients, reports, and historical measurements.
6. Generate historical summaries, statistical comparisons, and trend visualizations.
7. Train and evaluate Logistic Regression and Decision Tree models on an appropriate labeled diabetes-related dataset.
8. Introduce foundational MLOps practices for reproducibility, experiment tracking, testing, and model versioning.
9. Implement local file storage, access safeguards, and user-controlled deletion.
10. Maintain a clear separation between document extraction, historical analysis, and clinical prediction.

## 4. Proposed System Architecture

The application will consist of six principal modules.

### 4.1 Medical Report Upload

The upload module will accept PDF, JPG, and PNG files. It will validate file extensions, file signatures, file size, and processing limits before accepting a document.

Original reports will be stored in a restricted local directory using generated filenames rather than user-provided filenames.

### 4.2 Text Extraction and OCR

The document-processing module will use PyMuPDF to extract embedded text from text-based PDF documents. Scanned PDF pages and image files will be processed using Tesseract OCR.

A rule-based extraction component will identify candidate values associated with terms such as fasting glucose, blood glucose, post-meal glucose, and HbA1c. It will attempt to preserve associated units, dates, and source references.

Because OCR can misread digits, decimal points, and medical terminology, extracted information will remain unverified until reviewed by the user.

### 4.3 User Verification

The verification interface will display candidate measurements and allow users to correct or reject them before saving.

Each confirmed measurement will retain its source-report reference, measurement type, value, unit, and relevant date. The system will distinguish the date printed on the report from the date the report was uploaded.

### 4.4 Database and Historical Analysis

SQLite will provide persistent storage for structured records. The proposed database will include related tables for patients, uploaded reports, and glucose measurements.

Python and pandas will support historical queries, summaries, and time-based visualizations. The application will distinguish fasting, post-meal, and random glucose measurements instead of treating them as directly interchangeable.

### 4.5 Machine-Learning Module

The ML component will be developed separately from report extraction.

An appropriate labeled dataset will be used to train and evaluate Logistic Regression and Decision Tree classifiers for a defined diabetes-related classification task. The workflow will include preprocessing, train-test separation, model evaluation, and comparison using metrics such as precision, recall, F1-score, and ROC-AUC where appropriate.

The project will not assume that a model trained on a general public dataset is clinically valid for an individual user. Historical glucose trends and diabetes classification will remain separate analytical functions.

### 4.6 MLOps and Deployment

The MLOps component will introduce:

- MLflow for recording experiments, parameters, evaluation metrics, and model artifacts.
- Git and GitHub for source-code version control, excluding medical reports and sensitive records.
- Pytest for testing database operations, extraction logic, and ML functionality.
- GitHub Actions for automated test execution.
- FastAPI as a potential interface for serving approved model versions.
- Data-quality and drift monitoring as a later extension.

The initial application will operate locally. Deployment and remote access will only be considered after appropriate security measures are implemented.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| Database | SQLite |
| Database access | Python `sqlite3` |
| PDF processing | PyMuPDF |
| Optical character recognition | Tesseract OCR |
| Data processing | pandas, NumPy |
| Visualization | Matplotlib |
| Machine learning | scikit-learn |
| Experiment tracking | MLflow |
| API development | FastAPI |
| Automated testing | Pytest |
| Version control and CI | Git, GitHub Actions |

## 6. Database Design

The proposed relational database will contain three main entities.

**Patients:** Stores a patient identifier and the minimum personal information required by the application.

**Medical reports:** Stores report identifiers, generated local file references, upload timestamps, processing status, and related patient identifiers.

**Measurements:** Stores individual extracted and user-confirmed measurements, including measurement type, numerical value, unit, report date, verification status, and the source report identifier.

Primary keys and foreign keys will maintain relationships between records. Database constraints will enforce basic data integrity, while application-level validation will handle more complex checks.

Sensitive information will be minimized, and the database will not store unnecessary copies of extracted report text.

## 7. Security and Privacy

Since medical reports contain sensitive personal information, privacy will be treated as a core design requirement.

The initial implementation will use local processing and local file storage, avoiding external OCR services. File uploads will be restricted by type and size, and uploaded files will be handled using generated filenames and controlled storage paths.

The application will provide safeguards against unauthorized file access, unsafe document processing, and accidental exposure through source control or application logs. Database backups and stored files will require appropriate protection, since SQLite does not encrypt database contents by default.

The system will support deletion of stored reports and associated records. These measures will reduce privacy risks but will not, by themselves, guarantee complete security.

## 8. Evaluation Methodology

The project will be evaluated across four dimensions.

**Document extraction:** Test the extraction pipeline using representative text-based PDFs, scanned PDFs, and images. Measure extraction accuracy for relevant values, units, and dates against manually verified reference annotations.

**Database reliability:** Test record insertion, retrieval, updates, deletion, relational integrity, and correct handling of unverified measurements.

**Machine-learning performance:** Evaluate candidate classifiers using a suitable held-out test set and relevant performance metrics. Prevent data leakage and document the dataset's limitations.

**Engineering and privacy:** Test file-validation behavior, processing failures, deletion operations, reproducibility, and automated test execution.

No performance results or accuracy claims will be reported until experiments have been conducted.

## 9. Expected Outcomes

The expected deliverables are:

1. A functional local application for uploading PDF and image-based medical reports.
2. A local OCR and text-extraction pipeline with user verification.
3. A structured SQLite database containing verified historical measurements.
4. Historical data summaries and visualization features.
5. A separately evaluated diabetes-related ML classification experiment.
6. An MLflow-based experiment-tracking workflow.
7. Automated tests, project documentation, and a reproducible development environment.

The expected outcome is an educational prototype demonstrating how database engineering, document processing, machine learning, and MLOps can be combined in a privacy-conscious application.

## 10. Limitations and Future Scope

OCR performance may vary with image quality, document layout, handwriting, and the presence of ambiguous units. Rule-based extraction may fail on unfamiliar report formats and will require further testing.

The quality of the ML component will depend on the suitability, representativeness, and labeling quality of the selected dataset. A successful classification experiment will not establish clinical validity or demonstrate that the system can diagnose diabetes.

Future extensions may include support for additional laboratory measurements, encrypted storage, authenticated multi-user access, a validated retinal-image analysis experiment using a CNN, time-series forecasting research, and secure cloud deployment.

Any clinical prediction or forecasting functionality will require task-specific validation and appropriate clinical oversight before use in real healthcare decisions.

## 11. Conclusion

SugarSense AI proposes an integrated approach to personal health-data organization and diabetes-related ML experimentation. By combining secure local document processing, OCR, human-verified extraction, SQLite-based historical storage, statistical analysis, and a separately evaluated machine-learning pipeline, the project aims to demonstrate a practical end-to-end AI engineering workflow.

The addition of MLOps practices will extend the project beyond a standalone classifier by emphasizing reproducibility, evaluation, versioning, and maintainability. Its central design principle is that reliable analysis begins with correctly extracted, verified, and securely managed data.

**Project status:** Proposed design and implementation plan. Experimental results, model performance, and clinical validity remain to be established.

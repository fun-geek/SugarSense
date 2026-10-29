
# SugarSense AI 🩸

**A local-first glucose tracking and medical report management application built with Python and Streamlit.**

SugarSense AI helps users record glucose measurements, extract readable text from medical PDF reports, review detected measurements before saving them, and visualize their glucose history through a simple dashboard.

> **Project status:** Working prototype. Manual glucose tracking, SQLite storage, selectable-text PDF extraction, measurement review, and history visualization are implemented. OCR for scanned reports and advanced AI/ML features are planned.

## ✨ Features

- **Manual Glucose Tracking:** Record fasting, postprandial, and random glucose measurements.
- **HbA1c Tracking:** Store HbA1c results alongside other glucose measurements.
- **PDF Report Processing:** Extract selectable text from supported medical PDF reports.
- **Measurement Review:** Review and verify extracted measurement candidates before saving them.
- **Local Database:** Store measurements and report metadata using SQLite.
- **Glucose History:** View previous measurements and explore trends using charts.
- **Measurement Management:** Review and delete saved measurements.
- **Privacy-Focused Design:** Designed for local use, with private medical data excluded from Git tracking.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| SQLite | Local data storage |
| Pandas | Tabular data processing |
| PDF text extraction library | Extract selectable text from PDF reports |
| Pytest | Automated testing, where configured |

The exact dependencies are listed in [`requirements.txt`](requirements.txt).

## 📂 Project Structure

```text
SugarSense/
├── .github/
│   └── workflows/
├── artifacts/
├── config/
├── data/
├── database/
│   └── repository.py
├── report_processing/
├── services/
│   └── report_service.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── SugarSense_app_fixed.py
```

> If you rename `SugarSense_app_fixed.py` to `app.py`, update the filename in this structure accordingly.

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have installed:

- Python 3.10 or a compatible version required by your dependencies
- Git
- Visual Studio Code (recommended)

Check your Python installation:

```bash
python --version
```

### 2. Clone the repository

```bash
git clone https://github.com/fun-geek/SugarSense.git
cd SugarSense
```

### 3. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python executable directly instead.

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the application

If your main file is still named `SugarSense_app_fixed.py`:

```bash
streamlit run SugarSense_app_fixed.py
```

If you rename the main file to `app.py`:

```bash
streamlit run app.py
```

Streamlit will display a local URL in your terminal, usually:

```text
http://localhost:8501
```

Open that address in your browser.

## 📊 How to Use

1. Launch SugarSense AI.
2. Enter a glucose measurement manually or upload a supported PDF report.
3. Review any measurements extracted from the report.
4. Verify the values and dates before saving them.
5. Open the history section to review saved measurements and charts.
6. Delete an incorrect measurement when necessary.

**Important:** PDF extraction currently supports selectable text. Scanned PDFs and image-based reports require OCR, which is not yet implemented.

## 🔐 Privacy and Data Handling

SugarSense AI is designed with local-first data handling in mind.

- SQLite is used for local data storage.
- Private medical reports and database files should not be committed to Git.
- Environment files and credentials should remain outside version control.
- Do not upload real patient records, personal identifiers, or sensitive medical information to a public repository.

The `.gitignore` file excludes common database files and private report directories. Always inspect your Git changes before pushing them to GitHub.

## 🗺️ Roadmap

The following features are planned and should not be considered implemented until they are available in the application.

- [ ] OCR support for scanned PDFs and medical report images
- [ ] More robust medical report parsing and validation
- [ ] Improved measurement deduplication
- [ ] Exportable glucose history and summaries
- [ ] Additional analytics and trend insights
- [ ] Optional machine learning features, subject to appropriate validation
- [ ] Expanded automated testing and continuous integration

## 🧪 Testing

If the project dependencies and tests are configured, run:

```bash
python -m pytest
```

Use the test results to verify the current implementation before releasing changes.

## ⚠️ Medical Disclaimer

SugarSense AI is an educational and personal tracking project. It is **not a medical device** and does not diagnose diabetes, interpret results as a clinical diagnosis, or replace professional medical advice.

Extracted measurements may be incomplete or incorrect. Always verify values, units, and dates against the original laboratory report. Consult a qualified healthcare professional when interpreting glucose or HbA1c results or making treatment decisions.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and test them.
4. Submit a pull request describing the changes.

Please do not use real patient data in issues, pull requests, or test fixtures.

## 📄 License

No license has been specified yet. Until a license is added to the repository, do not assume that the code is available for unrestricted reuse or redistribution.

---

**Built with Python, Streamlit, and a focus on privacy-conscious health data management.**

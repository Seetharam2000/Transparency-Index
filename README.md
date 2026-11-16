# Transparency Index

A web app that detects dark patterns in fintech app terms & conditions and produces a single trust score (0–100).

## Features

- **Transparency Index Score**: Single score (0–100) rating the transparency of T&C text
- **Grade Classification**: Transparent (75+), Caution (50–74), Risky (<50)
- **Rule-Based Detection**: Regex-based checks for disclosure compliance
- **ML Pattern Detection**: Binary TF-IDF/logistic-regression classifier for general dark-pattern signals
- **Detailed Evidence**: Shows exactly which clauses triggered each check
- **Stripe-Inspired UI**: Clean, professional fintech aesthetic

## Project Structure

```
project-root/
├── requirements.txt
├── main.py                  # CLI test entry point
├── browser-extension/       # Chrome/Edge Manifest V3 extension
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   └── analyzer.js
├── data/
│   ├── raw/                 # sample T&C .txt files
│   │   ├── transparent_app.txt
│   │   ├── hidden_fees_app.txt
│   │   └── misleading_rate_app.txt
│   └── labeled/
│       ├── ec-darkpattern.tsv # e-commerce dark-pattern dataset (binary labels)
│       └── EC-DARKPATTERN-LICENSE.txt
└── src/
    ├── __init__.py
    ├── preprocess.py        # clean_text(), split_into_clauses()
    ├── rules.py              # rule-based disclosure/dark-pattern checks
    ├── model.py               # TF-IDF/logistic-regression binary classifier
    ├── score.py               # combines rules + model -> transparency_index()
    ├── samples.py             # predefined fintech terms for analysis
    ├── styles.py              # Streamlit dashboard styling
    └── app.py                  # Streamlit dashboard
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Streamlit Dashboard

```bash
streamlit run src/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Run CLI Tests

```bash
python main.py
```

This tests the core functionality without the UI.

### Install the browser extension (Chrome/Edge desktop)

1. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
2. Turn on **Developer mode**.
3. Choose **Load unpacked** and select the `browser-extension` folder.
4. Open a terms-and-conditions page, select the Transparency Index extension, and choose **Capture current page**.
5. Review or edit the captured text, then choose **Analyze terms**.

The extension analyzes text locally with the same weighted regex rules as the
web app. It does not send page text to a server and does not include the Python
machine-learning classifier. Browser extensions are generally not available in
iPhone browsers and support on Android varies by browser; use the mobile-friendly
Streamlit web app on phones.

### Classifier and Dataset

The app trains a lightweight TF-IDF/logistic-regression classifier on first use
and caches it with Streamlit for the running app process. The source dataset is the
[Yada et al. e-commerce dark-pattern dataset](https://github.com/yamanalab/ec-darkpattern)
([paper](https://arxiv.org/abs/2211.06543)), included at
`data/labeled/ec-darkpattern.tsv` under the upstream Apache 2.0 license. It has
2,356 text examples from 1,248 page IDs, with balanced binary labels
(`0` = not dark pattern, `1` = dark pattern). The dataset's original pattern
categories are retained in the TSV but are not predicted by this binary model.

The Model comparison tab reports Logistic Regression, Naive Bayes, and SVM
metrics on a 25% holdout split grouped by `page_id`, reducing leakage between
examples from the same source page. The production classifier is then fit on
the full dataset. Model signals are general e-commerce indicators; they may
not transfer to fintech terms and are shown as advisory, while the
rule-based fintech disclosure checks remain separate.

## How It Works

### 1. Preprocessing (`preprocess.py`)
- Strips HTML tags and URLs
- Normalizes whitespace
- Splits text into sentence-level clauses (5+ words)

### 2. Rule-Based Detection (`rules.py`)
Regex-based checks with weighted scores:
- Interest rate/APR clearly stated
- Total cost disclosed
- Fee amounts in numbers (not vague)
- Simple cancellation method
- Auto-renewal opt-out mechanism
- False urgency detection

### 3. AI Model (`model.py`)
TF-IDF features with a logistic-regression binary classifier trained on the
included e-commerce dataset. It predicts `none` or `dark_pattern`; it does not
predict fintech-specific pattern categories.

### 4. Scoring (`score.py`)
Combines rule score and model score (50/50 weight) into the final Transparency Index when the classifier runs. If it is not run, the index uses the rule score alone. Because the classifier is trained on e-commerce data, its contribution is advisory for fintech terms:
- Rule score: 0–100 based on disclosure checks
- Model score: 100 minus the mean predicted dark-pattern probability
- Final index: Average of both scores when the model runs; otherwise the rule score
- Detailed findings: Categorized rule-based risks and disclosure gaps with evidence and recommendations
- Grade thresholds: 75+ Transparent, 50–74 Caution, <50 Risky

The Streamlit dashboard adapts its spacing, typography, tabs, and controls to
narrow phone screens. On mobile, the dashboard columns stack vertically.

## Sample Data

The app includes 3 sample fintech app T&C files:
- **transparent_app.txt**: Clean, transparent terms
- **hidden_fees_app.txt**: Vague fees, complex cancellation
- **misleading_rate_app.txt**: Misleading rates, auto-renewal issues

## Requirements

- Python 3.8+
- Streamlit 1.39.0
- scikit-learn
- beautifulsoup4

## License

MIT License

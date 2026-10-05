# Transparency Index

A web app that detects dark patterns in fintech app terms & conditions and produces a single trust score (0–100).

## Features

- **Transparency Index Score**: Single score (0–100) rating the transparency of T&C text
- **Grade Classification**: Transparent (75+), Caution (50–74), Risky (<50)
- **Rule-Based Detection**: Regex-based checks for disclosure compliance
- **AI Pattern Detection**: DistilBERT classifier for dark pattern detection
- **Detailed Evidence**: Shows exactly which clauses triggered each check
- **Stripe-Inspired UI**: Clean, professional fintech aesthetic

## Project Structure

```
project-root/
├── requirements.txt
├── main.py                  # CLI test entry point
├── data/
│   ├── raw/                 # sample T&C .txt files
│   │   ├── transparent_app.txt
│   │   ├── hidden_fees_app.txt
│   │   └── misleading_rate_app.txt
│   └── labeled/             # darkpatterns.csv (text,label)
│       └── darkpatterns.csv
├── models/                  # saved fine-tuned model
└── src/
    ├── __init__.py
    ├── preprocess.py        # clean_text(), split_into_clauses()
    ├── rules.py              # rule-based disclosure/dark-pattern checks
    ├── model.py               # DistilBERT classifier: train(), predict()
    ├── score.py               # combines rules + model -> transparency_index()
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

### Train the AI Model (Optional)

To train the DistilBERT classifier on the labeled dataset:

```python
from src.model import DarkPatternClassifier

classifier = DarkPatternClassifier()
classifier.train('data/labeled/darkpatterns.csv', epochs=3, batch_size=8)
```

The trained model will be saved to `models/distilbert_darkpattern/`

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
DistilBERT fine-tuned on labeled dataset with classes:
- `none` - no dark pattern
- `fee_obfuscation` - hidden/unclear fees
- `false_urgency` - manipulative urgency
- `hard_cancellation` - difficult cancellation
- `misleading_rate` - unclear interest rates

### 4. Scoring (`score.py`)
Combines rule score and model score (50/50 weight) into final Transparency Index:
- Rule score: 0–100 based on disclosure checks
- Model score: 100 minus severity-weighted flagged clauses
- Final index: Average of both scores
- Grade thresholds: 75+ Transparent, 50–74 Caution, <50 Risky

## Sample Data

The app includes 3 sample fintech app T&C files:
- **transparent_app.txt**: Clean, transparent terms
- **hidden_fees_app.txt**: Vague fees, complex cancellation
- **misleading_rate_app.txt**: Misleading rates, auto-renewal issues

## Requirements

- Python 3.8+
- Streamlit 1.39.0
- Transformers 4.46.0
- PyTorch 2.5.0
- pandas, numpy, scikit-learn, beautifulsoup4

## License

MIT License

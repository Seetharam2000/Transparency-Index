import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap');

        :root {
            --page: #050505;
            --surface: #0B0B0B;
            --border: #2A2A2A;
            --text: #F4F4F4;
            --muted: #8A8A8A;
            --dim: #5C5C5C;
            --green: #7DDA8A;
            --amber: #E0B15B;
            --red: #E07A73;
        }

        html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp {
            font-family: 'Inter', sans-serif;
            color: var(--text);
            background: var(--page) !important;
        }

        [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer,
        [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }

        .block-container {
            max-width: 1440px;
            padding: 18px 40px 48px;
        }

        h1, h2, h3, h4 {
            color: var(--text);
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .top-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0 28px;
            letter-spacing: 0.22em;
            font-size: 12px;
            font-weight: 600;
        }

        .top-nav .brand { color: var(--text); }
        .top-nav .links { color: var(--muted); word-spacing: 18px; }

        .hero-kicker {
            color: var(--dim);
            font-size: 12px;
            letter-spacing: 0.28em;
            font-weight: 600;
            margin-bottom: 18px;
        }

        .hero-title {
            font-family: 'Oswald', sans-serif;
            font-size: clamp(52px, 7vw, 92px);
            line-height: 0.88;
            font-weight: 700;
            letter-spacing: -0.02em;
            text-transform: uppercase;
            margin: 0 0 24px;
            color: #fff;
        }

        .hero-copy, .hero-foot {
            color: var(--muted);
            font-size: 15px;
            max-width: 420px;
            line-height: 1.55;
        }

        .hero-foot {
            margin-top: 48px;
            letter-spacing: 0.22em;
            font-size: 11px;
        }

        .welcome-kicker {
            color: var(--dim);
            letter-spacing: 0.32em;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .welcome-title {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin: 0 0 6px;
        }

        .welcome-sub {
            color: var(--muted);
            font-size: 14px;
            margin-bottom: 28px;
        }

        .app-choice {
            padding: 18px 0 8px;
            border-bottom: 1px solid #1f1f1f;
            margin-bottom: 4px;
        }

        .app-choice .num {
            color: var(--dim);
            font-size: 11px;
            letter-spacing: 0.18em;
            margin-bottom: 6px;
        }

        .app-choice h3 {
            margin: 0;
            font-size: 18px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .app-choice p {
            color: var(--muted);
            font-size: 13px;
            margin: 6px 0 0;
        }

        .app-header {
            border-bottom: 1px solid var(--border);
            padding: 0 0 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            gap: 16px;
        }

        .app-header h1 {
            margin: 0;
            font-size: 22px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .app-header p {
            margin: 4px 0 0;
            color: var(--muted);
            font-size: 14px;
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: 8px;
            border-bottom: 1px solid var(--border);
        }

        [data-testid="stTabs"] button[role="tab"] {
            color: var(--muted);
            font-size: 13px;
            letter-spacing: 0.12em;
            padding: 8px 12px;
            background: transparent !important;
        }

        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #fff;
            border-bottom-color: #fff;
        }

        .section-title {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 0 0 16px;
        }

        .empty-state, .score-panel {
            background: transparent;
            border: 0;
            padding: 8px 0;
        }

        .empty-state {
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .empty-state strong { font-size: 15px; }
        .empty-state p { color: var(--muted); font-size: 14px; margin: 8px 0 0; }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label {
            color: var(--muted);
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        input, textarea, [data-baseweb="select"] > div {
            border-color: var(--border) !important;
            border-radius: 0 !important;
            color: var(--text) !important;
            background: transparent !important;
            font-size: 14px !important;
        }

        input::placeholder, textarea::placeholder {
            color: #6a6a6a !important;
            opacity: 1 !important;
        }

        textarea {
            font-family: Consolas, 'Courier New', monospace !important;
            line-height: 1.55 !important;
        }

        input:focus, textarea:focus {
            border-color: #fff !important;
            box-shadow: none !important;
        }

        [data-testid="stFileUploader"] section {
            border: 1px dashed var(--border);
            border-radius: 0;
            background: transparent;
        }

        .stButton > button {
            min-height: 40px;
            border: 0;
            border-bottom: 1px solid #2a2a2a;
            border-radius: 0;
            padding: 8px 4px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            background: transparent !important;
            color: var(--muted) !important;
        }

        .stButton > button:hover {
            color: #fff !important;
            border-bottom-color: #fff;
        }

        .stButton > button[kind="primary"] {
            color: #fff !important;
            border-bottom-color: #fff;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border-color: #1f1f1f !important;
            border-radius: 0 !important;
        }

        .score-row { display: flex; align-items: baseline; gap: 8px; }
        .score-number {
            font-family: 'Oswald', sans-serif;
            font-size: 64px;
            font-weight: 600;
            line-height: 1;
            letter-spacing: -0.04em;
            color: #fff;
        }
        .score-total { color: var(--muted); font-size: 16px; }
        .score-band { display: inline-block; margin-top: 8px; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; }
        .band-green { color: var(--green); }
        .band-amber { color: var(--amber); }
        .band-red { color: var(--red); }
        .score-track { height: 2px; margin: 16px 0 8px; overflow: hidden; background: #222; }
        .score-fill { height: 100%; }
        .score-meta { color: var(--muted); font-size: 13px; }

        .result-heading {
            margin: 24px 0 8px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .flagged-item { padding: 16px 0; border-bottom: 1px solid #1f1f1f; }
        .flagged-item:last-child { border-bottom: 0; }
        .flagged-category { font-size: 14px; font-weight: 600; }
        .flagged-passage { margin: 8px 0; font-size: 14px; line-height: 1.6; color: #d7d7d7; }
        .flagged-passage mark { background: #3a2e10; color: #f3e2a8; padding: 1px 2px; }
        .flagged-confidence { color: var(--muted); font-size: 13px; }

        [data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 0;
            background: transparent;
        }

        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--border);
        }

        .cred-hint {
            color: var(--dim);
            font-size: 12px;
            margin-top: 18px;
            letter-spacing: 0.04em;
        }

        @media (max-width: 900px) {
            .block-container { padding: 16px 16px 32px; }
            .hero-title { font-size: 48px; }
        }

        @media (max-width: 640px) {
            .block-container { padding: 12px 14px 28px; }
            .top-nav { padding-bottom: 20px; font-size: 10px; letter-spacing: 0.14em; }
            .top-nav .links { word-spacing: 6px; }
            .hero-title { font-size: clamp(42px, 13vw, 64px); }
            .hero-copy { font-size: 14px; }
            .hero-foot { margin-top: 20px; }
            .app-header { display: block; margin-bottom: 16px; }
            .app-header h1 { font-size: 19px; }
            .app-header p { font-size: 13px; line-height: 1.5; }
            .welcome-title { font-size: 24px; }
            .score-number { font-size: 54px; }
            .score-total { font-size: 14px; }
            .section-title { font-size: 13px; letter-spacing: 0.1em; }
            .result-heading { margin-top: 18px; }
            [data-testid="stTabs"] [role="tablist"] {
                overflow-x: auto;
                flex-wrap: nowrap;
            }
            [data-testid="stTabs"] button[role="tab"] {
                flex: 0 0 auto;
                white-space: nowrap;
                padding: 8px 10px;
                font-size: 12px;
            }
            input, textarea, [data-baseweb="select"] > div {
                font-size: 16px !important;
            }
            .stButton > button { min-height: 44px; letter-spacing: 0.08em; }
            [data-testid="stDataFrame"], [data-testid="stTable"] { max-width: 100%; }
        }

        @media (max-width: 380px) {
            .block-container { padding-right: 10px; padding-left: 10px; }
            .top-nav { letter-spacing: 0.08em; }
            .top-nav .links { word-spacing: 2px; }
            .hero-kicker { font-size: 10px; letter-spacing: 0.18em; }
            .score-number { font-size: 48px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

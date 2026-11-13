import streamlit as st
import sys
import hashlib
import html
import re
from pathlib import Path

st.set_page_config(
    page_title="Transparency Index",
    layout="wide",
    initial_sidebar_state="collapsed",
)

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.score import TransparencyScorer
from src.styles import load_css
from src.samples import SAMPLE_APPS, samples_by_name

DEMO_USERS = {
    "seetharam": "1234",
}


def init_state():
    defaults = {
        "authenticated": False,
        "screen": "login",
        "terms_text": "",
        "analysis_result": None,
        "app_name": "",
        "user_id": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_top_nav(show_logout=False):
    links = "HOME&nbsp;&nbsp;&nbsp;INDEX&nbsp;&nbsp;&nbsp;APPS"
    if show_logout:
        links += "&nbsp;&nbsp;&nbsp;ACCOUNT"
    st.markdown(
        f"""
        <div class="top-nav">
            <div class="brand">TRANSPARENCY</div>
            <div class="links">{links}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero-kicker">FINTECH · DARK PATTERN AUDIT</div>
        <div class="hero-title">TRANSPARENCY<br>INDEX<br>PLATFORM</div>
        <p class="hero-copy">
            Review predefined fintech apps, paste custom terms, and score
            disclosure risk in lending, BNPL, wallets, and insurance copy.
        </p>
        <div class="hero-foot">REVIEW · 2026</div>
        """,
        unsafe_allow_html=True,
    )


def try_login():
    username = st.session_state.get("login_user", "").strip().lower()
    password = st.session_state.get("login_pass", "")
    if DEMO_USERS.get(username) == password:
        st.session_state.authenticated = True
        st.session_state.user_id = username
        st.session_state.screen = "picker"
        st.session_state.login_error = ""
    else:
        st.session_state.login_error = "Invalid credentials. Use Seetharam / 1234."


def select_app(name, terms):
    st.session_state.app_name = name
    st.session_state.terms_text = terms
    st.session_state.selected_sample = name if name else "Select a sample"
    st.session_state.analysis_result = None
    st.session_state.screen = "dashboard"


def load_selected_sample(samples):
    selected = st.session_state.get("selected_sample")
    if selected in samples:
        st.session_state.terms_text = samples[selected]
        st.session_state.app_name = selected
        st.session_state.analysis_result = None


def highlight_phrase(text, category):
    patterns = {
        "fee_obfuscation": r"\b(?:fees?|charges?|costs?)\b.{0,55}\b(?:as applicable|may apply|variable|subject to|may be added)\b",
        "false_urgency": r"\b(?:limited time|act now|only \d+ (?:spots?|left|remaining)|expires? (?:soon|at midnight|today)|today only)\b",
        "hard_cancellation": r"\b(?:cancel|cancellation|termination)\b.{0,80}\b(?:written|certified mail|head office|headquarters|in writing)\b",
        "misleading_rate": r"\b(?:interest )?rates?\b.{0,65}\b(?:vary|variable|starting from|as low as|depending on|may change)\b",
    }
    escaped_text = html.escape(str(text))
    match = re.search(patterns.get(category, r"$^"), str(text), re.IGNORECASE)
    if not match:
        return escaped_text
    before = html.escape(str(text)[:match.start()])
    phrase = html.escape(str(text)[match.start():match.end()])
    after = html.escape(str(text)[match.end():])
    return f"{before}<mark>{phrase}</mark>{after}"


def render_results(result):
    score = result["transparency_index"]
    band_class = "band-green" if score >= 75 else "band-amber" if score >= 50 else "band-red"
    band_label = "Transparent" if score >= 75 else "Mixed" if score >= 50 else "Opaque"

    st.markdown('<div class="section-title">Transparency Index</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="score-panel">
            <div class="score-row">
                <span class="score-number">{score}</span>
                <span class="score-total">/ 100</span>
            </div>
            <div class="score-band {band_class}">{band_label}</div>
            <div class="score-track">
                <div class="score-fill {band_class}" style="width: {score}%; background: currentColor;"></div>
            </div>
            <div class="score-meta">{result['clauses_analyzed']} clauses analyzed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    findings = result["findings"]
    st.markdown('<div class="result-heading">Detected categories</div>', unsafe_allow_html=True)
    category_totals = {}
    for finding in findings:
        label = finding["category"]
        details = category_totals.setdefault(label, {"count": 0, "severity": "Low"})
        details["count"] += 1
        severity_order = {"Low": 0, "Medium": 1, "High": 2}
        if severity_order[finding["severity"]] > severity_order[details["severity"]]:
            details["severity"] = finding["severity"]

    if category_totals:
        categories = [
            {
                "Category": label,
                "Count": details["count"],
                "Highest severity": details["severity"],
            }
            for label, details in sorted(category_totals.items(), key=lambda item: item[0])
        ]
    else:
        categories = [{"Category": "No rule-based issues found", "Count": 0, "Highest severity": "—"}]
    st.dataframe(categories, use_container_width=True, hide_index=True)

    st.markdown('<div class="result-heading">Detailed findings</div>', unsafe_allow_html=True)
    if findings:
        for finding in findings:
            with st.container(border=True):
                st.markdown(
                    f"**{html.escape(finding['title'])}** · "
                    f"{html.escape(finding['severity'])} severity · "
                    f"{html.escape(finding['status'])}"
                )
                st.write(finding["explanation"])
                st.markdown(f"**Evidence:** {html.escape(finding['evidence'])}")
                st.markdown(f"**Recommended action:** {html.escape(finding['recommendation'])}")
    else:
        st.success("No issues were detected by the available rule-based checks.")

    with st.expander("How this score is calculated"):
        if result["model_used"]:
            st.write("The Transparency Index is the mean of the rule score and classifier score.")
            st.caption(
                f"Rule score: {result['rule_score']} / 100 · "
                f"Classifier score: {result['model_score']} / 100"
            )
        else:
            st.write(
                "This run uses the rule-based disclosure checks only. "
                "The trained AI classifier was not run, so the index is the rule score."
            )
            st.caption(f"Rule score: {result['rule_score']} / 100 · Classifier: not run")
        st.caption("Score bands: 75–100 Transparent, 50–74 Mixed, and below 50 Opaque.")

    st.markdown('<div class="result-heading">All disclosure checks</div>', unsafe_allow_html=True)
    st.dataframe(
        [
            {
                "Check": check["description"],
                "Status": check["status"],
                "Weight": check["weight"],
                "Evidence": check["evidence"],
            }
            for check in result["rule_results"]
        ],
        use_container_width=True,
        hide_index=True,
        height=360,
    )


@st.cache_data
def compare_models(dataset_path):
    import csv

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import LinearSVC
    from sklearn.tree import DecisionTreeClassifier

    with open(dataset_path, encoding="utf-8", newline="") as dataset_file:
        rows = list(csv.DictReader(dataset_file))
    texts = [row["text"] for row in rows]
    labels = [row["label"] for row in rows]
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
    train_features = vectorizer.fit_transform(train_texts)
    test_features = vectorizer.transform(test_texts)
    classifiers = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
        ("Naive Bayes", MultinomialNB()),
        ("Decision Tree", DecisionTreeClassifier(random_state=42)),
        ("SVM", LinearSVC(random_state=42)),
    ]

    metrics = []
    for name, classifier in classifiers:
        classifier.fit(train_features, train_labels)
        predictions = classifier.predict(test_features)
        metrics.append(
            {
                "Model": name,
                "Accuracy": accuracy_score(test_labels, predictions),
                "Precision": precision_score(test_labels, predictions, average="macro", zero_division=0),
                "Recall": recall_score(test_labels, predictions, average="macro", zero_division=0),
                "F1": f1_score(test_labels, predictions, average="macro", zero_division=0),
            }
        )
    return metrics, len(rows), len(test_texts)


def render_login():
    render_top_nav()
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        render_hero()
    with right:
        st.markdown('<div class="welcome-kicker">WELCOME</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-title">TRANSPARENCY</div>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-sub">Sign in to audit predefined apps</p>', unsafe_allow_html=True)
        st.text_input("Username", key="login_user", placeholder="Seetharam")
        st.text_input("Password", key="login_pass", type="password", placeholder="••••••••")
        if st.session_state.get("login_error"):
            st.error(st.session_state.login_error)
        st.button("Continue →", type="primary", use_container_width=True, on_click=try_login)
        st.markdown(
            '<p class="cred-hint">Demo access · Seetharam / 1234</p>',
            unsafe_allow_html=True,
        )


def render_picker():
    render_top_nav(show_logout=True)
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        render_hero()
    with right:
        st.markdown('<div class="welcome-kicker">WELCOME</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-title">TRANSPARENCY</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="welcome-sub">Select a predefined app to continue</p>',
            unsafe_allow_html=True,
        )

        for index, app in enumerate(SAMPLE_APPS, start=1):
            st.markdown(
                f"""
                <div class="app-choice">
                    <div class="num">{index:02d}</div>
                    <h3>{html.escape(app["name"])}</h3>
                    <p>{html.escape(app["category"])} · {html.escape(app["tagline"])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Continue →", key=f"pick_{index}", use_container_width=True):
                select_app(app["name"], app["terms"].strip())
                st.rerun()

        st.markdown(
            """
            <div class="app-choice">
                <div class="num">00</div>
                <h3>Custom terms</h3>
                <p>Paste or upload your own T&amp;C text</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Continue →", key="pick_custom", use_container_width=True):
            select_app("", "")
            st.rerun()

        logout_col, _ = st.columns([1, 2])
        with logout_col:
            if st.button("Log out", key="picker_logout"):
                st.session_state.authenticated = False
                st.session_state.screen = "login"
                st.rerun()


def render_dashboard():
    samples = samples_by_name()
    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.markdown(
            """
            <div class="app-header">
                <div>
                    <h1>Transparency Index</h1>
                    <p>Review fintech terms and conditions for disclosure risks and dark patterns.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_right:
        nav_a, nav_b = st.columns(2)
        with nav_a:
            if st.button("Apps", use_container_width=True):
                st.session_state.screen = "picker"
                st.rerun()
        with nav_b:
            if st.button("Log out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.screen = "login"
                st.rerun()

    analysis_tab, comparison_tab = st.tabs(["Analysis", "Model comparison"])
    with analysis_tab:
        input_column, result_column = st.columns([2, 3], gap="large")
        with input_column:
            with st.container(border=True):
                st.markdown('<div class="section-title">Terms and conditions</div>', unsafe_allow_html=True)
                st.text_input(
                    "App name",
                    placeholder="e.g., QuickCash Lending",
                    key="app_name",
                )
                st.selectbox(
                    "Predefined apps",
                    ["Select a sample"] + list(samples.keys()),
                    key="selected_sample",
                )
                uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"])
                if uploaded_file is not None:
                    file_contents = uploaded_file.getvalue()
                    file_digest = hashlib.sha256(file_contents).hexdigest()
                else:
                    file_contents = None
                    file_digest = None
                if uploaded_file is not None and st.session_state.get("uploaded_file_digest") != file_digest:
                    try:
                        st.session_state.terms_text = file_contents.decode("utf-8")
                    except UnicodeDecodeError:
                        st.error("The uploaded file must use UTF-8 text encoding.")
                    else:
                        st.session_state.uploaded_file_digest = file_digest
                        st.session_state.analysis_result = None

                st.text_area(
                    "Terms and conditions text",
                    placeholder="Paste the terms and conditions text here...",
                    height=240,
                    key="terms_text",
                )
                load_column, run_column = st.columns(2, gap="small")
                with load_column:
                    st.button(
                        "Load sample",
                        use_container_width=True,
                        on_click=load_selected_sample,
                        args=(samples,),
                    )
                with run_column:
                    analyze_clicked = st.button(
                        "Run analysis",
                        type="primary",
                        use_container_width=True,
                    )

        if analyze_clicked:
            text = st.session_state.terms_text.strip()
            if not text:
                st.warning("Enter terms, upload a text file, or load a sample before running analysis.")
            else:
                with st.spinner("Analyzing terms and conditions..."):
                    try:
                        scorer = TransparencyScorer()
                        st.session_state.analysis_result = scorer.calculate_index(text, use_model=False)
                    except Exception as error:
                        st.error(f"Analysis failed: {error}")

        with result_column:
            result = st.session_state.analysis_result
            if result is None:
                with st.container(border=True):
                    st.markdown(
                        """
                        <div class="empty-state">
                            <strong>Analysis results</strong>
                            <p>Run an analysis to view the score, detected categories, and supporting evidence.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                with st.container(border=True):
                    render_results(result)

    with comparison_tab:
        st.markdown('<div class="section-title">Classifier performance</div>', unsafe_allow_html=True)
        st.caption("Macro-averaged precision, recall, and F1 on a stratified 25% holdout split.")
        dataset_path = Path(__file__).parent.parent / "data" / "labeled" / "darkpatterns.csv"
        try:
            metrics, sample_count, test_count = compare_models(str(dataset_path))
        except Exception as error:
            st.error(f"Model comparison could not be calculated: {error}")
        else:
            st.table(
                [
                    {
                        "Model": row["Model"],
                        "Accuracy": f"{row['Accuracy']:.3f}",
                        "Precision": f"{row['Precision']:.3f}",
                        "Recall": f"{row['Recall']:.3f}",
                        "F1": f"{row['F1']:.3f}",
                    }
                    for row in metrics
                ]
            )
            st.caption(
                f"Evaluation uses {sample_count} labeled examples "
                f"({test_count} held out; random state 42)."
            )


def main():
    load_css()
    init_state()
    if not st.session_state.authenticated or st.session_state.screen == "login":
        render_login()
        return
    if st.session_state.screen == "picker":
        render_picker()
        return
    render_dashboard()


if __name__ == "__main__":
    main()

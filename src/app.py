import streamlit as st
import os
import sys
from pathlib import Path

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Transparency Index",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.score import TransparencyScorer
from src.preprocess import clean_text


# Custom CSS for Stripe-inspired design
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background-color: #F6F9FC;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #0A2540 0%, #635BFF 100%);
        padding: 40px 24px;
        border-radius: 16px;
        margin-bottom: 32px;
        color: white;
    }
    
    .hero h1 {
        font-size: 48px;
        font-weight: 800;
        margin: 0 0 12px 0;
        letter-spacing: -1px;
    }
    
    .hero p {
        font-size: 18px;
        font-weight: 400;
        margin: 0;
        opacity: 0.9;
    }
    
    /* Cards */
    .card {
        background: white;
        border: 1px solid #E3E8EE;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
    }
    
    .card h2 {
        color: #0A2540;
        font-size: 24px;
        font-weight: 700;
        margin: 0 0 16px 0;
    }
    
    .card h3 {
        color: #0A2540;
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 12px 0;
    }
    
    /* Score card */
    .score-card {
        text-align: center;
        padding: 32px;
    }
    
    .score-value {
        font-size: 72px;
        font-weight: 800;
        line-height: 1;
        margin: 16px 0;
    }
    
    .score-green { color: #0E9F6E; }
    .score-amber { color: #E5A100; }
    .score-red { color: #DF1B41; }
    
    .grade-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 8px 0;
    }
    
    .grade-transparent {
        background-color: #0E9F6E;
        color: white;
    }
    
    .grade-caution {
        background-color: #E5A100;
        color: white;
    }
    
    .grade-risky {
        background-color: #DF1B41;
        color: white;
    }
    
    /* Stat cards */
    .stat-card {
        background: white;
        border: 1px solid #E3E8EE;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #0A2540;
        margin: 8px 0;
    }
    
    .stat-label {
        font-size: 14px;
        color: #425466;
        font-weight: 500;
    }
    
    /* Status pills */
    .status-pass {
        background-color: #0E9F6E;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-fail {
        background-color: #DF1B41;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Pattern pills */
    .pattern-pill {
        background-color: #635BFF;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    /* Flagged pattern cards */
    .pattern-card {
        background: #F6F9FC;
        border: 1px solid #E3E8EE;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .pattern-text {
        color: #425466;
        font-size: 14px;
        font-style: italic;
        margin: 8px 0;
    }
    
    .confidence-score {
        font-size: 12px;
        color: #425466;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #635BFF;
        color: white;
        border: none;
        border-radius: 24px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #5048E6;
    }
    
    /* Text inputs and text areas */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: white;
        border: 1px solid #E3E8EE;
        border-radius: 8px;
        color: #0A2540;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #635BFF;
        box-shadow: 0 0 0 3px rgba(99, 91, 255, 0.1);
    }
    
    /* Selectbox - explicit colors for contrast */
    .stSelectbox > div > div > select {
        background-color: white;
        color: #0A2540;
        border: 1px solid #E3E8EE;
        border-radius: 8px;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: white;
        border: 2px dashed #E3E8EE;
        border-radius: 8px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #E3E8EE;
        border-radius: 8px;
        color: #0A2540;
        font-weight: 600;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Space between sections */
    .section-spacing {
        margin-bottom: 32px;
    }
    </style>
    """, unsafe_allow_html=True)


def load_sample_data():
    """Load sample T&C text data (built-in defaults)."""
    samples = {
        "Transparent Pay": """
TransparentPay Lending Services - Terms and Conditions

Welcome to TransparentPay. We believe in clear, honest lending. Here are our terms:

Interest Rate and APR
Our personal loans have a fixed interest rate of 12.5% APR. This rate is clearly stated on your loan agreement and will not change during the loan term.

Total Cost Disclosure
For a $5,000 loan over 24 months, the total repayment amount is $5,750. This includes all interest and fees with no hidden charges.

Fee Structure
- Origination fee: $50 (one-time)
- Late payment fee: $15 per missed payment
- No prepayment penalty

Cancellation Policy
You may cancel your loan application at any time before funds are disbursed. Simply send an email to cancel@transparentpay.com or call our customer service line. No written letters or physical mail required.

Auto-Renewal
This is a one-time loan, not a subscription. There is no auto-renewal. If you need another loan, you must apply again.

Early Repayment
You can pay off your loan early at any time with no additional fees. This will reduce your total interest cost.

Contact Information
Customer Service: 1-800-TRANSPARENT
Email: support@transparentpay.com
Address: 123 Clear Street, Honest City, HC 12345

We are committed to transparency in all our financial services.
        """,
        
        "QuickCash Lending": """
QuickCash Lending - Terms of Service

By using QuickCash, you agree to these terms. Please read carefully.

Interest Rates
Our competitive interest rates apply to your loan. Rates vary based on your credit profile.

Fees and Charges
Various fees may apply to your account including processing fees, service charges, and administrative costs as applicable. Additional fees may be charged for late payments, account maintenance, and other services.

Cancellation
To cancel your subscription, you must submit a written cancellation request to our head office via certified mail. Requests must be received at least 30 days before the next billing cycle. Email cancellations are not accepted.

Auto-Renewal
Your subscription will automatically renew each month. Your payment method will be charged automatically unless you cancel in accordance with our cancellation policy. No refunds will be provided for partial months.

Limited Time Offer
Act now! This special interest rate is available for a limited time only. Don't miss out on this exclusive offer expiring soon.

Additional Terms
We reserve the right to modify fees and charges at any time without prior notice. Continued use of the service constitutes acceptance of any changes.

All decisions are final and binding.
        """,
        
        "EasyCredit BNPL": """
EasyCredit BNPL - Buy Now Pay Later Terms

Get what you want today with EasyCredit! Split your payments into 4 easy installments.

Interest-Free Payment Plans
Enjoy 0% interest on all purchases! Just pay in 4 equal installments over 6 weeks.

Late Fees
If you miss a payment, a late fee of $10 or 5% of the installment amount (whichever is higher) will be charged. Additional fees may apply for extended delays.

Account Management
To manage your account or cancel your payment plan, you must submit a written request to our corporate headquarters. Allow 14 business days for processing. Phone and email requests are not accepted.

Special Offer Today Only
Limited time offer: Sign up now and get your first purchase fee-free! This exclusive offer expires at midnight.

Recurring Charges
After your initial purchase, your EasyCredit account may be enrolled in our premium membership program for $9.99/month, charged automatically to your payment method. You must cancel in writing to opt out.

Payment Processing
A small convenience fee of 2.5% may be added to all transactions. This fee is subject to change without notice.

Terms subject to modification at our discretion.
        """,
        
        "SimpleLoan Direct": """
SimpleLoan Direct - Loan Agreement

Loan Terms
You are borrowing $2,000 at an interest rate of 18% APR. The total amount payable is $2,360 over 12 months.

Fees Breakdown
- Application fee: $25
- Monthly service fee: $5
- Late payment fee: $20 per missed payment

Cancellation Rights
You may cancel this loan within 14 days of signing without penalty. To cancel, email us at cancel@simpleloan.com or call our support line.

Early Repayment
Pay off your loan early anytime with no extra charges. Early repayment saves you money on interest.

Payment Schedule
Monthly payments of $196.67 will be automatically deducted from your bank account on the 1st of each month.

No Hidden Fees
All fees are clearly stated above. We do not charge surprise fees or hidden costs.

Contact Us
Phone: 1-800-SIMPLE
Email: help@simpleloan.com
        """
    }
    
    return samples


def render_hero():
    """Render the hero section."""
    st.markdown("""
    <div class="hero">
        <h1>Transparency Index</h1>
        <p>Detect dark patterns in fintech app terms & conditions instantly</p>
    </div>
    """, unsafe_allow_html=True)


def render_input_section(samples):
    """Render the input section with all input options."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>Analyze Terms & Conditions</h2>', unsafe_allow_html=True)
    
    # App name (optional)
    app_name = st.text_input("App Name (optional)", placeholder="e.g., QuickCash Lending")
    
    # Sample app dropdown
    if samples:
        sample_options = ["-- Select a sample app --"] + list(samples.keys())
        selected_sample = st.selectbox("Or load a sample fintech app", sample_options)
    else:
        selected_sample = None
    
    # File upload
    uploaded_file = st.file_uploader("Or upload a .txt file", type=['txt'])
    
    # Text area for pasting
    text_input = st.text_area(
        "Or paste T&C text directly",
        placeholder="Paste the terms and conditions text here...",
        height=200
    )
    
    # Buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        analyze_button = st.button("Analyze", type="primary", use_container_width=True)
    
    with col2:
        load_sample_button = st.button("Load Sample", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return app_name, selected_sample, uploaded_file, text_input, analyze_button, load_sample_button


def render_results(result):
    """Render the results section."""
    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
    
    # Score card
    score_class = 'score-green' if result['transparency_index'] >= 75 else 'score-amber' if result['transparency_index'] >= 50 else 'score-red'
    grade_class = 'grade-transparent' if result['grade'] == 'Transparent' else 'grade-caution' if result['grade'] == 'Caution' else 'grade-risky'
    
    st.markdown(f"""
    <div class="card score-card">
        <h2>Transparency Index</h2>
        <div class="score-value {score_class}">{result['transparency_index']}</div>
        <div class="grade-badge {grade_class}">{result['grade']}</div>
        <p style="color: #425466; margin-top: 16px;">Based on {result['clauses_analyzed']} clauses analyzed</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stat cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Rule Score</div>
            <div class="stat-value">{result['rule_score']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">AI Model Score</div>
            <div class="stat-value">{result['model_score']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Clauses Analyzed</div>
            <div class="stat-value">{result['clauses_analyzed']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Disclosure checks card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>Disclosure Checks</h2>', unsafe_allow_html=True)
    
    for check in result['rule_results']:
        status_class = 'status-pass' if check['status'] == 'Pass' else 'status-fail'
        st.markdown(f"""
        <div style="margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #E3E8EE;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span class="{status_class}">{check['status']}</span>
                <span style="color: #0A2540; font-weight: 600;">{check['description']}</span>
            </div>
            <div style="color: #425466; font-size: 14px; margin-left: 0px;">
                <strong>Evidence:</strong> {check['evidence']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Flagged patterns card
    if result['flagged_patterns']:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2>Flagged Dark Patterns</h2>', unsafe_allow_html=True)
        
        for pattern in result['flagged_patterns']:
            st.markdown(f"""
            <div class="pattern-card">
                <span class="pattern-pill">{pattern['label'].replace('_', ' ').title()}</span>
                <div class="pattern-text">"{pattern['text']}"</div>
                <div class="confidence-score">Confidence: {pattern['confidence']:.1%} | Severity: {pattern['severity']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Collapsible all predictions table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander("See all predictions"):
        if result['flagged_patterns']:
            st.dataframe(
                result['flagged_patterns'],
                column_config={
                    'text': st.column_config.TextColumn('Clause Text', width='large'),
                    'label': st.column_config.TextColumn('Pattern Type'),
                    'confidence': st.column_config.ProgressColumn('Confidence', format='%.2f'),
                    'severity': st.column_config.NumberColumn('Severity')
                },
                hide_index=True
            )
        else:
            st.info("No dark patterns detected by AI model.")
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main Streamlit app."""
    load_css()
    
    # Render hero
    render_hero()
    
    # Load sample data
    samples = load_sample_data()
    
    # Initialize session state for text (auto-load first sample)
    if 'text_to_analyze' not in st.session_state:
        # Auto-load the first sample so user has data ready to analyze
        st.session_state.text_to_analyze = list(samples.values())[0]
    
    # Render input section
    app_name, selected_sample, uploaded_file, text_input, analyze_button, load_sample_button = render_input_section(samples)
    
    # Handle load sample button
    if load_sample_button and selected_sample and selected_sample != "-- Select a sample app --":
        st.session_state.text_to_analyze = samples[selected_sample]
        st.rerun()
    
    # Display loaded text in session state
    if st.session_state.text_to_analyze:
        st.text_area(
            "Loaded T&C text",
            value=st.session_state.text_to_analyze,
            height=200,
            key="loaded_text",
            label_visibility="collapsed"
        )
    
    # Handle file upload
    if uploaded_file is not None:
        st.session_state.text_to_analyze = uploaded_file.read().decode('utf-8')
        st.rerun()
    
    # Get text to analyze
    text_to_analyze = st.session_state.text_to_analyze or text_input
    
    # Handle analyze button
    if analyze_button and text_to_analyze:
        with st.spinner("Analyzing terms & conditions..."):
            try:
                scorer = TransparencyScorer()
                result = scorer.calculate_index(text_to_analyze, use_model=False)
                render_results(result)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
    elif analyze_button and not text_to_analyze:
        st.warning("Please enter T&C text, upload a file, or select a sample app first.")


if __name__ == "__main__":
    main()

"""
CLI test entry point for Transparency Index.
Tests the core functionality without the Streamlit UI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.score import TransparencyScorer
from src.preprocess import clean_text, split_into_clauses
from src.rules import RuleChecker


def test_preprocess():
    """Test text preprocessing."""
    print("=" * 60)
    print("Testing Preprocessing")
    print("=" * 60)
    
    sample_text = """
    <p>This is a test with <b>HTML</b> tags.</p>
    Visit http://example.com for more info.
    Multiple   spaces   should   be normalized.
    This is sentence one. This is sentence two! This is sentence three?
    """
    
    cleaned = clean_text(sample_text)
    print(f"Original: {sample_text[:50]}...")
    print(f"Cleaned: {cleaned[:50]}...")
    
    clauses = split_into_clauses(cleaned)
    print(f"\nClauses found: {len(clauses)}")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    
    print()


def test_rules():
    """Test rule-based detection."""
    print("=" * 60)
    print("Testing Rule-Based Detection")
    print("=" * 60)
    
    sample_text = """
    This loan has an interest rate of 15.5% APR. The total cost is $5000.
    Fees as applicable may apply to your account without notice.
    You can cancel by email anytime. Act now - limited time offer expires today!
    To cancel your subscription you must send written notice to our head office.
    """
    
    checker = RuleChecker()
    score, results = checker.check_text(sample_text)
    
    print(f"Rule Score: {score}/100")
    print(f"\nDetailed Results:")
    for r in results:
        print(f"  {r['rule']}: {r['status']} (weight: {r['weight']})")
        print(f"    Evidence: {r['evidence']}")
    
    print()


def test_scorer():
    """Test the full Transparency Scorer."""
    print("=" * 60)
    print("Testing Transparency Scorer")
    print("=" * 60)
    
    # Test with transparent app
    transparent_text = """
    TransparentPay Lending Services - Terms and Conditions
    
    Interest Rate and APR
    Our personal loans have a fixed interest rate of 12.5% APR. This rate is clearly stated on your loan agreement and will not change during the loan term.
    
    Total Cost Disclosure
    For a $5,000 loan over 24 months, the total repayment amount is $5,750. This includes all interest and fees with no hidden charges.
    
    Fee Structure
    - Origination fee: $50 (one-time)
    - Late payment fee: $15 per missed payment
    - No prepayment penalty
    
    Cancellation Policy
    You may cancel your loan application at any time before funds are disbursed. Simply send an email to cancel@transparentpay.com or call our customer service line.
    
    Auto-Renewal
    This is a one-time loan, not a subscription. There is no auto-renewal.
    """
    
    scorer = TransparencyScorer()
    result = scorer.calculate_index(transparent_text, use_model=False)
    
    print("Transparent App Results:")
    print(f"  Transparency Index: {result['transparency_index']}/100")
    print(f"  Grade: {result['grade']}")
    print(f"  Rule Score: {result['rule_score']}/100")
    print(f"  Model Score: {result['model_score']}/100")
    print(f"  Clauses Analyzed: {result['clauses_analyzed']}")
    
    print()
    
    # Test with problematic app
    problematic_text = """
    QuickCash Lending - Terms of Service
    
    Interest Rates
    Our competitive interest rates apply to your loan. Rates vary based on your credit profile.
    
    Fees and Charges
    Various fees may apply to your account including processing fees, service charges, and administrative costs as applicable.
    
    Cancellation
    To cancel your subscription, you must submit a written cancellation request to our head office via certified mail.
    
    Auto-Renewal
    Your subscription will automatically renew each month. Your payment method will be charged automatically unless you cancel.
    
    Limited Time Offer
    Act now! This special interest rate is available for a limited time only.
    """
    
    result = scorer.calculate_index(problematic_text, use_model=False)
    
    print("Problematic App Results:")
    print(f"  Transparency Index: {result['transparency_index']}/100")
    print(f"  Grade: {result['grade']}")
    print(f"  Rule Score: {result['rule_score']}/100")
    print(f"  Model Score: {result['model_score']}/100")
    print(f"  Clauses Analyzed: {result['clauses_analyzed']}")
    
    print()


def test_sample_files():
    """Test with actual sample files."""
    print("=" * 60)
    print("Testing with Sample Files")
    print("=" * 60)
    
    raw_dir = Path(__file__).parent / 'data' / 'raw'
    
    if not raw_dir.exists():
        print("Sample files not found. Run the app to generate them.")
        return
    
    scorer = TransparencyScorer()
    
    for file in raw_dir.glob('*.txt'):
        print(f"\nAnalyzing: {file.name}")
        text = file.read_text(encoding='utf-8')
        result = scorer.calculate_index(text, use_model=False)
        
        print(f"  Transparency Index: {result['transparency_index']}/100")
        print(f"  Grade: {result['grade']}")
        print(f"  Rule Score: {result['rule_score']}/100")
        print(f"  Clauses Analyzed: {result['clauses_analyzed']}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TRANSPARENCY INDEX - CLI TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_preprocess()
        test_rules()
        test_scorer()
        test_sample_files()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        print("\nTo run the Streamlit dashboard:")
        print("  streamlit run src/app.py")
        print("\nTo train the AI model:")
        print("  python -c \"from src.model import DarkPatternClassifier; c = DarkPatternClassifier(); c.train('data/labeled/darkpatterns.csv')\"")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

import re
from typing import Dict, List, Optional, Tuple
from .model import DarkPatternClassifier
from .rules import RuleChecker
from .preprocess import clean_text, split_into_clauses


class TransparencyScorer:
    """
    Combines rule-based checks and binary model predictions into a single
    Transparency Index score (0-100).
    """
    
    RULE_FINDING_DETAILS = {
        'vague_fee_language': {
            'category': 'Fee transparency',
            'title': 'Fees are described vaguely',
            'severity': 'High',
            'explanation': 'The terms mention fees without clearly defining when or how much may be charged.',
            'recommendation': 'List each possible fee, its amount or calculation method, and when it applies.',
        },
        'complex_cancellation': {
            'category': 'Cancellation barriers',
            'title': 'Cancellation may require a difficult process',
            'severity': 'High',
            'explanation': 'The terms appear to require written notice, mail, or a physical office to cancel.',
            'recommendation': 'Provide a clear cancellation option through the app, website, email, or phone.',
        },
        'hidden_auto_renewal': {
            'category': 'Renewal and billing',
            'title': 'Automatic renewal or billing terms need attention',
            'severity': 'High',
            'explanation': 'Automatic renewal or charges are mentioned alongside restrictive refund language.',
            'recommendation': 'Disclose renewal timing, upcoming charges, and a simple way to stop renewal.',
        },
        'false_urgency': {
            'category': 'Pressure and urgency',
            'title': 'Urgency language detected',
            'severity': 'Medium',
            'explanation': 'The terms use time pressure or scarcity language that may rush a decision.',
            'recommendation': 'Use verifiable offer dates and avoid unsupported urgency claims.',
        },
        'interest_rate_stated': {
            'category': 'Interest-rate disclosure',
            'title': 'A clear interest rate was not found',
            'severity': 'Medium',
            'explanation': 'The text discusses borrowing or interest, but a clearly stated percentage rate was not found.',
            'recommendation': 'State the applicable APR or interest rate and explain when variable rates can change.',
        },
        'total_cost_disclosed': {
            'category': 'Total-cost disclosure',
            'title': 'A total repayment or cost amount was not found',
            'severity': 'High',
            'explanation': 'The text describes a loan, payment plan, or subscription without a clear total cost.',
            'recommendation': 'Show the total amount payable, including interest and mandatory fees.',
        },
        'fee_amounts_numeric': {
            'category': 'Fee transparency',
            'title': 'A numeric fee amount was not found',
            'severity': 'Medium',
            'explanation': 'Fees or charges are mentioned, but a specific amount or calculation was not found.',
            'recommendation': 'Give an amount or a clear formula for each fee mentioned.',
        },
        'simple_cancellation': {
            'category': 'Cancellation options',
            'title': 'A simple cancellation option was not found',
            'severity': 'Medium',
            'explanation': 'Cancellation is mentioned, but no email, phone, online, or in-app method was found.',
            'recommendation': 'Explain a direct, accessible way to cancel and when the request takes effect.',
        },
        'auto_renewal_optout': {
            'category': 'Renewal and billing',
            'title': 'A renewal opt-out method was not found',
            'severity': 'High',
            'explanation': 'Renewal is mentioned, but the terms do not clearly describe how to stop it.',
            'recommendation': 'Explain how and when users can disable renewal before the next charge.',
        },
    }
    
    def __init__(self, model: Optional[DarkPatternClassifier] = None):
        self.rule_checker = RuleChecker()
        self.model = model
    
    def calculate_index(self, text: str, use_model: bool = True) -> Dict:
        """
        Calculate the Transparency Index for given T&C text.
        
        Returns dict with:
        - transparency_index: final score (0-100)
        - grade: 'Transparent' / 'Caution' / 'Risky'
        - rule_score: rule-based score (0-100)
        - model_score: binary classifier score (0-100), or None when not run
        - rule_results: detailed rule check results
        - flagged_patterns: list of classifier-detected dark-pattern signals
        - findings: categorized rule-based risks and disclosure gaps
        - clauses_analyzed: number of clauses processed
        """
        # Clean text
        cleaned_text = clean_text(text)
        
        # Split into clauses
        clauses = split_into_clauses(cleaned_text)
        clauses_analyzed = len(clauses)
        
        # Get rule-based score
        rule_score, rule_results = self.rule_checker.check_text(cleaned_text)
        
        # Get binary classifier score
        model_used = False
        if use_model and clauses:
            if self.model is None:
                self.model = DarkPatternClassifier()
            predictions = self.model.predict_batch(clauses)
            model_score, flagged_patterns = self._calculate_model_score(predictions)
            model_used = True
        else:
            model_score = None
            flagged_patterns = []
        
        # Use the rule score on its own when no trained classifier is available.
        transparency_index = (
            int((rule_score + model_score) / 2)
            if model_score is not None
            else int(rule_score)
        )
        
        # Determine grade
        grade = self._get_grade(transparency_index)
        
        return {
            'transparency_index': transparency_index,
            'grade': grade,
            'rule_score': int(rule_score),
            'model_score': int(model_score) if model_score is not None else None,
            'rule_results': rule_results,
            'flagged_patterns': flagged_patterns,
            'findings': self._build_findings(cleaned_text, rule_results, flagged_patterns),
            'model_used': model_used,
            'clauses_analyzed': clauses_analyzed
        }

    def _build_findings(
        self,
        text: str,
        rule_results: List[Dict],
        flagged_patterns: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """Create actionable risk findings from rule failures and disclosure gaps."""
        results_by_rule = {result['rule']: result for result in rule_results}
        lowered_text = text.lower()
        has_renewal = bool(re.search(
            r'\b(?:automatically\s+renew|auto[-\s]?renew(?:s|ed|ing)?|'
            r'subscription.{0,30}renew(?:s|ed|ing)?)\b|'
            r'\bauto[-\s]?renewal\b.{0,40}\b(?:every|each|month|year|charge|payment|unless)\b',
            lowered_text,
        ))
        has_fee_language = bool(re.search(r'\bfees?|charges?|penalt(?:y|ies)\b', lowered_text))
        has_cancellation_language = bool(re.search(r'\bcancel|cancellation|termination\b', lowered_text))
        has_credit_terms = bool(re.search(r'\binterest|apr|loan|borrow|advance\b', lowered_text))
        has_total_cost_context = bool(re.search(
            r'\bloan|borrow|advance|repayment|installment|subscription|membership|premium\b',
            lowered_text,
        ))

        applicable_gaps = {
            'interest_rate_stated': has_credit_terms,
            'total_cost_disclosed': has_total_cost_context,
            'fee_amounts_numeric': has_fee_language,
            'simple_cancellation': has_cancellation_language,
            'auto_renewal_optout': has_renewal,
        }
        findings = []
        for rule_name, details in self.RULE_FINDING_DETAILS.items():
            rule_result = results_by_rule.get(rule_name)
            if not rule_result:
                continue

            risk_detected = rule_name in {
                'vague_fee_language',
                'complex_cancellation',
                'hidden_auto_renewal',
                'false_urgency',
            } and rule_result['status'] == 'Fail'
            disclosure_gap = (
                rule_name in applicable_gaps
                and applicable_gaps[rule_name]
                and rule_result['status'] == 'Fail'
            )
            if not risk_detected and not disclosure_gap:
                continue

            # Avoid duplicating one issue as both a risk and a missing-disclosure finding.
            if rule_name == 'fee_amounts_numeric' and results_by_rule['vague_fee_language']['status'] == 'Fail':
                continue
            if rule_name == 'simple_cancellation' and results_by_rule['complex_cancellation']['status'] == 'Fail':
                continue

            findings.append({
                **details,
                'status': 'Risk detected' if risk_detected else 'Disclosure gap',
                'evidence': (
                    'No matching disclosure was found in the submitted text.'
                    if rule_result['evidence'] == 'No match found'
                    else rule_result['evidence']
                ),
            })

        for pattern in flagged_patterns or []:
            severity = "High" if pattern["confidence"] >= 0.8 else "Medium"
            findings.append(
                {
                    "category": "General dark-pattern signal (e-commerce-trained)",
                    "title": "Potential dark-pattern language",
                    "severity": severity,
                    "status": "ML signal — review in context",
                    "explanation": (
                        "The classifier detected language associated with dark patterns in an "
                        "e-commerce dataset. This signal is not fintech-specific and may not "
                        "indicate a financial disclosure violation."
                    ),
                    "evidence": pattern["text"],
                    "recommendation": (
                        "Review this passage in the context of the product and verify the claim "
                        "before treating it as a dark pattern."
                    ),
                    "confidence": pattern["confidence"],
                }
            )
        return findings
    
    def _calculate_model_score(self, predictions: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Calculate model score from predictions.
        Score is 100 minus the mean predicted dark-pattern probability.
        """
        if not predictions:
            return 100, []

        mean_dark_probability = sum(
            prediction["dark_pattern_probability"] for prediction in predictions
        ) / len(predictions)
        flagged = []
        for pred in predictions:
            if pred["label"] == "dark_pattern":
                flagged.append(pred)
        model_score = round(100 * (1 - mean_dark_probability))
        return model_score, flagged
    
    def _get_grade(self, score: int) -> str:
        """Determine grade based on score threshold."""
        if score >= 75:
            return 'Transparent'
        elif score >= 50:
            return 'Caution'
        else:
            return 'Risky'


if __name__ == "__main__":
    # Test the scorer
    scorer = TransparencyScorer()
    
    sample_text = """
    This loan has an interest rate of 15.5% APR. The total cost is $5000.
    Fees as applicable may apply to your account without notice.
    You can cancel by email anytime. Act now - limited time offer expires today!
    To cancel your subscription you must send written notice to our head office.
    """
    
    result = scorer.calculate_index(sample_text, use_model=False)
    print(f"Transparency Index: {result['transparency_index']}")
    print(f"Grade: {result['grade']}")
    print(f"Rule Score: {result['rule_score']}")
    print(f"Model Score: {result['model_score']}")
    print(f"Clauses Analyzed: {result['clauses_analyzed']}")

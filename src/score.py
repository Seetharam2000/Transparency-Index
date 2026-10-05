from typing import Dict, List, Tuple
from .rules import RuleChecker
from .preprocess import clean_text, split_into_clauses


class TransparencyScorer:
    """
    Combines rule-based checks and AI model predictions into a single
    Transparency Index score (0-100).
    """
    
    # Severity weights for different dark pattern types
    SEVERITY_WEIGHTS = {
        'none': 0,
        'fee_obfuscation': 15,
        'false_urgency': 10,
        'hard_cancellation': 20,
        'misleading_rate': 25
    }
    
    # Confidence threshold for counting a prediction
    CONFIDENCE_THRESHOLD = 0.6
    
    def __init__(self, model_path: str = None):
        self.rule_checker = RuleChecker()
        self.model_path = model_path
        self.model = None  # Lazy load only when needed
    
    def calculate_index(self, text: str, use_model: bool = True) -> Dict:
        """
        Calculate the Transparency Index for given T&C text.
        
        Returns dict with:
        - transparency_index: final score (0-100)
        - grade: 'Transparent' / 'Caution' / 'Risky'
        - rule_score: rule-based score (0-100)
        - model_score: AI model score (0-100)
        - rule_results: detailed rule check results
        - flagged_patterns: list of AI-detected dark patterns
        - clauses_analyzed: number of clauses processed
        """
        # Clean text
        cleaned_text = clean_text(text)
        
        # Split into clauses
        clauses = split_into_clauses(cleaned_text)
        clauses_analyzed = len(clauses)
        
        # Get rule-based score
        rule_score, rule_results = self.rule_checker.check_text(cleaned_text)
        
        # Get AI model score
        if use_model and clauses:
            try:
                # Lazy load model only when needed
                if self.model is None:
                    from .model import DarkPatternClassifier
                    self.model = DarkPatternClassifier(self.model_path)
                predictions = self.model.predict_batch(clauses)
                model_score, flagged_patterns = self._calculate_model_score(predictions)
            except Exception as e:
                print(f"Model prediction failed: {e}")
                model_score = 50  # neutral if model fails
                flagged_patterns = []
        else:
            model_score = 50  # neutral if no model
            flagged_patterns = []
        
        # Combine scores (50/50 weight)
        transparency_index = int((rule_score + model_score) / 2)
        
        # Determine grade
        grade = self._get_grade(transparency_index)
        
        return {
            'transparency_index': transparency_index,
            'grade': grade,
            'rule_score': int(rule_score),
            'model_score': int(model_score),
            'rule_results': rule_results,
            'flagged_patterns': flagged_patterns,
            'clauses_analyzed': clauses_analyzed
        }
    
    def _calculate_model_score(self, predictions: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Calculate model score from predictions.
        Base score is 100, subtract severity-weighted points for
        confidently-flagged dark patterns.
        """
        if not predictions:
            return 50, []
        
        total_penalty = 0
        flagged = []
        
        for pred in predictions:
            label = pred['label']
            confidence = pred['confidence']
            
            # Only count high-confidence predictions
            if label != 'none' and confidence >= self.CONFIDENCE_THRESHOLD:
                severity = self.SEVERITY_WEIGHTS.get(label, 10)
                # Penalty scales with confidence
                penalty = severity * confidence
                total_penalty += penalty
                
                flagged.append({
                    'text': pred['text'],
                    'label': label,
                    'confidence': confidence,
                    'severity': severity
                })
        
        # Start at 100, subtract penalties, clamp to 0-100
        model_score = max(0, min(100, 100 - total_penalty))
        
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

import re
from typing import List, Dict, Tuple


class RuleChecker:
    """
    Rule-based detection of dark patterns in T&C text.
    Each rule has a regex pattern, weight, and description.
    Returns a score (0-100) and detailed check results.
    """
    
    def __init__(self):
        self.rules = {
            'interest_rate_stated': {
                'pattern': r'(interest\s+rate|apr|annual\s+percentage\s+rate).{0,50}?\d+(\.\d+)?%',
                'weight': 20,
                'description': 'Interest rate/APR clearly stated with percentage',
                'type': 'pass'
            },
            'total_cost_disclosed': {
                'pattern': r'(total\s+cost|total\s+amount|total\s+repayment).{0,50}?\$?\d+(\.\d+)?',
                'weight': 15,
                'description': 'Total cost of loan/subscription disclosed',
                'type': 'pass'
            },
            'fee_amounts_numeric': {
                'pattern': r'(fee|charge|penalty).{0,30}\$?\d+(\.\d+)?',
                'weight': 15,
                'description': 'Fee amounts stated in numbers (not vague)',
                'type': 'pass'
            },
            'vague_fee_language': {
                'pattern': r'(fee|charge|penalty).{0,30}(as\s+applicable|may\s+apply|variable|subject\s+to)',
                'weight': -20,
                'description': 'Vague fee language (avoid)',
                'type': 'fail'
            },
            'simple_cancellation': {
                'pattern': r'(cancel|termination).{0,50}(email|phone|online|app|portal)',
                'weight': 15,
                'description': 'Cancellation method is simple (email/phone/online)',
                'type': 'pass'
            },
            'complex_cancellation': {
                'pattern': r'(cancel|termination).{0,50}(written|mail|head\s+office|physical\s+location)',
                'weight': -15,
                'description': 'Cancellation requires complex written process',
                'type': 'fail'
            },
            'auto_renewal_optout': {
                'pattern': r'(auto.{0,10}renew|renewal).{0,50}(opt.{0,10}out|cancel|unsubscribe|manage)',
                'weight': 10,
                'description': 'Auto-renewal has clear opt-out mechanism',
                'type': 'pass'
            },
            'hidden_auto_renewal': {
                'pattern': r'(auto.{0,10}renew|renewal).{0,100}(no\s+refund|non.{0,5}refundable|charged\s+automatically)',
                'weight': -15,
                'description': 'Auto-renewal with hidden charges/no refund',
                'type': 'fail'
            },
            'false_urgency': {
                'pattern': r'(limited\s+time|act\s+now|only\s+\d+\s+(left|remaining)|expires\s+soon|today\s+only)',
                'weight': -10,
                'description': 'False urgency language',
                'type': 'fail'
            },
            'clear_termination_fee': {
                'pattern': r'(termination|cancellation)\s+fee.{0,30}\$?\d+(\.\d+)?',
                'weight': 10,
                'description': 'Termination fee clearly stated',
                'type': 'pass'
            }
        }
    
    def check_text(self, text: str) -> Tuple[float, List[Dict]]:
        """
        Run all rules on the text and return:
        - rule_score (0-100)
        - list of check results with evidence
        """
        results = []
        total_score = 0
        max_score = sum(abs(r['weight']) for r in self.rules.values() if r['weight'] > 0)
        
        for rule_name, rule in self.rules.items():
            matches = re.findall(rule['pattern'], text, re.IGNORECASE)
            passed = len(matches) > 0
            
            if rule['type'] == 'pass':
                if passed:
                    total_score += rule['weight']
                    status = 'Pass'
                    evidence = self._extract_evidence(text, rule['pattern'])
                else:
                    status = 'Fail'
                    evidence = 'No match found'
            else:  # fail rule
                if passed:
                    total_score += rule['weight']  # negative weight
                    status = 'Fail'
                    evidence = self._extract_evidence(text, rule['pattern'])
                else:
                    status = 'Pass'
                    evidence = 'No dark pattern detected'
            
            results.append({
                'rule': rule_name,
                'description': rule['description'],
                'status': status,
                'weight': rule['weight'],
                'evidence': evidence
            })
        
        # Normalize to 0-100 scale
        if max_score > 0:
            normalized_score = max(0, min(100, (total_score / max_score) * 100))
        else:
            normalized_score = 50  # neutral if no positive rules
        
        return normalized_score, results
    
    def _extract_evidence(self, text: str, pattern: str) -> str:
        """Extract the matching text as evidence."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            return '...' + text[start:end] + '...'
        return 'No match'


if __name__ == "__main__":
    # Test the rule checker
    checker = RuleChecker()
    sample_text = """
    This loan has an interest rate of 15.5% APR. The total cost is $5000.
    Fees as applicable may apply. You can cancel by email anytime.
    Act now - limited time offer!
    """
    score, results = checker.check_text(sample_text)
    print(f"Rule Score: {score}")
    for r in results:
        print(f"{r['rule']}: {r['status']} - {r['evidence']}")

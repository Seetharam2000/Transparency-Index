import unittest

from src.rules import RuleChecker


class CancellationRuleTests(unittest.TestCase):
    def test_email_cancellation_is_not_classified_as_mail_in_cancellation(self):
        _, results = RuleChecker().check_text("You may cancel your subscription by email.")
        checks = {result["rule"]: result for result in results}

        self.assertEqual(checks["simple_cancellation"]["status"], "Pass")
        self.assertEqual(checks["complex_cancellation"]["status"], "Pass")

    def test_written_mail_cancellation_is_classified_as_complex(self):
        _, results = RuleChecker().check_text(
            "To cancel, send a written request by mail to our head office."
        )
        checks = {result["rule"]: result for result in results}

        self.assertEqual(checks["complex_cancellation"]["status"], "Fail")


if __name__ == "__main__":
    unittest.main()

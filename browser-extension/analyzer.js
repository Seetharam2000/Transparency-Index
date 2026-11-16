(function (root) {
  const RULES = [
    {
      id: "interest_rate_stated",
      description: "Interest rate/APR stated with a percentage",
      weight: 20,
      type: "pass",
      pattern: /(?:(interest\s+rate|apr|annual\s+percentage\s+rate).{0,50}?\d+(\.\d+)?%|\d+(\.\d+)?%\s*(?:interest|apr))/i
    },
    {
      id: "total_cost_disclosed",
      description: "Total loan/subscription cost disclosed",
      weight: 15,
      type: "pass",
      pattern: /(total\s+cost|total\s+amount|total\s+repayment).{0,50}?\$?\d+(\.\d+)?/i
    },
    {
      id: "fee_amounts_numeric",
      description: "Fee amounts stated numerically",
      weight: 15,
      type: "pass",
      pattern: /(fee|charge|penalty).{0,30}\$?\d+(\.\d+)?/i
    },
    {
      id: "vague_fee_language",
      description: "Vague fee language",
      weight: -20,
      type: "fail",
      pattern: /(fee|charge|penalty).{0,30}(as\s+applicable|may\s+apply|variable|subject\s+to)/i
    },
    {
      id: "simple_cancellation",
      description: "Cancellation method is simple (email/phone/online)",
      weight: 15,
      type: "pass",
      pattern: /(cancel|termination).{0,50}(email|phone|online|app|portal)/i
    },
    {
      id: "complex_cancellation",
      description: "Cancellation requires a complex written process",
      weight: -15,
      type: "fail",
      pattern: /(cancel|termination).{0,50}(written|\bmail\b|head\s+office|physical\s+location)/i
    },
    {
      id: "auto_renewal_optout",
      description: "Auto-renewal has a clear opt-out mechanism",
      weight: 10,
      type: "pass",
      pattern: /(auto.{0,10}renew|renewal).{0,50}(opt.{0,10}out|cancel|unsubscribe|manage)/i
    },
    {
      id: "hidden_auto_renewal",
      description: "Auto-renewal with hidden charges/no refund",
      weight: -15,
      type: "fail",
      pattern: /(auto.{0,10}renew|renewal).{0,100}(no\s+refund|non.{0,5}refundable|charged\s+automatically)/i
    },
    {
      id: "false_urgency",
      description: "False urgency language",
      weight: -10,
      type: "fail",
      pattern: /(limited\s+time|act\s+now|only\s+\d+\s+(left|remaining)|expires\s+soon|today\s+only)/i
    },
    {
      id: "clear_termination_fee",
      description: "Termination fee clearly stated",
      weight: 10,
      type: "pass",
      pattern: /(termination|cancellation)\s+fee.{0,30}\$?\d+(\.\d+)?/i
    }
  ];

  const FINDING_DETAILS = {
    vague_fee_language: {
      title: "Fees are described vaguely",
      recommendation: "List each possible fee, its amount or calculation method, and when it applies."
    },
    complex_cancellation: {
      title: "Cancellation may require a difficult process",
      recommendation: "Provide a clear cancellation option through the app, website, email, or phone."
    },
    hidden_auto_renewal: {
      title: "Automatic renewal or billing terms need attention",
      recommendation: "Disclose renewal timing, upcoming charges, and a simple way to stop renewal."
    },
    false_urgency: {
      title: "Urgency language detected",
      recommendation: "Use verifiable offer dates and avoid unsupported urgency claims."
    },
    interest_rate_stated: {
      title: "A clear interest rate was not found",
      recommendation: "State the applicable APR or interest rate and explain when variable rates can change."
    },
    total_cost_disclosed: {
      title: "A total repayment or cost amount was not found",
      recommendation: "Show the total amount payable, including interest and mandatory fees."
    },
    fee_amounts_numeric: {
      title: "A numeric fee amount was not found",
      recommendation: "Give an amount or a clear formula for each fee mentioned."
    },
    simple_cancellation: {
      title: "A simple cancellation option was not found",
      recommendation: "Explain a direct, accessible way to cancel and when the request takes effect."
    },
    auto_renewal_optout: {
      title: "A renewal opt-out method was not found",
      recommendation: "Explain how and when users can disable renewal before the next charge."
    }
  };

  function evidenceFor(text, pattern) {
    const match = pattern.exec(text);
    if (!match) return "No match found";
    return `...${text.slice(Math.max(0, match.index - 20), Math.min(text.length, match.index + match[0].length + 20))}...`;
  }

  function analyze(text) {
    const cleaned = String(text || "").replace(/\s+/g, " ").trim();
    const checks = RULES.map((rule) => {
      const matched = rule.pattern.test(cleaned);
      const failed = rule.type === "pass" ? !matched : matched;
      return {
        id: rule.id,
        description: rule.description,
        status: failed ? "Fail" : "Pass",
        weight: rule.weight,
        evidence: matched
          ? evidenceFor(cleaned, rule.pattern)
          : rule.type === "pass" ? "No match found" : "No dark pattern detected"
      };
    });

    const total = checks.reduce((sum, check) => {
      if (check.status === "Pass" && check.weight > 0) return sum + check.weight;
      if (check.status === "Fail" && check.weight < 0) return sum + check.weight;
      return sum;
    }, 0);
    const maxScore = RULES.reduce((sum, rule) => sum + (rule.weight > 0 ? rule.weight : 0), 0);
    const score = Math.floor(Math.max(0, Math.min(100, total / maxScore * 100)));
    const lowered = cleaned.toLowerCase();
    const hasRenewal = /\b(?:automatically\s+renew|auto[-\s]?renew(?:s|ed|ing)?|subscription.{0,30}renew(?:s|ed|ing)?)\b|\bauto[-\s]?renewal\b.{0,40}\b(?:every|each|month|year|charge|payment|unless)\b/i.test(lowered);
    const applicability = {
      interest_rate_stated: /\b(?:interest|apr|loan|borrow|advance)\b/i.test(lowered),
      total_cost_disclosed: /\b(?:loan|borrow|advance|repayment|installment|subscription|membership|premium)\b/i.test(lowered),
      fee_amounts_numeric: /\b(?:fees?|charges?|penalt(?:y|ies))\b/i.test(lowered),
      simple_cancellation: /\b(?:cancel|cancellation|termination)\b/i.test(lowered),
      auto_renewal_optout: hasRenewal
    };
    const byId = Object.fromEntries(checks.map((check) => [check.id, check]));
    const riskRules = new Set([
      "vague_fee_language",
      "complex_cancellation",
      "hidden_auto_renewal",
      "false_urgency"
    ]);
    const findings = [];
    for (const [id, details] of Object.entries(FINDING_DETAILS)) {
      const check = byId[id];
      const risk = riskRules.has(id) && check.status === "Fail";
      const gap = Boolean(applicability[id]) && check.status === "Fail";
      if (!risk && !gap) continue;
      if (id === "fee_amounts_numeric" && byId.vague_fee_language.status === "Fail") continue;
      if (id === "simple_cancellation" && byId.complex_cancellation.status === "Fail") continue;
      findings.push({
        title: details.title,
        status: risk ? "Risk detected" : "Disclosure gap",
        evidence: check.evidence === "No match found"
          ? "No matching disclosure was found in the submitted text."
          : check.evidence,
        recommendation: details.recommendation
      });
    }
    return {
      score,
      grade: score >= 75 ? "Transparent" : score >= 50 ? "Caution" : "Risky",
      checks,
      findings,
      clausesAnalyzed: cleaned ? cleaned.split(/[.!?;:]\s+/).filter((part) => part.trim().split(/\s+/).length >= 5).length : 0
    };
  }

  const api = { analyze };
  root.TransparencyAnalyzer = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(globalThis);

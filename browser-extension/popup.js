const captureButton = document.getElementById("capture");
const analyzeButton = document.getElementById("analyze");
const terms = document.getElementById("terms");
const message = document.getElementById("message");
const resultSection = document.getElementById("result");

function showMessage(text) {
  message.textContent = text;
  message.hidden = !text;
}

function captureCurrentPage() {
  showMessage("");
  captureButton.disabled = true;
  captureButton.textContent = "Capturing...";
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const tab = tabs[0];
    if (!tab || typeof tab.id !== "number") {
      showMessage("No active browser tab was found.");
      captureButton.disabled = false;
      captureButton.textContent = "Capture current page";
      return;
    }
    try {
      const [injected] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body ? document.body.innerText : ""
      });
      terms.value = injected.result || "";
      resultSection.hidden = true;
      if (!terms.value.trim()) showMessage("No readable page text was found. Paste terms into the box instead.");
    } catch (error) {
      showMessage("This page cannot be read by the extension. Open a regular webpage or paste the terms.");
    } finally {
      captureButton.disabled = false;
      captureButton.textContent = "Capture current page";
    }
  });
}

function appendListItem(list, title, status, evidence, recommendation) {
  const item = document.createElement("li");
  item.append(document.createTextNode(title));
  if (status) {
    const statusLine = document.createElement("span");
    statusLine.className = `status${status === "Fail" || status === "Risk detected" || status === "Disclosure gap" ? " fail" : ""}`;
    statusLine.textContent = status;
    item.append(statusLine);
  }
  if (evidence) {
    const evidenceLine = document.createElement("span");
    evidenceLine.className = "evidence";
    evidenceLine.textContent = evidence;
    item.append(evidenceLine);
  }
  if (recommendation) {
    const recommendationLine = document.createElement("span");
    recommendationLine.className = "status";
    recommendationLine.textContent = `Recommended action: ${recommendation}`;
    item.append(recommendationLine);
  }
  list.append(item);
}

function renderResult(result) {
  const score = document.getElementById("score");
  const grade = document.getElementById("grade");
  const meter = document.getElementById("meter-fill");
  const band = result.score >= 75 ? "green" : result.score >= 50 ? "amber" : "red";
  score.textContent = result.score;
  grade.textContent = result.grade;
  grade.className = `grade ${band}`;
  meter.style.width = `${result.score}%`;
  meter.className = band;
  document.getElementById("clause-count").textContent = `${result.clausesAnalyzed} clauses analyzed`;

  const findings = document.getElementById("findings");
  findings.replaceChildren();
  if (result.findings.length) {
    result.findings.forEach((finding) => {
      appendListItem(findings, finding.title, finding.status, finding.evidence, finding.recommendation);
    });
  } else {
    appendListItem(findings, "No issues found by the available rule checks.", "", "", "");
  }

  const checks = document.getElementById("checks");
  checks.replaceChildren();
  result.checks.forEach((check) => {
    appendListItem(checks, check.description, check.status, check.evidence, "");
  });
  resultSection.hidden = false;
}

captureButton.addEventListener("click", captureCurrentPage);
analyzeButton.addEventListener("click", () => {
  showMessage("");
  const text = terms.value.trim();
  if (!text) {
    showMessage("Capture a page, paste terms, or enter some text before analyzing.");
    resultSection.hidden = true;
    return;
  }
  renderResult(TransparencyAnalyzer.analyze(text));
});

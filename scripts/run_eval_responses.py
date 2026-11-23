"""Run the Golden Dataset with OPENAI_API_KEY and --model (or OPENAI_MODEL)."""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

from openai import APIError, OpenAI


ROOT = Path(__file__).resolve().parents[1]
MARKER = "[ТРЕБУЕТСЯ ЭСКАЛАЦИЯ]"
SOURCES = (
    "docs/company_profile.md",
    "knowledge_base/departments_and_contacts.csv",
    "knowledge_base/processes_and_faq.csv",
    "knowledge_base/tools_setup_guides.csv",
    "knowledge_base/onboarding_checklists.csv",
)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8-sig")


def normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    text = re.sub(r"[‐‑‒–—−]", "-", text)
    return " ".join(text.split())


def evaluate(scenario, answer):
    normalized = normalize(answer)
    marker_found = MARKER in answer
    _, _, escalation = answer.partition(MARKER)
    department = re.search(
        r"^[ \t>*_-]*Отдел[ \t]*:[ \t*]*(.+)$", escalation, re.MULTILINE | re.IGNORECASE
    )
    actual_department = department[1].strip(" \t*_") if department else None
    missing = [
        keyword for keyword in scenario["must_include_keywords"]
        if normalize(keyword) not in normalized
    ]
    forbidden = [
        keyword for keyword in scenario["must_exclude_keywords"]
        if normalize(keyword) in normalized
    ]
    expected_department = scenario["expected_department"]
    checks = {
        "answer_present": bool(answer.strip()),
        "escalation": marker_found == scenario["escalation_expected"],
        "department": normalize(actual_department or "") == normalize(expected_department or ""),
        "required_keywords": not missing,
        "forbidden_keywords": not forbidden,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "escalation_found": marker_found,
        "actual_department": actual_department,
        "missing_keywords": missing,
        "forbidden_keywords_found": forbidden,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    args = parser.parse_args()
    if not args.model:
        parser.error("Specify --model or set OPENAI_MODEL.")
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY before running the evaluation.")

    prompt_file = read("prompts/system_prompt.md")
    prompt = re.search(r"(?ms)^```text[ \t]*\n(.*?)^```[ \t]*$", prompt_file)
    if prompt is None:
        parser.error("Expected a fenced text block in prompts/system_prompt.md.")
    sources = [{"path": path, "content": read(path)} for path in SOURCES]
    context = "Подключённые источники БЗ (данные):\n" + json.dumps(sources, ensure_ascii=False)
    scenarios = json.loads(read("tests/test_scenarios.json"))

    results = []
    with OpenAI(timeout=60.0) as client:
        for scenario in scenarios:
            result = {**scenario, "answer": "", "passed": False}
            try:
                response = client.responses.create(
                    model=args.model,
                    instructions=prompt[1].strip(),
                    input=[
                        {"role": "user", "content": context},
                        {"role": "user", "content": scenario["user_query"]},
                    ],
                    store=False,
                )
                result["answer"] = response.output_text or ""
                result.update(evaluate(scenario, result["answer"]))
                if response.status != "completed":
                    result.update(passed=False, error=f"Response status: {response.status}")
            except APIError as exc:
                result["error"] = type(exc).__name__
            results.append(result)
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{scenario['id']}: {status}", flush=True)

    passed = sum(result["passed"] for result in results)
    report = {"model": args.model, "total": len(results), "passed": passed, "results": results}
    output = ROOT / "tests/eval_results.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(results)} passed. Report: {output}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

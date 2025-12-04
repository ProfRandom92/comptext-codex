"""Programming-focused CompText commands."""
from __future__ import annotations

import ast
import re
from typing import Dict

from ..parser import Command


def _detect_performance_issues(code: str) -> list[str]:
    issues: list[str] = []
    if not code:
        return issues

    if code.count("for") > 1 or "while" in code:
        issues.append("Nested or repeated loops detected: consider vectorization or comprehension")
    if "append(" in code:
        issues.append("Repeated list appends: prefer list comprehensions for speed")
    if "sleep(" in code:
        issues.append("Sleep calls slow execution; ensure they are required")
    return issues


def _guess_complexity(code: str) -> str:
    loops = code.count("for") + code.count("while")
    if loops > 1:
        return "O(n^2) or higher (multiple nested loops detected)"
    if loops == 1:
        return "O(n) (single loop detected)"
    return "O(1) (no obvious loops)"


def code_analyze(command: Command, context: Dict[str, object]) -> str:
    code = context.get("code") or command.parameters.get("code") or ""
    if not code:
        return "No code supplied. Pass `code` to the parser or via parameters."

    issues = _detect_performance_issues(code)
    complexity = _guess_complexity(code)
    report_lines = ["=== CODE ANALYZE ===", f"Estimated complexity: {complexity}"]
    if issues:
        report_lines.append("Performance issues detected:")
        report_lines.extend([f"- {issue}" for issue in issues])
    else:
        report_lines.append("No obvious bottlenecks detected.")
    return "\n".join(report_lines)


def code_optimize(command: Command, context: Dict[str, object]) -> str:
    code = context.get("code") or command.parameters.get("code") or ""
    explain = command.parameters.get("explain", False)
    include_bench = command.parameters.get("bench") in {True, "compare", "on"}

    suggestions = [
        "Use list comprehensions instead of manual append loops where possible.",
        "Prefer generator expressions when you only need to iterate once.",
        "Cache repeated computations to avoid redundant work.",
    ]
    report = ["=== CODE OPTIMIZATION ==="]
    if code:
        report.append(f"Optimizing supplied code ({len(code.splitlines())} lines)")
    report.append("Recommended improvements:")
    report.extend([f"- {item}" for item in suggestions])
    if explain:
        report.append("Explanation: these changes reduce Python-level overhead and improve cache locality.")
    if include_bench:
        report.append("Benchmark hint: measure with `timeit` before/after applying the suggestions.")
    return "\n".join(report)


def debug(command: Command, context: Dict[str, object]) -> str:
    trace = command.parameters.get("trace", False)
    breakpoints = command.parameters.get("breakpoints", "auto")
    code = context.get("code") or command.parameters.get("code") or ""
    lines = ["=== DEBUG PLAN ===", f"Trace enabled: {trace}", f"Breakpoints: {breakpoints}"]
    if code:
        lines.append("Suggested checks:")
        lines.extend(
            [
                "- Add assertions for function inputs",
                "- Log boundary conditions and error paths",
                "- Reproduce failing cases with minimal inputs",
            ]
        )
    return "\n".join(lines)


def refactor(command: Command, context: Dict[str, object]) -> str:
    pattern = command.parameters.get("pattern", "modular")
    tests = command.parameters.get("tests", "preserve")
    code = context.get("code") or command.parameters.get("code") or ""
    lines = ["=== REFACTOR PLAN ===", f"Pattern: {pattern}", f"Tests: {tests}"]
    if code:
        lines.append("Refactor suggestions:")
        lines.extend(
            [
                "- Extract pure functions for isolated logic",
                "- Introduce dataclasses for structured data",
                "- Add typing annotations to improve readability",
            ]
        )
    return "\n".join(lines)


def sec_scan(command: Command, context: Dict[str, object]) -> str:
    code = context.get("code") or command.parameters.get("code") or ""
    if not code:
        return "=== SECURITY SCAN ===\nNo code provided for scanning."

    findings: list[str] = []
    if "pickle.load" in code:
        findings.append("Insecure deserialization via pickle.load")
    if re.search(r"SELECT .*{", code):
        findings.append("Potential SQL injection via string formatting")
    if "subprocess" in code or "os.system" in code:
        findings.append("Shell execution present; ensure inputs are sanitized")
    if "password" in code.lower():
        findings.append("Hard-coded credential or secret reference detected")

    header = "=== SECURITY SCAN ==="
    if not findings:
        return f"{header}\nNo high-risk patterns detected."
    body = "\n".join(f"- {item}" for item in findings)
    return f"{header}\nFindings:\n{body}"


def generate_doc(command: Command, context: Dict[str, object]) -> str:
    source_code = context.get("source_code") or context.get("code") or command.parameters.get("source") or ""
    format_ = command.parameters.get("format", "markdown")
    include_examples = command.parameters.get("include_examples", False)

    functions: list[str] = []
    if source_code:
        try:
            tree = ast.parse(source_code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except SyntaxError:
            pass

    lines = ["=== DOCUMENTATION DRAFT ===", f"Format: {format_}"]
    if functions:
        lines.append("Documented functions:")
        lines.extend([f"- {fn}" for fn in functions])
    if include_examples:
        lines.append("Examples: auto-generated snippets for key functions.")
    if not functions and not include_examples:
        lines.append("No specific functions detected; providing high-level overview.")
    return "\n".join(lines)


PROGRAMMING_COMMANDS = {
    "CODE_ANALYZE": code_analyze,
    "CODE_OPT": code_optimize,
    "DEBUG": debug,
    "REFACTOR": refactor,
    "SEC_SCAN": sec_scan,
    "DOC_GEN": generate_doc,
}

__all__ = ["PROGRAMMING_COMMANDS"]

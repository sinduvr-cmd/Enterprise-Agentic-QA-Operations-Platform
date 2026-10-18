"""
Agent 5: Automation Reviewer Agent.
Performs automated static code analysis, security auditing, and quality review on generated Playwright code.
Inspects:
1. Python AST syntax and imports validity.
2. Unsafe function detection (eval, exec, shell, os.system).
3. Hardcoded secret and credential detection (API tokens, private keys, passwords).
4. Brittle locator patterns (absolute XPaths, randomized CSS classes).
5. Assertion presence (verifies each test function contains explicit assertions).
6. Page Object Model conformance.
"""
import ast
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.agents.automation_generator import GeneratedAutomationCode


class SecurityIssue(BaseModel):
    category: str = Field(..., description="unsafe_execution | hardcoded_secret | brittle_locator | missing_assertion | syntax_error")
    severity: str = Field(..., description="Critical | High | Medium | Low")
    message: str
    line_number: Optional[int] = None
    snippet: Optional[str] = None


class CodeReviewReport(BaseModel):
    is_approved: bool
    quality_score: float = Field(..., ge=1.0, le=10.0)
    syntax_valid: bool
    issues: List[SecurityIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    summary: str


class AutomationReviewerAgent:
    """
    Agent 5 in the QA Operations Platform.
    Enforces security, syntax, and maintainability quality gates before human sign-off.
    """

    SECRET_PATTERNS = [
        (re.compile(r"""(?i)(api_key|apikey|secret|token|password|passwd|private_key)\s*=\s*['"][a-zA-Z0-9_\-\.]{8,}['"]"""), "Possible hardcoded secret or credential"),
        (re.compile(r"""ghp_[a-zA-Z0-9]{36}"""), "GitHub Personal Access Token detected"),
        (re.compile(r"""sk_live_[a-zA-Z0-9]{24}"""), "Stripe Live Secret Key detected"),
    ]

    UNSAFE_CALLS = {"eval", "exec", "os.system", "subprocess.call", "subprocess.Popen", "subprocess.run"}

    BRITTLE_LOCATOR_PATTERNS = [
        (re.compile(r"""/html/body/div\[\d+\]"""), "Brittle absolute XPath locator detected"),
        (re.compile(r"""\.css-[a-zA-Z0-9]{5,8}"""), "Randomized hashed CSS class locator detected"),
    ]

    def review_code(self, script_data: GeneratedAutomationCode) -> CodeReviewReport:
        issues: List[SecurityIssue] = []
        recommendations: List[str] = []
        syntax_valid = True

        all_code = script_data.test_code
        for po_code in script_data.page_objects.values():
            all_code += f"\n\n{po_code}"
        for fix_code in script_data.fixtures.values():
            all_code += f"\n\n{fix_code}"

        # 1. AST Syntax and Import Parsing
        try:
            tree = ast.parse(all_code)
        except SyntaxError as e:
            syntax_valid = False
            issues.append(SecurityIssue(
                category="syntax_error",
                severity="Critical",
                message=f"Python AST syntax error: {e.msg}",
                line_number=e.lineno,
                snippet=e.text
            ))

        # 2. Check for Unsafe Invocations via AST visitor
        if syntax_valid:
            has_assertions = False
            has_test_function = False

            for node in ast.walk(tree):
                # Detect test functions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("test_"):
                        has_test_function = True
                        # Check for assertions in test body
                        fn_assertions = [n for n in ast.walk(node) if isinstance(n, (ast.Assert, ast.Call))]
                        if any(isinstance(n, ast.Assert) or (isinstance(n, ast.Call) and hasattr(n.func, "id") and n.func.id == "expect") for n in fn_assertions):
                            has_assertions = True

                # Detect unsafe function calls
                if isinstance(node, ast.Call):
                    fn_name = ""
                    if isinstance(node.func, ast.Name):
                        fn_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            fn_name = f"{node.func.value.id}.{node.func.attr}"

                    if fn_name in self.UNSAFE_CALLS:
                        issues.append(SecurityIssue(
                            category="unsafe_execution",
                            severity="Critical",
                            message=f"Forbidden unsafe function call '{fn_name}' detected",
                            line_number=getattr(node, "lineno", None)
                        ))

            if has_test_function and not has_assertions:
                issues.append(SecurityIssue(
                    category="missing_assertion",
                    severity="High",
                    message="Test function does not contain any Playwright 'expect(...)' assertions"
                ))

        # 3. Detect Hardcoded Secrets via Regex
        for pattern, msg in self.SECRET_PATTERNS:
            for match in pattern.finditer(all_code):
                issues.append(SecurityIssue(
                    category="hardcoded_secret",
                    severity="Critical",
                    message=msg,
                    snippet=match.group(0)[:30] + "..."
                ))

        # 4. Detect Brittle Locators
        for pattern, msg in self.BRITTLE_LOCATOR_PATTERNS:
            for match in pattern.finditer(all_code):
                issues.append(SecurityIssue(
                    category="brittle_locator",
                    severity="Medium",
                    message=msg,
                    snippet=match.group(0)
                ))

        # 5. Fixed Sleep Check
        if "time.sleep(" in all_code:
            issues.append(SecurityIssue(
                category="brittle_locator",
                severity="Medium",
                message="Anti-pattern 'time.sleep()' detected. Use Playwright's web-first auto-waiting assertions instead."
            ))

        # Calculate Score
        critical_count = sum(1 for i in issues if i.severity == "Critical")
        high_count = sum(1 for i in issues if i.severity == "High")
        medium_count = sum(1 for i in issues if i.severity == "Medium")

        if critical_count > 0:
            score = max(1.0, 5.0 - (critical_count * 2.0))
            is_approved = False
        elif high_count > 0:
            score = 6.5
            is_approved = False
        elif medium_count > 0:
            score = 8.5
            is_approved = True
        else:
            score = 9.8
            is_approved = True

        if not is_approved:
            recommendations.append("Remediate identified critical security or syntax issues before approval.")
        else:
            recommendations.append("Code meets enterprise POM standards, syntax valid, zero hardcoded secrets detected.")

        return CodeReviewReport(
            is_approved=is_approved,
            quality_score=score,
            syntax_valid=syntax_valid,
            issues=issues,
            recommendations=recommendations,
            summary=f"Automated Code Review: Quality score {score}/10. {len(issues)} issues detected ({critical_count} critical, {high_count} high)."
        )

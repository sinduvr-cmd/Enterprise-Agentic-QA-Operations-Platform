"""
LangGraph Cyclic Agent Workflow Orchestrator for Enterprise Agentic QA.
Implements the stateful loop:
Requirement Input -> Requirement Analyzer -> Test Case Generator -> Critic Evaluator
  -> If score < 8 and attempts < 5: Loop back to Test Case Generator with Critic Feedback
  -> Else: Transition to Human Test Case Approval gate.

Persists state to PostgreSQL / SQLite checkpoints. Supports pause, resume, retry, and cancellation.
"""
from datetime import datetime, timezone
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from backend.app.models.workflow import AgentRun, WorkflowCheckpoint
from backend.app.models.test_case import TestCase, QualityEvaluation
from backend.app.models.requirement import Requirement
from backend.app.models.approval import ApprovalRequest
from backend.app.models.automation_script import AutomationScript
from backend.app.agents.requirement_analyzer import RequirementAnalyzerAgent
from backend.app.agents.test_case_generator import TestCaseGeneratorAgent
from backend.app.agents.critic_evaluator import CriticEvaluatorAgent
from backend.app.agents.automation_generator import AutomationGeneratorAgent
from backend.app.agents.automation_reviewer import AutomationReviewerAgent
from backend.app.agents.schemas import (
    RequirementAnalysisResult,
    TestCaseGenerationResult,
    CriticEvaluationResult,
)

logger = logging.getLogger(__name__)


class AgenticQAGraph:
    """
    Stateful Cyclic Workflow Orchestrator.
    Manages transitions, checkpoints, agent invocation, and human approval gates.
    """

    def __init__(self, db: Session):
        self.db = db
        self.analyzer = RequirementAnalyzerAgent()
        self.generator = TestCaseGeneratorAgent()
        self.critic = CriticEvaluatorAgent()
        self.automation_gen = AutomationGeneratorAgent()
        self.automation_rev = AutomationReviewerAgent()

    def create_workflow(
        self,
        project_id: str,
        workflow_id: str,
        run_name: str,
        requirement_title: str,
        requirement_description: str,
        acceptance_criteria: Optional[List[str]] = None,
        requirement_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initializes workflow state and creates initial database checkpoint.
        """
        now = datetime.now(timezone.utc)
        state: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "requirement_id": requirement_id,
            "run_name": run_name,
            "requirement_title": requirement_title,
            "requirement_description": requirement_description,
            "acceptance_criteria": acceptance_criteria or [],
            "current_stage": "initialized",
            "status": "running",
            "requirement_analysis": None,
            "generated_test_suite": None,
            "critic_evaluation": None,
            "critic_attempts": 0,
            "critic_feedback": None,
            "quality_score": 0.0,
            "reasoning_log": [],
            "error_message": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        self._save_checkpoint(workflow_id, "initialized", state)
        return state

    def run_step(self, workflow_id: str) -> Dict[str, Any]:
        """
        Executes one node in the state graph and persists checkpoint.
        """
        state = self.load_state(workflow_id)
        if not state or state.get("status") in ("completed", "failed", "paused", "awaiting_approval"):
            return state or {}

        current_stage = state.get("current_stage", "initialized")

        if current_stage in ("initialized", "requirement_analysis"):
            state = self._node_requirement_analysis(state)
        elif current_stage == "test_case_generation":
            state = self._node_test_case_generation(state)
        elif current_stage == "critic_evaluation":
            state = self._node_critic_evaluation(state)
        elif current_stage == "human_test_approval":
            state["status"] = "awaiting_approval"
            self._sync_agent_run(state)

        return state

    def run_until_approval_or_complete(self, workflow_id: str) -> Dict[str, Any]:
        """
        Runs the cyclic Generator-Critic workflow autonomously until it reaches
        human approval, max attempts, completion, or an error.
        """
        max_loop_guard = 15  # Prevents infinite loops under any circumstances
        steps = 0

        state = self.load_state(workflow_id)
        while steps < max_loop_guard and state.get("status") == "running":
            state = self.run_step(workflow_id)
            steps += 1
            if state.get("status") in ("awaiting_approval", "completed", "failed", "paused"):
                break

        return state

    # ==========================================
    # Node Implementations
    # ==========================================

    def _node_requirement_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state["workflow_id"]
        now = datetime.now(timezone.utc)
        logger.info(f"[{workflow_id}] Executing Node: Requirement Analyzer")

        analysis = self.analyzer.analyze(
            title=state["requirement_title"],
            description=state["requirement_description"],
            acceptance_criteria=state.get("acceptance_criteria")
        )

        state["requirement_analysis"] = analysis.model_dump()
        state["current_stage"] = "test_case_generation"
        state["reasoning_log"].append({
            "timestamp": now.strftime("%H:%M:%S"),
            "agent": "Requirement Analyzer",
            "stage": "requirement_analysis",
            "thought": f"Analyzed requirement '{state['requirement_title']}'. Sufficiency: {analysis.sufficiency_score}/10.",
            "action": "Extracted positive, negative, boundary, and edge scenarios.",
            "result": f"Extracted {len(analysis.positive_scenarios) + len(analysis.negative_scenarios) + len(analysis.boundary_scenarios) + len(analysis.edge_scenarios)} testable scenarios."
        })

        self._save_checkpoint(workflow_id, "requirement_analysis", state)
        self._sync_agent_run(state)
        return state

    def _node_test_case_generation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state["workflow_id"]
        attempt = state.get("critic_attempts", 0) + 1
        now = datetime.now(timezone.utc)
        logger.info(f"[{workflow_id}] Executing Node: Test Case Generator (Attempt #{attempt})")

        analysis_obj = RequirementAnalysisResult.model_validate(state["requirement_analysis"])
        req_ref = state.get("requirement_id") or "REQ-001"

        test_suite = self.generator.generate(
            analysis=analysis_obj,
            requirement_uid=req_ref,
            critic_feedback=state.get("critic_feedback"),
            attempt_number=attempt
        )

        state["generated_test_suite"] = test_suite.model_dump()
        state["current_stage"] = "critic_evaluation"
        thought_msg = f"Synthesizing test cases for attempt #{attempt}."
        if state.get("critic_feedback"):
            thought_msg += " Incorporating Critic Agent feedback."

        state["reasoning_log"].append({
            "timestamp": now.strftime("%H:%M:%S"),
            "agent": "Test Case Generator",
            "stage": "test_case_generation",
            "thought": thought_msg,
            "action": f"Generated {test_suite.total_generated} structured test cases.",
            "result": f"{test_suite.positive_count} pos, {test_suite.negative_count} neg, {test_suite.boundary_count} boundary."
        })

        self._save_checkpoint(workflow_id, "test_case_generation", state)
        self._sync_agent_run(state)
        return state

    def _node_critic_evaluation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state["workflow_id"]
        now = datetime.now(timezone.utc)
        state["critic_attempts"] = state.get("critic_attempts", 0) + 1
        attempt = state["critic_attempts"]
        logger.info(f"[{workflow_id}] Executing Node: Critic Evaluator (Attempt #{attempt})")

        analysis_obj = RequirementAnalysisResult.model_validate(state["requirement_analysis"])
        test_suite_obj = TestCaseGenerationResult.model_validate(state["generated_test_suite"])

        evaluation = self.critic.evaluate(
            analysis=analysis_obj,
            test_suite=test_suite_obj,
            attempt_number=attempt
        )

        state["critic_evaluation"] = evaluation.model_dump()
        state["quality_score"] = evaluation.overall_quality_score
        state["critic_feedback"] = evaluation.actionable_feedback

        # Decision / Conditional Branching logic
        if evaluation.overall_quality_score >= self.critic.PASS_THRESHOLD:
            # Score >= 8.0: Passed Critic Gate -> proceed to Human Approval!
            state["current_stage"] = "human_test_approval"
            state["status"] = "awaiting_approval"
            thought = f"Attempt #{attempt}: Quality score {evaluation.overall_quality_score}/10 EXCEEDS threshold (8.0). Approved for human review."
            action = "Quality gate passed"
            result = "Transitioned to Human Test Approval"

            # Persist test cases & approval request into database
            self._persist_test_cases_and_approval(state)
        elif attempt < self.critic.MAX_ATTEMPTS:
            # Score < 8.0 and attempts < 5: Loop back to Test Case Generator!
            state["current_stage"] = "test_case_generation"
            state["status"] = "running"
            thought = f"Attempt #{attempt}: Quality score {evaluation.overall_quality_score}/10 is below 8.0. Returning feedback to Generator."
            action = "Critic regeneration loop triggered"
            result = f"Attempt {attempt}/{self.critic.MAX_ATTEMPTS} completed. Looping back."
        else:
            # Attempts exhausted -> flag for human review
            state["current_stage"] = "human_test_approval"
            state["status"] = "awaiting_approval"
            thought = f"Attempt #{attempt}: Max regeneration attempts (5) exhausted. Flagging for human review."
            action = "Regeneration limit reached"
            result = "Flagged for human review"
            self._persist_test_cases_and_approval(state)

        state["reasoning_log"].append({
            "timestamp": now.strftime("%H:%M:%S"),
            "agent": "Critic Evaluator",
            "stage": "critic_evaluation",
            "thought": thought,
            "action": action,
            "result": result
        })

        self._save_checkpoint(workflow_id, "critic_evaluation", state)
        self._sync_agent_run(state)
        return state

    # ==========================================
    # Persistence & Checkpoint Helpers
    # ==========================================

    def load_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        checkpoint = self.db.query(WorkflowCheckpoint).filter(
            WorkflowCheckpoint.workflow_id == workflow_id
        ).order_by(WorkflowCheckpoint.created_at.desc()).first()

        if checkpoint:
            return checkpoint.state_payload

        # Fallback to AgentRun table if no checkpoint record yet
        run = self.db.query(AgentRun).filter(AgentRun.workflow_id == workflow_id).first()
        if run:
            return {
                "workflow_id": run.workflow_id,
                "project_id": run.project_id,
                "requirement_id": run.requirement_id,
                "run_name": run.run_name,
                "current_stage": run.current_stage,
                "status": run.status,
                "quality_score": run.quality_score,
                "critic_attempts": run.critic_attempts,
                "reasoning_log": run.agent_reasoning_log or []
            }
        return None

    def _save_checkpoint(self, workflow_id: str, step_name: str, state: Dict[str, Any]):
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        checkpoint = WorkflowCheckpoint(
            workflow_id=workflow_id,
            step_name=step_name,
            state_payload=state
        )
        self.db.add(checkpoint)
        self.db.commit()

    def _sync_agent_run(self, state: Dict[str, Any]):
        run = self.db.query(AgentRun).filter(AgentRun.workflow_id == state["workflow_id"]).first()
        if run:
            run.current_stage = state.get("current_stage", run.current_stage)
            run.status = state.get("status", run.status)
            run.quality_score = state.get("quality_score", run.quality_score)
            run.critic_attempts = state.get("critic_attempts", run.critic_attempts)
            run.agent_reasoning_log = state.get("reasoning_log", [])
            run.error_message = state.get("error_message")
            if run.status in ("completed", "failed"):
                run.completed_at = datetime.now(timezone.utc)
            self.db.commit()

    def _persist_test_cases_and_approval(self, state: Dict[str, Any]):
        """
        Inserts generated test cases into the database and creates an ApprovalRequest.
        """
        suite_data = state.get("generated_test_suite", {})
        cases = suite_data.get("test_cases", [])
        project_id = state["project_id"]
        workflow_id = state["workflow_id"]
        eval_data = state.get("critic_evaluation", {})

        first_tc_id = None
        for item in cases:
            existing = self.db.query(TestCase).filter(
                TestCase.project_id == project_id,
                TestCase.test_uid == item["test_uid"]
            ).first()

            if not existing:
                tc = TestCase(
                    project_id=project_id,
                    requirement_id=state.get("requirement_id"),
                    test_uid=item["test_uid"],
                    title=item["title"],
                    objective=item["objective"],
                    preconditions=item.get("preconditions", []),
                    steps=[s if isinstance(s, dict) else s.model_dump() for s in item.get("steps", [])],
                    test_data=item.get("test_data", {}),
                    expected_results=item["expected_results"],
                    priority=item.get("priority", "Medium"),
                    category=item.get("category", "Functional"),
                    quality_score=state.get("quality_score", 0.0),
                    critic_feedback=state.get("critic_feedback"),
                    status="pending_approval"
                )
                self.db.add(tc)
                self.db.flush()
                if not first_tc_id:
                    first_tc_id = tc.id

                # Save individual evaluation record
                self.db.add(QualityEvaluation(
                    test_case_id=tc.id,
                    score=state.get("quality_score", 0.0),
                    completeness=eval_data.get("dimension_scores", {}).get("completeness", 9.0),
                    accuracy=eval_data.get("dimension_scores", {}).get("accuracy", 9.0),
                    coverage=eval_data.get("dimension_scores", {}).get("coverage", 9.0),
                    clarity=eval_data.get("dimension_scores", {}).get("clarity", 9.0),
                    traceability=eval_data.get("dimension_scores", {}).get("traceability", 9.0),
                    duplication_risk=eval_data.get("dimension_scores", {}).get("duplication_risk", 0.5),
                    feedback=state.get("critic_feedback", "Quality score >= 8.0 approved"),
                    attempt_number=state.get("critic_attempts", 1)
                ))

        # Create Approval Request for Human Signoff
        existing_approval = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.workflow_id == workflow_id,
            ApprovalRequest.status == "pending"
        ).first()

        if not existing_approval:
            app_req = ApprovalRequest(
                project_id=project_id,
                workflow_id=workflow_id,
                artifact_type="test_cases",
                artifact_id=first_tc_id,
                artifact_summary=f"{len(cases)} Test Cases for '{state['requirement_title']}' (Score: {state.get('quality_score'):.1f}/10)",
                quality_score=state.get("quality_score", 0.0),
                status="pending"
            )
            self.db.add(app_req)

        self.db.commit()

    def execute_automation_pipeline(
        self,
        workflow_id: str,
        test_case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Phase 3:
        Converts approved test case(s) into Python Playwright Page Object Model scripts (Agent 4),
        reviews them using AST syntax and security audit (Agent 5),
        and gates them behind Human Code Approval.
        """
        state = self.load_state(workflow_id)
        if not state:
            raise ValueError(f"Workflow '{workflow_id}' not found.")

        now = datetime.now(timezone.utc)
        project_id = state["project_id"]

        # Fetch target approved test case
        query = self.db.query(TestCase).filter(TestCase.project_id == project_id)
        if test_case_id:
            query = query.filter(TestCase.id == test_case_id)
        target_tc = query.order_by(TestCase.created_at.desc()).first()

        if not target_tc:
            raise ValueError(f"No test cases available to automate for project '{project_id}'.")

        logger.info(f"[{workflow_id}] Executing Node: Automation Generator for test case {target_tc.test_uid}")

        # 1. Agent 4: Generate Playwright POM Code
        script_data = self.automation_gen.generate_script(
            test_case=target_tc,
            project_name=state.get("run_name", "Enterprise Service")
        )

        state["reasoning_log"].append({
            "timestamp": now.strftime("%H:%M:%S"),
            "agent": "Automation Generator",
            "stage": "automation_generation",
            "thought": f"Synthesized Playwright Page Object Model suite '{script_data.file_path}' for {target_tc.test_uid}.",
            "action": "Generated POM classes, fixtures, and web-first expect assertions.",
            "result": f"Class {script_data.class_name} generated successfully."
        })

        # 2. Agent 5: Code Review & Security Audit
        logger.info(f"[{workflow_id}] Executing Node: Automation Reviewer for {script_data.file_path}")
        review_report = self.automation_rev.review_code(script_data)

        state["reasoning_log"].append({
            "timestamp": now.strftime("%H:%M:%S"),
            "agent": "Automation Reviewer",
            "stage": "automation_review",
            "thought": f"Static AST & Security audit score: {review_report.quality_score}/10. Syntax valid: {review_report.syntax_valid}.",
            "action": "Audited for unsafe calls, hardcoded credentials, and brittle selectors.",
            "result": review_report.summary
        })

        # Persist AutomationScript in DB
        existing_script = self.db.query(AutomationScript).filter(
            AutomationScript.test_case_id == target_tc.id
        ).first()

        if not existing_script:
            script_record = AutomationScript(
                project_id=project_id,
                test_case_id=target_tc.id,
                file_path=script_data.file_path,
                class_name=script_data.class_name,
                test_code=script_data.test_code,
                page_objects=script_data.page_objects,
                fixtures=script_data.fixtures,
                language="python",
                framework="playwright",
                review_status="approved" if review_report.is_approved else "changes_requested",
                reviewer_notes=review_report.summary,
                syntax_valid="valid" if review_report.syntax_valid else "invalid",
            )
            self.db.add(script_record)
            self.db.flush()
            script_id = script_record.id
        else:
            existing_script.test_code = script_data.test_code
            existing_script.page_objects = script_data.page_objects
            existing_script.fixtures = script_data.fixtures
            existing_script.review_status = "approved" if review_report.is_approved else "changes_requested"
            existing_script.reviewer_notes = review_report.summary
            script_id = existing_script.id

        target_tc.is_automated = True
        self.db.commit()

        # Update Workflow State -> Human Code Approval Gate
        state["current_stage"] = "human_code_approval"
        state["status"] = "awaiting_approval"
        state["quality_score"] = review_report.quality_score
        state["automation_script"] = script_data.model_dump()
        state["code_review_report"] = review_report.model_dump()

        # Queue Human Code Approval Request
        existing_code_approval = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.workflow_id == workflow_id,
            ApprovalRequest.artifact_type == "automation_code",
            ApprovalRequest.status == "pending"
        ).first()

        if not existing_code_approval:
            code_app_req = ApprovalRequest(
                project_id=project_id,
                workflow_id=workflow_id,
                artifact_type="automation_code",
                artifact_id=script_id,
                artifact_summary=f"Playwright POM Automation Suite: {script_data.file_path} (Review Score: {review_report.quality_score}/10)",
                quality_score=review_report.quality_score,
                status="pending"
            )
            self.db.add(code_app_req)
            self.db.commit()

        self._save_checkpoint(workflow_id, "automation_review", state)
        self._sync_agent_run(state)
        return state


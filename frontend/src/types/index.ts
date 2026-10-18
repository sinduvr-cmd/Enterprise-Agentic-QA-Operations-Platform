export interface Project {
  id: string;
  name: string;
  description?: string;
  source_repo: string;
  automation_repo: string;
  default_branch: string;
  framework_config?: Record<string, any>;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  active_runs_count: number;
  test_cases_count: number;
  automation_coverage: number;
}

export interface DashboardSummary {
  total_qa_runs: number;
  total_qa_runs_delta: string;
  running_workflows: number;
  awaiting_approval: number;
  passed_tests: number;
  failed_tests: number;
  test_cases_generated: number;
  automation_coverage: number;
  active_projects: number;
}

export interface RecentRun {
  id: string;
  workflow_id: string;
  project_id: string;
  project_name: string;
  run_name: string;
  branch: string;
  status: string;
  current_stage: string;
  quality_score: number;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  duration_seconds: number;
  started_at: string;
}

export interface AgentActivity {
  id: string;
  timestamp: string;
  agent_name: string;
  project_name: string;
  workflow_id: string;
  action: string;
  status: string;
  detail: string;
  score?: number;
}

export interface DashboardOverview {
  summary: DashboardSummary;
  recent_runs: RecentRun[];
  agent_activity: AgentActivity[];
  execution_trends: any[];
  pass_fail_distribution: {
    passed: number;
    failed: number;
    skipped: number;
    pass_rate: number;
  };
  requirement_coverage: any[];
  pending_approvals: any[];
  demo_mode: boolean;
}

export interface AutomationScript {
  id: string;
  project_id: string;
  test_case_id: string;
  workflow_id: string;
  script_path: string;
  language: string;
  framework: string;
  syntax_valid: string;
  created_at: string;
  test_code?: string;
  page_objects?: Array<{ class_name: string; file_path: string; code: string }>;
  fixtures_code?: string;
}

export interface FailureAnalysis {
  id: string;
  root_cause_category: string;
  confidence_score: number;
  explanation: string;
  suggested_fix: string;
  evidence: string[];
  analyzed_at: string;
}

export interface TestResult {
  id: string;
  test_name: string;
  status: string;
  duration_ms: number;
  error_message?: string;
  stack_trace?: string;
  failure_analysis?: FailureAnalysis;
}

export interface CIExecution {
  id: string;
  project_id: string;
  workflow_id?: string;
  run_number: number;
  branch: string;
  commit_sha?: string;
  pr_number?: number;
  pr_url?: string;
  status: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  skipped_tests: number;
  duration_seconds: number;
  trigger_type: string;
  artifacts_url?: string;
  started_at: string;
  completed_at?: string;
  raw_logs?: string;
  test_results?: TestResult[];
}

export interface Requirement {
  id: string;
  project_id: string;
  req_uid: string;
  title: string;
  description: string;
  source: string;
  github_issue_url?: string;
  github_issue_number?: string;
  acceptance_criteria: string[];
  status: string;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  project_id: string;
  workflow_id: string;
  artifact_type: string;
  artifact_summary: string;
  quality_score: number;
  status: string;
  reviewer_comment?: string;
  created_at: string;
}


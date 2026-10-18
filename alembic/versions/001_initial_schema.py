"""Initial enterprise QA operations schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='QA Engineer'),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 2. projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_repo', sa.String(length=512), nullable=False),
        sa.Column('automation_repo', sa.String(length=512), nullable=False),
        sa.Column('default_branch', sa.String(length=100), nullable=False, server_default='main'),
        sa.Column('framework_config', sa.JSON(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # 3. project_memberships
    op.create_table(
        'project_memberships',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='QA Engineer'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 4. repository_configurations
    op.create_table(
        'repository_configurations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('github_owner', sa.String(length=255), nullable=False),
        sa.Column('source_repo_name', sa.String(length=255), nullable=False),
        sa.Column('automation_repo_name', sa.String(length=255), nullable=False),
        sa.Column('token_secret_ref', sa.String(length=255), nullable=True),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 5. requirements
    op.create_table(
        'requirements',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('req_uid', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('github_issue_url', sa.String(length=512), nullable=True),
        sa.Column('github_issue_number', sa.String(length=50), nullable=True),
        sa.Column('acceptance_criteria', sa.JSON(), nullable=False),
        sa.Column('extracted_scenarios', sa.JSON(), nullable=False),
        sa.Column('ambiguities', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # 6. test_cases
    op.create_table(
        'test_cases',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id', ondelete='SET NULL'), nullable=True),
        sa.Column('test_uid', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('preconditions', sa.JSON(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('test_data', sa.JSON(), nullable=False),
        sa.Column('expected_results', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='Medium'),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='Functional'),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('critic_feedback', sa.Text(), nullable=True),
        sa.Column('is_automated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='generated'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # 7. test_case_versions
    op.create_table(
        'test_case_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('test_case_id', sa.String(length=36), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('snapshot', sa.JSON(), nullable=False),
        sa.Column('diff_summary', sa.Text(), nullable=True),
        sa.Column('critic_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 8. automation_scripts
    op.create_table(
        'automation_scripts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_case_id', sa.String(length=36), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('class_name', sa.String(length=255), nullable=True),
        sa.Column('test_code', sa.Text(), nullable=False),
        sa.Column('page_objects', sa.JSON(), nullable=False),
        sa.Column('fixtures', sa.JSON(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False, server_default='python'),
        sa.Column('framework', sa.String(length=50), nullable=False, server_default='playwright'),
        sa.Column('review_status', sa.String(length=50), nullable=False, server_default='pending_review'),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('syntax_valid', sa.String(length=10), nullable=False, server_default='valid'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # 9. agent_runs
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workflow_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id', ondelete='SET NULL'), nullable=True),
        sa.Column('run_name', sa.String(length=255), nullable=False),
        sa.Column('current_stage', sa.String(length=100), nullable=False, server_default='requirement_analysis'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='running'),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('critic_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_critic_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('agent_reasoning_log', sa.JSON(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # 10. workflow_checkpoints
    op.create_table(
        'workflow_checkpoints',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workflow_id', sa.String(length=100), sa.ForeignKey('agent_runs.workflow_id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_name', sa.String(length=100), nullable=False),
        sa.Column('state_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 11. quality_evaluations
    op.create_table(
        'quality_evaluations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('agent_run_id', sa.String(length=36), sa.ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=True),
        sa.Column('test_case_id', sa.String(length=36), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('completeness', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('accuracy', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('coverage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('clarity', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('traceability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('duplication_risk', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 12. approval_requests
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), sa.ForeignKey('agent_runs.workflow_id', ondelete='CASCADE'), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('artifact_id', sa.String(length=100), nullable=True),
        sa.Column('artifact_summary', sa.Text(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('reviewer_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewer_name', sa.String(length=255), nullable=True),
        sa.Column('reviewer_comment', sa.Text(), nullable=True),
        sa.Column('reviewer_changes', sa.JSON(), nullable=False),
        sa.Column('decision_timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 13. ci_executions
    op.create_table(
        'ci_executions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), sa.ForeignKey('agent_runs.workflow_id', ondelete='SET NULL'), nullable=True),
        sa.Column('run_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('branch', sa.String(length=255), nullable=False, server_default='main'),
        sa.Column('commit_sha', sa.String(length=64), nullable=True),
        sa.Column('pr_number', sa.Integer(), nullable=True),
        sa.Column('pr_url', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='running'),
        sa.Column('total_tests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed_tests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_tests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skipped_tests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('trigger_type', sa.String(length=50), nullable=False, server_default='workflow_dispatch'),
        sa.Column('raw_logs', sa.Text(), nullable=True),
        sa.Column('artifacts_url', sa.String(length=512), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # 14. test_results
    op.create_table(
        'test_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('ci_execution_id', sa.String(length=36), sa.ForeignKey('ci_executions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_case_id', sa.String(length=36), sa.ForeignKey('test_cases.id', ondelete='SET NULL'), nullable=True),
        sa.Column('test_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('screenshot_url', sa.String(length=512), nullable=True),
        sa.Column('trace_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 15. failure_analyses
    op.create_table(
        'failure_analyses',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('test_result_id', sa.String(length=36), sa.ForeignKey('test_results.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('root_cause_category', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('suggested_fix', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False),
    )

    # 16. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('project_id', sa.String(length=64), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('failure_analyses')
    op.drop_table('test_results')
    op.drop_table('ci_executions')
    op.drop_table('approval_requests')
    op.drop_table('quality_evaluations')
    op.drop_table('workflow_checkpoints')
    op.drop_table('agent_runs')
    op.drop_table('automation_scripts')
    op.drop_table('test_case_versions')
    op.drop_table('test_cases')
    op.drop_table('requirements')
    op.drop_table('repository_configurations')
    op.drop_table('project_memberships')
    op.drop_table('projects')
    op.drop_table('users')

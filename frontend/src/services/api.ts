import { DashboardOverview, Project } from '../types';

const BASE_URL = '/api/v1';

export async function fetchDashboardOverview(role = 'Admin'): Promise<DashboardOverview> {
  const res = await fetch(`${BASE_URL}/dashboard/overview`, {
    headers: { 'X-Demo-User-Role': role }
  });
  if (!res.ok) throw new Error('Failed to fetch dashboard data');
  return res.json();
}

export async function fetchProjects(includeArchived = true, role = 'Admin'): Promise<Project[]> {
  const res = await fetch(`${BASE_URL}/projects?include_archived=${includeArchived}`, {
    headers: { 'X-Demo-User-Role': role }
  });
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function createProject(data: Partial<Project>, role = 'Admin'): Promise<Project> {
  const res = await fetch(`${BASE_URL}/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-User-Role': role
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}

export async function triggerWorkflow(data: { project_id: string; run_name?: string; requirement_text?: string }, role = 'Admin') {
  const res = await fetch(`${BASE_URL}/workflows`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-User-Role': role
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to trigger workflow');
  return res.json();
}

export async function fetchAutomationScripts(role = 'Admin') {
  const res = await fetch(`${BASE_URL}/automation/scripts`, {
    headers: { 'X-Demo-User-Role': role }
  });
  if (!res.ok) throw new Error('Failed to fetch automation scripts');
  return res.json();
}

export async function fetchExecutions(role = 'Admin') {
  const res = await fetch(`${BASE_URL}/executions`, {
    headers: { 'X-Demo-User-Role': role }
  });
  if (!res.ok) throw new Error('Failed to fetch executions');
  return res.json();
}

export async function fetchRequirements(role = 'Admin') {
  const res = await fetch(`${BASE_URL}/requirements`, {
    headers: { 'X-Demo-User-Role': role }
  });
  if (!res.ok) throw new Error('Failed to fetch requirements');
  return res.json();
}

export async function importGithubIssues(projectId: string, issueNumber?: number, role = 'Admin') {
  const body: any = { project_id: projectId };
  if (issueNumber) body.issue_number = issueNumber;
  const res = await fetch(`${BASE_URL}/github/import-issues`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-User-Role': role
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error('Failed to import GitHub issues');
  return res.json();
}

export async function submitApprovalDecision(approvalId: string, decision: string, comment: string, role = 'Admin') {
  const res = await fetch(`${BASE_URL}/approvals/${approvalId}/decision`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-User-Role': role
    },
    body: JSON.stringify({ decision, reviewer_comment: comment })
  });
  if (!res.ok) throw new Error('Failed to submit approval decision');
  return res.json();
}


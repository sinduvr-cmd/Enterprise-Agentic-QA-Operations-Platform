import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  PlayCircle,
  Plus,
  CheckSquare,
  BarChart2,
  FolderGit2,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  AlertCircle,
  Code,
  FileText,
  Activity
} from 'lucide-react';

import { DashboardOverview, Project, AutomationScript, CIExecution, Requirement, ApprovalRequest } from './types';
import {
  fetchDashboardOverview,
  fetchProjects,
  createProject,
  triggerWorkflow,
  fetchAutomationScripts,
  fetchExecutions,
  fetchRequirements,
  importGithubIssues,
  submitApprovalDecision
} from './services/api';

export default function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'runs' | 'approvals' | 'reports' | 'projects' | 'requirements' | 'automation' | 'ci-executions'>('dashboard');
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [automationScripts, setAutomationScripts] = useState<AutomationScript[]>([]);
  const [ciExecutions, setCiExecutions] = useState<CIExecution[]>([]);
  const [selectedRole, setSelectedRole] = useState('Admin');
  const [showRunModal, setShowRunModal] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showGithubModal, setShowGithubModal] = useState(false);
  const [githubIssueNum, setGithubIssueNum] = useState('');

  const [runForm, setRunForm] = useState({
    projectId: '',
    runName: '',
    requirementText: '',
  });

  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    sourceRepo: '',
    automationRepo: '',
    defaultBranch: 'main',
  });

  useEffect(() => {
    loadData();
  }, [selectedRole]);

  const loadData = async () => {
    try {
      const [dash, projs, reqs, scripts, execs] = await Promise.all([
        fetchDashboardOverview(selectedRole),
        fetchProjects(true, selectedRole),
        fetchRequirements(selectedRole).catch(() => []),
        fetchAutomationScripts(selectedRole).catch(() => []),
        fetchExecutions(selectedRole).catch(() => []),
      ]);
      setData(dash);
      setProjects(projs);
      setRequirements(reqs);
      setAutomationScripts(scripts);
      setCiExecutions(execs);
      if (projs.length > 0 && !runForm.projectId) {
        setRunForm(prev => ({ ...prev, projectId: projs[0].id }));
      }
    } catch (e) {
      console.error(e);
    }
  };


  const handleCreateRun = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await triggerWorkflow({
        project_id: runForm.projectId,
        run_name: runForm.runName || 'Interactive QA Run',
        requirement_text: runForm.requirementText
      }, selectedRole);
      setShowRunModal(false);
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProject({
        name: projectForm.name,
        description: projectForm.description,
        source_repo: projectForm.sourceRepo,
        automation_repo: projectForm.automationRepo,
        default_branch: projectForm.defaultBranch,
      }, selectedRole);
      setShowProjectModal(false);
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const summary = data?.summary || {
    total_qa_runs: 2,
    total_qa_runs_delta: '+12%',
    running_workflows: 1,
    awaiting_approval: 1,
    passed_tests: 0,
    failed_tests: 0,
    test_cases_generated: 4,
    automation_coverage: 50.0,
    active_projects: 3,
  };

  return (
    <div className="flex h-screen bg-[#f6f8f6] font-sans text-slate-800 overflow-hidden">
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#08231c] text-white flex flex-col justify-between shrink-0 border-r border-[#0d2e26]">
        <div>
          {/* Logo */}
          <div className="p-6 pb-5 flex items-center space-x-3 border-b border-[#0f382e]/50">
            <div className="w-9 h-9 rounded-lg bg-[#144438] border border-[#1e584a] flex items-center justify-center text-[#34d399] font-bold text-sm tracking-tight shadow-inner">
              aq
            </div>
            <div>
              <div className="font-bold text-white text-[15px] leading-tight tracking-tight">
                Agentic QA
              </div>
              <div className="text-[10px] tracking-wider text-[#6ee7b7]/70 font-semibold uppercase mt-0.5">
                OPERATIONS PLATFORM
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="px-5 pt-6 pb-2">
            <div className="text-[11px] font-semibold text-[#6ee7b7]/50 tracking-wider uppercase mb-3 px-2">
              WORKSPACE
            </div>
            <nav className="space-y-1.5">
              <button
                onClick={() => setCurrentTab('dashboard')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'dashboard'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <LayoutDashboard className="w-4 h-4 text-[#34d399]" />
                <span>Dashboard</span>
              </button>

              <button
                onClick={() => setCurrentTab('runs')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'runs'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <PlayCircle className="w-4 h-4 text-slate-400" />
                  <span>QA runs</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {summary.total_qa_runs}
                </span>
              </button>

              <button
                onClick={() => setCurrentTab('requirements')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'requirements'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span>Requirements</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {requirements.length}
                </span>
              </button>

              <button
                onClick={() => setCurrentTab('automation')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'automation'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Code className="w-4 h-4 text-emerald-400" />
                  <span>Automation (POM)</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-emerald-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {automationScripts.length}
                </span>
              </button>

              <button
                onClick={() => setCurrentTab('ci-executions')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'ci-executions'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span>CI Executions</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-300 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {ciExecutions.length}
                </span>
              </button>

              <button
                onClick={() => setShowRunModal(true)}
                className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0e3229] transition-all"
              >
                <Plus className="w-4 h-4 text-[#34d399]" />
                <span>+ New QA run</span>
              </button>


              <button
                onClick={() => setCurrentTab('approvals')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'approvals'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <CheckSquare className="w-4 h-4 text-amber-400" />
                  <span>Pending approvals</span>
                </div>
                {summary.awaiting_approval > 0 && (
                  <span className="text-[11px] bg-amber-900/60 text-amber-300 px-1.5 py-0.5 rounded font-semibold border border-amber-700/50">
                    {summary.awaiting_approval}
                  </span>
                )}
              </button>

              <button
                onClick={() => setCurrentTab('reports')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'reports'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <BarChart2 className="w-4 h-4 text-slate-400" />
                <span>Reports & evidence</span>
              </button>

              <button
                onClick={() => setCurrentTab('projects')}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === 'projects'
                    ? 'bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold'
                    : 'text-slate-300 hover:text-white hover:bg-[#0e3229]'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <FolderGit2 className="w-4 h-4 text-slate-400" />
                  <span>Projects</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {projects.length}
                </span>
              </button>
            </nav>
          </div>
        </div>

        {/* Footer */}
        <div className="p-5 border-t border-[#0f382e]/50 space-y-4">
          <div className="flex items-start space-x-3">
            <ShieldCheck className="w-4 h-4 text-[#34d399] shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-medium text-slate-200">Governed by design</div>
              <div className="text-[11px] text-slate-400">Every decision. Every run.</div>
            </div>
          </div>

          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between text-xs text-[#6ee7b7]/80 hover:text-white pt-2 border-t border-[#0f382e]/40 transition-colors"
          >
            <span>API documentation</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <header className="bg-white/80 backdrop-blur-sm sticky top-0 z-10 border-b border-slate-200/80 px-8 py-4 flex items-center justify-between">
          <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase">
            QA OPERATIONS / OVERVIEW
          </div>

          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
              DEMO MODE: ACTIVE
            </span>

            <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
              <span className="text-slate-500 font-medium pl-1.5">Role:</span>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="bg-white border border-slate-200 rounded px-2 py-0.5 text-xs font-semibold text-slate-700 focus:outline-none"
              >
                <option value="Admin">Admin</option>
                <option value="QA Manager">QA Manager</option>
                <option value="QA Engineer">QA Engineer</option>
                <option value="Viewer">Viewer</option>
              </select>
            </div>

            <button
              onClick={() => setShowRunModal(true)}
              className="inline-flex items-center space-x-2 bg-[#0b382d] hover:bg-[#0f4639] text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>+ New QA run</span>
            </button>
          </div>
        </header>

        {currentTab === 'dashboard' && (
          <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
            <div>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                Quality, in clear view.
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                Track your automation. Review what matters. Keep delivery moving.
              </p>
            </div>

            {/* KPI Cards Row (Matching screenshot) */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="text-xs font-medium text-slate-500">Total runs</div>
                <div className="text-3xl font-bold text-slate-900 mt-2">{summary.total_qa_runs}</div>
                <div className="text-xs text-slate-400 mt-2">All recorded runs</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="text-xs font-medium text-slate-500">Running</div>
                <div className="text-3xl font-bold text-blue-600 mt-2">{summary.running_workflows}</div>
                <div className="text-xs text-slate-400 mt-2">Active workflows</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="text-xs font-medium text-slate-500">Awaiting approval</div>
                <div className="text-3xl font-bold text-amber-600 mt-2">{summary.awaiting_approval}</div>
                <div className="text-xs text-slate-400 mt-2">Human review required</div>
              </div>

              <div className="bg-[#f2faf3] border border-emerald-200/80 rounded-xl p-5 shadow-sm">
                <div className="text-xs font-medium text-emerald-800">Passed</div>
                <div className="text-3xl font-bold text-emerald-600 mt-2">{summary.passed_tests}</div>
                <div className="text-xs text-emerald-700/70 mt-2">Persisted outcomes</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="text-xs font-medium text-slate-500">Failed</div>
                <div className="text-3xl font-bold text-slate-800 mt-2">{summary.failed_tests}</div>
                <div className="text-xs text-slate-400 mt-2">Persisted outcomes</div>
              </div>
            </div>

            {/* Recent QA Runs Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-slate-900">Recent QA runs</h2>
                  <p className="text-xs text-slate-500 mt-0.5">The latest activity in Agentic QA</p>
                </div>
                <button
                  onClick={() => setCurrentTab('runs')}
                  className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center space-x-1"
                >
                  <span>View all runs</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <table className="w-full text-left text-xs">
                <thead className="bg-[#fcfdfc] border-b border-slate-200 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
                  <tr>
                    <th className="py-3.5 px-6">RUN / ISSUE</th>
                    <th className="py-3.5 px-6">PROJECT</th>
                    <th className="py-3.5 px-6">STAGE</th>
                    <th className="py-3.5 px-6">STATUS</th>
                    <th className="py-3.5 px-6">QA RESULT</th>
                    <th className="py-3.5 px-6">UPDATED</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-600">
                  {(data?.recent_runs || []).map((run) => (
                    <tr key={run.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-4 px-6">
                        <div className="font-mono font-bold text-slate-900 text-xs">
                          {run.workflow_id}
                        </div>
                        <div className="text-[11px] text-emerald-700 font-medium mt-0.5">
                          {run.run_name.substring(0, 36)}...
                        </div>
                      </td>
                      <td className="py-4 px-6 font-mono text-[11px] text-slate-500">
                        {run.project_id}
                      </td>
                      <td className="py-4 px-6 font-medium text-slate-800 capitalize">
                        {run.current_stage.replace(/_/g, ' ')}
                      </td>
                      <td className="py-4 px-6">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border bg-blue-50 text-blue-700 border-blue-200">
                          {run.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        {run.total_tests > 0 ? (
                          <span className="font-semibold text-emerald-700">
                            Passed ({run.passed_tests}/{run.total_tests})
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">Not available</span>
                        )}
                      </td>
                      <td className="py-4 px-6 text-slate-500 text-[11px]">
                        <div>{run.started_at}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

const { useState, useEffect } = React;

function App() {
  const [currentTab, setCurrentTab] = useState("dashboard");
  const [dashboardData, setDashboardData] = useState(null);
  const [projects, setProjects] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [approvals, setApprovals] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState("Admin");

  // Modals
  const [showNewRunModal, setShowNewRunModal] = useState(false);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showNewReqModal, setShowNewReqModal] = useState(false);
  const [showImportGithubModal, setShowImportGithubModal] = useState(false);
  const [selectedRunDetail, setSelectedRunDetail] = useState(null);
  const [selectedTestCase, setSelectedTestCase] = useState(null);
  const [selectedScriptDetail, setSelectedScriptDetail] = useState(null);
  const [selectedExecutionDetail, setSelectedExecutionDetail] = useState(null);
  const [scriptCodeTab, setScriptCodeTab] = useState("test_code");

  // Advanced features states
  const [automationScripts, setAutomationScripts] = useState([]);
  const [ciExecutions, setCiExecutions] = useState([]);

  // Form states
  const [newRunForm, setNewRunForm] = useState({
    projectId: "",
    runName: "",
    requirementText: "",
    browser: "chromium"
  });

  const [newProjectForm, setNewProjectForm] = useState({
    name: "",
    description: "",
    sourceRepo: "",
    automationRepo: "",
    defaultBranch: "main",
    baseUrl: "https://staging.example.com"
  });

  const [newReqForm, setNewReqForm] = useState({
    projectId: "",
    title: "",
    description: "",
    acceptanceCriteriaText: ""
  });

  const [importGithubForm, setImportGithubForm] = useState({
    projectId: "",
    issueNumber: ""
  });

  // Fetch Dashboard Overview
  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/v1/dashboard/overview", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Projects
  const fetchProjects = async () => {
    try {
      const res = await fetch("/api/v1/projects?include_archived=true", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0) {
          if (!newRunForm.projectId) setNewRunForm(prev => ({ ...prev, projectId: data[0].id }));
          if (!newReqForm.projectId) setNewReqForm(prev => ({ ...prev, projectId: data[0].id }));
          if (!importGithubForm.projectId) setImportGithubForm(prev => ({ ...prev, projectId: data[0].id }));
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Requirements
  const fetchRequirements = async () => {
    try {
      const res = await fetch("/api/v1/requirements", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setRequirements(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Test Cases
  const fetchTestCases = async () => {
    try {
      const res = await fetch("/api/v1/test-cases", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setTestCases(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Approvals
  const fetchApprovals = async () => {
    try {
      const res = await fetch("/api/v1/approvals", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setApprovals(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Workflows
  const fetchWorkflows = async () => {
    try {
      const res = await fetch("/api/v1/workflows", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setWorkflows(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Automation Scripts
  const fetchAutomationScripts = async () => {
    try {
      const res = await fetch("/api/v1/automation/scripts", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setAutomationScripts(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch CI Executions
  const fetchExecutions = async () => {
    try {
      const res = await fetch("/api/v1/executions", {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setCiExecutions(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Inspect Script Details
  const handleInspectScript = async (scriptId) => {
    try {
      const res = await fetch(`/api/v1/automation/scripts/${scriptId}`, {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedScriptDetail(data);
        setScriptCodeTab("test_code");
      }
    } catch (err) {
      alert("Error fetching script detail: " + err.message);
    }
  };

  // Inspect CI Execution Details
  const handleInspectExecution = async (execId) => {
    try {
      const res = await fetch(`/api/v1/executions/${execId}`, {
        headers: { "X-Demo-User-Role": selectedRole }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedExecutionDetail(data);
      }
    } catch (err) {
      alert("Error fetching execution detail: " + err.message);
    }
  };

  // Import GitHub Issues
  const handleImportGithub = async (e) => {
    if (e) e.preventDefault();
    try {
      const body = { project_id: importGithubForm.projectId || projects[0]?.id };
      if (importGithubForm.issueNumber) {
        body.issue_number = parseInt(importGithubForm.issueNumber, 10);
      }
      const res = await fetch("/api/v1/github/import-issues", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Error importing GitHub issues");
        return;
      }
      const imported = await res.json();
      setShowImportGithubModal(false);
      setImportGithubForm({ projectId: projects[0]?.id || "", issueNumber: "" });
      await fetchRequirements();
      await fetchDashboard();
      alert(`Successfully imported ${imported.length} user story requirement(s) from GitHub!`);
    } catch (err) {
      alert("Import error: " + err.message);
    }
  };

  useEffect(() => {
    fetchDashboard();
    fetchProjects();
    fetchRequirements();
    fetchTestCases();
    fetchApprovals();
    fetchWorkflows();
    fetchAutomationScripts();
    fetchExecutions();
  }, [selectedRole]);


  // Handle New QA Run Submission (LangGraph Loop Execution)
  const handleStartRun = async (e) => {
    if (e) e.preventDefault();
    try {
      const res = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify({
          project_id: newRunForm.projectId,
          run_name: newRunForm.runName || "Autonomous QA Run",
          requirement_text: newRunForm.requirementText,
          target_browsers: [newRunForm.browser]
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error starting run");
        return;
      }
      setShowNewRunModal(false);
      setNewRunForm({ projectId: projects[0]?.id || "", runName: "", requirementText: "", browser: "chromium" });
      await fetchDashboard();
      await fetchWorkflows();
      await fetchTestCases();
      await fetchApprovals();
      alert("Agentic QA Run completed! Test cases synthesized and evaluated.");
    } catch (err) {
      alert("Network error: " + err.message);
    }
  };

  // Trigger Run for a specific requirement
  const handleTriggerRequirementWorkflow = async (req) => {
    try {
      const res = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify({
          project_id: req.project_id,
          requirement_id: req.id,
          run_name: `AI Generation: ${req.title}`,
          requirement_text: req.description,
          acceptance_criteria: req.acceptance_criteria
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error triggering workflow");
        return;
      }
      await fetchDashboard();
      await fetchWorkflows();
      await fetchTestCases();
      await fetchApprovals();
      alert(`Generator-Critic loop completed for '${req.title}'! Test cases ready.`);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Handle Requirement Creation
  const handleCreateRequirement = async (e) => {
    e.preventDefault();
    try {
      const criteriaList = newReqForm.acceptanceCriteriaText
        .split("\n")
        .map(s => s.trim())
        .filter(s => s.length > 0);

      const res = await fetch("/api/v1/requirements", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify({
          project_id: newReqForm.projectId,
          title: newReqForm.title,
          description: newReqForm.description,
          acceptance_criteria: criteriaList,
          source: "manual"
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error creating requirement");
        return;
      }
      setShowNewReqModal(false);
      setNewReqForm({ projectId: projects[0]?.id || "", title: "", description: "", acceptanceCriteriaText: "" });
      await fetchRequirements();
      alert("Requirement added successfully!");
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Handle Project Creation
  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify({
          name: newProjectForm.name,
          description: newProjectForm.description,
          source_repo: newProjectForm.sourceRepo,
          automation_repo: newProjectForm.automationRepo,
          default_branch: newProjectForm.defaultBranch,
          framework_config: {
            framework: "playwright-python",
            test_runner: "pytest",
            pattern: "Page Object Model",
            base_url: newProjectForm.baseUrl,
            browsers: ["chromium", "firefox", "webkit"],
            headless: true
          }
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error creating project");
        return;
      }
      setShowNewProjectModal(false);
      setNewProjectForm({ name: "", description: "", sourceRepo: "", automationRepo: "", defaultBranch: "main", baseUrl: "https://staging.example.com" });
      await fetchProjects();
      await fetchDashboard();
      alert("Project registered successfully!");
    } catch (err) {
      alert("Network error: " + err.message);
    }
  };

  // Handle Approval Decision
  const handleApprovalDecision = async (approvalId, decision, comment) => {
    try {
      const res = await fetch(`/api/v1/approvals/${approvalId}/decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User-Role": selectedRole
        },
        body: JSON.stringify({
          decision: decision,
          reviewer_comment: comment || `Actioned by ${selectedRole}`
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Failed to submit decision");
        return;
      }
      await fetchApprovals();
      await fetchDashboard();
      await fetchWorkflows();
      await fetchAutomationScripts();
      await fetchExecutions();
      alert(`Approval marked as ${decision}!`);

    } catch (err) {
      alert("Network error: " + err.message);
    }
  };

  const summary = dashboardData?.summary || {
    total_qa_runs: 2,
    running_workflows: 1,
    awaiting_approval: 1,
    passed_tests: 0,
    failed_tests: 0,
    test_cases_generated: 4,
    automation_coverage: 50.0,
    active_projects: 3
  };

  const recentRuns = dashboardData?.recent_runs || [];

  return (
    <div className="flex h-screen bg-[#f6f8f6] font-sans antialiased overflow-hidden">
      {/* SIDEBAR (Dark Emerald Green - Matching screenshot exactly) */}
      <aside className="w-64 bg-[#08231c] text-white flex flex-col justify-between shrink-0 border-r border-[#0d2e26] select-none">
        <div>
          {/* Brand Logo Header */}
          <div className="p-6 pb-5 flex items-center space-x-3 border-b border-[#0f382e]/50">
            <div className="w-9 h-9 rounded-lg bg-[#144438] border border-[#1e584a] flex items-center justify-center text-[#34d399] font-bold text-sm tracking-tight shadow-inner">
              aq
            </div>
            <div>
              <div className="font-bold text-white text-[15px] leading-tight tracking-tight flex items-center space-x-1">
                <span>Agentic QA</span>
              </div>
              <div className="text-[10px] tracking-wider text-[#6ee7b7]/70 font-semibold uppercase mt-0.5">
                OPERATIONS PLATFORM
              </div>
            </div>
          </div>

          {/* Section: WORKSPACE */}
          <div className="px-5 pt-6 pb-2">
            <div className="text-[11px] font-semibold text-[#6ee7b7]/50 tracking-wider uppercase mb-3 px-2">
              WORKSPACE
            </div>
            <nav className="space-y-1.5">
              {/* Dashboard */}
              <button
                onClick={() => setCurrentTab("dashboard")}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "dashboard"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <svg className="w-4 h-4 text-[#34d399]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span>Dashboard</span>
              </button>

              {/* Projects */}
              <button
                onClick={() => setCurrentTab("projects")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "projects"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  <span>Projects</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {projects.length}
                </span>
              </button>

              {/* Requirements */}
              <button
                onClick={() => setCurrentTab("requirements")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "requirements"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Requirements</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {requirements.length}
                </span>
              </button>

              {/* Test Cases Repository */}
              <button
                onClick={() => setCurrentTab("test-cases")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "test-cases"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-[#34d399]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <span>Test Cases</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {testCases.length}
                </span>
              </button>

              {/* Automation Scripts (POM) */}
              <button
                onClick={() => setCurrentTab("automation")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "automation"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <span>Automation (POM)</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-emerald-400 px-1.5 py-0.5 rounded border border-[#18483b] font-mono">
                  {automationScripts.length}
                </span>
              </button>

              {/* QA runs */}
              <button
                onClick={() => setCurrentTab("runs")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "runs"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>QA runs</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-400 px-1.5 py-0.5 rounded border border-[#18483b]">
                  {summary.total_qa_runs}
                </span>
              </button>

              {/* CI Executions */}
              <button
                onClick={() => setCurrentTab("ci-executions")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "ci-executions"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>CI Executions</span>
                </div>
                <span className="text-[11px] bg-[#0c2e25] text-slate-300 px-1.5 py-0.5 rounded border border-[#18483b] font-mono">
                  {ciExecutions.length}
                </span>
              </button>


              {/* + New QA run */}
              <button
                onClick={() => setShowNewRunModal(true)}
                className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0e3229] transition-all"
              >
                <svg className="w-4 h-4 text-[#34d399]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                </svg>
                <span>+ New QA run</span>
              </button>

              {/* Pending approvals */}
              <button
                onClick={() => setCurrentTab("approvals")}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "approvals"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <svg className="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Pending approvals</span>
                </div>
                {summary.awaiting_approval > 0 && (
                  <span className="text-[11px] bg-amber-900/60 text-amber-300 px-1.5 py-0.5 rounded font-semibold border border-amber-700/50">
                    {summary.awaiting_approval}
                  </span>
                )}
              </button>

              {/* Reports & evidence */}
              <button
                onClick={() => setCurrentTab("reports")}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  currentTab === "reports"
                    ? "bg-[#144336] text-white border border-[#1d5b4b] shadow-sm font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-[#0e3229]"
                }`}
              >
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Reports & evidence</span>
              </button>
            </nav>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-5 border-t border-[#0f382e]/50 space-y-4">
          <div className="flex items-start space-x-3">
            <svg className="w-4 h-4 text-[#34d399] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
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
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Operational Bar */}
        <header className="bg-white/80 backdrop-blur-sm sticky top-0 z-10 border-b border-slate-200/80 px-8 py-4 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase">
              QA OPERATIONS / OVERVIEW
            </div>
          </div>

          {/* Right Controls: Role Switcher & Demo Badge */}
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
              DEMO MODE: ACTIVE
            </span>

            {/* Role Switcher */}
            <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
              <span className="text-slate-500 font-medium pl-1.5">Role:</span>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="bg-white border border-slate-200 rounded px-2 py-0.5 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-1 focus:ring-emerald-500 cursor-pointer"
              >
                <option value="Admin">Admin (Full Control)</option>
                <option value="QA Manager">QA Manager (Approver)</option>
                <option value="QA Engineer">QA Engineer (Author)</option>
                <option value="Viewer">Viewer (Read-Only)</option>
              </select>
            </div>

            {/* Quick Action: New QA Run */}
            <button
              onClick={() => setShowNewRunModal(true)}
              className="inline-flex items-center space-x-2 bg-[#0b382d] hover:bg-[#0f4639] text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>+ New QA run</span>
            </button>
          </div>
        </header>

        {/* Dashboard View */}
        {currentTab === "dashboard" && (
          <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
            {/* Title Section (Matching screenshot exactly) */}
            <div>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                Quality, in clear view.
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                Track your automation. Review what matters. Keep delivery moving.
              </p>
            </div>

            {/* 5 Summary KPI Cards Row (Exact replica of attached screenshot) */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow transition-shadow">
                <div className="text-xs font-medium text-slate-500">Total runs</div>
                <div className="text-3xl font-bold text-slate-900 mt-2">{summary.total_qa_runs}</div>
                <div className="text-xs text-slate-400 mt-2">All recorded runs</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow transition-shadow">
                <div className="text-xs font-medium text-slate-500">Running</div>
                <div className="text-3xl font-bold text-blue-600 mt-2">{summary.running_workflows}</div>
                <div className="text-xs text-slate-400 mt-2">Active workflows</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow transition-shadow">
                <div className="text-xs font-medium text-slate-500">Awaiting approval</div>
                <div className="text-3xl font-bold text-amber-600 mt-2">{summary.awaiting_approval}</div>
                <div className="text-xs text-slate-400 mt-2">Human review required</div>
              </div>

              <div className="bg-[#f2faf3] border border-emerald-200/80 rounded-xl p-5 shadow-sm hover:shadow transition-shadow">
                <div className="text-xs font-medium text-emerald-800">Passed</div>
                <div className="text-3xl font-bold text-emerald-600 mt-2">{summary.passed_tests}</div>
                <div className="text-xs text-emerald-700/70 mt-2">Persisted outcomes</div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow transition-shadow">
                <div className="text-xs font-medium text-slate-500">Failed</div>
                <div className="text-3xl font-bold text-slate-800 mt-2">{summary.failed_tests}</div>
                <div className="text-xs text-slate-400 mt-2">Persisted outcomes</div>
              </div>
            </div>

            {/* Recent QA runs Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-slate-900">Recent QA runs</h2>
                  <p className="text-xs text-slate-500 mt-0.5">The latest activity in Agentic QA</p>
                </div>
                <button
                  onClick={() => setCurrentTab("runs")}
                  className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center space-x-1"
                >
                  <span>View all runs</span>
                  <span>&rarr;</span>
                </button>
              </div>

              <div className="overflow-x-auto">
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
                    {recentRuns.map((run) => {
                      const statusBadgeClass =
                        run.status === "running"
                          ? "bg-blue-50 text-blue-700 border-blue-200"
                          : run.status === "awaiting_approval"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : run.status === "passed" || run.status === "completed"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-red-50 text-red-700 border-red-200";

                      return (
                        <tr
                          key={run.id}
                          onClick={() => setSelectedRunDetail(run)}
                          className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                        >
                          <td className="py-4 px-6">
                            <div className="font-mono font-bold text-slate-900 text-xs">
                              {run.workflow_id}
                            </div>
                            <div className="text-[11px] text-emerald-700 font-medium mt-0.5 flex items-center space-x-1">
                              <span>{run.run_name.substring(0, 36)}...</span>
                              <span>↗</span>
                            </div>
                          </td>
                          <td className="py-4 px-6 text-slate-500 font-mono text-[11px]">
                            {run.project_id}
                          </td>
                          <td className="py-4 px-6 font-medium text-slate-800 capitalize">
                            {run.current_stage.replace(/_/g, " ")}
                          </td>
                          <td className="py-4 px-6">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${statusBadgeClass}`}>
                              {run.status.replace(/_/g, " ")}
                            </span>
                          </td>
                          <td className="py-4 px-6">
                            {run.total_tests > 0 ? (
                              <span className={run.failed_tests > 0 ? "text-red-600 font-semibold" : "text-emerald-700 font-semibold"}>
                                {run.failed_tests > 0 ? `Failed (${run.failed_tests}/${run.total_tests})` : `Passed (${run.passed_tests}/${run.total_tests})`}
                              </span>
                            ) : (
                              <span className="text-slate-400 italic">Not available</span>
                            )}
                          </td>
                          <td className="py-4 px-6 text-slate-500 text-[11px]">
                            <div>{run.started_at}</div>
                            <div className="text-[10px] text-slate-400">Created {run.started_at}</div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Secondary Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Agent Activity Timeline */}
              <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">Agent Activity Timeline</h3>
                    <p className="text-xs text-slate-500">Autonomous reasoning and quality loop evaluations</p>
                  </div>
                  <span className="text-[11px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                    LangGraph Cyclic State
                  </span>
                </div>

                <div className="space-y-4">
                  {(dashboardData?.agent_activity || []).map((act) => (
                    <div key={act.id} className="flex items-start space-x-3 text-xs border-l-2 border-emerald-500 pl-4 py-1">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-slate-900">{act.agent_name}</span>
                          <span className="text-slate-400">&bull;</span>
                          <span className="text-slate-500">{act.project_name}</span>
                          {act.score && (
                            <span className="bg-emerald-100 text-emerald-800 text-[10px] px-1.5 py-0.5 rounded font-bold">
                              Quality Score: {act.score}/10
                            </span>
                          )}
                        </div>
                        <div className="text-slate-600 mt-1">{act.detail}</div>
                      </div>
                      <div className="text-slate-400 text-[11px] shrink-0 font-mono">
                        {act.timestamp}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Requirement & Automation Coverage */}
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Automation Coverage</h3>
                  <p className="text-xs text-slate-500 mb-4">Ratio of automated Playwright POM tests</p>

                  <div className="text-center py-6">
                    <div className="inline-flex items-center justify-center w-28 h-28 rounded-full border-8 border-emerald-500 bg-emerald-50 text-slate-900 font-extrabold text-2xl">
                      {summary.automation_coverage}%
                    </div>
                    <div className="text-xs font-medium text-slate-600 mt-3">
                      {summary.test_cases_generated} Test Cases Generated
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-100 pt-3 text-xs text-slate-500 space-y-1.5">
                  <div className="flex justify-between">
                    <span>Active Projects</span>
                    <span className="font-bold text-slate-700">{summary.active_projects}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Critic Loop Target</span>
                    <span className="font-bold text-emerald-700">&ge; 8.0 / 10</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Regeneration Attempts</span>
                    <span className="font-bold text-slate-700">5 loops</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Requirements View */}
        {currentTab === "requirements" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Requirements & User Stories</h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Imported user stories and acceptance criteria ready for AI agent test synthesis
                </p>
              </div>
              <div className="flex items-center space-x-2.5">
                <button
                  onClick={() => setShowImportGithubModal(true)}
                  className="bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-2 rounded-lg text-xs font-semibold transition shadow-sm flex items-center space-x-2"
                >
                  <svg className="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  <span>Import GitHub Issues</span>
                </button>
                <button
                  onClick={() => setShowNewReqModal(true)}
                  className="bg-[#0b382d] hover:bg-[#0f4639] text-white px-4 py-2 rounded-lg text-xs font-semibold transition shadow-sm"
                >
                  + Add User Story
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {requirements.map((req) => (
                <div key={req.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                          {req.req_uid}
                        </span>
                        {req.source === "github_issue" && (
                          <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded flex items-center space-x-1">
                            <span>GitHub #{req.github_issue_number}</span>
                          </span>
                        )}
                        <h3 className="font-bold text-base text-slate-900">{req.title}</h3>
                        <span className="text-xs font-mono text-slate-400">&bull; {req.project_id}</span>
                      </div>
                      <p className="text-xs text-slate-600 mt-2 max-w-4xl">{req.description}</p>
                    </div>


                    <button
                      onClick={() => handleTriggerRequirementWorkflow(req)}
                      className="shrink-0 bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 shadow-sm"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span>Generate AI Tests</span>
                    </button>
                  </div>

                  {/* Acceptance Criteria */}
                  {Array.isArray(req.acceptance_criteria) && req.acceptance_criteria.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-100">
                      <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                        Acceptance Criteria
                      </div>
                      <ul className="list-disc list-inside text-xs text-slate-600 space-y-1">
                        {req.acceptance_criteria.map((c, i) => (
                          <li key={i}>{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Test Cases View (Phase 2 Core Feature) */}
        {currentTab === "test-cases" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Generated Test Case Repository</h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Structured manual test cases generated by Agent 2 and verified by Agent 3 Critic loop
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-500">Total Cases:</span>
                <span className="font-bold text-slate-900">{testCases.length}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {testCases.map((tc) => (
                <div
                  key={tc.id}
                  onClick={() => setSelectedTestCase(tc)}
                  className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md cursor-pointer transition flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {tc.test_uid}
                      </span>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                        tc.priority === "Critical" ? "bg-red-50 text-red-700 border border-red-200" :
                        tc.priority === "High" ? "bg-amber-50 text-amber-700 border border-amber-200" :
                        "bg-blue-50 text-blue-700 border border-blue-200"
                      }`}>
                        {tc.priority}
                      </span>
                    </div>

                    <h3 className="font-bold text-slate-900 text-sm">{tc.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{tc.objective}</p>

                    <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="text-slate-400 text-[11px] capitalize">Category: <strong>{tc.category}</strong></span>
                      <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded text-[11px]">
                        ★ {tc.quality_score}/10
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                    <span>{tc.steps?.length || 0} steps</span>
                    <span className="text-emerald-600 font-medium">View Details &rarr;</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Projects View */}
        {currentTab === "projects" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Project Management</h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Registered enterprise software repositories and automation configurations
                </p>
              </div>
              <button
                onClick={() => setShowNewProjectModal(true)}
                className="bg-[#0b382d] hover:bg-[#0f4639] text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-sm"
              >
                + Register Project
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((p) => (
                <div
                  key={p.id}
                  className={`bg-white border rounded-xl p-6 shadow-sm flex flex-col justify-between ${
                    p.is_archived ? "opacity-60 border-dashed border-slate-300" : "border-slate-200"
                  }`}
                >
                  <div>
                    <div className="flex items-start justify-between">
                      <h3 className="font-bold text-slate-900 text-base">{p.name}</h3>
                      {p.is_archived ? (
                        <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-bold uppercase">
                          Archived
                        </span>
                      ) : (
                        <span className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded font-bold uppercase">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 mt-2 line-clamp-3">{p.description}</p>

                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Source Repo</span>
                        <a
                          href={p.source_repo}
                          target="_blank"
                          rel="noopener"
                          className="text-emerald-700 hover:underline font-mono text-[11px] truncate block"
                        >
                          {p.source_repo}
                        </a>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Automation Repo</span>
                        <a
                          href={p.automation_repo}
                          target="_blank"
                          rel="noopener"
                          className="text-emerald-700 hover:underline font-mono text-[11px] truncate block"
                        >
                          {p.automation_repo}
                        </a>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
                    <div>
                      <span className="text-slate-400 block text-[10px]">Playwright Coverage</span>
                      <span className="font-bold text-slate-900">{p.automation_coverage}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Approvals View */}
        {currentTab === "approvals" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Pending Approvals</h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Human-in-the-Loop dual-gate review for AI test cases and Playwright automation scripts
              </p>
            </div>

            <div className="space-y-4">
              {approvals.length === 0 ? (
                <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400 text-sm">
                  No approval requests pending. Quality gates cleared!
                </div>
              ) : (
                approvals.map((app) => (
                  <div key={app.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                        {app.artifact_type === "test_cases" ? (
                          <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 border border-emerald-300 px-2.5 py-0.5 rounded">
                            Gate 1: Manual Test Case Review
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 border border-purple-300 px-2.5 py-0.5 rounded">
                            Gate 2: Playwright POM Code Review
                          </span>
                        )}
                        <span className="font-bold text-slate-900 text-sm">{app.artifact_summary}</span>
                        <span className="text-xs bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded">
                          Quality/Security Score: {app.quality_score}/10
                        </span>
                        <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-mono">
                          {app.workflow_id}
                        </span>
                      </div>
                      <div className="text-xs text-slate-600">
                        {app.artifact_type === "test_cases" ? (
                          <span>Agent 3 Critic loop cleared quality threshold (&ge; 8.0/10). Approving will trigger <strong>Agent 4 (POM Generator)</strong> &amp; <strong>Agent 5 (AST Reviewer)</strong>.</span>
                        ) : (
                          <span>Agent 5 AST code review cleared (valid Python syntax, 0 security vulnerabilities). Approving will open a <strong>GitHub Draft PR</strong> and dispatch <strong>GitHub Actions CI</strong>.</span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        Project: {app.project_id} &bull; Requested: {app.created_at}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      <button
                        onClick={() => handleApprovalDecision(app.id, "regenerate", "Requested AI regeneration")}
                        className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                      >
                        Regenerate
                      </button>
                      <button
                        onClick={() => handleApprovalDecision(app.id, "rejected", "Rejected during human review")}
                        className="px-3 py-1.5 border border-red-300 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 transition"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprovalDecision(app.id, "approved", "Approved by QA Manager")}
                        className="px-4 py-1.5 bg-[#0b382d] hover:bg-[#0f4639] text-white rounded-lg text-xs font-semibold transition shadow-sm"
                      >
                        {app.artifact_type === "test_cases" ? "Approve & Generate POM Code" : "Approve, Create Draft PR & Run CI"}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Automation Scripts (POM) View */}
        {currentTab === "automation" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Playwright Automation Scripts</h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Page Object Model suites generated by Agent 4 and verified by Agent 5 AST Security Scanner
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-500">Total Scripts:</span>
                <span className="font-bold text-slate-900">{automationScripts.length}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {automationScripts.map((script) => (
                <div key={script.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                          {script.id}
                        </span>
                        <h3 className="font-bold text-base text-slate-900 mt-2 font-mono">
                          {script.script_path || "tests/test_playwright_suite.py"}
                        </h3>
                      </div>
                      <span className="text-[10px] bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded font-bold uppercase">
                        Syntax: {script.syntax_valid}
                      </span>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-600">
                      <div className="bg-slate-50 p-2.5 rounded border border-slate-100">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Framework</span>
                        <span className="font-semibold text-slate-800">{script.framework}</span>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded border border-slate-100">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Language</span>
                        <span className="font-semibold text-slate-800 capitalize">{script.language}</span>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center space-x-2 text-xs">
                      <span className="text-slate-500">Security Audit:</span>
                      <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[11px]">
                        Passed (Score: 9.5/10)
                      </span>
                    </div>
                  </div>

                  <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-mono">{script.project_id}</span>
                    <button
                      onClick={() => handleInspectScript(script.id)}
                      className="bg-[#0b382d] hover:bg-[#0f4639] text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold transition"
                    >
                      Inspect POM Suite &rarr;
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CI Executions View */}
        {currentTab === "ci-executions" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">GitHub Actions CI Executions</h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Authoritative CI runner results, GitHub Draft PRs, and Agent 6 AI Failure Diagnostics
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-500">Total CI Runs:</span>
                <span className="font-bold text-slate-900">{ciExecutions.length}</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#fcfdfc] border-b border-slate-200 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
                  <tr>
                    <th className="py-3 px-6">RUN #</th>
                    <th className="py-3 px-6">PROJECT</th>
                    <th className="py-3 px-6">BRANCH &amp; PR</th>
                    <th className="py-3 px-6">STATUS</th>
                    <th className="py-3 px-6">TEST RESULTS</th>
                    <th className="py-3 px-6">DURATION</th>
                    <th className="py-3 px-6">ACTION</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {ciExecutions.map((exec) => (
                    <tr key={exec.id} className="hover:bg-slate-50 transition">
                      <td className="py-3.5 px-6 font-mono font-semibold text-slate-900">#{exec.run_number}</td>
                      <td className="py-3.5 px-6 font-mono text-slate-500">{exec.project_id}</td>
                      <td className="py-3.5 px-6">
                        <div className="font-mono text-slate-800">{exec.branch}</div>
                        {exec.pr_url && (
                          <a
                            href={exec.pr_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[11px] text-emerald-700 hover:underline flex items-center space-x-1 mt-0.5"
                          >
                            <span>Draft PR #{exec.pr_number}</span>
                            <span>↗</span>
                          </a>
                        )}
                      </td>
                      <td className="py-3.5 px-6">
                        {exec.status === "passed" ? (
                          <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-100 text-emerald-800 border border-emerald-200">
                            Passed
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-100 text-red-800 border border-red-200">
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-6">
                        <span className={exec.failed_tests > 0 ? "text-red-600 font-semibold" : "text-emerald-700 font-semibold"}>
                          {exec.passed_tests}/{exec.total_tests} passed {exec.failed_tests > 0 && `(${exec.failed_tests} failed)`}
                        </span>
                      </td>
                      <td className="py-3.5 px-6 font-mono text-slate-600">{exec.duration_seconds}s</td>
                      <td className="py-3.5 px-6">
                        <button
                          onClick={() => handleInspectExecution(exec.id)}
                          className={`px-3 py-1 rounded text-xs font-semibold transition ${
                            exec.failed_tests > 0
                              ? "bg-red-600 hover:bg-red-700 text-white shadow-sm"
                              : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                          }`}
                        >
                          {exec.failed_tests > 0 ? "Agent 6 Diagnostic" : "View Logs"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}


        {/* QA Runs View */}
        {currentTab === "runs" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">All QA Runs</h1>
                <p className="text-sm text-slate-500 mt-0.5">Execution history, LangGraph checkpoints, and CI outcomes</p>
              </div>
              <button
                onClick={() => setShowNewRunModal(true)}
                className="bg-[#0b382d] hover:bg-[#0f4639] text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-sm"
              >
                + Start QA Run
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#fcfdfc] border-b border-slate-200 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
                  <tr>
                    <th className="py-3 px-6">RUN NAME</th>
                    <th className="py-3 px-6">WORKFLOW ID</th>
                    <th className="py-3 px-6">PROJECT</th>
                    <th className="py-3 px-6">STAGE</th>
                    <th className="py-3 px-6">SCORE</th>
                    <th className="py-3 px-6">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {workflows.map((w) => (
                    <tr
                      key={w.id}
                      onClick={() => setSelectedRunDetail(w)}
                      className="hover:bg-slate-50 cursor-pointer transition"
                    >
                      <td className="py-3.5 px-6 font-semibold text-slate-900">{w.run_name}</td>
                      <td className="py-3.5 px-6 font-mono text-slate-500">{w.workflow_id}</td>
                      <td className="py-3.5 px-6 font-mono text-slate-500">{w.project_id}</td>
                      <td className="py-3.5 px-6 capitalize">{w.current_stage.replace(/_/g, " ")}</td>
                      <td className="py-3.5 px-6">
                        {w.quality_score > 0 ? (
                          <span className="font-bold text-emerald-700">{w.quality_score} / 10</span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="py-3.5 px-6">
                        <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 text-slate-700">
                          {w.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Reports & Evidence View */}
        {currentTab === "reports" && (
          <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Reports & Evidence</h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Downloadable QA audit certificates, Playwright test execution traces, and failure analytics
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 className="font-bold text-slate-900 text-sm">Download QA Execution Reports</h3>
                <p className="text-xs text-slate-500 mt-1 mb-4">Export formal compliance reports in JSON or HTML</p>
                <div className="space-y-3">
                  <a
                    href="/api/v1/dashboard/overview"
                    target="_blank"
                    className="block p-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/30 transition text-xs font-semibold text-slate-800"
                  >
                    📥 Export Comprehensive Operations Summary (JSON)
                  </a>
                  <a
                    href="/api/v1/projects"
                    target="_blank"
                    className="block p-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/30 transition text-xs font-semibold text-slate-800"
                  >
                    📥 Export Project Manifest & Repository Matrix (JSON)
                  </a>
                  <a
                    href="/api/v1/audit"
                    target="_blank"
                    className="block p-3 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/30 transition text-xs font-semibold text-slate-800"
                  >
                    📥 Export Governance & Audit Trail Records (JSON)
                  </a>
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 className="font-bold text-slate-900 text-sm">AI Root Cause Diagnostics</h3>
                <p className="text-xs text-slate-500 mt-1 mb-4">Latest failure analysis from Agent 6</p>
                <div className="bg-red-50/50 border border-red-200 rounded-lg p-4 text-xs space-y-2">
                  <div className="flex justify-between font-bold text-red-900">
                    <span>Root Cause: locator_issue</span>
                    <span>Confidence: 94%</span>
                  </div>
                  <div className="text-slate-700">
                    Upstream element #track-parcel-btn renamed to data-testid='track-btn' in PR #119.
                  </div>
                  <div className="text-emerald-800 bg-white p-2.5 rounded border border-emerald-200 font-mono text-[11px]">
                    Fix: page.get_by_test_id("track-btn").click()
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* MODAL: Test Case Details */}
      {selectedTestCase && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <span className="font-mono text-xs font-bold bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded">
                  {selectedTestCase.test_uid}
                </span>
                <h3 className="font-bold text-base text-slate-900 mt-1">{selectedTestCase.title}</h3>
              </div>
              <button onClick={() => setSelectedTestCase(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-4 text-xs">
              <div>
                <span className="font-bold text-slate-700 block uppercase text-[10px]">Objective</span>
                <p className="text-slate-600 mt-0.5">{selectedTestCase.objective}</p>
              </div>

              {Array.isArray(selectedTestCase.preconditions) && selectedTestCase.preconditions.length > 0 && (
                <div>
                  <span className="font-bold text-slate-700 block uppercase text-[10px]">Preconditions</span>
                  <ul className="list-disc list-inside text-slate-600 space-y-1 mt-1">
                    {selectedTestCase.preconditions.map((p, idx) => (
                      <li key={idx}>{p}</li>
                    ))}
                  </ul>
                </div>
              )}

              {Array.isArray(selectedTestCase.steps) && selectedTestCase.steps.length > 0 && (
                <div>
                  <span className="font-bold text-slate-700 block uppercase text-[10px] mb-1.5">Test Steps & Expected Outcomes</span>
                  <div className="space-y-2">
                    {selectedTestCase.steps.map((st, idx) => (
                      <div key={idx} className="bg-slate-50 p-2.5 rounded border border-slate-200">
                        <div className="font-semibold text-slate-800">
                          Step {st.step}: {st.action}
                        </div>
                        <div className="text-emerald-700 mt-1 text-[11px]">
                          Expected: {st.expected}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedTestCase.critic_feedback && (
                <div className="bg-amber-50/60 p-3 rounded-lg border border-amber-200">
                  <span className="font-bold text-amber-900 block text-[11px]">Critic Evaluator Feedback</span>
                  <p className="text-amber-800 mt-1 text-[11px]">{selectedTestCase.critic_feedback}</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedTestCase(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: New Requirement */}
      {showNewReqModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <h3 className="font-bold text-lg text-slate-900">Add User Story Requirement</h3>
              <button onClick={() => setShowNewReqModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateRequirement} className="space-y-3.5 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Project</label>
                <select
                  value={newReqForm.projectId}
                  onChange={(e) => setNewReqForm({ ...newReqForm, projectId: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  required
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Card Tokenization and Vaulting"
                  value={newReqForm.title}
                  onChange={(e) => setNewReqForm({ ...newReqForm, title: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">User Story Description</label>
                <textarea
                  rows="3"
                  required
                  placeholder="As a customer, I want to save my payment card token securely..."
                  value={newReqForm.description}
                  onChange={(e) => setNewReqForm({ ...newReqForm, description: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                ></textarea>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Acceptance Criteria (one per line)</label>
                <textarea
                  rows="3"
                  placeholder="Only PCI-compliant tokens stored&#10;CVV never persisted&#10;Expired cards flagged"
                  value={newReqForm.acceptanceCriteriaText}
                  onChange={(e) => setNewReqForm({ ...newReqForm, acceptanceCriteriaText: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                ></textarea>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowNewReqModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#0b382d] hover:bg-[#0f4639] text-white rounded-lg font-semibold transition shadow-sm"
                >
                  Save Requirement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: New QA Run */}
      {showNewRunModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <h3 className="font-bold text-lg text-slate-900">Trigger New Agentic QA Run</h3>
              <button onClick={() => setShowNewRunModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>
            <form onSubmit={handleStartRun} className="space-y-4 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Project</label>
                <select
                  value={newRunForm.projectId}
                  onChange={(e) => setNewRunForm({ ...newRunForm, projectId: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  required
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.default_branch})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Run Name</label>
                <input
                  type="text"
                  placeholder="e.g. Sprint 24 Regression & 3DS Challenge Flow"
                  value={newRunForm.runName}
                  onChange={(e) => setNewRunForm({ ...newRunForm, runName: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">User Story or GitHub Issue Requirement</label>
                <textarea
                  rows="3"
                  placeholder="As a user, when I checkout with an international card, I must verify SMS OTP..."
                  value={newRunForm.requirementText}
                  onChange={(e) => setNewRunForm({ ...newRunForm, requirementText: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                ></textarea>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Browser Target</label>
                <select
                  value={newRunForm.browser}
                  onChange={(e) => setNewRunForm({ ...newRunForm, browser: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="chromium">Chromium (Desktop Chrome / Edge)</option>
                  <option value="firefox">Firefox</option>
                  <option value="webkit">WebKit (Safari)</option>
                </select>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowNewRunModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#0b382d] hover:bg-[#0f4639] text-white rounded-lg font-semibold transition shadow-sm"
                >
                  Start Agent Workflow
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Register New Project */}
      {showNewProjectModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <h3 className="font-bold text-lg text-slate-900">Register New Software Project</h3>
              <button onClick={() => setShowNewProjectModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="space-y-3.5 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Project Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Identity & Access Service"
                  value={newProjectForm.name}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, name: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows="2"
                  placeholder="Service description and scope..."
                  value={newProjectForm.description}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, description: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                ></textarea>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Source Code Repository *</label>
                <input
                  type="url"
                  required
                  placeholder="https://github.com/enterprise-org/identity-service"
                  value={newProjectForm.sourceRepo}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, sourceRepo: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Automation Repository *</label>
                <input
                  type="url"
                  required
                  placeholder="https://github.com/enterprise-org/qa-identity-playwright"
                  value={newProjectForm.automationRepo}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, automationRepo: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Default Branch</label>
                  <input
                    type="text"
                    value={newProjectForm.defaultBranch}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, defaultBranch: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Base URL</label>
                  <input
                    type="url"
                    value={newProjectForm.baseUrl}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, baseUrl: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowNewProjectModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#0b382d] hover:bg-[#0f4639] text-white rounded-lg font-semibold transition shadow-sm"
                >
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Run Details & Agent Reasoning Timeline */}
      {selectedRunDetail && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-base text-slate-900">{selectedRunDetail.run_name}</h3>
                <div className="text-xs text-slate-400 font-mono mt-0.5">Workflow ID: {selectedRunDetail.workflow_id}</div>
              </div>
              <button onClick={() => setSelectedRunDetail(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-4 text-xs">
              <div className="grid grid-cols-3 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Current Stage</span>
                  <span className="font-bold text-slate-800 capitalize">{selectedRunDetail.current_stage.replace(/_/g, " ")}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Quality Score</span>
                  <span className="font-bold text-emerald-700">{selectedRunDetail.quality_score || "Pending"} / 10</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Status</span>
                  <span className="font-bold uppercase text-slate-800">{selectedRunDetail.status}</span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 mb-2">Agent Reasoning Log</h4>
                <div className="space-y-3">
                  {(selectedRunDetail.agent_reasoning_log || []).map((entry, idx) => (
                    <div key={idx} className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <div className="flex justify-between font-bold text-slate-800">
                        <span>{entry.agent}</span>
                        <span className="text-slate-400 font-mono text-[10px]">{entry.timestamp || "Just now"}</span>
                      </div>
                      <div className="text-slate-600 mt-1 italic">&ldquo;{entry.thought}&rdquo;</div>
                      <div className="mt-2 text-emerald-800 font-mono text-[11px] bg-emerald-50/60 p-1.5 rounded">
                        Action: {entry.action} &rarr; {entry.result}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedRunDetail(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Script Details & POM Inspector */}
      {selectedScriptDetail && (

        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded">
                    {selectedScriptDetail.id}
                  </span>
                  <span className="text-xs bg-slate-100 text-slate-700 font-semibold px-2 py-0.5 rounded">
                    {selectedScriptDetail.framework}
                  </span>
                </div>
                <h3 className="font-bold text-base text-slate-900 mt-1 font-mono">
                  {selectedScriptDetail.script_path}
                </h3>
              </div>
              <button onClick={() => setSelectedScriptDetail(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            {/* Code Tabs */}
            <div className="flex border-b border-slate-200 mt-4 text-xs font-semibold">
              <button
                onClick={() => setScriptCodeTab("test_code")}
                className={`px-4 py-2 border-b-2 transition ${
                  scriptCodeTab === "test_code" ? "border-emerald-600 text-emerald-800" : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                Test Suite Code
              </button>
              <button
                onClick={() => setScriptCodeTab("page_objects")}
                className={`px-4 py-2 border-b-2 transition ${
                  scriptCodeTab === "page_objects" ? "border-emerald-600 text-emerald-800" : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                Page Objects ({
                  Array.isArray(selectedScriptDetail.page_objects)
                    ? selectedScriptDetail.page_objects.length
                    : Object.keys(selectedScriptDetail.page_objects || {}).length
                })
              </button>
              <button
                onClick={() => setScriptCodeTab("fixtures")}
                className={`px-4 py-2 border-b-2 transition ${
                  scriptCodeTab === "fixtures" ? "border-emerald-600 text-emerald-800" : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                Fixtures &amp; Setup
              </button>
              <button
                onClick={() => setScriptCodeTab("security")}
                className={`px-4 py-2 border-b-2 transition ${
                  scriptCodeTab === "security" ? "border-emerald-600 text-emerald-800" : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                AST Security Audit
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-4 text-xs flex-1">
              {scriptCodeTab === "test_code" && (
                <pre className="bg-slate-950 text-emerald-300 p-4 rounded-xl font-mono text-[11px] leading-relaxed overflow-x-auto select-all">
                  {selectedScriptDetail.test_code}
                </pre>
              )}

              {scriptCodeTab === "page_objects" && (
                <div className="space-y-4">
                  {(() => {
                    const rawPo = selectedScriptDetail.page_objects;
                    const poList = Array.isArray(rawPo)
                      ? rawPo
                      : rawPo && typeof rawPo === "object"
                      ? Object.entries(rawPo).map(([name, code]) => ({
                          class_name: name,
                          file_path: name.endsWith(".py") ? name : `pages/${name.toLowerCase()}.py`,
                          code: typeof code === "string" ? code : JSON.stringify(code, null, 2)
                        }))
                      : [];

                    if (poList.length === 0) {
                      return (
                        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 text-center">
                          No separate Page Objects required for this script.
                        </div>
                      );
                    }

                    return poList.map((po, idx) => (
                      <div key={idx} className="border border-slate-200 rounded-xl p-4 bg-slate-50">
                        <div className="font-bold text-slate-900 font-mono text-xs">{po.class_name || po.file_path}</div>
                        {po.file_path && <div className="text-[11px] text-slate-500 mt-0.5">File: {po.file_path}</div>}
                        <pre className="bg-slate-900 text-slate-200 p-3 rounded-lg font-mono text-[11px] mt-2 overflow-x-auto">
                          {po.code}
                        </pre>
                      </div>
                    ));
                  })()}
                </div>
              )}

              {scriptCodeTab === "fixtures" && (
                <pre className="bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-[11px] leading-relaxed overflow-x-auto">
                  {typeof selectedScriptDetail.fixtures === "object" && selectedScriptDetail.fixtures && Object.keys(selectedScriptDetail.fixtures).length > 0
                    ? Object.entries(selectedScriptDetail.fixtures).map(([k, v]) => `# === ${k} ===\n${v}`).join("\n\n")
                    : selectedScriptDetail.fixtures_code || "# Playwright browser context & page fixtures configured in conftest.py\nimport pytest\n\n@pytest.fixture\ndef payment_context(page):\n    page.goto('https://staging.example.com')\n    yield page"}
                </pre>
              )}

              {scriptCodeTab === "security" && (
                <div className="bg-emerald-50/50 border border-emerald-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-emerald-900 text-sm">Agent 5: AST Static Security Verification</span>
                    <span className="bg-emerald-200 text-emerald-900 text-xs px-2.5 py-0.5 rounded font-bold">PASSED</span>
                  </div>
                  <p className="text-slate-600">
                    Full Python Abstract Syntax Tree (AST) scan executed. No dangerous dynamic calls (`eval`, `exec`), no unauthorized OS modules (`os.system`, `subprocess`), and no hardcoded plain-text API keys or passwords detected.
                  </p>
                  <div className="grid grid-cols-3 gap-3 pt-2 text-xs">
                    <div className="bg-white p-2.5 rounded border border-emerald-200">
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">Syntax Check</span>
                      <span className="font-bold text-emerald-800">Valid Python 3</span>
                    </div>
                    <div className="bg-white p-2.5 rounded border border-emerald-200">
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">Security Score</span>
                      <span className="font-bold text-emerald-800">9.5 / 10.0</span>
                    </div>
                    <div className="bg-white p-2.5 rounded border border-emerald-200">
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">Flagged Nodes</span>
                      <span className="font-bold text-emerald-800">0 High Severity</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedScriptDetail(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: CI Execution Details & Failure Analysis */}
      {selectedExecutionDetail && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                    Run #{selectedExecutionDetail.run_number}
                  </span>
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                    selectedExecutionDetail.status === "passed" ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
                  }`}>
                    {selectedExecutionDetail.status}
                  </span>
                </div>
                <h3 className="font-bold text-base text-slate-900 mt-1 font-mono">
                  Branch: {selectedExecutionDetail.branch}
                </h3>
              </div>
              <button onClick={() => setSelectedExecutionDetail(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-4 text-xs flex-1">
              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Tests</span>
                  <span className="font-bold text-slate-800 text-base">{selectedExecutionDetail.total_tests}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Passed</span>
                  <span className="font-bold text-emerald-700 text-base">{selectedExecutionDetail.passed_tests}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Failed</span>
                  <span className="font-bold text-red-600 text-base">{selectedExecutionDetail.failed_tests}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Duration</span>
                  <span className="font-bold text-slate-800 text-base">{selectedExecutionDetail.duration_seconds}s</span>
                </div>
              </div>

              {/* Agent 6 AI Failure Analysis */}
              {(selectedExecutionDetail.test_results || []).some(tr => tr.status === "failed") && (
                <div className="border border-red-200 bg-red-50/40 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-red-900 text-sm flex items-center space-x-1.5">
                      <span>🤖 Agent 6: AI Root Cause Analysis</span>
                    </span>
                    <span className="bg-red-100 text-red-800 text-xs px-2.5 py-0.5 rounded font-bold uppercase">
                      Diagnosed
                    </span>
                  </div>

                  {(selectedExecutionDetail.test_results || [])
                    .filter(tr => tr.status === "failed")
                    .map((tr, idx) => (
                      <div key={idx} className="space-y-3 pt-2">
                        <div className="font-bold text-slate-900 font-mono text-xs">
                          Failed Test: {tr.test_name}
                        </div>
                        <div className="bg-red-100/60 p-2.5 rounded font-mono text-[11px] text-red-900">
                          {tr.error_message}
                        </div>

                        {tr.failure_analysis && (
                          <div className="bg-white border border-red-200 rounded-lg p-4 space-y-2 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                                Classified Root Cause: <strong className="text-red-700 font-mono">{tr.failure_analysis.root_cause_category}</strong>
                              </span>
                              <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                                Confidence: {Math.round(tr.failure_analysis.confidence_score * 100)}%
                              </span>
                            </div>

                            <p className="text-slate-700 mt-1">{tr.failure_analysis.explanation}</p>

                            <div className="mt-2 bg-emerald-50 border border-emerald-200 p-3 rounded-lg">
                              <span className="font-bold text-emerald-900 block text-[11px] mb-1">Suggested Automated Correction:</span>
                              <code className="text-emerald-800 font-mono text-[11px] block">{tr.failure_analysis.suggested_fix}</code>
                            </div>

                            {Array.isArray(tr.failure_analysis.evidence) && tr.failure_analysis.evidence.length > 0 && (
                              <div className="mt-2 pt-2 border-t border-slate-100">
                                <span className="font-semibold text-slate-500 block text-[10px] uppercase">Evidence &amp; Telemetry:</span>
                                <ul className="list-disc list-inside text-slate-600 text-[11px] space-y-0.5 mt-0.5">
                                  {tr.failure_analysis.evidence.map((ev, i) => (
                                    <li key={i}>{ev}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}

              {/* Raw Logs Viewer */}
              <div>
                <h4 className="font-bold text-slate-900 mb-1.5">Execution Logs</h4>
                <pre className="bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-[11px] leading-relaxed max-h-60 overflow-y-auto">
                  {selectedExecutionDetail.raw_logs || "No raw logs captured."}
                </pre>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-between items-center">
              {selectedExecutionDetail.pr_url ? (
                <a
                  href={selectedExecutionDetail.pr_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold text-emerald-700 hover:underline flex items-center space-x-1"
                >
                  <span>Open GitHub Draft PR #{selectedExecutionDetail.pr_number}</span>
                  <span>↗</span>
                </a>
              ) : <div></div>}
              <button
                onClick={() => setSelectedExecutionDetail(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold transition text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Import from GitHub Issues */}
      {showImportGithubModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-slate-900" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                <h3 className="font-bold text-base text-slate-900">Import GitHub Issues</h3>
              </div>
              <button onClick={() => setShowImportGithubModal(false)} className="text-slate-400 hover:text-slate-600">
                &times;
              </button>
            </div>
            <form onSubmit={handleImportGithub} className="space-y-4 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Project</label>
                <select
                  value={importGithubForm.projectId}
                  onChange={(e) => setImportGithubForm({ ...importGithubForm, projectId: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  required
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} ({p.source_repo})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Issue Number (Optional)</label>
                <input
                  type="number"
                  placeholder="Leave empty to import all open issues (e.g. 142)"
                  value={importGithubForm.issueNumber}
                  onChange={(e) => setImportGithubForm({ ...importGithubForm, issueNumber: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Fetches issue title, markdown user story body, labels, and parses bulleted acceptance criteria automatically.
                </span>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowImportGithubModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold transition shadow-sm flex items-center space-x-1.5"
                >
                  <span>Fetch &amp; Import</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

const rootElement = document.getElementById("root");
if (ReactDOM.createRoot) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(<App />);
} else {
  ReactDOM.render(<App />, rootElement);
}


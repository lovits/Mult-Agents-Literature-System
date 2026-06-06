const state = {
  papers: [],
  paperId: null,
  runs: [],
  runId: null,
  workspace: null,
  weaknessId: null,
};

const elements = Object.fromEntries(
  [
    "paper-list",
    "run-list",
    "paper-id",
    "paper-title",
    "run-status",
    "metric-boundary",
    "weakness-list",
    "evidence-list",
    "evidence-count",
    "finding-detail",
    "trace-list",
    "report-button",
    "report-status",
    "refresh-button",
  ].map((id) => [id, document.getElementById(id)]),
);

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const empty = (message) => `<div class="empty-state">${escapeHtml(message)}</div>`;

async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadPapers() {
  elements["paper-list"].innerHTML = empty("正在读取论文...");
  state.papers = await api("/api/papers");
  if (!state.papers.length) {
    elements["paper-list"].innerHTML = empty("尚未导入论文。");
    clearWorkspace();
    return;
  }
  if (!state.paperId || !state.papers.some((paper) => paper.paper_id === state.paperId)) {
    state.paperId = state.papers[0].paper_id;
  }
  renderPapers();
  await loadRuns();
}

function renderPapers() {
  elements["paper-list"].innerHTML = state.papers
    .map(
      (paper) => `
        <button class="nav-item ${paper.paper_id === state.paperId ? "active" : ""}" data-paper-id="${escapeHtml(paper.paper_id)}">
          <strong>${escapeHtml(paper.title)}</strong>
          <span>${escapeHtml(paper.paper_id)}</span>
        </button>`,
    )
    .join("");
  elements["paper-list"].querySelectorAll("[data-paper-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.paperId = button.dataset.paperId;
      state.runId = null;
      renderPapers();
      await loadRuns();
    });
  });
}

async function loadRuns() {
  elements["run-list"].innerHTML = empty("正在读取运行...");
  state.runs = await api(`/api/papers/${encodeURIComponent(state.paperId)}/runs`);
  if (!state.runs.length) {
    elements["run-list"].innerHTML = empty("该论文尚无审计运行。");
    clearWorkspace();
    const paper = state.papers.find((item) => item.paper_id === state.paperId);
    elements["paper-id"].textContent = paper?.paper_id || "";
    elements["paper-title"].textContent = paper?.title || "Paper Workspace";
    return;
  }
  if (!state.runId || !state.runs.some((run) => run.run_id === state.runId)) {
    state.runId = state.runs[0].run_id;
  }
  renderRuns();
  await loadWorkspace();
}

function renderRuns() {
  elements["run-list"].innerHTML = state.runs
    .map(
      (run) => `
        <button class="nav-item ${run.run_id === state.runId ? "active" : ""}" data-run-id="${escapeHtml(run.run_id)}">
          <strong>${escapeHtml(run.status)}</strong>
          <span>${escapeHtml(run.run_id)}</span>
        </button>`,
    )
    .join("");
  elements["run-list"].querySelectorAll("[data-run-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.runId = button.dataset.runId;
      renderRuns();
      await loadWorkspace();
    });
  });
}

async function loadWorkspace() {
  state.workspace = await api(`/api/runs/${encodeURIComponent(state.runId)}/workspace`);
  state.weaknessId =
    state.workspace.ranked_findings[0]?.weakness_id || state.workspace.weaknesses[0]?.weakness_id || null;
  renderWorkspace();
}

function clearWorkspace() {
  state.workspace = null;
  state.weaknessId = null;
  elements["run-status"].textContent = "idle";
  elements["metric-boundary"].textContent = "未选择运行";
  elements["weakness-list"].innerHTML = empty("选择带有审计运行的论文。");
  elements["evidence-list"].innerHTML = empty("暂无证据。");
  elements["finding-detail"].innerHTML = empty("暂无校验结果。");
  elements["trace-list"].innerHTML = "";
  elements["evidence-count"].textContent = "0 blocks";
}

function renderWorkspace() {
  const workspace = state.workspace;
  elements["paper-id"].textContent = workspace.paper.paper_id;
  elements["paper-title"].textContent = workspace.paper.title;
  elements["run-status"].textContent = workspace.run.status;
  elements["run-status"].className = `status-badge status-${workspace.run.status}`;
  elements["metric-boundary"].textContent = workspace.metric_boundary;
  elements["evidence-count"].textContent = `${workspace.evidence_blocks.length} blocks`;
  renderWeaknesses();
  renderFindingDetail();
  renderEvidence();
  renderTrace();
  elements["report-status"].textContent = workspace.reports.length
    ? `${workspace.reports.length} 份已生成报告`
    : "尚未生成报告";
}

function rankedByWeakness(weaknessId) {
  return state.workspace.ranked_findings.find((finding) => finding.weakness_id === weaknessId);
}

function renderWeaknesses() {
  const weaknesses = state.workspace.weaknesses;
  if (!weaknesses.length) {
    elements["weakness-list"].innerHTML = empty("该运行没有弱点输入。");
    return;
  }
  elements["weakness-list"].innerHTML = weaknesses
    .map((weakness) => {
      const ranked = rankedByWeakness(weakness.weakness_id);
      return `
        <button class="weakness-item ${weakness.weakness_id === state.weaknessId ? "active" : ""}" data-weakness-id="${escapeHtml(weakness.weakness_id)}">
          <strong>${escapeHtml(weakness.weakness_text)}</strong>
          <span>${escapeHtml(weakness.category)} · ${escapeHtml(weakness.severity)}${ranked ? ` · rank ${ranked.rank}` : ""}</span>
        </button>`;
    })
    .join("");
  elements["weakness-list"].querySelectorAll("[data-weakness-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.weaknessId = button.dataset.weaknessId;
      renderWeaknesses();
      renderFindingDetail();
      renderEvidence();
    });
  });
}

function renderFindingDetail() {
  if (!state.weaknessId) {
    elements["finding-detail"].innerHTML = empty("选择一个弱点查看校验结果。");
    return;
  }
  const verified = state.workspace.verification[state.weaknessId] || {};
  const ranked = rankedByWeakness(state.weaknessId) || {};
  const retrieval = state.workspace.retrieval[state.weaknessId] || [];
  elements["finding-detail"].innerHTML = `
    <div class="detail-grid">
      <span>Label</span><strong>${escapeHtml(verified.label || "pending")}</strong>
      <span>Support score</span><strong>${Number(verified.support_score || 0).toFixed(4)}</strong>
      <span>Rank</span><strong>${escapeHtml(ranked.rank || "-")}</strong>
      <span>Rank score</span><strong>${Number(ranked.rank_score || 0).toFixed(4)}</strong>
      <span>Retriever candidates</span><strong>${retrieval.length}</strong>
      <span>Verifier</span><strong>${escapeHtml(verified.verifier || "-")}</strong>
      <span>Paper version</span><strong>${escapeHtml(state.workspace.run.paper_version_id || "-")}</strong>
      <span>Evidence source</span><strong>${escapeHtml(state.workspace.run.evidence_source || "-")}</strong>
    </div>
    <p class="muted">${escapeHtml(verified.rationale || "运行完成后显示校验依据。")}</p>`;
}

function renderEvidence() {
  const selectedIds = new Set(state.workspace.verification[state.weaknessId]?.evidence_block_ids || []);
  if (!state.workspace.evidence_blocks.length) {
    elements["evidence-list"].innerHTML = empty("该论文版本没有证据块。");
    return;
  }
  elements["evidence-list"].innerHTML = state.workspace.evidence_blocks
    .map(
      (block) => `
        <article class="evidence-item ${selectedIds.has(block.block_id) ? "selected" : ""}">
          <strong>${escapeHtml(block.section_path)}</strong>
          <span>${escapeHtml(block.section_type)} · ${escapeHtml(block.block_id)}</span>
          <p>${escapeHtml(block.text)}</p>
        </article>`,
    )
    .join("");
}

function renderTrace() {
  elements["trace-list"].innerHTML = state.workspace.trace
    .map((event) => `<li><strong>${escapeHtml(event.event_type)}</strong><br><span>${escapeHtml(event.created_at)}</span></li>`)
    .join("");
}

async function openReport() {
  if (!state.runId) return;
  elements["report-button"].disabled = true;
  elements["report-status"].textContent = "正在生成报告...";
  try {
    let report = state.workspace.reports[0];
    if (!report) {
      report = await api(`/api/runs/${encodeURIComponent(state.runId)}/report`, { method: "POST" });
    }
    window.location.href = `/api/reports/${encodeURIComponent(report.report_id)}/markdown`;
  } catch (error) {
    elements["report-status"].textContent = error.message;
  } finally {
    elements["report-button"].disabled = false;
  }
}

elements["refresh-button"].addEventListener("click", () => loadPapers().catch(showFatal));
elements["report-button"].addEventListener("click", openReport);

function showFatal(error) {
  elements["paper-list"].innerHTML = empty(error.message);
}

loadPapers().catch(showFatal);

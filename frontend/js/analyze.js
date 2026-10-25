// Sends code to /api/analyze and renders the report. Also reopens a saved report via ?report=ID.
Auth.require();
setupNav();

const btn = document.getElementById("find");
const out = document.getElementById("results");
let marks = [];

function clearMarks() { marks.forEach(l => editor.removeLineClass(l, "background", "bug-line")); marks = []; }

function render(r) {
  clearMarks();
  r.bugs.forEach(b => {
    const n = (parseInt(b.line, 10) || 0) - 1;
    if (n >= 0 && n < editor.lineCount()) { editor.addLineClass(n, "background", "bug-line"); marks.push(n); }
  });
  if (MODES[r.language]) { langSelect.value = r.language; setMode(r.language); }

  const m = r.requirements_match;
  const LABEL = { matches: "Code matches the problem statement", partial: "Code partly matches the problem statement", does_not_match: "Code does not match the problem statement" };
  const matchHtml = m && LABEL[m.verdict] ? `
    <div class="match">
      <h3><span class="badge ${esc(m.verdict)}">${esc(m.verdict.replace(/_/g, " "))}</span> ${esc(LABEL[m.verdict])}</h3>
      <p>${esc(m.summary)}</p>
      <ul class="checks">${(m.checks || []).map(c => `
        <li><span class="mark ${c.met ? "yes" : "no"}">${c.met ? "&#10003;" : "&#10007;"}</span>
        <span>${esc(c.requirement)}<small>${esc(c.note)}</small></span></li>`).join("")}</ul>
    </div>` : "";

  const bugs = r.bugs.map(b => `
    <div class="bug" data-line="${esc(b.line)}">
      <h3>${esc(b.title)}</h3>
      <div class="meta">
        <span class="badge ${esc(b.severity)}">${esc(b.severity)}</span>
        <span class="badge type">${esc(b.type)}</span>
        ${b.line ? `<span>Line ${esc(b.line)}</span>` : ""}
      </div>
      <p>${esc(b.explanation)}</p>
      <div class="fix"><strong>Fix:</strong> ${esc(b.fix)}</div>
    </div>`).join("");

  out.innerHTML = `
    <div class="summary">
      <span class="badge ${esc(r.overall_severity)}">${esc(r.overall_severity)}</span>
      <p><strong>${esc(r.language)}</strong>: ${r.bugs.length ? r.bugs.length + " issue(s) found. " : "No bugs found. "}${esc(r.summary)}</p>
    </div>
    ${matchHtml}
    ${bugs}
    <div class="corrected">
      <h3>Corrected code <button class="btn ghost" id="copy" type="button">Copy</button></h3>
      <pre>${esc(r.corrected_code)}</pre>
    </div>`;

  out.querySelectorAll(".bug[data-line]").forEach(el => el.onclick = () => {
    const n = parseInt(el.dataset.line, 10) - 1;
    if (n >= 0) { editor.setCursor(n, 0); editor.scrollIntoView({ line: n, ch: 0 }, 80); editor.focus(); }
  });
  document.getElementById("copy").onclick = e => {
    navigator.clipboard.writeText(r.corrected_code);
    e.target.textContent = "Copied";
  };
}

btn.addEventListener("click", async () => {
  const code = editor.getValue();
  if (!code.trim()) { out.innerHTML = `<div class="err">Paste or upload some code first.</div>`; return; }
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Analysing...`;
  try {
    render(await api("/analyze", { method: "POST", body: { code, language: langSelect.value, problem_statement: document.getElementById("problem").value } }));
  } catch (err) {
    out.innerHTML = `<div class="err">${esc(err.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "Find bugs";
  }
});

const reportId = new URLSearchParams(location.search).get("report");
if (reportId) {
  api("/history/" + encodeURIComponent(reportId)).then(r => {
    editor.setValue(r.code);
    document.getElementById("problem").value = r.problem_statement || "";
    r.overall_severity = r.severity; r.summary = "";
    render(r);
  }).catch(err => { out.innerHTML = `<div class="err">${esc(err.message)}</div>`; });
}

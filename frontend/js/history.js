Auth.require();
setupNav();

const list = document.getElementById("list");
const search = document.getElementById("search");

async function load() {
  try {
    const { reports } = await api("/history?q=" + encodeURIComponent(search.value.trim()));
    if (!reports.length) {
      list.innerHTML = `<div class="empty">No reports yet. <a href="dashboard.html">Analyse some code</a> and it will show up here.</div>`;
      return;
    }
    list.innerHTML = reports.map(r => `
      <div class="item">
        <div class="info">
          <strong>${esc(r.language || "Unknown")} <span class="badge ${esc(r.severity)}">${esc(r.severity)}</span> ${r.bug_count} issue(s)</strong>
          <code>${esc(r.preview)}</code>
        </div>
        <time>${esc(r.created_at)}</time>
        <a class="btn ghost" href="dashboard.html?report=${r.id}">Open</a>
        <button class="btn danger" data-id="${r.id}" type="button">Delete</button>
      </div>`).join("");
  } catch (err) {
    list.innerHTML = `<div class="err">${esc(err.message)}</div>`;
  }
}

list.addEventListener("click", async e => {
  const id = e.target.dataset.id;
  if (!id || !confirm("Delete this report?")) return;
  try { await api("/history/" + id, { method: "DELETE" }); load(); } catch (err) { alert(err.message); }
});

let t;
search.addEventListener("input", () => { clearTimeout(t); t = setTimeout(load, 250); });
load();

// Shared helpers: API calls, token storage, page guards.
const API = "/api"; // change to "http://localhost:5000/api" if the frontend is hosted separately

const Auth = {
  token: () => localStorage.getItem("bz_token"),
  user: () => localStorage.getItem("bz_user"),
  save(token, username) { localStorage.setItem("bz_token", token); localStorage.setItem("bz_user", username); },
  logout() { localStorage.removeItem("bz_token"); localStorage.removeItem("bz_user"); location.href = "login.html"; },
  require() { if (!Auth.token()) location.href = "login.html"; },
};

async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (Auth.token()) headers.Authorization = "Bearer " + Auth.token();
  let res;
  try {
    res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && Auth.token()) Auth.logout();
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function setupNav() {
  const el = document.getElementById("nav-user");
  if (el) el.innerHTML = `<span>${esc(Auth.user())}</span> <a href="#" id="logout">Log out</a>`;
  const out = document.getElementById("logout");
  if (out) out.onclick = e => { e.preventDefault(); Auth.logout(); };
}

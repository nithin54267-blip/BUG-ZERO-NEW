// Handles the login and register forms.
if (Auth.token()) location.href = "dashboard.html";

const form = document.getElementById("auth-form");
const msg = document.getElementById("msg");
const isRegister = form.dataset.mode === "register";

form.addEventListener("submit", async e => {
  e.preventDefault();
  msg.textContent = "";
  const btn = form.querySelector("button");
  btn.disabled = true;
  const f = Object.fromEntries(new FormData(form));
  try {
    const data = await api(isRegister ? "/register" : "/login", { method: "POST", body: f });
    Auth.save(data.token, data.username);
    location.href = "dashboard.html";
  } catch (err) {
    msg.textContent = err.message;
    btn.disabled = false;
  }
});

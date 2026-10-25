"""Checks the BUG-ZERO code against the problem statement.
Run from the project root:  python tests/check_requirements.py
The LLM call is replaced by a fake, so no API key or internet is needed."""
import os, re, sqlite3, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from config import Config
Config.DATABASE_PATH = os.path.join(tempfile.mkdtemp(), "test.db")
import routes.analyze_routes as ar
from services import llm_service

FAKE = {"language": "Python", "summary": "One crash risk.", "overall_severity": "high",
        "bugs": [{"line": 5, "type": "runtime", "severity": "high", "title": "Division by zero",
                  "explanation": "len(nums) can be 0.", "fix": "Check for an empty list."}],
        "corrected_code": "def f(n):\n    return 0 if not n else sum(n)/len(n)"}
def fake_analyze(code, hint=None, problem_statement=None):
    rep = dict(FAKE)
    rep["requirements_match"] = ({"verdict": "partial", "summary": "Empty list not handled.", "checks": [
        {"requirement": "Return 0 for an empty list", "met": False, "note": "Divides by len(nums)."}]}
        if problem_statement else {"verdict": "not_provided", "summary": "", "checks": []})
    return rep
ar.analyze_code = fake_analyze

from app import create_app
c = create_app().test_client()
results = []

def check(req, ok):
    results.append((req, bool(ok)))
    print(("PASS  " if ok else "FAIL  ") + req)

def hdr(t): return {"Authorization": "Bearer " + t}
def read(*p): return open(os.path.join(ROOT, *p), encoding="utf-8").read()

# --- Folder structure and architecture ---
needed = ["frontend/index.html", "frontend/login.html", "frontend/register.html", "frontend/dashboard.html",
          "frontend/history.html", "frontend/css/style.css", "frontend/css/dashboard.css",
          "frontend/js/auth.js", "frontend/js/editor.js", "frontend/js/analyze.js", "frontend/js/history.js",
          "frontend/assets", "backend/app.py", "backend/config.py", "backend/requirements.txt",
          "backend/routes/auth_routes.py", "backend/routes/analyze_routes.py", "backend/routes/history_routes.py",
          "backend/services/llm_service.py", "backend/middleware/auth_middleware.py", "backend/models/db.py",
          "backend/utils/helpers.py", "database/schema.sql", "database/sample_data.sql",
          "docs/problem_statement.md", ".env.example", "README.md"]
missing = [p for p in needed if not os.path.exists(os.path.join(ROOT, p))]
check("Folder structure matches the problem statement" + (f" (missing: {missing})" if missing else ""), not missing)
check("Separate frontend and backend (modular architecture)", os.path.isdir(os.path.join(ROOT, "frontend")) and os.path.isdir(os.path.join(ROOT, "backend")))

# --- Authentication ---
r = c.post("/api/register", json={"username": "alice", "email": "a@x.com", "password": "password123"})
tok = r.get_json().get("token")
check("Registration works and returns a JWT", r.status_code == 201 and tok)
check("Duplicate registration is rejected", c.post("/api/register", json={"username": "alice", "email": "a@x.com", "password": "password123"}).status_code == 409)
check("Weak password / bad email are rejected", c.post("/api/register", json={"username": "bob", "email": "bad", "password": "1"}).status_code == 400)
row = sqlite3.connect(Config.DATABASE_PATH).execute("select password_hash from users").fetchone()[0]
check("Passwords are stored hashed, not as plain text", row != "password123" and ":" in row)
check("Login with correct password returns a JWT", c.post("/api/login", json={"identifier": "alice", "password": "password123"}).get_json().get("token"))
check("Login with wrong password is rejected", c.post("/api/login", json={"identifier": "alice", "password": "wrong"}).status_code == 401)
check("Protected routes reject requests without a token", all(
    c.open(u, method=m).status_code == 401 for u, m in [("/api/analyze", "POST"), ("/api/history", "GET"), ("/api/history/1", "DELETE")]))
check("Logout exists in the interface", "logout" in read("frontend/js/api.js") and "nav-user" in read("frontend/dashboard.html"))

# --- Analysis ---
check("Empty code is rejected", c.post("/api/analyze", json={"code": "  "}, headers=hdr(tok)).status_code == 400)
check("Oversized code is rejected", c.post("/api/analyze", json={"code": "x" * (Config.MAX_CODE_CHARS + 1)}, headers=hdr(tok)).status_code == 413)
rep = c.post("/api/analyze", json={"code": "print(x)"}, headers=hdr(tok)).get_json()
bug = (rep.get("bugs") or [{}])[0]
check("Report has bug location (line) and type", "line" in bug and bug.get("type") in
      ("syntax", "logical", "runtime", "security", "performance"))
check("Report has plain-language explanation and fix per bug", bug.get("explanation") and bug.get("fix"))
check("Report has severity per issue and overall", bug.get("severity") and rep.get("overall_severity"))
check("Report has corrected code", rep.get("corrected_code"))
check("Language is auto-detected / reported", rep.get("language"))
p = llm_service.SYSTEM_PROMPT.lower()
check("LLM prompt covers syntax, logical, runtime, security, performance",
      all(w in p for w in ["syntax", "logical", "runtime", "security", "performance"]))
src = "".join(read("backend", d, f) for d in ["routes", "services"]
              for f in os.listdir(os.path.join(ROOT, "backend", d)) if f.endswith(".py"))
check("Code is never executed on the server (out of scope)", not re.search(r"\b(exec|eval|subprocess|os\.system)\(", src))

# --- Database and history ---
con = sqlite3.connect(Config.DATABASE_PATH)
cols_u = [x[1] for x in con.execute("pragma table_info(users)")]
cols_r = [x[1] for x in con.execute("pragma table_info(reports)")]
check("users table has the designed columns", cols_u == ["id", "username", "email", "password_hash", "created_at"])
check("reports table has the designed columns", {"id", "user_id", "language", "code", "bugs_json", "corrected_code", "severity", "created_at"} <= set(cols_r)
      and {"problem_statement", "match_json"} <= set(cols_r))
check("Each analysis is saved in the SQL database", con.execute("select count(*) from reports").fetchone()[0] == 1)

# --- Problem statement check ---
PS = "Return the average of a list. Return 0 for an empty list."
rep2 = c.post("/api/analyze", json={"code": "print(x)", "problem_statement": PS}, headers=hdr(tok)).get_json()
rm = rep2.get("requirements_match", {})
check("Problem statement + code returns a verdict and per-requirement checks",
      rm.get("verdict") in ("matches", "partial", "does_not_match") and rm.get("checks")
      and {"requirement", "met", "note"} <= set(rm["checks"][0]))
check("Report without a problem statement says verdict not_provided", rep.get("requirements_match", {}).get("verdict") == "not_provided")
check("Oversized problem statement is rejected", c.post("/api/analyze", json={"code": "x=1", "problem_statement": "p" * (Config.MAX_PROBLEM_CHARS + 1)}, headers=hdr(tok)).status_code == 413)
saved = c.get(f"/api/history/{rep2['id']}", headers=hdr(tok)).get_json()
check("Problem statement and match result are saved and reopened from history",
      saved.get("problem_statement") == PS and saved.get("requirements_match", {}).get("checks"))
c.delete(f"/api/history/{rep2['id']}", headers=hdr(tok))

class _Resp:
    status_code = 200
    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": '{"language":"Python","bugs":[{"line":1,"type":"logical","severity":"high","title":"t","explanation":"e","fix":"f"}],"corrected_code":"x"}'}]}}]}
sent = {}
def fake_post(url, headers=None, json=None, timeout=None):
    sent["body"] = json
    return _Resp()
Config.GEMINI_API_KEY = "test"
llm_service.requests.post = fake_post
out = llm_service.analyze_code("print(1)", None, PS)
text = sent["body"]["contents"][0]["parts"][0]["text"]
check("Problem statement is sent to the LLM together with the code", "<problem_statement>" in text and PS in text and "print(1)" in text)
check("LLM prompt tells the model to check every requirement and fix the code to meet it",
      "requirement" in llm_service.SYSTEM_PROMPT.lower() and "satisfy every requirement" in llm_service.SYSTEM_PROMPT)
check("Missing match data from the LLM still gives a safe verdict structure", out["requirements_match"]["verdict"] and "checks" in out["requirements_match"])

# Older database (created before this feature) is upgraded automatically
import models.db as dbm
old = os.path.join(tempfile.mkdtemp(), "old.db"); keep = Config.DATABASE_PATH
sqlite3.connect(old).executescript("create table users(id integer primary key, username text, email text, password_hash text, created_at text);"
    "create table reports(id integer primary key, user_id integer, language text, code text, bugs_json text, corrected_code text, severity text, created_at text);")
Config.DATABASE_PATH = old; dbm.init_db()
upgraded = {x[1] for x in sqlite3.connect(old).execute("pragma table_info(reports)")}
Config.DATABASE_PATH = keep
check("Existing databases are upgraded automatically (no manual migration)", {"problem_statement", "match_json"} <= upgraded)
h = c.get("/api/history", headers=hdr(tok)).get_json()["reports"]
check("History lists the user's past reports", len(h) == 1)
check("History search works", len(c.get("/api/history?q=python", headers=hdr(tok)).get_json()["reports"]) == 1
      and len(c.get("/api/history?q=zzzz", headers=hdr(tok)).get_json()["reports"]) == 0)
check("A saved report can be reopened with bugs and corrected code",
      c.get(f"/api/history/{h[0]['id']}", headers=hdr(tok)).get_json().get("bugs"))
tok2 = c.post("/api/register", json={"username": "carol", "email": "c@x.com", "password": "password123"}).get_json()["token"]
check("Users cannot see or delete each other's reports",
      c.get("/api/history", headers=hdr(tok2)).get_json()["reports"] == []
      and c.delete(f"/api/history/{h[0]['id']}", headers=hdr(tok2)).status_code == 404)
check("User can delete their own report", c.delete(f"/api/history/{h[0]['id']}", headers=hdr(tok)).status_code == 200
      and c.get("/api/history", headers=hdr(tok)).get_json()["reports"] == [])

# --- Frontend features ---
ed, dash = read("frontend/js/editor.js"), read("frontend/dashboard.html")
check("Code editor with line numbers and syntax highlighting (CodeMirror)", "lineNumbers: true" in ed and "codemirror" in dash.lower())
check("File upload supported", 'type="file"' in dash and "FileReader" in ed)
block = re.search(r"const MODES = \{(.*?)\};", ed, re.S).group(1)
names = set(re.findall(r'"([^"]+)":|(?<![\w"])(\w+):', block) and [a or b for a, b in re.findall(r'"([^"]+)":|(?<![\w"])(\w+):', block)])
check("Editor offers Python, Java, C, C++, JavaScript, PHP, SQL", {"Python", "Java", "C", "C++", "JavaScript", "PHP", "SQL"} <= names)
check("Auto language detection option present", "Auto-detect" in dash)
check("Results panel shows explanation, severity and corrected code", all(k in read("frontend/js/analyze.js") for k in ["explanation", "severity", "corrected_code"]))
check("Dashboard has a problem statement box and shows the match verdict", 'id="problem"' in dash and "requirements_match" in read("frontend/js/analyze.js"))
check("History page has search and delete", "search" in read("frontend/history.html") and "DELETE" in read("frontend/js/history.js"))
check("Responsive layout (media queries)", "@media" in read("frontend/css/dashboard.css"))
check("Pages require login (dashboard and history)", "Auth.require()" in read("frontend/js/analyze.js") and "Auth.require()" in read("frontend/js/history.js"))
check("Secrets are kept out of Git (.env ignored)", ".env" in read(".gitignore").split())

failed = [r for r, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} requirements satisfied")
sys.exit(1 if failed else 0)

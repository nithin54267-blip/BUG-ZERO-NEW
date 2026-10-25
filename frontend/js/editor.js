// CodeMirror setup, language modes and file upload.
const MODES = {
  Python: "python", Java: "text/x-java", C: "text/x-csrc", "C++": "text/x-c++src", "C#": "text/x-csharp",
  JavaScript: "javascript", TypeScript: "text/typescript", PHP: "application/x-httpd-php", SQL: "text/x-sql",
  HTML: "htmlmixed", CSS: "css", Go: "go", Rust: "rust", Ruby: "ruby", Kotlin: "text/x-kotlin",
};
const EXT = { py: "Python", java: "Java", c: "C", cpp: "C++", cc: "C++", cs: "C#", js: "JavaScript", ts: "TypeScript",
  php: "PHP", sql: "SQL", html: "HTML", css: "CSS", go: "Go", rs: "Rust", rb: "Ruby", kt: "Kotlin" };

const editor = CodeMirror(document.getElementById("editor"), {
  value: "", lineNumbers: true, indentUnit: 4, lineWrapping: false, mode: "python",
  placeholder: "Paste your code here, or upload a file...",
});

const langSelect = document.getElementById("language");
Object.keys(MODES).forEach(l => langSelect.add(new Option(l, l)));

function setMode(lang) { editor.setOption("mode", MODES[lang] || null); }
langSelect.addEventListener("change", () => setMode(langSelect.value));

document.getElementById("file").addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    editor.setValue(String(reader.result));
    const lang = EXT[file.name.split(".").pop().toLowerCase()];
    if (lang) { langSelect.value = lang; setMode(lang); }
  };
  reader.readAsText(file);
  e.target.value = "";
});

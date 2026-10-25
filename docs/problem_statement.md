# BUG-ZERO: AI-Powered Code Bug Finder

## Problem Statement
Software bugs are among the most common and costly problems in software development. Developers, and especially students and beginners, spend a large share of their time manually reading code, running it repeatedly, and searching the internet to find the cause of errors. This process is slow and frustrating, and it often misses logical errors, security flaws, and bad coding practices that do not produce an obvious error message.

Existing tools have clear limitations:
- **Language-specific:** Most linters and debuggers work for only one language (for example, Pylint for Python or ESLint for JavaScript), so developers need many tools to work across languages.
- **Rule-based:** Traditional static analysers catch only predefined patterns and cannot understand the intent or context of the code.
- **Poor explanations:** Compiler errors are often cryptic and do not explain why the bug occurred or how to fix it.
- **No history:** Users cannot easily save, revisit, or track the bugs they have found and fixed over time.
- **No personalised access:** Most free tools do not offer user accounts or a saved workspace.

There is a need for a single, intelligent, easy-to-use platform that can analyse code in any programming language, identify bugs, explain them in plain language, and suggest corrected code.

## Proposed Solution
BUG-ZERO is an interactive web-based application that uses a Large Language Model (LLM) through an API to detect bugs in source code written in any programming language. Users sign in securely, paste or upload their code, and receive an instant analysis that includes:
- the location and type of each bug (syntax, logical, runtime, security, performance)
- a simple explanation of why it occurs
- a corrected version of the code
- a severity level for each issue

All analyses are stored in an SQL database so users can review their history at any time.

## Objectives
1. Build a bug detection system that supports multiple programming languages (Python, Java, C, C++, JavaScript, PHP, SQL, and more) using an LLM API.
2. Provide a secure registration and login system with user authentication.
3. Design an interactive, professional interface with a code editor, syntax highlighting, and a clear results panel.
4. Store user details, submitted code, and bug reports in an SQL database.
5. Give clear explanations and suggested fixes, not just error messages.
6. Follow a clean, modular architecture with a separate frontend and backend.

## Scope
**In scope:** user registration, login and logout; code input through an editor or file upload; automatic language detection and AI-based bug analysis; bug report with explanation, severity and corrected code; history of past analyses per user; responsive, interactive user interface.

**Out of scope (initially):** running or compiling the code on the server; real-time collaborative editing; automatic fixing of entire large projects or repositories.

## Key Features
| Feature | Description |
|---|---|
| Secure authentication | Register and log in with password hashing and token-based sessions |
| Multi-language support | Works for any programming language through the LLM |
| Interactive code editor | Syntax highlighting, line numbers, and file upload |
| AI bug analysis | Detects syntax, logical, security, and performance issues |
| Explanation and fix | Plain-language reason plus corrected code |
| History dashboard | View, search, and delete earlier bug reports |

## Technology Stack
| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript (CodeMirror via CDN) | Login page, code editor page, results panel, history page |
| Backend | Python (Flask) | REST API, authentication, LLM integration |
| Database | SQL (SQLite for development, MySQL for deployment) | Stores users, submitted code, and bug reports |
| AI/LLM | LLM API (Google Gemini in this build) | Analyses code and returns bugs, explanations, and fixes |
| Authentication | JWT with password hashing (werkzeug) | Secure login and sessions |

## Database Design
- **users:** id, username, email, password_hash, created_at
- **reports:** id, user_id (foreign key), language, code, bugs_json, corrected_code, severity, created_at

## System Workflow
1. The user registers or logs in on the HTML pages, and JavaScript sends the details to the Flask API.
2. The backend verifies the password and returns a JWT token.
3. The user pastes code into the editor and clicks Find bugs.
4. analyze.js sends the code and token to the /analyze endpoint.
5. The backend sends the code to the LLM API with a structured prompt and receives the bug report.
6. The report is saved in the SQL database and displayed in the results panel.
7. The user can open the history page to view or delete earlier reports.

## Expected Outcome
BUG-ZERO will reduce the time developers and students spend on debugging, improve code quality, and help users learn from their mistakes through clear explanations. It brings multi-language bug detection, AI-driven fix suggestions, and secure personal history into one easy-to-use platform.

# 📜 Team Development Rules & Operating Guidelines (`Rule.md`)

All team members (Vikash, Krishna, Harshit) and AI assistants working on the **Cyclone Risk Assessment & Action Engine** project must strictly adhere to these rules.

---

## 🚫 Rule 1: No Unauthorized Git/GitHub Pushes
- **Never push code directly to the remote repository (GitHub)** without explicit permission from the project lead / team.
- Always work on dedicated feature branches (e.g., `feature/gee-pipeline`, `feature/risk-engine`, `feature/react-map`).
- Code must be reviewed, tested locally, and explicitly approved before opening a Pull Request or pushing to `main` / `master`.

---

## 🧠 Rule 2: Strict "Analyze $\rightarrow$ Plan $\rightarrow$ Approve $\rightarrow$ Code $\rightarrow$ Test" Workflow
1. **Thorough Analysis First**: Before writing any code, understand the problem, identify dependencies, and verify API data formats.
2. **Implementation Plan & Approval**:
   - Write out a clear plan describing what files will be created/modified and what the expected behavior is.
   - **Do NOT start generating or modifying code until the plan is reviewed and approved (or when the user clicks "Proceed").**
3. **Execute & Code**: Implement clean, well-structured, modular code matching the approved plan.
4. **Mandatory Testing & Bug Fixing**:
   - Test every function, endpoint, or UI component locally.
   - Reproduce and fix any bugs immediately before marking the task complete.
   - Never leave broken builds, missing dependencies, or unhandled exceptions.

---

## 🛡️ Rule 3: Respect Code Ownership & Boundary Protocol
- **Strict Domain Ownership**:
  - **🧑‍💻 Vikash**: `geospatial_ai/` (Cyclone feeds, Weather APIs, GEE scripts, Gemini AI prompts/multimodal reasoning).
  - **🧑‍💻 Krishna**: `backend/` (FastAPI routes, PostGIS schemas, Risk calculation engine, Action trigger engine).
  - **🧑‍💻 Harshit**: `frontend/` (React components, Mapbox/GIS layers, state management, Dashboard UI).

- **No Unauthorized Modifications to Other Domains**:
  - Do **NOT** modify or overwrite another developer's codebase (e.g., frontend developer altering backend models, or backend developer modifying GEE scripts).
  - **Sync & Agreement Protocol**: If a feature requires changes to another domain (e.g., modifying an API response schema or adding a new database field):
    1. **Notify and discuss with that developer first**.
    2. Agree on the updated contract / schema together.
    3. The owner of that domain will make the update, or grant explicit approval for the change.

---

## 📋 Quick Reference Checklist

| Step | Action Required | Status Check |
| :--- | :--- | :--- |
| **Before Starting** | Analyze problem & write implementation plan | ⏸️ Wait for user approval / "Proceed" |
| **During Coding** | Respect domain ownership (`geospatial_ai`, `backend`, `frontend`) | 🔒 Do not alter others' files without sync |
| **After Coding** | Run local tests & resolve all bugs | 🧪 Must pass all checks |
| **Before Pushing** | Ask for permission before running any `git push` to GitHub | 🛑 Explicit permission required |

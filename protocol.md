# 📑 Master Project Protocol (`protocol.md`)

This document serves as the **Master Governance Protocol** for the **Cyclone Risk Assessment & Action Engine** project. Every team member (**Vikash**, **Krishna**, **Harshit**) and any AI coding assistant **MUST strictly follow and enforce all project markdown files**.

---

## 🏛️ Documentation Hierarchy & Relationship

```
                          ┌───────────────────────────┐
                          │       protocol.md         │
                          │ (Master Project Protocol) │
                          └─────────────┬─────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
  ┌───────────────┐              ┌───────────────┐              ┌───────────────┐
  │    Rule.md    │              │    days.md    │              │ IMPLEMENTATION│
  │ (Team Rules & │              │  (3-Day Task  │              │   _PLAN.md    │
  │  Boundaries)  │              │  Checklists)  │              │ (Tech & APIs) │
  └───────────────┘              └───────────────┘              └───────────────┘
```

| Document | Primary Purpose | Authority Level |
| :--- | :--- | :---: |
| **`protocol.md`** | Master operational protocol enforcing all project workflows | **Supreme** |
| **`Rule.md`** | Strict rules on Git permissions, approval gates, and code boundaries | **Mandatory** |
| **`days.md`** | 3-Day day-by-day deliverables, tasks, and sync schedule | **Mandatory** |
| **`IMPLEMENTATION_PLAN.md`** | Technical architecture, API contracts, GEE pipelines & algorithms | **Mandatory** |
| **`README.md`** | Project overview and quick reference | **Informational** |

---

## 🔒 Mandatory Protocols to Follow

### Protocol 1: Plan-Before-Execution (Approval Gate Protocol)
> *(Enforcing Rule #2 from `Rule.md`)*
1. **Analyze First**: For any new feature, bug fix, or modification, review existing code and dependencies.
2. **Present Plan**: Document what will change, which files will be created/modified, and expected outcomes.
3. **Approval Gate**: **No source code may be written, generated, or modified until explicit user approval (or clicking "Proceed") is received.**
4. **Build & Verify**: Once approved, implement the code, run local verification, and fix any emerging issues immediately.

---

### Protocol 2: Code Domain Boundary Protocol
> *(Enforcing Rule #3 from `Rule.md`)*
- Work strictly inside your assigned domain:
  - **🧑‍💻 Vikash**: `geospatial_ai/` *(Weather feeds, GEE scripts, Gemini AI prompts)*
  - **🧑‍💻 Krishna**: `backend/` *(FastAPI routes, PostGIS schemas, Risk/Action Engine)*
  - **🧑‍💻 Harshit**: `frontend/` *(React components, Mapbox GIS layers, Dashboard UI)*
- **Cross-Domain Sync**: If a feature requires changes outside your domain (e.g., frontend requests a new field in the backend API response):
  1. Notify the domain owner first.
  2. Agree on the updated data schema in `IMPLEMENTATION_PLAN.md`.
  3. The domain owner implements the change, or gives explicit permission.

---

### Protocol 3: Daily Sprint Execution Protocol
> *(Enforcing Schedule & Deliverables from `days.md`)*
- Every team member must track their daily tasks against `days.md`:
  - **Day 1 Goal**: Ingest cyclone/weather data + build FastAPI mock APIs + initialize React base map.
  - **Day 2 Goal**: GEE SAR flood tile generation + Risk & Action engine calculations + interactive Mapbox layers.
  - **Day 3 Goal**: Gemini multimodal reasoning + WebSocket live alerts + Action triage checklist + complete live demo.
- Attend the 3 daily check-ins:
  - **09:30 AM**: Morning Standup (Blockers & Goals)
  - **02:00 PM**: Midday API/Contract Check
  - **07:00 PM**: Evening Code Integration & Test

---

### Protocol 4: Definition of Done (DoD) & Testing Protocol
A task or feature is considered **DONE** only when:
1. Code is clean, modular, and well-commented.
2. Local tests have passed (endpoints return valid HTTP 200 responses; frontend renders without console errors; GEE scripts return valid image/tile URLs).
3. All edge cases and bugs identified during testing are resolved.
4. The corresponding task in `days.md` is marked as completed (`[x]`).

---

### Protocol 5: Git & GitHub Safety Protocol
> *(Enforcing Rule #1 from `Rule.md`)*
- **Zero unapproved pushes**: Never execute `git push` to the remote GitHub repository without prior user/team review and approval.
- Keep all local commits atomic, well-described, and linked to the active task.

---

## ⚡ Conflict Resolution & Protocol Violations
- If any discrepancy arises between code and documentation, **`protocol.md`** and **`Rule.md`** take precedence.
- Updates to any `.md` file must be reviewed and agreed upon by all three team members.

# Git Commit Suggestions

This file tracks suggested commits for manual review and execution by the user.

---

## Commit 1: Update CLAUDE.md for MVP specifications

**Files changed:**
- `CLAUDE.md`

**Type:** docs

**Description:**
Comprehensive rewrite of CLAUDE.md to align with MVP requirements:
- Add "Simplicity First" constraint (no auth, no error handling)
- Update data model from 4 tables to 3 tables (Tag, Post, MediaAsset)
- Remove PostTag junction table, use direct foreign keys
- Add detailed seed data section with 3 specific test cases
- Add conditional rendering logic with Jinja2 examples
- Update project structure to show current state + MVP changes
- Add testing checklist for verifying 3 test cases
- Clarify Git workflow (suggest commits, don't make them)
- Add comprehensive sections: Routes, Templates, UI Patterns, Dependencies
- Update commands to use `uv` package manager
- Add Markdown processing section
- Add development workflow with step-by-step guide

**Why:**
The previous CLAUDE.md had incorrect data model (4 tables vs 3), missing MVP constraints, and didn't reflect the actual project structure. This rewrite provides a complete guide for implementing the simplified MVP.

---

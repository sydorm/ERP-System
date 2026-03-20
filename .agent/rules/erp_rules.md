# ERP Development Rules

This document outlines the core development principles for our ERP system.

## 1. Directory Structure
- `backend/app/models`: SQLAlchemy models.
- `backend/app/schemas`: Pydantic schemas (Base, Create, Update, Response patterns).
- `backend/app/api`: FastAPI route modules.
- `frontend/src/views`: Page components.
- `frontend/src/components`: Reusable UI elements.

## 2. Backend Standards
- Always use `gen_random_uuid()` for primary keys in migrations.
- Always include `created_at` and `updated_at` in shared `BaseModel`.
- Relationships must use `cascade="all, delete-orphan"` where appropriate.
- API endpoints must return Pydantic schemas, never raw SQLAlchemy models.

## 3. Frontend Standards
- Use Vue 3 `<script setup>` with Composition API.
- Prefer Element Plus components for consistency.
- All API calls must go through the `@/api` axios instance.
- Avoid deep prop drilling; use Pinia for global state or `v-model` for components.

## 4. Database Migrations
- Every change to `app/models` must be accompanied by an Alembic migration in `backend/alembic/versions`.
- Migrations must have unique IDs and proper `down_revision`.

## 5. Security
- Never expose sensitive fields (like password hashes) in `Response` schemas.
- Use the `get_current_user` dependency for any protected route.
- Company isolation: Always filter queries by `company_id`.

## 6. AI Agent Collaboration (Antigravity)
- **Rules**: If you want me to follow specific coding patterns, add them to this file (`.agent/rules/erp_rules.md`).
- **Workflows**: For repetitive tasks (like deployments), describe them in `.agent/workflows/filename.md`. Use the `/filename` command to trigger them.
- **Context**: I always read these files before starting a task, so updating them is the fastest way to "upgrade" my knowledge for this project.
- **Feedback**: If I make a mistake, tell me directly, and I will update these rules to prevent it in the future.

## 7. Safety & Incremental Changes
- **No Deletions**: Never delete existing code, functions, or classes unless explicitly asked. Only add new code or expand existing features.
- **Incremental Progress**: NEVER rewrite 100% from scratch. Always build on top of what works.
- **Data Security**: Max security for data handling. Always check authorization, prevent SQL injection (use SQLAlchemy ORM), and isolate companies.
- **Testing**: Before finalizing, verify that new features don't break existing user flows.

## 8. Performance & User Experience
- **Speed First**: Keep the site as fast as possible. Avoid heavy libraries or unnecessary background processes.
- **Simplicity**: Maintain a clean and user-friendly management system. Don't make it unnecessarily complex for the user.
- **Efficiency**: Use lazy loading, efficient database queries, and minimal network requests to ensure a premium, snappy feel.

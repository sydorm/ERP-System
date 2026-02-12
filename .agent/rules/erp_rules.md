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

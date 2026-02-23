# Antigravity ERP Development Constitution (FastAPI + Vue + Postgres + Docker)

## 1. Purpose
Цей документ встановлює обов'язкові правила розробки ERP-системи.
Мета:
- мінімізувати поломки після змін
- забезпечити передбачуваний деплой
- зробити роботу AI-агентів стабільною та контрольованою
- зменшити хаотичні рефакторинги

---

## 2. Project Stack (Source of Truth)
- Frontend: Vue (Vite)
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Cache/Queue (якщо використовується): Redis
- Migrations: Alembic
- Runtime/Deployment: Docker + Docker Compose V2
- Repo: GitHub

---

## 3. Non-Negotiable Rules (Обов'язкові правила)

### 3.1 Docker / Deployment
- Використовувати тільки `docker compose` (Compose V2)
- НЕ використовувати `docker-compose` (Compose V1)
- Будь-які команди в документації повинні бути у форматі `docker compose ...`

### 3.2 Database Changes
- Будь-яка зміна таблиць/полів/індексів = обов'язкова Alembic migration
- Заборонено покладатися на `Base.metadata.create_all()` у production
- Після зміни моделей потрібно:
  1) створити міграцію
  2) застосувати `alembic upgrade head`
  3) перевірити наявність таблиць/полів

### 3.3 Scope Discipline
- Один таск = одна логічна зміна (bounded change)
- Заборонено робити "попутний рефакторинг", якщо це не входить у scope
- Якщо знайдена стороння проблема — зафіксувати як окремий TODO/issue, але не змішувати в поточний таск

### 3.4 Verification Before Completion
Завдання не вважається завершеним без перевірок:
- контейнери підняті
- міграції застосовані
- цільовий endpoint працює
- цільова сторінка UI працює без 500/console errors (критичних)

### 3.5 No Silent Breaking Changes
- Не змінювати API response schema без оновлення frontend client + UI
- Не перейменовувати поля/роути без явного опису у звіті
- Не видаляти код без пояснення, що його замінює

---

## 4. Development Workflow (Обов'язковий порядок роботи)

### Step 1. Plan First
Перед змінами агент повинен надати:
- короткий план (3–7 кроків)
- список файлів, які буде змінювати
- ризики (якщо є)

### Step 2. Implement in Small Scope
- Вносити зміни тільки в заявлений scope
- Не чіпати unrelated модулі

### Step 3. Run Technical Checks
Мінімум:
- `docker compose up -d`
- `docker compose ps`
- `docker compose logs --tail=100 backend`
- `docker compose exec backend alembic upgrade head`

### Step 4. Verify Feature
- перевірити endpoint (200 / expected response)
- перевірити UI сторінку
- перевірити, що немає нових критичних помилок у логах

### Step 5. Report Result
Агент повинен повернути:
- що зроблено
- які файли змінено
- які команди виконані
- що перевірено
- ризики / що залишилось

---

## 5. ERP-Specific Rules (Для ERP логіки)

### 5.1 New ERP Document Module (order, purchase, invoice, receipt)
Порядок реалізації:
1. DB model / schema design
2. Alembic migration
3. Pydantic schemas
4. Backend routes/services
5. Business logic / posting (якщо потрібно)
6. Frontend API client
7. UI page/form/list
8. Verification

### 5.2 Document Numbering
- Нумерація документів повинна працювати через єдиний механізм (`document_sequences` або еквівалент)
- Якщо UI очікує нумерацію, таблиця/міграція має існувати до запуску UI

### 5.3 Posting / Registers
- Проведення документів має бути ідемпотентним (повторний запуск не дублює записи)
- Перед повторним проведенням — unpost старих записів
- Будь-які регістри мають бути прив'язані до `document_type + document_id`

---

## 6. File / Code Quality Rules

### 6.1 File Size / Complexity
- Не створювати надто великі файли без потреби
- Якщо файл росте занадто сильно — винести helper/service/components

### 6.2 Naming
- Зрозумілі імена файлів/роутів/сервісів
- Узгоджені назви між backend і frontend

### 6.3 Error Handling
- Backend: повертати зрозумілі HTTP помилки
- Frontend: показувати користувачу людинозрозуміле повідомлення, а не тільки "500"

---

## 7. Forbidden Actions (Без окремого дозволу)
Заборонено:
- масово рефакторити код поза задачою
- змінювати docker volumes / видаляти volumes
- видаляти таблиці/дані
- змінювати auth/roles у задачі, що не стосується авторизації
- міняти структуру repo без погодження
- переходити на інший стек/бібліотеку "по дорозі"

---

## 8. Definition of Done (DoD)
Завдання вважається завершеним тільки якщо:
1. Реалізовано заявлену зміну
2. Міграції застосовані (якщо були зміни БД)
3. Цільові endpoint/UI працюють
4. Є короткий технічний звіт
5. Немає критичних нових помилок у логах

---

## 9. If Something Fails (Failure Protocol)
Якщо щось не працює:
1. Зупинити хаотичні зміни
2. Зібрати діагностику (ps, logs, migrations, endpoint error)
3. Визначити: infra / DB / backend / frontend
4. Фіксити кореневу причину, а не симптом
5. Після фіксу — повторна перевірка

---

## 10. Source of Truth Priority
Якщо є конфлікт між шарами:
1. DB schema + Alembic migration
2. Backend API contracts (schemas/routes)
3. Frontend API client
4. UI views/components
5. Docs/examples/mock data

---

## 11. Commit Discipline
Кожен commit має бути вузьким і зрозумілим:
- ✅ `fix(numbering): apply document_sequences migration and handle empty list`
- ✅ `feat(sales-order): add create endpoint and UI form save`
- ❌ `fix all`
- ❌ `many changes`

---

## 12. ERP Domain Core Rules (Critical Invariants)

### 12.1 Document Lifecycle (Mandatory)
Every ERP document MUST follow lifecycle:

- DRAFT → POSTED → (optional) UNPOSTED → POSTED
- CANCELLED (terminal state)

Rules:
- Document is created ONLY in DRAFT state.
- DRAFT documents do NOT create register entries.
- POST operation creates register entries.
- Editing is allowed ONLY in DRAFT.
- Editing POSTED requires explicit UNPOST first.
- DELETE allowed ONLY in DRAFT.

Auto-posting on create is forbidden.

---

### 12.2 Transaction Atomicity
For any document operation:

Header + Lines + Register entries MUST be written in ONE database transaction.

If any part fails → entire operation must rollback.

---

### 12.3 Register Integrity
- All register records must contain:
  - document_type
  - document_id
  - line_id (if applicable)
- Re-post must:
  - delete previous register entries
  - insert new ones
- Duplicate register rows for same document are forbidden.

---

### 12.4 Backend Validation is Source of Truth
- total_amount must be recalculated on backend.
- Client-sent totals are not trusted.
- Any mismatch returns 400 error.

---

### 12.5 No Business Logic in Routes
Routes:
- validate input
- call service
- return response

All posting logic must live in services layer.

---

### 12.6 Stock Calculation Rule
- Stock balance is derived only from AccumulationRegister.
- No direct stock fields allowed in product tables.

# TASK_TEMPLATE.md
# Template for AI Agent Tasks (Antigravity / Kimi / other)

## Task Title
[коротка назва задачі]

---

## 1. Goal (Мета)
Що саме потрібно зробити:
- [ ]
- [ ]

Приклад:
- Виправити завантаження сторінки "Нумерація документів"
- Усунути помилку `document_sequences does not exist`
- Забезпечити коректну роботу endpoint `/api/v1/document-sequences`

---

## 2. Scope (Що дозволено змінювати)
Дозволено змінювати тільки:
- backend routes/services/schemas для [модуль]
- alembic migration (якщо потрібно)
- frontend API client / view для [сторінка]
- docs (якщо потрібно)

---

## 3. Out of Scope (Що НЕ чіпати)
Не змінювати:
- auth / roles
- інші модулі ERP
- docker volumes / infra config
- unrelated UI pages
- масовий рефакторинг

---

## 4. Current Problem / Symptoms
Опиши симптоми:
- UI помилка:
- Console помилка:
- Backend traceback:
- SQL помилка:
- URL сторінки:
- Endpoint:

---

## 5. Root Cause Hypothesis (Гіпотеза причини)
Агент має перед змінами написати 1–3 гіпотези:
1.
2.
3.

---

## 6. Mandatory Plan (3–7 steps)
Агент повинен спочатку написати план:
1.
2.
3.
4.

---

## 7. Files To Be Changed (before implementation)
Агент повинен перелічити файли, які планує змінити:
- `backend/...`
- `frontend/...`
- `alembic/versions/...`
- `docs/...`

> Без дозволу не змінювати файли поза цим списком.

---

## 8. Implementation Rules (Обов'язково)
- Використовувати тільки `docker compose`
- Якщо змінюється БД → зробити Alembic migration
- Не робити рефакторинг поза scope
- Не міняти API contract без оновлення frontend client
- Після змін виконати перевірки (розділ 10)

---

## 9. Deliverables (Що має повернути агент)
Агент у відповіді має надати:
- короткий список змін
- список змінених файлів
- команди для перевірки
- результат перевірки
- ризики / що залишилось

---

## 10. Verification Checklist (Обов'язково)
### A. Infra
- [ ] `docker compose up -d`
- [ ] `docker compose ps`

### B. Logs
- [ ] `docker compose logs --tail=100 backend`
- [ ] `docker compose logs --tail=100 db`

### C. Migrations (if DB changed)
- [ ] `docker compose exec backend alembic upgrade head`
- [ ] перевірка таблиці/колонки

### D. Backend endpoint
- [ ] target endpoint returns expected response

### E. Frontend UI
- [ ] сторінка відкривається
- [ ] немає критичних console errors
- [ ] функція працює (list/create/save/etc.)

---

## 11. Definition of Done (DoD)
Задача завершена тільки якщо:
- [ ] симптом усунуто
- [ ] коренева причина підтверджена
- [ ] перевірки пройдені
- [ ] зміни зафіксовані без побічних поломок

---

## 12. Rollback / Risk Notes
Якщо щось піде не так:
- що відкотити
- які файли / міграції перевірити
- які команди виконані для діагностики

# PROJECT_STRUCTURE

Архітектурна карта ERP-проєкту. Мета файлу: швидко зрозуміти, де живе потрібна логіка, і зменшити ризик змінити не той компонент перед новими задачами.

## Загальні Правила Роботи

- Page-level файли у `frontend/src/views/**` часто містять і UI, і локальну бізнес-логіку. Перед правкою перевіряти пов'язані API, store і дочірні компоненти.
- Великі файли понад 1000 рядків не бажано розширювати новими великими блоками. Краще виносити UI у компоненти, а логіку у composables/services.
- Backend має типову структуру: `api/*_routes.py` для endpoint-ів, `models/*.py` для SQLAlchemy моделей, `schemas/*.py` для Pydantic схем, `services/*.py` для доменної логіки.
- Не міняти routing, permissions, posting, document numbering або drag/drop без окремої перевірки пов'язаних місць.

---

# Global Layout

### `frontend/src/layouts/DashboardLayout.vue`
Responsibility:
Глобальний layout авторизованої ERP: sidebar, topbar, відкриті вкладки, системні іконки, command palette пошуку, notifications/profile entry points.

Contains:
- Загальна оболонка сторінок.
- Sidebar navigation і collapse behavior.
- Topbar з відкритими вкладками.
- Global search icon/modal.
- Notification/profile/quick add controls.

Related files:
- `frontend/src/components/layout/TabsBar.vue`
- `frontend/src/stores/tabs.js`
- `frontend/src/stores/notification.js`
- `frontend/src/stores/user.js`
- `frontend/src/router/index.js`

Use this file when:
- Змінюється topbar або sidebar.
- Потрібно змінити глобальний пошук.
- Потрібно змінити поведінку відкритих вкладок.

Do not use this file for:
- Зміни CRM Kanban карток.
- Зміни форм документів.
- Зміни backend permissions.

### `frontend/src/components/layout/TabsBar.vue`
Responsibility:
UI відкритих вкладок у topbar.

Contains:
- Відображення tabs.
- Активна вкладка.
- Закриття/перехід між вкладками.

Related files:
- `frontend/src/stores/tabs.js`
- `frontend/src/layouts/DashboardLayout.vue`
- `frontend/src/router/index.js`

Typical tasks:
- Візуально змінити tabs.
- Додати overflow/horizontal scroll.
- Виправити активний стан вкладки.

### `frontend/src/stores/notification.js`
Responsibility:
Frontend state для системних сповіщень.

Contains:
- Список notifications.
- Unread count.
- Дії для завантаження/позначення прочитаними.

Related files:
- `backend/app/api/notification_routes.py`
- `backend/app/models/notification.py`
- `backend/app/schemas/notification.py`
- `frontend/src/layouts/DashboardLayout.vue`

### `frontend/src/stores/user.js`
Responsibility:
Frontend user session, current user, roles/permissions helpers.

Related files:
- `backend/app/api/auth_routes.py`
- `backend/app/api/user_routes.py`
- `backend/app/core/permissions.py`
- `frontend/src/permissions/registry.js`

---

# CRM

### `frontend/src/views/CRM/CrmOrdersBoard.vue`
Responsibility:
Головна CRM Kanban сторінка. Рендерить header, KPI, filters, attention strip, Kanban columns і CRM order cards.

Contains:
- Kanban board layout.
- Kanban/Analytics switch.
- Board filters/search.
- KPI cards and attention logic.
- Drag/drop між CRM stages.
- CRM card UI.
- Communication buttons on card.
- Rule-based hints popover.
- Manager filter and manager display.
- Next/last contact chips.

Related files:
- `frontend/src/views/CRM/CrmOrderEditor.vue`
- `frontend/src/views/CRM/CrmAnalytics.vue`
- `frontend/src/views/CRM/ClientProfile.vue`
- `frontend/src/components/crm/CallResultDialog.vue`
- `backend/app/api/order_routes.py`
- `backend/app/api/crm_routes.py`
- `backend/app/models/order.py`
- `backend/app/models/crm.py`
- `backend/app/services/sla_service.py`

Use this file when:
- Змінюється CRM board layout.
- Змінюються Kanban columns або card UI.
- Змінюється card-level contact/attention/hints display.
- Змінюються board filters.

Do not use this file for:
- Додавання полів у форму створення/редагування CRM заявки.
- Зміну backend stage transitions.
- Зміну товарів/BOM/закупівель.

Refactor note:
Файл дуже великий. Першими кандидатами на винесення є `CrmOrderCard.vue`, `CrmKanbanColumn.vue`, `CrmBoardHeader.vue`, `CrmAttentionStrip.vue`, `useCrmFilters.ts`, `useCrmKanban.ts`, `useCrmContacts.ts`.

### `frontend/src/views/CRM/CrmOrderEditor.vue`
Responsibility:
Page-level контейнер форми створення/редагування CRM заявки. Після рефакторингу відповідає за route params, load/save orchestration, API calls, high-level state і передачу props/emits у блоки.

Contains:
- Composition layout CRM editor.
- Save draft / send to production orchestration.
- Existing API integration for order, contacts, materials, dictionaries and counterparties.
- Automation modal and print preview modal wiring.

Related UI files:
- `frontend/src/views/CRM/components/CrmOrderHeader.vue`
- `frontend/src/views/CRM/components/CrmOrderStageStepper.vue`
- `frontend/src/views/CRM/components/CrmClientBlock.vue`
- `frontend/src/views/CRM/components/CrmManagerBlock.vue`
- `frontend/src/views/CRM/components/CrmProductBlock.vue`
- `frontend/src/views/CRM/components/CrmReferencePhotosBlock.vue`
- `frontend/src/views/CRM/components/CrmFinanceBlock.vue`
- `frontend/src/views/CRM/components/CrmMaterialsCheckBlock.vue`
- `frontend/src/views/CRM/components/CrmDeadlinesBlock.vue`
- `frontend/src/views/CRM/components/CrmReadinessChecklist.vue`
- `frontend/src/views/CRM/components/CrmContactPanel.vue`
- `frontend/src/views/CRM/components/CrmCommunicationHistory.vue`
- `frontend/src/views/CRM/components/CrmOrderHistoryNotes.vue`
- `frontend/src/views/CRM/components/CrmAiAssistant.vue`
- `frontend/src/views/CRM/components/CrmRelatedDocuments.vue`
- `frontend/src/views/CRM/components/CrmNewClientDialog.vue`
- `frontend/src/views/CRM/components/CrmCommunicationDrawer.vue`

Related styles:
- `frontend/src/views/CRM/styles/CrmOrderEditor.css`
- `frontend/src/views/CRM/styles/CrmOrdersBoard.css`

Related composables:
- `frontend/src/views/CRM/composables/useCrmOrderForm.ts`
- `frontend/src/views/CRM/composables/useCrmOrderValidation.ts`
- `frontend/src/views/CRM/composables/useCrmContactLogic.ts`
- `frontend/src/views/CRM/composables/useCrmReadiness.ts`
- `frontend/src/views/CRM/composables/useCrmOrderDocuments.ts`

Related backend/API files:
- `backend/app/api/order_routes.py`
- `backend/app/models/order.py`
- `backend/app/schemas/order.py`
- `backend/app/api/counterparty_routes.py`
- `backend/app/api/product_routes.py`

Use this file when:
- Змінюється порядок блоків CRM editor на сторінці.
- Змінюється load/save orchestration або route-level behavior.
- Потрібно підключити новий блок через props/emits.

Use extracted files when:
- Змінюється UI клієнта, виробу, фінансів, дедлайнів, готовності, комунікацій або AI-підказок.
- Змінюється стартовий стан форми, validation, contact presets або readiness checklist.

Do not use this file for:
- Зміни Kanban card layout.
- Зміни глобального topbar/sidebar.
- Зміни BOM логіки товару.

### `frontend/src/views/CRM/CrmAnalytics.vue`
Responsibility:
Аналітика CRM funnel/pipeline.

Contains:
- KPI по CRM.
- Funnel/analytics blocks.
- Aggregated order metrics.

Related files:
- `frontend/src/views/CRM/CrmOrdersBoard.vue`
- `backend/app/api/crm_routes.py`
- `backend/app/api/order_routes.py`

### `frontend/src/views/CRM/ClientProfile.vue`
Responsibility:
Картка клієнта у CRM/sales контексті.

Contains:
- Client summary.
- Контакти/історія/пов'язані документи, якщо доступно.

Related files:
- `frontend/src/views/Sales/CounterpartyEditor.vue`
- `backend/app/api/counterparty_routes.py`
- `backend/app/models/counterparty.py`

### `frontend/src/components/crm/CallResultDialog.vue`
Responsibility:
Модалка фіксації результату контакту.

Contains:
- Communication result form.
- Comment/next step fields.

Related files:
- `frontend/src/views/CRM/CrmOrdersBoard.vue`
- `frontend/src/views/CRM/CrmOrderEditor.vue`
- `backend/app/api/order_routes.py`

### CRM backend

`backend/app/api/order_routes.py`
Responsibility:
Основні endpoint-и CRM/order workflow. Тут обробляються створення/оновлення заявок, stage/status transitions, manager assignment/reassign, activity/contact pieces.

`backend/app/api/crm_routes.py`
Responsibility:
CRM-specific endpoints and auxiliary CRM operations.

`backend/app/models/order.py`
Responsibility:
SQLAlchemy модель заявки/замовлення.

`backend/app/schemas/order.py`
Responsibility:
Pydantic схеми створення/оновлення/відповіді order.

`backend/app/models/crm.py`, `backend/app/schemas/crm.py`
Responsibility:
CRM-допоміжні моделі/схеми.

`backend/app/services/sla_service.py`
Responsibility:
SLA/attention calculation service.

---

# Nomenclature / Products

### `frontend/src/views/Inventory/Nomenclature.vue`
Responsibility:
Список номенклатури/товарів.

Contains:
- Product table/list.
- Search/filtering.
- Actions for open/create/edit product.
- Possibly product type/status display.

Related files:
- `frontend/src/views/Inventory/ProductEditor.vue`
- `backend/app/api/product_routes.py`
- `backend/app/models/product.py`
- `backend/app/schemas/product.py`

Use this file when:
- Змінюється список товарів.
- Змінюються фільтри/табличний вигляд номенклатури.

Do not use this file for:
- Зміни вкладок картки товару.
- Зміни BOM розрахунків.

### `frontend/src/views/Inventory/ProductEditor.vue`
Responsibility:
Page shell картки товару. Координує header, sticky tabs, завантаження/збереження товару і передачу `form` у вкладки.

Contains:
- Product header/actions.
- Product tabs navigation.
- Load/save product.
- Common product form state.

Related files:
- `frontend/src/views/Inventory/ProductTabs/GeneralTab.vue`
- `frontend/src/views/Inventory/ProductTabs/CharacteristicsTab.vue`
- `frontend/src/views/Inventory/ProductTabs/PricingTab.vue`
- `frontend/src/views/Inventory/ProductTabs/SpecificationTab.vue`
- `frontend/src/views/Inventory/ProductTabs/InventoryTab.vue`
- `frontend/src/views/Inventory/ProductTabs/FilesTab.vue`
- `frontend/src/views/Inventory/ProductTabs/ProcurementTab.vue`
- `frontend/src/views/Inventory/ProductTabs/ManufacturingTab.vue`
- `frontend/src/components/ProductVariantsManager.vue`
- `backend/app/api/product_routes.py`

Use this file when:
- Змінюється header картки товару.
- Змінюються tabs або save/load orchestration.
- Потрібно додати нову вкладку.

Do not use this file for:
- Детальну логіку конкретної вкладки.
- Backend schema/model changes без відповідної backend правки.

### `frontend/src/views/Inventory/ProductTabs/GeneralTab.vue`
Responsibility:
Загальна інформація товару.

Contains:
- Basic product fields.
- Dimensions/common attributes.
- Type/status/basic settings.

Related files:
- `frontend/src/views/Inventory/ProductEditor.vue`
- `backend/app/schemas/product.py`
- `backend/app/models/product.py`

### `frontend/src/views/Inventory/ProductTabs/CharacteristicsTab.vue`
Responsibility:
Характеристики/атрибути товару.

Contains:
- Product attributes UI.
- Characteristic values.
- Attribute configuration/selection.

Related files:
- `frontend/src/views/Settings/ProductAttributesManager.vue`
- `backend/app/api/attribute_routes.py`
- `backend/app/models/attribute.py`
- `backend/app/schemas/attribute.py`

### `frontend/src/views/Inventory/ProductTabs/PricingTab.vue`
Responsibility:
Ціни та комерційні параметри товару.

Contains:
- Price/cost fields.
- Margin/commercial settings if present.

Related files:
- `backend/app/services/cost_service.py`
- `backend/app/models/product_cost_history.py`

### `frontend/src/views/Inventory/ProductTabs/SpecificationTab.vue`
Responsibility:
BOM/specification tab for product.

Contains:
- BOM lines.
- Materials/components.
- Specification calculations.
- Variant/dimension-sensitive BOM logic.

Related files:
- `backend/app/api/specification_routes.py`
- `backend/app/services/specification_service.py`
- `backend/app/models/specification.py`
- `frontend/src/views/Sales/VariantSelectorDialog.vue`

Do not modify notes:
Це високоризиковий файл. Перед змінами перевірити sales order variant logic, product dimensions, specification backend service.

### `frontend/src/views/Inventory/ProductTabs/InventoryTab.vue`
Responsibility:
Складський запас товару.

Related files:
- `frontend/src/views/Inventory/Warehouses.vue`
- `backend/app/api/warehouse_routes.py`
- `backend/app/models/warehouse.py`

### `frontend/src/views/Inventory/ProductTabs/FilesTab.vue`
Responsibility:
Файли/вкладення товару.

Related files:
- `backend/app/api/upload_routes.py`
- `backend/app/models/product_file.py`

### `frontend/src/views/Inventory/ProductTabs/ProcurementTab.vue`
Responsibility:
Закупівлі та постачальники для товару.

Contains:
- Supplier/procurement settings.
- Supplier links for purchase ordering.
- Default supplier flags.
- Supplier SKU/order URL UI.

Related files:
- `frontend/src/views/Purchases/PurchaseOrderEditor.vue`
- `frontend/src/components/DocumentItemsTable.vue`
- `backend/app/api/product_routes.py`
- `backend/app/models/product.py`
- `backend/app/models/supplier_price.py`

### `frontend/src/views/Inventory/ProductTabs/ManufacturingTab.vue`
Responsibility:
Виробничі налаштування товару.

Related files:
- `frontend/src/views/Production/ProductionOrderEditor.vue`
- `backend/app/api/production_routes.py`
- `backend/app/models/production.py`

### Product backend

`backend/app/api/product_routes.py`
Responsibility:
CRUD товарів, product metadata, supplier/product related fields.

`backend/app/models/product.py`
Responsibility:
Product SQLAlchemy model.

`backend/app/schemas/product.py`
Responsibility:
Product Pydantic schemas.

`backend/app/api/attribute_routes.py`, `backend/app/models/attribute.py`
Responsibility:
Product attributes/characteristics.

`backend/app/api/specification_routes.py`, `backend/app/services/specification_service.py`
Responsibility:
BOM/specification API and calculations.

---

# Purchasing

### `frontend/src/views/Purchases/Purchases.vue`
Responsibility:
Верхній wrapper/entry для модуля закупівель, якщо використовується як container.

Related files:
- `frontend/src/views/Purchases/PurchaseOrderList.vue`
- `frontend/src/views/Purchases/PurchasesPlanning.vue`
- `frontend/src/views/Purchases/PurchaseReceiptsList.vue`

### `frontend/src/views/Purchases/PurchaseOrderList.vue`
Responsibility:
Сторінка "Закупівлі -> Замовлення". Контроль supplier orders.

Contains:
- Header/KPI закупівель.
- Filters.
- Purchase orders table.
- Status/payment/priority display.
- Modal/drawer створення з потреб виробництва.

Related files:
- `frontend/src/views/Purchases/PurchaseOrderEditor.vue`
- `backend/app/api/purchase_order_routes.py`
- `backend/app/models/purchase_order.py`
- `backend/app/schemas/purchase_order.py`
- `frontend/src/views/Purchases/PurchasesPlanning.vue`

Use this file when:
- Змінюється список замовлень постачальникам.
- Змінюються KPI/фільтри/таблиця закупівель.

Do not use this file for:
- Редагування рядків конкретного замовлення.
- Прибуткові накладні.

### `frontend/src/views/Purchases/PurchaseOrderEditor.vue`
Responsibility:
Форма створення/редагування замовлення постачальнику.

Contains:
- Supplier selection.
- Purchase order header fields.
- Items table via `DocumentItemsTable.vue`.
- Totals/status/payment basics.

Related files:
- `frontend/src/components/DocumentItemsTable.vue`
- `frontend/src/views/Inventory/ProductTabs/ProcurementTab.vue`
- `backend/app/api/purchase_order_routes.py`
- `backend/app/api/product_routes.py`
- `backend/app/api/counterparty_routes.py`

### `frontend/src/components/DocumentItemsTable.vue`
Responsibility:
Спільна таблиця рядків документів.

Contains:
- Product select in document lines.
- Quantity/price/totals.
- Warehouse/characteristics if enabled.
- Purchase-specific supplier SKU/link actions.

Related files:
- `frontend/src/views/Purchases/PurchaseOrderEditor.vue`
- `frontend/src/views/Sales/OrderEditor.vue`
- `frontend/src/views/Purchases/PurchaseReceiptEditor.vue`

Do not modify notes:
Це shared component. Зміни можуть зачепити закупівлі, продажі, прибуткові накладні.

### `frontend/src/views/Purchases/PurchaseReceiptEditor.vue`
Responsibility:
Форма прибуткової накладної/receipt.

Related files:
- `frontend/src/views/Purchases/PurchaseReceiptsList.vue`
- `backend/app/api/purchase_receipt_routes.py`
- `backend/app/models/purchase_receipt.py`

### `frontend/src/views/Purchases/PurchaseReceiptsList.vue`
Responsibility:
Список прибуткових накладних.

### `frontend/src/views/Purchases/PurchasesPlanning.vue`
Responsibility:
Планування закупівель/потреб.

Related files:
- `frontend/src/views/Purchases/WhatToOrder.vue`
- `backend/app/api/production_routes.py`
- `backend/app/api/purchase_order_routes.py`

### Purchasing backend

`backend/app/api/purchase_order_routes.py`
Responsibility:
Purchase order endpoints.

`backend/app/models/purchase_order.py`, `backend/app/schemas/purchase_order.py`
Responsibility:
Purchase order data model/schema.

`backend/app/api/purchase_receipt_routes.py`
Responsibility:
Purchase receipt/incoming documents endpoints.

---

# Sales

### `frontend/src/views/Sales/OrdersList.vue`
Responsibility:
Список продажів/замовлень клієнтів.

Contains:
- Sales orders table/cards.
- Filters/search/status actions.

Related files:
- `frontend/src/views/Sales/OrderEditor.vue`
- `backend/app/api/order_routes.py`

### `frontend/src/views/Sales/OrderEditor.vue`
Responsibility:
Форма замовлення продажу.

Contains:
- Customer/order fields.
- Items/variant selection.
- Totals/document actions.

Related files:
- `frontend/src/components/DocumentItemsTable.vue`
- `frontend/src/views/Sales/VariantSelectorDialog.vue`
- `backend/app/api/order_routes.py`
- `backend/app/api/specification_routes.py`

Do not modify notes:
Файл має попередження build щодо `eval`. Не розширювати без плану винесення variant/calculation logic.

### `frontend/src/views/Sales/InvoicesList.vue`
Responsibility:
Список рахунків/інвойсів.

Related files:
- `frontend/src/views/Sales/InvoiceEditor.vue`
- `backend/app/api/sales_invoice_routes.py`

### `frontend/src/views/Sales/InvoiceEditor.vue`
Responsibility:
Форма інвойсу.

### `frontend/src/views/Sales/CounterpartiesList.vue`
Responsibility:
Список клієнтів/постачальників/контрагентів.

Related files:
- `frontend/src/views/Sales/CounterpartyEditor.vue`
- `backend/app/api/counterparty_routes.py`

### `frontend/src/views/Sales/CounterpartyEditor.vue`
Responsibility:
Картка контрагента.

Contains:
- Counterparty core fields.
- Contacts/details.
- Customer/supplier related metadata.

### Sales backend

`backend/app/api/order_routes.py`
Responsibility:
Sales/CRM order endpoints.

`backend/app/api/sales_invoice_routes.py`
Responsibility:
Invoice endpoints.

`backend/app/api/counterparty_routes.py`
Responsibility:
Customers/suppliers/counterparties endpoints.

---

# Production

### `frontend/src/views/Production/ProductionOrdersList.vue`
Responsibility:
Список виробничих замовлень/задач.

Contains:
- Production order table/cards.
- Status/stage display.

Related files:
- `frontend/src/views/Production/ProductionOrderEditor.vue`
- `backend/app/api/production_routes.py`

### `frontend/src/views/Production/ProductionOrderEditor.vue`
Responsibility:
Форма виробничого замовлення.

Contains:
- Production order header.
- Stage/status controls.
- Materials/BOM usage.
- Links to CRM/order/product if present.

Related files:
- `frontend/src/views/Inventory/ProductTabs/SpecificationTab.vue`
- `frontend/src/views/Purchases/PurchasesPlanning.vue`
- `backend/app/api/production_routes.py`
- `backend/app/models/production.py`
- `backend/app/services/specification_service.py`

### Production backend

`backend/app/api/production_routes.py`
Responsibility:
Production orders/tasks endpoints, materials requirements, stage/status operations.

`backend/app/models/production.py`, `backend/app/schemas/production.py`
Responsibility:
Production data model/schema.

---

# Finance

### `backend/app/api/finance_routes.py`
Responsibility:
Finance endpoints: payments, bank/cash accounts, financial status pieces.

Related files:
- `backend/app/models/finance.py`
- `backend/app/schemas/finance.py`
- `backend/app/models/bank_account.py`
- `backend/app/schemas/bank_account.py`

### `backend/app/models/finance.py`
Responsibility:
Finance SQLAlchemy models.

### `backend/app/services/posting_service.py`
Responsibility:
Posting/accounting side effects for documents.

Do not modify notes:
High impact. Posting changes can affect sales, purchases, inventory, finance reports.

---

# Admin / Settings

### `frontend/src/views/Settings/Users.vue`
Responsibility:
Список користувачів.

Related files:
- `frontend/src/views/Settings/UserCreate.vue`
- `backend/app/api/user_routes.py`
- `backend/app/core/permissions.py`

### `frontend/src/views/Settings/UserCreate.vue`
Responsibility:
Створення/редагування користувача.

Contains:
- Main user form.
- Permissions tabs/registry rendering.
- Roles assignment.
- Activity/security/history UI if enabled.

Related files:
- `frontend/src/permissions/registry.js`
- `backend/app/api/user_routes.py`
- `backend/app/schemas/user.py`
- `backend/app/models/user.py`
- `backend/app/core/permissions.py`

### `frontend/src/permissions/registry.js`
Responsibility:
Frontend centralized permissions registry.

Contains:
- Modules.
- Permission actions.
- Role presets if implemented.

Related files:
- `backend/app/core/permissions.py`
- `frontend/src/views/Settings/UserCreate.vue`

### `backend/app/core/permissions.py`
Responsibility:
Backend permission checks/helpers.

Do not modify notes:
Будь-яка зміна має перевірятись і на frontend, і на backend.

### `frontend/src/views/Settings/Dictionaries.vue`
Responsibility:
Довідники.

Related files:
- `backend/app/api/dictionary_routes.py`
- `backend/app/services/dictionary_service.py`

### `frontend/src/views/Settings/PrintTemplatesList.vue`
Responsibility:
Список шаблонів документів.

Related files:
- `frontend/src/views/Settings/PrintTemplateEditor.vue`
- `backend/app/api/print_routes.py`
- `backend/app/models/print_template.py`
- `frontend/src/utils/templateEngine.ts`
- `frontend/src/utils/defaultTemplates.ts`

### `frontend/src/views/Settings/BusinessProcessRules.vue`
Responsibility:
Список правил бізнес-процесів.

Related files:
- `frontend/src/views/Settings/BusinessProcessRuleEditor.vue`
- `backend/app/api/business_process_routes.py`
- `backend/app/services/business_process_engine.py`

### `frontend/src/views/Settings/ProductAttributesManager.vue`
Responsibility:
Налаштування характеристик/атрибутів товарів.

Related files:
- `frontend/src/views/Inventory/ProductTabs/CharacteristicsTab.vue`
- `backend/app/api/attribute_routes.py`

---

# Shared / Cross-Cutting Files

### `frontend/src/router/index.js`
Responsibility:
Frontend routes and page mapping.

Use this file when:
- Додається нова сторінка.
- Змінюється path/name/meta route.

Do not use this file for:
- UI changes inside pages.

### `frontend/src/api/index.js`
Responsibility:
Base API client/config.

### `frontend/src/api/specifications.js`
Responsibility:
Frontend API helper for specifications/BOM.

### `backend/app/main.py`
Responsibility:
FastAPI app setup, routers registration, startup schema patching if present.

Do not modify notes:
Не додавати багато доменної логіки. Краще routes/services/migrations.

### `backend/app/api/dependencies.py`
Responsibility:
Shared API dependencies: DB session/current user/auth.

### `backend/app/services/audit_service.py`
Responsibility:
Audit logging service.

### `frontend/src/components/AuditLogViewer.vue`
Responsibility:
UI перегляду audit/activity log.

---

# Large Files Audit

## Files over 2000 lines

| File | Lines | Risk | Suggested split |
|---|---:|---|---|
| `frontend/src/views/CRM/CrmOrderEditor.vue` | 843 | Medium | UI/style blocks extracted; next split candidates: load/save orchestration and material-check composable |
| `frontend/src/views/CRM/CrmOrdersBoard.vue` | 778 | Medium | UI/style blocks extracted; next split candidates: board data loading, filters, attention rules and drag/drop orchestration |

## Files over 1000 lines

| File | Lines | Risk | Suggested split |
|---|---:|---|---|
| `frontend/src/views/Inventory/Nomenclature.vue` | 1666 | High | `NomenclatureToolbar`, `NomenclatureTable`, `ProductQuickActions`, `useNomenclatureFilters` |
| `frontend/src/views/Inventory/ProductTabs/SpecificationTab.vue` | 1475 | High | `BomLinesTable`, `BomMaterialPicker`, `BomCalculatorPanel`, `useProductBOM`, `useProductDimensions` |
| `frontend/src/views/Sales/OrdersList.vue` | 1411 | High | `SalesOrdersToolbar`, `SalesOrdersTable`, `SalesOrderStatusBadges`, `useSalesOrderFilters` |
| `frontend/src/views/Sales/OrderEditor.vue` | 1334 | High | `SalesOrderHeader`, `SalesClientBlock`, `SalesItemsBlock`, `SalesTotalsPanel`, `useSalesOrderForm` |
| `frontend/src/views/Purchases/PurchaseOrderList.vue` | 1052 | Medium/High | `PurchaseOrdersHeader`, `PurchaseKpiCards`, `PurchaseFilters`, `PurchaseOrdersTable`, `ProductionNeedsDrawer`, `usePurchases` |

## Files over 500 lines

| File | Lines | Risk | Suggested split |
|---|---:|---|---|
| `frontend/src/views/Inventory/ProductTabs/CharacteristicsTab.vue` | 963 | Medium/High | `CharacteristicsEditor`, `AttributeValuePicker`, `useProductCharacteristics` |
| `frontend/src/views/Settings/CompanySettings.vue` | 954 | Medium | Split by settings sections/tabs |
| `frontend/src/views/Personnel/AttendanceBoard.vue` | 872 | Medium | `AttendanceToolbar`, `AttendanceGrid`, `useAttendance` |
| `frontend/src/views/Inventory/ProductTabs/GeneralTab.vue` | 795 | Medium/High | `ProductMainFields`, `ProductDimensionsBlock`, `useProductDimensions` |
| `frontend/src/views/Inventory/Warehouses.vue` | 789 | Medium | `WarehousesTable`, `WarehouseEditorDialog` |
| `frontend/src/views/Sales/CounterpartyEditor.vue` | 788 | Medium | `CounterpartyMainBlock`, `CounterpartyContactsBlock`, `CounterpartyHistoryBlock` |
| `frontend/src/views/Sales/VariantSelectorDialog.vue` | 733 | Medium/High | `VariantOptionsGrid`, `VariantPreview`, `useVariantSelection` |
| `frontend/src/views/Purchases/PurchaseOrderEditor.vue` | 717 | Medium | `PurchaseOrderHeader`, `PurchaseSupplierBlock`, `PurchaseTotalsPanel` |
| `frontend/src/views/Calculator/DrawerCalculator.vue` | 705 | Medium | Calculator sections/composables |
| `frontend/src/views/Settings/Users.vue` | 677 | Medium | `UsersTable`, `UserFilters`, `UserStatusActions` |
| `frontend/src/layouts/DashboardLayout.vue` | 657 | Medium/High | `SidebarNav`, `Topbar`, `GlobalSearchCommand`, `NotificationDropdown`, `ProfileMenu` |
| `frontend/src/views/Production/ProductionOrderEditor.vue` | 653 | Medium | `ProductionHeader`, `ProductionStages`, `ProductionMaterials` |
| `frontend/src/views/Inventory/ProductEditor.vue` | 649 | Medium | Keep as page shell, extract `ProductHeader`, `ProductTabsNav`, `useProductEditor` |
| `frontend/src/views/Settings/Dictionaries.vue` | 630 | Medium | `DictionaryList`, `DictionaryItemsTable` |
| `backend/app/api/product_routes.py` | 629 | Medium/High | Split product CRUD, attributes, variants, files/procurement endpoints |
| `backend/app/api/order_routes.py` | 582 | High | Split CRM order, sales order, contacts/activity, stage/status endpoints |
| `frontend/src/components/ProductVariantsManager.vue` | 554 | Medium/High | `VariantMatrix`, `VariantRow`, `useProductVariants` |
| `frontend/src/views/Settings/ProductAttributesManager.vue` | 514 | Medium | `AttributesTable`, `AttributeEditorDialog` |

---

# Refactor Recommendations

## Refactor first

1. `frontend/src/views/CRM/CrmOrderEditor.vue`
   - Найбільший файл і найбільший ризик для щоденних CRM задач.
   - Винести форму в блоки: client/product/finance/contact/history/stages.
   - Створити `useCrmOrderForm.ts` і `useCrmContacts.ts`.

2. `frontend/src/views/CRM/CrmOrdersBoard.vue`
   - Часто змінюється дизайн і логіка Kanban.
   - Винести `CrmOrderCard.vue` першим, потім `CrmKanbanColumn.vue`, `CrmAttentionStrip.vue`.
   - Створити `useCrmFilters.ts`, `useCrmKanban.ts`, `useCrmAttention.ts`.

3. `frontend/src/views/Inventory/ProductTabs/SpecificationTab.vue`
   - Високий ризик через BOM, dimensions, variants, build warning around eval.
   - Винести `BomLinesTable`, `BomCalculatorPanel`.
   - Створити `useProductBOM.ts`, `useProductDimensions.ts`.

4. `frontend/src/views/Inventory/Nomenclature.vue`
   - Великий списоковий файл, кандидат на table/filters/actions split.

5. `frontend/src/views/Purchases/PurchaseOrderList.vue`
   - Вже має складний закупівельний UI. Винести filters/table/production needs drawer.

## Suggested composables

- `frontend/src/composables/useCrmOrders.ts`
- `frontend/src/composables/useCrmFilters.ts`
- `frontend/src/composables/useCrmKanban.ts`
- `frontend/src/composables/useCrmContacts.ts`
- `frontend/src/composables/useCrmAttention.ts`
- `frontend/src/composables/useProductBOM.ts`
- `frontend/src/composables/useProductDimensions.ts`
- `frontend/src/composables/useProductVariants.ts`
- `frontend/src/composables/usePurchases.ts`
- `frontend/src/composables/useDocumentItems.ts`

## Components to extract

- `CrmOrderCard.vue` from `CrmOrdersBoard.vue`.
- `CrmKanbanColumn.vue` from `CrmOrdersBoard.vue`.
- `CrmBoardHeader.vue` from `CrmOrdersBoard.vue`.
- `CrmContactPanel.vue` from `CrmOrderEditor.vue`.
- `ProductHeader.vue` from `ProductEditor.vue`.
- `BomLinesTable.vue` from `SpecificationTab.vue`.
- `PurchaseOrdersTable.vue` from `PurchaseOrderList.vue`.
- `ProductionNeedsDrawer.vue` from `PurchaseOrderList.vue`.
- `Topbar.vue`, `SidebarNav.vue`, `GlobalSearchCommand.vue` from `DashboardLayout.vue`.

## Files that should remain page-level only

- `frontend/src/views/Inventory/ProductEditor.vue`
  - Keep orchestration, load/save, tabs state only.
- `frontend/src/views/CRM/CrmOrdersBoard.vue`
  - After split, keep page layout and high-level state only.
- `frontend/src/views/CRM/CrmOrderEditor.vue`
  - After split, keep route param, load/save orchestration only.
- `frontend/src/views/Purchases/PurchaseOrderList.vue`
  - After split, keep page composition only.
- `frontend/src/layouts/DashboardLayout.vue`
  - After split, keep layout composition only.

## Backend split recommendations

- `backend/app/api/order_routes.py`
  - Split into `crm_order_routes.py`, `sales_order_routes.py`, `order_contact_routes.py`, `order_activity_routes.py` if route count keeps growing.
- `backend/app/api/product_routes.py`
  - Split product core CRUD from variants/files/procurement endpoints.
- Keep heavy calculation logic in `backend/app/services/*`, not in routes.
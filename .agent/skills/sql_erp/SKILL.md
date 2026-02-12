# SQL ERP Skill

Advanced skills for database management in the ERP system.

## Core Capabilities
- **Schema Design**: Creating normalized tables for inventory, accounting, and CRM.
- **SQLAlchemy ORM**: Implementing complex relationships (One-to-Many, Many-to-Many) with proper cascade logic.
- **Migrations**: Managing Alembic versions safely to prevent data loss.
- **Query Optimization**: Using `joinedload` and `subqueryload` to prevent N+1 issues.

## Best Practices
- Use UUID4 for primary keys to support distributed data.
- Index frequently searched columns (SKU, name, category, company_id).
- Use `Numeric` for monetary values instead of `Float`.
- Always implement soft-deletion patterns where historical data is required.

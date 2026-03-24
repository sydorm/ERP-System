# Critical Thinking Skill

Advanced logic validation and architectural decision-making for complex systems.

## Core Capabilities
- **Logic Auditing**: Identifying potential flaws in business logic (e.g., negative stock, currency mismatches).
- **Edge Case Analysis**: Predicting system behavior in unusual scenarios (concurrency locks, partial data updates).
- **Security Reasoning**: Analyzing authentication and company isolation boundaries.
- **Self-Correction**: Detecting and resolving implementation loops and property name mismatches.

## Best Practices
- **Environment Awareness**: Be cognizant of OS-specific issues (e.g., path encoding on Windows vs Linux) and deployment gaps (Remote server vs Local DB).
- **Manual Backups**: If automated tools (like Alembic autogenerate) fail due to environmental constraints, be ready to manually draft structural changes based on existing patterns.
- Ask "What if?" for every data mutation (What if the user clicks twice? What if the network fails?).
- Verify naming consistency across the entire stack (DB -> Backend -> Frontend).
- Double-check calculations involving decimals and precision.
- Prioritize data integrity over UI convenience in critical business paths.

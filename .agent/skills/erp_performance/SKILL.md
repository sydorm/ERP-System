# ERP Performance Skill

Optimization strategies for high-performance enterprise resource planning systems.

## Core Capabilities
- **Backend Optimization**: SQL profiling and N+1 query elimination.
- **Caching**: Implementing Redis strategies for frequently accessed dictionary data.
- **Frontend Speed**: Virtual scrolling for large lists and selective component rendering.
- **Bundle Optimization**: Managing dependencies and using code splitting.

## Best Practices
- Batch database writes when processing bulk operations (e.g., variant generation).
- Use server-side pagination for any collection potentially exceeding 100 items.
- Debounce search and filter inputs to reduce API traffic.
- Profile and monitor API response times in different environments (dev/prod).

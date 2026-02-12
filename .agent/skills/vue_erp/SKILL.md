# Vue ERP Skill

High-efficiency frontend development for ERP interfaces using Vue 3 and Element Plus.

## Core Capabilities
- **Dynamic Forms**: Building complex, validated forms for document entry (Orders, Invoices).
- **Advanced Tables**: Implementing server-side sorting, filtering, and mass actions.
- **Component Coordination**: Managing complex parent-child interactions and event emitting.
- **Reactivity Management**: Handling deep state updates without triggering infinite loops.

## Best Practices
- Follow the "Single Source of Truth" principle for state (use Pinia or props/emit).
- **Reactivity Loop Prevention**: When using `watch` to sync props with internal state, always compare the new value with the current state (e.g., using `JSON.stringify`) before updating to prevent infinite recursive loops.
- Modularize large pages into functional sub-components (e.g., Header, Table, Summary).
- **Icon Management**: Consolidate all `@element-plus/icons-vue` imports in a single block at the top of the script to prevent module loading failures in some build environments.
- Implement optimistic UI updates for better user perceived performance.
- Use `v-loading` and disabled states during API transitions.

# ERP Development Strict Rules

1.  **Visual Verification**: Any UI change MUST be verified via Browser MCP on `http://70.34.247.20:5173/` before pushing.
2.  **Layout Constants**:
    *   Sidebar width: `260px`.
    *   Top Navbar height: `64px`.
    *   Sticky elements must account for these offsets.
3.  **Modern SaaS Style**:
    *   Use `backdrop-filter: blur(16px)` for headers.
    *   Standard border-radius: `12px` or `14px`.
    *   Primary color: `#6366F1` (Indigo).
    *   Success color: `#10B981` (Emerald).
4.  **Button Standards**:
    *   Draft/Secondary: `.btn-draft-modern`.
    *   Primary/Post: `.btn-primary-modern`.
5.  **Commit Policy**: Commits must be atomic and verified.

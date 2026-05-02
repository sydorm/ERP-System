# Nexora ERP Design Standards (2026 Edition)

1.  **Grid & Layout**:
    *   Container padding: `32px`.
    *   Card border-radius: `16px`.
    *   Card box-shadow: `0 10px 30px rgba(15, 20, 34, 0.03)`.
    *   Sticky Header height: must touch the top navbar (`64px` offset if global header is active).

2.  **Color Palette**:
    *   Primary (Indigo): `#7367f0`.
    *   Primary Gradient: `linear-gradient(135deg, #7367f0 0%, #a8a1f8 100%)`.
    *   Success (Emerald): `#28c76f`.
    *   Warning (Amber): `#ff9f43`.
    *   Danger (Red): `#ea5455`.
    *   Background Page: `#F8F9FA`.
    *   Background Input: `#F8FAFC`.

3.  **Button Standard "VARIANT B" (Primary Action)**:
    *   **Class**: `.btn-nexora-primary` or `.btn-vuexy-glow`.
    *   **Background**: `linear-gradient(135deg, #7367f0 0%, #a8a1f8 100%)`.
    *   **Shadow**: `0 8px 25px -8px #7367f0`.
    *   **Font**: Weight `700`, size `14px`, letter-spacing `-0.01em`.
    *   **Interaction**: 
        *   Hover: `transform: translateY(-2px); box-shadow: 0 10px 30px -10px #7367f0;`.
        *   Active: `transform: scale(0.98);`.

4.  **Secondary Action (Ghost Style)**:
    *   **Class**: `.btn-ghost-modern`.
    *   **Border**: `1px solid #E2E8F0`.
    *   **Hover**: `background: #F8FAFC; border-color: #CBD5E1; color: #7367f0;`.

5.  **Iconography (Standard Variant 5)**:
    *   **Style**: Gradient Stroke (thin minimalist lines).
    *   **Colors**: Indigo-to-Violet linear gradient (`#7367f0` to `#a8a1f8`).
    *   **Size**: Primary icons `24px`, secondary/inline icons `18px`.

6.  **Typography (Hierarchy & Styles)**:
    *   **Font Family**: 'Public Sans' or 'Inter' (Sans-serif).
    *   **Display Texts**: Light weight (300), large size (32px-48px), grey-blue color.
    *   **Headings**: Bold (700/800), charcoal color (`#2D3748`).
    *   **Body Text**: Medium weight (400), grey-blue color (`#4A5568`).
    *   **Accent Border**: Section titles must have a `3px` indigo left border.

7.  **List & Table Design (Standard Reference)**:
    *   **Layout**: High-density rows with multi-line data stacking (e.g., Name on top, ID/Email below).
    *   **Avatars**: Rounded grey squares with centered initials.
    *   **Cells**: Use vertical stacking for related info to save horizontal space.
    *   **Status Badges**: Small green "pills" with an active status dot indicator.
    *   **Typography**: Bold for primary info, smaller muted font for secondary info.

8.  **Form Controls (Standard Variant 2 - Glass Focus)**:
    *   **Inputs/Selects**: Rounded corners `10px`, light background `#F8FAFC`.
    *   **Focus State**: Glowing indigo border (`#7367f0`), soft outer shadow/aura, and slightly lightened background.
    *   **Checkboxes/Switches**: Use the same indigo gradient as Button B when active.

9.  **Sidebar & Navigation (Standard Variant 2 - Deep Indigo)**:
    *   **Background**: Solid Deep Indigo (`#2f3349` or similar dark-violet/indigo shade).
    *   **Text/Icons**: White or light lavender for readability.
    *   **Active Item**: Gradient highlight matching Button B, with a soft glow effect.
    *   **Width**: Fixed at `260px` with a clean border separation from the main content.

10. **Modals & Dialogs (Standard Reference - Glassmorphism)**:
    *   **Style**: Frosted Glass (Background blur `15px`, opacity `0.8`).
    *   **Border-radius**: `20px`.
    *   **Buttons**: Use Button B for primary actions, Ghost style for cancel.
    *   **Shadow**: Deep soft glow shadow (`rgba(15, 20, 34, 0.15)`).

11. **Unified Design System Summary**:
    *   **Primary Action**: Button Variant B (Gradient Glow).
    *   **Iconography**: Variant 5 (Gradient Stroke).
    *   **List Layout**: High-density stacked data (User's reference).
    *   **Form Controls**: Variant 2 (Glass Focus).
    *   **Navigation**: Variant 2 (Deep Indigo Sidebar).
    *   **Popups**: Glassmorphism (Frosted Glass).

12. **Development Policy**:
    *   AI MUST read this file before creating any new UI component.
    *   No ad-hoc styles. All elements must use these tokens.
    *   Commits must be atomic and verified visually.

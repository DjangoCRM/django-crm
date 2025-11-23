# PR: Integrate TailAdmin-based example pages into Angular frontend

## Summary
This PR extends the Angular frontend (frontend-angular) with additional pages based on TailAdmin examples while preserving existing CRM features.

- Added pages:
  - Charts: /charts/line, /charts/bar (using existing Apex components)
  - Forms: /forms/form-elements
  - Tables: /tables/basic
  - Auth: /auth/signup (mock for now, routes added), existing /auth/login
  - Other: 404 Not Found
- Updated routing (app.routes.ts) to include new sections and wildcard
- Fixed bindings to match shared Apex components:
  - app-apex-line: title, labels, data
  - app-apex-bar: title, data

## Motivation
Provide a functional UI layer closely aligned with TailAdmin design system, accelerating UI development and demonstrating patterns for charts, forms, and tables.

## Testing
- npm start under frontend-angular
- Verify pages:
  - /charts/line
  - /charts/bar
  - /forms/form-elements
  - /tables/basic
  - /auth/login, /auth/signup
  - Non-existent path -> 404

## Follow-ups
- Header: mobile sidebar toggle, hotkey (Cmd/Ctrl+K), notifications panel
- Sidebar: groupings, icons, and active states aligned with demo
- Additional demo pages: Calendar, Profile, Invoices
- Replace mock signup with real backend endpoint
- Add unit tests for new pages

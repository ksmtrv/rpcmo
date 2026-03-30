# Implementation Tasks: Authentication

## Tasks

### Product / Spec
- [ ] Add authentication as a first-class module in `openspec/project.md`
- [ ] Require login before any financial data screen is accessible
- [ ] Define registration, login, logout, and current-user endpoints
- [ ] Define user-owned data isolation rules across all modules

### Backend
- [ ] Create `User` model with `email`, `password_hash`, `full_name`, `status`
- [ ] Add password hashing and credential validation
- [ ] Implement `POST /auth/register`
- [ ] Implement `POST /auth/login`
- [ ] Implement `POST /auth/logout`
- [ ] Implement `GET /auth/me`
- [ ] Replace demo identity resolution with authenticated `current_user`
- [ ] Protect all financial routes with auth dependency

### Frontend
- [ ] Add login page
- [ ] Add registration page
- [ ] Add logout action
- [ ] Redirect unauthenticated users to login
- [ ] Persist auth state across page reloads

## Acceptance Criteria

- A new user can register and log in with email and password
- Unauthenticated user cannot access imports, transactions, reports, recurring payments, forecast, or backups
- Authenticated user sees only own financial data
- Logout removes access to protected routes until next login

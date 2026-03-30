# Implementation Tasks: Import Management

## Tasks

### Backend
- [ ] Create `import_sessions` table and repository
- [ ] Create `mapping_templates` table and repository
- [ ] Implement CSV parser with encoding and delimiter detection
- [ ] Implement `POST /imports/upload` with preview response
- [ ] Implement `POST /imports/:id/confirm`
- [ ] Normalize dates, amounts, descriptions, and directions
- [ ] Implement duplicate hash computation
- [ ] Persist import counters: imported, skipped, duplicates

### Frontend
- [ ] Import page with file upload
- [ ] Column-mapping wizard
- [ ] Preview table
- [ ] Import confirmation screen with counters

## Acceptance Criteria

- User can upload a CSV and get preview without creating transactions
- User can confirm import after checking mapping
- Duplicate transactions are skipped safely
- Import result shows imported, skipped, and duplicate counts
- Mapping can be reused for future imports

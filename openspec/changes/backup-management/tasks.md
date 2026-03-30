# Implementation Tasks: Backup Management

## Tasks

### Backend
- [ ] Create `backup_files` table and repository
- [ ] Implement `POST /backups/export`
- [ ] Serialize all user-owned entities into backup archive
- [ ] Implement `POST /backups/import`
- [ ] Validate archive structure and ownership before restore

### Frontend
- [ ] Backup page
- [ ] Export action
- [ ] Import action with restore summary

## Acceptance Criteria

- User can export own data into backup file
- User can restore backup explicitly
- Restore validates structure before writing data
- Backup operations do not expose another user's data

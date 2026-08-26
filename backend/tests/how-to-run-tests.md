# How to Run Tests

## Quick Tests (SQLite)

```bash
export TEST_MODE=test
python -m pytest backend/tests/ -v -m "not slow" --tb=short
```

## Full Tests (PostgreSQL + Testcontainers)

```bash
export TEST_MODE=slow
python -m pytest backend/tests/ -v -m "slow" --tb=short
```

## Run All Tests

```bash
export TEST_MODE=test
python -m pytest backend/tests/ -v --tb=short
```

## Test Runner Script

```bash
python run_dual_tests.py --mode test --path backend/tests/
python run_dual_tests.py --mode slow --path backend/tests/
python run_dual_tests.py --mode both --path backend/tests/
```

## Test Configuration

Set `TEST_MODE` environment variable:
- `TEST_MODE=test` - SQLite quick tests with mocked PostgreSQL types
- `TEST_MODE=slow` - PostgreSQL + PostGIS via Testcontainers

Default: `TEST_MODE=test` (set in `.env`)

## Files Involved

### Core Configuration
- `backend/tests/test_config.py` - Test mode detection, environment config
- `backend/app/config.py` - App settings with test mode support
- `backend/app/db.py` - Database engine with test mode awareness
- `backend/app/main.py` - Middleware with test mode mock DB
- `backend/.env` - Environment variables (includes TEST_MODE)

### Test Fixtures
- `backend/tests/conftest.py` - Main test fixtures, service mocking
- `backend/tests/conftest_sqlite.py` - SQLite quick test fixtures
- `backend/tests/conftest_postgres.py` - PostgreSQL Testcontainers fixtures

### Test Files
- `backend/tests/test_admin.py` - Admin endpoints RBAC
- `backend/tests/test_masjids.py` - Masjid CRUD RBAC
- `backend/tests/test_people.py` - People CRUD RBAC
- `backend/tests/test_photos.py` - Photo upload/delete RBAC
- `backend/tests/test_programs.py` - Program CRUD RBAC
- `backend/tests/test_schedules.py` - Salat schedule CRUD RBAC
- `backend/tests/test_people.py` - People CRUD RBAC
- `backend/tests/test_photos.py` - Photo CRUD RBAC
- `backend/tests/test_rbac_permissions.py` - Unit tests for auth permissions
- `backend/tests/test_sync.py` - Sync API and service logic tests

### Runner
- `run_dual_tests.py` - Test runner with mode selection

## Items Remaining

### Mock Service Completeness
- Add missing service methods to `conftest.py` mocks:
  - `get_all()` for all services
  - `get_programs_by_masjid()`, `get_program()`, `upload_photo()`, etc.
  - Complete `person_service`, `photo_service`, `sync_service` mocks

### Permission Enforcement
- Admin endpoints: Masjid Editor should be blocked for other masjid_id (2 tests fail)
- UUID validation: Fix invalid UUID formats in test data (causes 422 instead of 403)

### Service Interface Coverage
- `program_service`: `get_all()`, `get_programs_by_masjid()`, `get_program()`
- `person_service`: `get_all()`, `get_persons_by_masjid()`, `get_person()`
- `photo_service`: `upload_photo()`, `delete_photo()`
- `sync_service`: `get_snapshot()`, `process_mutations()`
- `masjid_service`: `list_masjids()`, `get_masjid()`, `create_masjid()`, `update_masjid()`, `delete_masjid()`
- `salat_service`: `get_all()`, `get_by_masjid()`, `create_schedule()`, `update_schedule()`, `delete_schedule()`

### PostgreSQL Full Tests
- Docker/Testcontainers setup for CI
- PostGIS extension initialization
- Transaction rollback isolation
- Real spatial/JSONB operation tests

### CI Integration
- GitHub Actions workflow for both test modes
- Docker service for PostgreSQL tests
- Test result reporting
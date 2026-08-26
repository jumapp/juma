# Plan Name
Masjid Save and Display Frontend-Backend Implementation

## Description
Implement complete masjid management functionality including data collection, storage, and display across all platforms. This involves creating comprehensive backend APIs with SQLAlchemy ORM, implementing frontend forms for masjid data entry, and building display components for showing masjid information with salat schedules. The solution must support offline-first operations, role-based access control, and cross-platform consistency for iOS, Android, and Web users.

## Design

### Backend Architecture

**Core Data Models (SQLAlchemy with PostgreSQL/PostGIS):**

1. **Masjid Table**
   - UUID primary key with composite indexes on latitude/longitude
   - Normalized transportation fields: `accessible_by_public_transport`, `accessibility_details`, `highway_masjid`, `on_road_masjid`, `map_id`
   - Filterable operating hours: `opensAt`, `closesAt`, `is24Hours`, `ramadanAdjustedHours`
   - photos array (max 5 per masjid), other_items text, metadata JSON
   - Spatial index for location-based discovery queries

2. **MasjidProgram Table (Separate entity)**
   - Program types: `maktab`, `elder_maktab`, `tafseer`, `hadith`, `other_course`
   - Schedule patterns with frequency and timing details
   - Instructor relationships (references `MasjidPerson`), participant limits
   - Index on `type` and `is_active` for fast filtering

3. **SalatSchedule Table (Simplified)**
   - All 5 required salat times: `fajr`, `zuhr`, `asr`, `maghrib`, `isha`
   - Both `adhan_time` (client-calculated) and `iqama_time` (server-stored)
   - Composite unique index on `masjid_id` + `salat_name`
   - Frontend responsibility for adhan calculation, server stores both times

4. **MasjidPerson Table (Enhanced)**
   - Complete contact info including phone numbers
   - Access levels: `admin`, `general`, `viewer`, `editor`
   - Roles: `imam`, `muazzin`, `committee_member`, `other`
   - Skills, bio, photo_url, is_active flags
   - Composite index on `masjid_id`, `role`, `access_level`, `is_active`

### Frontend Architecture (React Native + Expo Router)

1. **Multi-Step Masjid Form** (6 steps)
   - Step 1: Basic info (name, address, coordinates via map picker)
   - Step 2: Transportation details + accessibility text
   - Step 3: Salat schedules (iqama inputs, adhan auto-calculated)
   - Step 4: Program offerings (Maktab, Tafseer, Hadith, etc.)
   - Step 5: Amenities, parking, other details
   - Step 6: Committee members (optional)

2. **Salat Calculation Service**
   - Local adhan time calculation using established algorithms
   - Real-time display of both adhan and iqama times
   - Frontend decides which salats to show based on current time

3. **Display Components**
   - Masjid detail cards with photos, address, operating hours
   - Map view with location pins and filtering
   - Salat schedule display (upcoming and past)
   - Committee member sections with access level filtering

### Key Technical Features

**Performance Optimizations:**
- Composite indexes on all filterable field combinations
- PostGIS spatial queries for location-based discovery
- Boolean fields indexed for rapid filtering
- Client-side adhan calculation reduces server load

**User Experience:**
- Offline-first with local queue for all mutations
- Progressive form with real-time validation
- Cross-platform consistency (iOS, Android, Web)
- Role-based access control for all operations

**Security & Compliance:**
- Server-authoritative data with client-owned presentation
- Audit trail for all masjid changes
- Photo validation and GCS integration
- GDPR-compliant data handling

## Implementation Plan

1. **Phase 1: Database Setup (Weeks 1-2) - ✅ COMPLETED**
   - ✅ Create PostgreSQL database with PostGIS extension
   - ✅ Implement SQLAlchemy models with all relationships
   - ✅ Run database migrations (via init_db.py instead of Alembic)
   - ✅ Set up database indexes and constraints
   - ✅ Implement seed data for testing

2. **Phase 2: Backend APIs (Weeks 3-4) - ✅ MOSTLY COMPLETED**
   - ✅ Implement FastAPI CRUD endpoints for all entities
   - ✅ Add role-based authorization middleware
   - ✅ Implement photo upload service with GCS/local integration
   - ✅ Add validation and error handling
   - ✅ Implement sync endpoints for offline support
   - ✅ Implement admin endpoints (role requests, audit events)
   - ⬜ Create comprehensive API tests (remaining)

3. **Phase 3: Frontend Core (Weeks 5-6) - 🔄 IN PROGRESS (Detailed in `phase3-frontend-core.md`)**
   - 3.0: Backend sync prerequisite fixes & tests
   - 3.1: Scaffolding, config, and environment setup
   - 3.2: Full design tokens theming system & ThemeProvider
   - 3.3: i18n localization (EN/HI/UR + RTL)
   - 3.4: Reusable core UI component kit (~16 components)
   - 3.5: Typed API client with error normalization and auth injection
   - 3.6: Dev-mode auth service, session persistence, role switcher & RBAC permissions
   - 3.7: TanStack Query data layer with offline persistence
   - 3.8: Offline cache and persistent outbox sync queue

4. **Phase 4: Masjid Form Implementation (Weeks 7-8) - ⬜ NOT STARTED**
   - Implement multi-step form with all 6 steps
   - Add map integration for coordinate selection
   - Build salat calculation service
   - Implement form validation and error handling

5. **Phase 5: Display Components (Weeks 9-10) - ⬜ NOT STARTED**
   - Build masjid detail cards and map views
   - Implement program and committee member displays
   - Create salat schedule viewer with filtering
   - Add search and discovery interfaces

6. **Phase 6: Integration & Testing (Weeks 11-12) - ⬜ NOT STARTED**
   - Connect frontend to backend APIs
   - Implement end-to-end user workflows
   - Add comprehensive testing (unit, integration, e2e)
   - Perform offline/online sync testing

7. **Phase 7: Production Deployment (Week 13) - ⬜ NOT STARTED**
   - Deploy to staging environment
   - Run smoke tests and user acceptance testing
   - Fix critical issues and optimize performance
   - Deploy to production

## Task Breakdown

- [x] **Database Setup**
  - [x] Create PostgreSQL database with PostGIS extension
  - [x] Implement SQLAlchemy models for Masjid, MasjidProgram, SalatSchedule, MasjidPerson
  - [x] Run database migrations (via init_db.py)
  - [x] Set up composite indexes and constraints
  - [x] Create seed data for testing

- [x] **Backend API Implementation** (mostly complete)
  - [x] Implement FastAPI CRUD endpoints for all entities
  - [x] Add role-based authorization and validation
  - [x] Create photo upload service with GCS/local integration
  - [x] Implement sync endpoints for offline support
  - [x] Implement admin endpoints (role requests, audit events)
  - [ ] Write comprehensive API tests

- [ ] **Frontend Core Infrastructure**
  - [ ] Set up Expo project with existing architecture patterns
  - [ ] Implement theming system and common UI components
  - [ ] Build offline support (AsyncStorage cache + sync queue)
  - [ ] Create authentication service with role management

- [ ] **Masjid Multi-Step Form**
  - [ ] Implement all 6 form steps with validation
  - [ ] Add map integration for address/coordinate selection
  - [ ] Build salat calculation service (client-side)
  - [ ] Implement form state management and persistence

- [ ] **Program Management**
  - [ ] Create program form components
  - [ ] Implement CRUD for Maktab, Tafseer, Hadith, etc.
  - [ ] Add schedule pattern management
  - [ ] Build instructor assignment UI

- [ ] **Salat Schedule Implementation**
  - [ ] Implement SalatSchedule CRUD operations
  - [ ] Create frontend salat calculator service
  - [ ] Build salat display components with filtering
  - [ ] Add iqama time input forms

- [ ] **Person/Committee Management**
  - [ ] Create person form with phone number support
  - [ ] Implement role-based access level management
  - [ ] Build committee member display and filtering
  - [ ] Add active/inactive status management

- [ ] **Masjid Display Components**
  - [ ] Create masjid detail cards with all fields
  - [ ] Implement map view with clustering and filters
  - [ ] Build discovery/list views with search
  - [ ] Add photo gallery with upload capabilities

- [ ] **Offline Support**
  - [ ] Implement local queue for all mutations
  - [ ] Add connectivity change detection
  - [ ] Build retry mechanism for failed syncs
  - [ ] Create offline status indicators

- [ ] **Testing & Quality Assurance**
  - [ ] Write unit tests for all services and components
  - [ ] Implement integration tests for API endpoints
  - [ ] Create end-to-end tests for user workflows
  - [ ] Perform offline/online sync testing
  - [ ] Run performance and accessibility testing

- [ ] **Deployment & Production**
  - [ ] Deploy to staging environment
  - [ ] Run smoke tests and user acceptance testing
  - [ ] Monitor performance and fix issues
  - [ ] Deploy to production with monitoring

## Ready-made Prompts

### Implementation Status (as of Phase 1-2 Completion)

**Backend Implementation Summary:**

The backend is implemented as a modular FastAPI application with the following structure:

```
backend/
├── app/
│   ├── config.py          # Settings management (pydantic-settings)
│   ├── db.py              # Database engine and session management
│   ├── main.py            # FastAPI application entry point
│   ├── health_check.py    # Health check endpoints
│   ├── auth.py            # Authentication and authorization
│   ├── init_db.py         # Database initialization and seeding
│   ├── enums.py           # Domain enumerations
│   ├── ddl.py             # DDL triggers for updated_at timestamps
│   ├── models/            # SQLAlchemy models
│   │   ├── base.py        # Base model with UUID and timestamps
│   │   ├── masjid.py      # Masjid model with PostGIS
│   │   ├── salat.py       # SalatSchedule model
│   │   ├── person.py      # MasjidPerson model
│   │   ├── program.py     # MasjidProgram and ProgramSchedule models
│   │   ├── photo.py       # MasjidPhoto model
│   │   ├── audit.py       # AuditEvent model
│   │   └── outbox.py      # OutboxEvent model
│   ├── repositories/      # Data access layer
│   │   └── __init__.py    # Generic repositories
│   ├── services/          # Business logic layer
│   │   ├── __init__.py    # All domain services
│   │   ├── auth.py        # Auth service
│   │   └── photo_service.py # Photo storage (local/GCS)
│   └── routers/           # FastAPI route definitions
│       └── __init__.py    # All API routes
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # Backend documentation
```

**Key Implementation Details:**

1. **Database Models (Phase 1 Complete):**
   - All models use UUID primary keys with proper indexes
   - Masjid model includes PostGIS spatial columns with spatial index
   - Composite indexes on all filterable field combinations
   - DDL triggers for automatic `updated_at` timestamp updates
   - Unique constraints on composite fields (masjid_id + salat_name, etc.)

2. **Authentication & Authorization (Phase 2 Complete):**
   - Dev mode authentication with super_admin_token
   - Role-based access control: `super_admin`, `masjid_editor`, `viewer`
   - Permission system for all CRUD operations
   - Ready for production identity provider integration

3. **API Endpoints (Phase 2 Complete):**
   - Masjids: `GET/POST/PATCH/DELETE /api/v1/masjids` with spatial filtering
   - Salat Schedules: `GET/POST/PATCH/DELETE /api/v1/schedules`
   - Programs: `GET/POST/PATCH/DELETE /api/v1/programs`
   - People: `GET/POST/PATCH/DELETE /api/v1/people`
   - Photos: `POST/DELETE /api/v1/photos/masjids/{id}/photos`
   - Sync: `GET/POST /api/v1/sync` for offline support
   - Admin: `GET/PATCH /api/v1/admin/*` for role requests and audit logs

4. **Business Logic (Phase 2 Complete):**
   - Service layer with audit trail for all changes
   - Outbox pattern for domain events
   - Photo validation and storage (local/GCS)
   - Sync service for offline-first operations
   - Comprehensive validation and error handling

5. **Environment Configuration:**
   - `.env` file support via pydantic-settings
   - `.env.example` template provided
   - All secrets managed through environment variables
   - No Alembic migrations - uses init_db.py for schema creation

**Remaining Work:**
- Comprehensive API tests (unit, integration)
- Frontend implementation (Phases 3-7)
- Production deployment configuration

### Task: Database Setup
```
You are a backend developer implementing the database setup for the doonjuma project. Your task is to:

1. Create a PostgreSQL database with PostGIS extension
2. Implement SQLAlchemy models for these entities:
   - Masjid (with normalized transportation fields, operating hours, spatial coordinates)
   - MasjidProgram (separate table for programs like Maktab, Tafseer, Hadith)
   - SalatSchedule (5 salat times with adhan/iqama, unique constraint per masjid)
   - MasjidPerson (with phone numbers, access levels, roles)

3. Set up indexes for performance:
   - Composite indexes on all filterable field combinations
   - Spatial index on coordinates
   - Unique constraints where appropriate

4. Create initial seed data for testing

5. Ensure the database follows the existing repository patterns

Return: Complete database schema SQL and SQLAlchemy model definitions
```

### Task: Backend API Implementation
```
You are a FastAPI developer implementing the backend APIs for masjid management. Your task:

1. Create FastAPI routers for all entities (Masjid, Program, SalatSchedule, Person)
2. Implement CRUD endpoints with proper validation
3. Add role-based authorization middleware
4. Create photo upload service with GCS integration
5. Implement sync endpoints for offline support (queue management)
6. Add comprehensive error handling and response formats
7. Write OpenAPI documentation

Key endpoints to implement:
- Masjid: GET/POST/PATCH/DELETE /api/v1/masjids
- Programs: GET/POST/PATCH/DELETE /api/v1/programs
- Salat schedules: GET/POST/PATCH/DELETE /api/v1/schedules
- Persons: GET/POST/PATCH/DELETE /api/v1/people
- Photos: POST/DELETE /api/v1/masjids/{id}/photos
- Sync: GET/POST /api/v1/sync

Return: Complete FastAPI implementation with routes, services, and validation
```

### Task: Frontend Core Infrastructure
```
You are a React Native developer setting up the core infrastructure for the doonjuma frontend. Your task:

1. Set up Expo project with existing architecture patterns
2. Implement theming system with light/dark mode support
3. Create common UI components (cards, buttons, forms)
4. Build offline support infrastructure:
   - AsyncStorage cache for local data
   - Sync queue for mutations
   - Connectivity change detection
   - Offline status indicators

5. Implement authentication service with role management
6. Set up Expo Router for navigation
7. Integrate existing components from the codebase

Return: Complete frontend project setup with all core services
```

### Task: Masjid Multi-Step Form
```
You are a React Native developer implementing the masjid multi-step form. Your task:

1. Create 6-step form component with progressive validation
2. Implement Step 1: Basic info (name, address, map picker for coordinates)
3. Step 2: Transportation details (checkboxes + accessibility text)
4. Step 3: Salat schedules (iqama time inputs, adhan auto-calculated display)
5. Step 4: Program offerings (multi-select with schedule builder)
6. Step 5: Amenities, parking, other details
7. Step 6: Committee members (optional with roles)

8. Implement form state management with auto-save to local queue
9. Add real-time validation and error handling
10. Create form navigation and progress indicators

Key features:
- Map integration for coordinate selection
- Salat calculator integration
- Offline support (save to queue)
- Role-based field visibility

Return: Complete multi-step form implementation
```

### Task: Program Management
```
You are a React Native developer implementing program management for masjids. Your task:

1. Create program management UI components
2. Implement CRUD for different program types:
   - Maktab (children Islamic education)
   - Tafseer (Quran interpretation)
   - Hadith (religious teachings)
   - Other courses and elder Maktab

3. Add schedule pattern management:
   - Day/time selection
   - Frequency options (daily, weekly, monthly)
   - Instructor assignment from committee members

4. Implement participant management (max limits)
5. Add filtering and search capabilities
6. Create program display components for masjid details

Key features:
- Multi-step program form
- Schedule builder interface
- Instructor selection with search
- Active/inactive status management

Return: Complete program management implementation
```

### Task: Salat Schedule Implementation
```
You are a React Native developer implementing salat schedule management. Your task:

1. Create SalatSchedule CRUD operations
2. Implement client-side salat calculation service:
   - Local adhan time calculation using established algorithms
   - Real-time display of both adhan and iqama times
   - Accuracy across different locations and dates

3. Build frontend salat display components:
   - Show all 5 salat times (adhan + iqama)
   - Filter logic for current/future/previous salats
   - Responsive design for all screen sizes
   - Real-time clock and remaining time display

4. Implement iqama time input forms with validation
5. Add schedule synchronization between frontend and backend
6. Create schedule management for different masjids

Key features:
- Local adhan calculation (no server dependency)
- Flexible display options
- Offline support for schedule updates
- Location-based time calculation

Return: Complete salat schedule implementation
```

### Task: Person/Committee Management
```
You are a React Native developer implementing person and committee management. Your task:

1. Create person form with complete contact information:
   - Name, roles (imam/muazzin/committee)
   - Phone numbers (primary, alternate)
   - Email addresses
   - Access levels (admin/general/viewer/editor)

2. Implement committee member management:
   - Skills and bio fields
   - Photo upload support
   - Active/inactive status toggles
   - Role-based filtering

3. Create display components for committee members:
   - Individual member cards
   - Role-based filtering (imams, muazzins, committee)
   - Contact information display
   - Skills and bio sections

4. Add permission controls:
   - Role-based access to edit functions
   - Visibility controls based on access levels
   - Admin-only features

Key features:
- Enhanced contact information
- Role-based access control
- Skills and bio management
- Photo support
- Permission-based UI

Return: Complete person and committee management implementation
```

### Task: Offline Support
```
You are a React Native developer implementing offline support for the doonjuma project. Your task:

1. Implement offline data storage:
   - AsyncStorage for local data caching
   - Local database for complex data
   - Conflict resolution strategies

2. Create sync queue system:
   - Queue for all mutations (create, update, delete)
   - Idempotency keys for duplicate prevention
   - Retry mechanisms with exponential backoff
   - Connection change detection

3. Build sync service:
   - Batch processing of queued items
   - Error handling and recovery
   - Progress tracking and status updates
   - User notifications for sync status

4. Implement offline-first UI:
   - Offline status indicators
   - Sync progress indicators
   - Conflict resolution dialogs
   - Retry action buttons

Key features:
- Complete offline capability
- Automatic sync when online
- Conflict resolution
- User feedback for sync status
- Graceful degradation

Return: Complete offline support implementation
```

### Task: Testing & Quality Assurance
```
You are a QA engineer implementing comprehensive testing for the doonjuma project. Your task:

1. Write unit tests for all backend services:
   - Service layer unit tests
   - Repository tests
   - Validation and business logic tests

2. Implement integration tests:
   - API endpoint testing
   - Database relationship tests
   - Authentication and authorization tests

3. Create end-to-end tests:
   - User workflow testing (masjid creation, editing)
   - Offline/online sync testing
   - Role-based access testing
   - Cross-platform testing scenarios

4. Performance testing:
   - Database query performance
   - API response times
   - Frontend rendering performance

5. Accessibility testing:
   - Screen reader compatibility
   - Keyboard navigation
   - Color contrast and typography

Return: Complete testing strategy and implementation
```

### Task: Deployment & Production
```
You are a DevOps engineer implementing deployment for the doonjuma project. Your task:

1. Set up CI/CD pipeline:
   - GitHub Actions for linting, testing, building
   - Environment-specific configurations
   - Database migration automation

2. Configure production deployments:
   - Backend: Cloud Run with managed PostgreSQL
   - Frontend: Netlify static hosting
   - Database migrations and backups
   - Monitoring and logging setup

3. Implement staging environment:
   - Clone production config with test data
   - Performance testing before production
   - User acceptance testing pipeline

4. Create rollback and recovery procedures:
   - Database backup and restore
   - Blue-green deployment strategy
   - Monitoring and alerting setup

Key considerations:
- Security and compliance
- Performance optimization
- Cost management
- Disaster recovery

Return: Complete deployment strategy and configuration
```
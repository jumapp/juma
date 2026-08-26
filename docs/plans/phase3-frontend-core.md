# Phase 3: Frontend Core Implementation Plan & Architecture Decisions

This document details the architecture, design decisions, and step-by-step implementation for **Phase 3: Frontend Core Infrastructure** (covering sub-phases 3.0 through 3.8), unblocking Phases 4–6.

---

## 1. Context & Scope

- **Backend Status:** FastAPI backend with PostgreSQL + PostGIS is implemented through Phase 2. Sub-phase 3.0 addresses specific sync wire-format and idempotency fixes needed before frontend integration.
- **Frontend Status:** Initialized with Expo SDK 54 (Expo Router, typed routes, static web export, PWA service worker). Phase 3 establishes the production-grade core infrastructure (theming, i18n, UI component kit, API client, dev-mode authentication, TanStack Query data layer, and offline outbox sync queue).
- **Target Platforms:** iOS, Android, and Web/PWA with strict cross-platform compatibility and offline-first support.

---

## 2. Key Architectural Decisions

| Decision Area | Decision | Rationale |
|---|---|---|
| **Authentication** | Dev-mode header-based auth (`X-Super-Admin-Token`, `X-Masjid-Editor-Token`, `X-Salat-Editor-Token`, `X-Viewer-Token`) with an in-app role switcher and persistent session store. | The backend is currently configured for dev-mode header authentication while the production identity provider is resolved. The frontend session module isolates this so production OIDC/Firebase can be slotted in seamlessly later. |
| **Data Layer** | TanStack Query (`@tanstack/react-query`) with `@tanstack/query-async-storage-persister`. | Provides industry-standard query caching, automatic stale-while-revalidate, retry logic with network awareness, and persistent cache across app restarts. |
| **i18n & RTL** | `i18next` + `react-i18next` + `expo-localization` supporting English (`en`), Hindi (`hi`), and Urdu (`ur`). | Meets the trilingual requirement from `docs/user-journey.md`. Urdu uses RTL layout via React Native `I18nManager` on native and `dir="rtl"` on web. Setting up i18n in Phase 3 ensures all subsequent screens are built localized from day one. |
| **Theming** | Comprehensive design tokens system (semantic color roles, spacing scale, radii scale, typography scale, elevations) with `ThemeProvider` supporting `system`, `light`, and `dark` modes with AsyncStorage persistence. | Clean abstraction over raw colors, ensures contrast compliance, dark mode readiness, and responsive typography. |
| **UI Component Kit** | Custom cross-platform core UI components (~16 components) built on React Native primitives with accessible touch targets (≥44px), semantic styling, and no heavy external UI library dependencies. | Guarantees predictable behavior across iOS, Android, and Web with minimal bundle footprint. |
| **Offline Sync Outbox** | Persistent mutation queue stored in AsyncStorage (`jumapp:outbox`) with idempotency keys (`uuid`), batch flushing to `POST /api/v1/sync/mutations`, exponential backoff, and reconnect triggers (`NetInfo` + `AppState`). | Guarantees zero data loss when users perform actions offline, reconciling operations via echoed mutation IDs upon connectivity restoration. |
| **Backend Sync Protocol** | Align backend `_process_single_mutation` with documented schema `{ id, entity, type: "CREATE"|"UPDATE"|"DELETE", payload }` and add server-side idempotency tracking table. | Fixes wire-format discrepancy where backend expected compound snake_case types and `data` field instead of `payload`. |

---

## 3. Sub-Phase Breakdown

### 3.0 Backend Sync Fixes (Prerequisite)
- **POST `/api/v1/sync/mutations`**: Update `_process_single_mutation` to dispatch on `(entity, type)` matching the documented `MutationItem` schema (`payload` attribute). Support `CREATE`, `UPDATE`, `DELETE` operations for masjids, salat schedules, programs, and people.
- **Server-Side Idempotency**: Track processed mutation IDs in a dedicated table or cache, returning `status: "duplicate"` on replays.
- **GET `/api/v1/sync/` Permissions**: Ensure authenticated read access for all valid roles to fetch the snapshot delta.
- **Pytest Coverage**: Add comprehensive tests for sync batch processing, idempotency deduplication, and error handling.

### 3.1 Scaffolding & Configuration
- Create clean directory hierarchy: `services/`, `lib/`, `providers/`, `i18n/`, `design/`, `components/ui/`.
- Configure `EXPO_PUBLIC_API_URL` and `EXPO_PUBLIC_DEV_SUPER_ADMIN_TOKEN` via `.env` / `lib/config.ts`.
- Set up root `ErrorBoundary` and `+not-found.tsx` fallback.

### 3.2 Theming System (Full Design Tokens)
- `design/tokens.ts`: Semantic colors (light/dark palettes with brand `#0a7ea4`), 6-step spacing scale, 4-step border radius scale, typography scale with platform font families, elevation shadows.
- `providers/theme-provider.tsx`: Persisted mode (`system` | `light` | `dark`), system change listener, `useTheme()` hook exposing active theme, tokens, and mode toggle.

### 3.3 i18n & Localization (EN / HI / UR + RTL)
- `i18n/index.ts`: Configured with `i18next`, auto-detecting device locale via `expo-localization`.
- Translation catalogs: `locales/en.json`, `locales/hi.json`, `locales/ur.json` (namespaces: `common`, `auth`, `home`, `explore`, `settings`, `sync`, `errors`).
- RTL support via `I18nManager.forceRTL` on native and web document direction handling.

### 3.4 UI Core Kit
Reusable, accessible, token-styled components:
- `Button`: Primary, secondary, outline, ghost, danger variants; sm/md/lg sizes; loading spinner; disabled state; ≥44px target.
- `IconButton`: Accessible circular/square icon trigger.
- `Text`: Typography scale variants (`display`, `h1`, `h2`, `h3`, `body`, `bodySmall`, `caption`, `label`).
- `TextInput` & `FormField`: Label, error message, helper text, clear button, left/right accessory icons.
- `Card`: Surface container with elevation, padding variants, interactive pressable support.
- `ListItem`: Leading icon/avatar slot, title, subtitle, trailing accessory/chevron.
- `Badge` & `Chip`: Selectable filter chips and status indicator badges.
- `Skeleton`: Animated shimmer loading placeholder with reduced-motion support.
- `Spinner`: Theme-colored activity indicator.
- `Toast`: Context-driven toast alerts (success, error, info).
- `EmptyState` & `ErrorState`: Friendly illustrations/icons with retry action button.
- `Screen`: SafeArea-aware container with scrollable and non-scrollable modes.
- `Header`: Standard navigation and screen header with back action and title.
- `Divider`: Subtle horizontal/vertical separator.
- `Switch` & `Checkbox`: Controlled boolean toggles with accessible labels.

### 3.5 API Client
- `services/api/client.ts`: Fetch wrapper handling base URL resolution, trailing-slash normalization, configurable timeouts via `AbortController`, typed JSON parsing, and normalized `ApiError` format.
- Automatic injection of dev-mode auth headers from the active session.
- Generation and attachment of `X-Request-ID` for audit tracking on write operations.
- Typed service modules: `masjidService`, `salatService`, `programService`, `personService`, `photoService`, `syncService`, `healthService`.

### 3.6 Auth Service & Role Management
- `services/auth/`: Session management with roles (`super_admin`, `masjid_editor`, `salat_editor`, `viewer`) and scoped `masjidId`.
- Header mapping engine translating session state into backend-compatible headers (`X-Super-Admin-Token`, `X-Masjid-Editor-Token`, etc.).
- Permission evaluation engine `can(session, permission, targetMasjidId)` implementing the backend RBAC rules.
- `providers/auth-provider.tsx`: Context exposing current user, active role, switchRole helper, and login/logout methods.

### 3.7 Data Layer (TanStack Query)
- `providers/query-provider.tsx`: Configures `QueryClient` with offline-first defaults (`networkMode: "offlineFirst"`, 5-minute stale time, 7-day GC time).
- AsyncStorage cache persistence for native and web.
- Custom query hooks: `useMasjids`, `useMasjidDetail`, `useSalatSchedules`, `useHealthCheck`.

### 3.8 Offline Cache & Outbox Sync Queue
- `services/sync/outbox.ts`: Persistent queue in AsyncStorage (`jumapp:outbox`) storing pending mutations with UUIDs, entity types, actions, payloads, and retry metadata.
- Automatic flushing on reconnection via `@react-native-community/netinfo` and `AppState` change listeners.
- Exponential backoff retry strategy with jitter.
- Snapshot delta ingestion: `useSyncSnapshot` hook to populate local cache from `GET /api/v1/sync/`.
- UI Sync Status: Global sync indicator showing pending queue count, active sync animation, and error states.

---

## 4. Verification & Quality Gates

1. **Backend Tests:** `pytest backend/tests` passing with 100% success on sync, auth, and CRUD endpoints.
2. **Frontend Typecheck:** `npm run typecheck` (tsc with no errors).
3. **Frontend Lint:** `npm run frontend:lint` (ESLint 9 passing).
4. **Frontend Unit Tests:** `npm run test` (Jest testing tokens, i18n, API client, auth permissions, outbox queue).
5. **Web Build Export:** `npm run frontend:build:web` (`expo export --platform web`) generating clean static output with PWA assets.

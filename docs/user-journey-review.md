# DoonJuma — User Journey Review

**Reviewer role:** Senior Product Strategist / UX Architect / Design Systems Expert  
**Inputs:** `docs/user-journey.md`, `docs/idea.md`, `docs/architecture.md`, `docs/api.md`, `README.md`  
**Date:** 2026-08-11

---

## 0\. Clarifying Questions (flagged before analysis — do not silently guess)

| # | Question | Why It Matters | Impact if Unanswered |
| --- | --- | --- | --- |
| 1 | Which "trusted source" provides the moonsighting committee date? | Dashboard shows it; needs an API/feed contract. | Feature cannot ship; risk of wrong religious date. |
| 2 | Notification timing — how many minutes _before_ each salat, or at salat time? | Per-salat notification config needs a timing model. | Users miss prayers or get spammed; config UX undefined. |
| 3 | What is the "vicinity" radius for masjid search? Fixed or user-configurable? | Map/list results depend on it. | Empty or overwhelming result sets. |
| 4 | Who assigns the **Masjid Editor** role? Is there a super-admin? | Role-based access is core; assignment flow is undefined. | Privilege escalation or dead-end requests. |
| 5 | Are Juma Khutbah/Iqama times manually entered or calculated? | Juma emphasis is a key touchpoint. | Wrong Friday times = trust loss. |
| 6 | Photo upload access — who can upload, and is there moderation? | "Proper access" is mentioned but unspecified. | Spam/inappropriate content on masjid pages. |

---

## STEP 1 — JOURNEY DECONSTRUCTION

### Actors

*   **Primary:** Worshipper, Traveler
*   **Secondary (privileged):** Masjid Editor, Salat Editor
*   **Implicit:** Admin (role assigner), System (adhan.js, cache, notifications, map), 3rd parties (Google OAuth, moonsighting source, map tile provider)

### Journey Map Table

| Step # | Actor | Action | System Response | User Goal |
| --- | --- | --- | --- | --- |
| 1 | Worshipper/Traveler | Install, launch, grant location, sign in (social/Google), choose language | Permission prompt, OAuth flow, locale-synced UI (EN/HI/UR) | Trust + language comfort |
| 2 | Worshipper | View dashboard: location name, date, moonsighting date, next-salat highlight | Render cached/current data; bold Juma on Fridays | "Is it time yet?" answered at a glance |
| 3 | Worshipper/Traveler | Find masjid: map view, list view, search/sort/filter | Vicinity results, dual-view toggle | Locate nearest/accessible masjid |
| 4 | Worshipper/Traveler | View masjid details: salat times, amenities, transport, photos | Render full detail page | Decide where to pray with confidence |
| 5 | Worshipper | Configure per-salat notifications; rely on offline cache | Schedule notifications; serve cached times | Never miss a prayer |
| 6 | Masjid/Salat Editor | Add/edit masjid, update salat times, request role | Role check, change history, admin approval flow | Keep data accurate & auditable |
| 7 | Worshipper | Revisit; use saved/last-known location | Restore last context | Trusted daily companion |

### Assumed Happy Path

Location granted → dashboard shows next salat → nearest masjid found → times/notifications configured → daily habit with offline reliability.

---

## STEP 2 — MISSING FUNCTIONALITY

### 🔴 Explicitly Missing Functionality

| # | Missing Item | Where in Journey | Why It's Needed | Suggested Solution |
| --- | --- | --- | --- | --- |
| 1 | Moonsighting date **source/API contract** | Dashboard (Phase 2) | "Trusted source" is named but not specified | Define provider + fallback; cache with TTL; show source attribution |
| 2 | **Admin role definition & assignment flow** | Contributing (Phase 6) | Masjid Editor assignment is undefined | Add super-admin role + assignment UI + audit log |
| 3 | **Salat Editor request → approval workflow** | Contributing (Phase 6) | Mentioned but no states (pending/approved/rejected) | Define request states, notifications, and expiry |
| 4 | **Notification timing model** (before/at salat, per-salat) | Salat Awareness (Phase 5) | Config UX needs a timing model | Offer "X min before" presets + custom; per-salat toggles |
| 5 | **Juma Khutbah/Iqama data source** | Dashboard/Details (Phases 2, 4) | Key touchpoint; source undefined | Manual entry by editors + fallback to calculated Juma |
| 6 | **Photo upload access & moderation** | Masjid Details (Phase 4) | "Proper access" unspecified | Role-gated uploads + moderation queue + storage policy |
| 7 | **"Vicinity" radius definition** | Finding a Masjid (Phase 3) | Results depend on it | Configurable radius (e.g., 5/10/25 km) + "expand" control |

### 🟠 Implicitly Missing Functionality

| # | Hidden Requirement | Assumption Being Made | Risk if Ignored | Suggested Solution |
| --- | --- | --- | --- | --- |
| 1 | **Auth session timeout & token refresh** | Session lasts forever | Security breach; silent logout | Refresh tokens, idle timeout, re-auth on sensitive actions |
| 2 | **Role change mid-session** | Roles are static | Privilege escalation persists in UI | Re-fetch permissions on each privileged action; server-side checks |
| 3 | **Validation & error states** | Inputs are always valid | Bad data, confusing failures | Client + server validation; inline errors; retry states |
| 4 | **Empty / loading / offline states** | Data always loads | Confusion, perceived brokenness | Skeletons, empty-state copy, offline banner with cache indicator |
| 5 | **Offline sync & conflict resolution** | Cache is always fresh | Stale times, lost edits | Last-write-wins + conflict UI; versioned cache |
| 6 | **Notification permission flow** | Permissions auto-granted | Users miss prayers silently | In-context permission prompt + re-prompt strategy |
| 7 | **Undo / delete / edit history for masjids** | Edits are permanent | Data corruption, no recovery | Soft-delete, undo toast, full change history |
| 8 | **Search debounce, sort, filter, pagination** | Small datasets | Performance issues at scale | Debounced search, indexed filters, paginated lists |
| 9 | **Audit logs for role changes** | Role changes are traceable | No accountability | Log actor, action, timestamp, reason |
| 10 | **Data export / privacy controls** | Users trust data handling | GDPR/trust issues | Export my data, delete account, consent management |
| 11 | **Rate limiting & abuse prevention** | Users are well-behaved | Spam edits, API abuse | Rate limits on edits/requests; CAPTCHA on requests |
| 12 | **Accessibility (WCAG 2.2)** | All users can see/touch | Excludes disabled users | ARIA, keyboard nav, contrast, screen-reader labels |
| 13 | **RTL support for Urdu** | Urdu renders LTR | Broken layout for Urdu users | RTL layout + proper font + text direction handling |
| 14 | **Timezone / DST handling** | Times are local | Wrong salat times across zones | Store UTC + localize; handle DST transitions |
| 15 | **Analytics events & error tracking** | Product decisions are data-driven | Blind to drop-offs | Instrument key events; Sentry/error boundary |

---

## STEP 3 — CORNER & EDGE CASES

| # | Corner Case | Trigger Scenario | Impact | Recommended Handling |
| --- | --- | --- | --- | --- |
| 1 | **Empty search results** | User searches a non-existent area | Confusion, drop-off | Empty state with "expand radius" + nearby suggestions |
| 2 | **Max-length / unicode input** | Urdu/Hindi masjid names, long addresses | Truncation, broken search | Length limits, unicode normalization, proper collation |
| 3 | **Injection / XSS** | Malicious masjid name or description | Data corruption, client-side attacks | Server-side sanitization, output encoding |
| 4 | **Concurrent editors** | Two editors update same masjid | Lost updates, conflicting times | Optimistic locking + conflict resolution UI |
| 5 | **Stale cache** | Offline cache older than server data | Wrong salat times | Cache TTL + "last updated" indicator + refresh |
| 6 | **Partial save** | Network drops mid-edit | Incomplete masjid record | Transactional saves + retry + draft state |
| 7 | **Offline mid-flow** | User loses network while viewing map | Broken map, no times | Offline map tiles + cached times + banner |
| 8 | **Role revoked mid-session** | Admin demotes an editor while editing | Unauthorized save attempt | Server-side re-check on save; graceful error |
| 9 | **Expired token** | Long idle session | Silent 401s | Auto-refresh + re-auth prompt |
| 10 | **Timezone / DST change** | Traveler crosses timezone; DST shift | Wrong salat times | Store UTC, localize on device, handle DST |
| 11 | **Moonsighting date mismatch** | Committee date differs from calculated | Confusion on dashboard | Show both + source label |
| 12 | **0 / 1 / 10k+ masjids** | New region (0), single masjid, dense city (10k+) | Empty map or performance lag | Empty states; clustering; pagination/virtualization |
| 13 | **Small screens / touch** | Small phone, fat-finger taps | Mis-taps on map/list | Min 44px touch targets, map pinch-zoom |
| 14 | **Screen readers** | Visually impaired user | Inaccessible journey | ARIA labels, semantic HTML, alt text |
| 15 | **Duplicate masjid** | Two editors add same masjid | Confusion, split data | Duplicate detection + merge flow |
| 16 | **Disputed salat times** | Community disagrees with editor | Trust erosion | Dispute flag + admin review + change history |

---

## STEP 4 — PROFESSIONAL & INDUSTRY-STANDARD GAPS

| # | Standard / Best Practice | What's Missing | Clarification / Recommendation |
| --- | --- | --- | --- |
| 1 | **OWASP / Security** | PII handling, geolocation privacy, secure storage | Encrypt tokens; minimize location retention; HTTPS-only; OAuth scopes |
| 2 | **GDPR / Privacy** | Consent for location, data export, delete account | Consent flow at onboarding; "export my data"; account deletion |
| 3 | **WCAG 2.2** | Keyboard nav, ARIA, contrast, screen reader | Audit all screens; target AA; test with VoiceOver/TalkBack |
| 4 | **Observability** | Analytics events, error tracking, logging | Instrument key events; Sentry; structured logs |
| 5 | **Performance (Core Web Vitals)** | Map tile budget, LCP, INP | Lazy-load map; cache tiles; budget for web/PWA |
| 6 | **i18n / l10n** | RTL for Urdu, locale sync edge cases | RTL layout; font support; locale fallback |
| 7 | **Data integrity** | Transactions, idempotency, backups | Idempotent edit endpoints; DB backups; audit trail |
| 8 | **Documentation / help** | Tooltips, onboarding help, FAQ | In-app help for editors; tooltips on settings |
| 9 | **SLAs / rate limiting** | Abuse prevention, API limits | Rate limits on edits/requests; CAPTCHA on role requests |

---

## STEP 5 — DESIGN ADVICE

### Top 5 Design Recommendations

1.  **Map/List toggle as a first-class IA pattern** — _Why:_ Users switch between spatial and list mental models. _How:_ Persistent segmented control; preserve filter/sort state across toggles.
2.  **Next-salat as the visual anchor** — _Why:_ Reduces "is it time yet?" anxiety. _How:_ Large countdown card at top of dashboard; color-coded by proximity.
3.  **Juma emphasis with clear hierarchy** — _Why:_ Friday is the highest-stakes day. _How:_ Bold Khutbah/Iqama with distinct color + "Today is Juma" banner.
4.  **Amenity iconography over text** — _Why:_ Faster scanning, language-agnostic. _How:_ Standard icons (Parking/Toilet/Urinals) + tooltips; transport as a compact row.
5.  **Progressive disclosure on masjid details** — _Why:_ Avoids cognitive overload. _How:_ Collapsible sections (Times / Amenities / Transport / Photos); "expand all" for power users.

---

## STEP 6 — UX ADVICE

### Grouped by Heuristic

| Heuristic | Recommendation |
| --- | --- |
| **Visibility of system status** | Show "last updated" on times; offline banner; loading skeletons; notification schedule preview |
| **User control & freedom** | Undo on edits; back/cancel everywhere; "reset to default" on settings |
| **Error prevention** | Validate before submit; confirm destructive actions; prevent duplicate masjid |
| **Recognition over recall** | Persistent next-salat card; saved location; recent searches |
| **Flexibility & efficiency** | Shortcuts for power users (quick-add masjid, bulk time edit); keyboard nav on web |
| **Aesthetic & minimalist** | Declutter dashboard; one primary action per screen |
| **Help & recovery** | Inline error messages; retry buttons; help links for editors |
| **Onboarding** | Progressive permission requests (location → notifications); language choice upfront |
| **Micro-interactions** | Haptic on salat-time arrival; subtle animation on next-salat change; toast on save |

### Accessibility Checklist (specific to this journey)

*   Keyboard navigation for map/list/search on web
*   ARIA labels on map markers, amenity icons, notification toggles
*   Contrast ≥ 4.5:1 for text; ≥ 3:1 for UI components
*   Screen-reader announcements for next-salat changes and Juma emphasis
*   Touch targets ≥ 44px on mobile
*   RTL layout for Urdu; proper font + text direction
*   Alt text for masjid photos
*   Focus states visible on all interactive elements
*   No time-based content that requires fast reaction (salat countdown is informational, not blocking)

---

## STEP 7 — PAIN POINTS & IMPROVEMENTS

| Step | Pain Point | Root Cause | Severity (H/M/L) | Improvement | Expected Impact |
| --- | --- | --- | --- | --- | --- |
| 1 | Permission friction at onboarding | Asking location + notifications upfront | H | Progressive permission requests; explain _why_ | Higher opt-in, less drop-off |
| 1 | Language barrier | Locale sync may not match preference | M | Manual override + remember choice | Broader adoption |
| 2 | "Is it time yet?" anxiety | No clear next-salat countdown | H | Prominent countdown card | Reduced anxiety, daily habit |
| 2 | Moonsighting date confusion | Source unspecified, no attribution | M | Show source + fallback | Trust in religious data |
| 3 | Overwhelming map | Dense results, no clustering | H | Clustering + "expand radius" | Faster decision-making |
| 3 | No direction/route | Map lacks navigation | M | "Get directions" deep link | Traveler confidence |
| 4 | Missing info (parking, toilets) | Amenities not always filled | M | Editor prompts + "unknown" state | Realistic expectations |
| 5 | Notification config complexity | Per-salat toggles + timing unclear | M | Presets + preview of schedule | Higher notification adoption |
| 5 | Network dead zones | Offline cache not obvious | H | Offline banner + cache freshness | Reliability trust |
| 6 | Unauthorized edits | Role checks unclear | H | Server-side enforcement + audit log | Data integrity |
| 6 | Slow approval flow | Salat Editor request states undefined | M | Clear status + notifications | Editor motivation |
| 7 | Stale data | Community maintenance gaps | M | "Last updated" + stale flags | Trust retention |

---

## STEP 8 — ADDITIONAL STRATEGIC ITEMS

*   **KPIs:** Time-to-next-salat (≤30s), notification opt-in rate, weekly active users, editor retention, data freshness (median age of masjid records), crash-free sessions.
*   **A/B tests:** Notification timing (before vs at salat), map-first vs list-first default, Juma banner style, onboarding permission order.
*   **Growth loops:** Share masjid card → invite others; "add your masjid" CTA for community growth; referral for editors.
*   **Retention hooks:** Daily next-salat widget; weekly "masjid of the week"; streak for daily check-ins.
*   **Cross-journey dependencies:** Editor data feeds Worshipper trust; notification config depends on accurate times; offline cache depends on sync strategy.
*   **Scalability:** Geospatial queries (Neon/PostGIS) at 10k+ masjids; map tile caching; CDN for photos.
*   **Ethics / dark patterns:** Avoid guilt-trip notifications; be transparent about location use; no fake urgency on Juma.
*   **Cost implications:** Map tiles, photo storage, notification infra (FCM/APNs), backend on Cloud Run — budget for scale.

---

## STEP 9 — EXECUTIVE SUMMARY

### 1\. Overall Journey Health Score: **62 / 100**

| Dimension | Score | Notes |
| --- | --- | --- |
| Clarity of journey | 70 | 7 phases well-defined; happy path clear |
| Functionality completeness | 55 | Several explicit + implicit gaps (moonsighting source, admin flow, notifications) |
| Edge-case coverage | 50 | Many unhandled (offline sync, concurrency, RTL, timezone) |
| Professional standards | 55 | Security/GDPR/WCAG/observability largely absent |
| Design & UX quality | 70 | Strong touchpoints (next-salat, Juma, trilingual) but IA/accessibility gaps |
| Strategic readiness | 65 | Good personas & metrics; missing KPIs instrumentation |

### 2\. Top 3 Critical Issues (fix immediately)

1.  **Moonsighting date source undefined** — dashboard trust depends on it. _Fix:_ Define provider + fallback + attribution.
2.  **Role-based access & admin flow unspecified** — core to data integrity. _Fix:_ Define roles, assignment, approval states, server-side enforcement.
3.  **Offline sync & conflict resolution missing** — offline-first is a headline feature. _Fix:_ Versioned cache, last-write-wins, conflict UI.

### 3\. Top 3 Quick Wins (low effort, high impact)

1.  **Next-salat countdown card** on dashboard (reduces anxiety, drives habit).
2.  **Progressive permission requests** (location → notifications) to cut onboarding drop-off.
3.  **"Last updated" + offline banner** to build trust in data freshness.

### 4\. Top 3 Strategic Bets (higher effort, transformative)

1.  **Community data trust engine** — audit logs, dispute flags, editor reputation → differentiator.
2.  **Offline-first as a moat** — robust cache + sync across all platforms → reliability brand.
3.  **Trilingual + RTL as a growth lever** — full EN/HI/UR with locale sync → broad India adoption.

### 5\. Suggested Next Steps / Prioritized Roadmap

| Priority | Item | Effort | Impact |
| --- | --- | --- | --- |
| P0 | Define moonsighting source + fallback | M | H |
| P0 | Define roles, admin flow, approval states | M | H |
| P0 | Offline sync + conflict resolution | H | H |
| P1 | Notification timing model + permission flow | M | H |
| P1 | Accessibility audit (WCAG 2.2) + RTL | M | M |
| P1 | Analytics + error tracking instrumentation | M | M |
| P2 | Map clustering + "expand radius" | M | M |
| P2 | Photo upload moderation + storage | M | M |
| P2 | Data export / privacy controls (GDPR) | M | M |

---

_Review complete. All recommendations include rationale (WHY) and implementation hints (HOW). Assumptions are flagged in Section 0._
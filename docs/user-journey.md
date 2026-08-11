# DoonJuma — User Journey Map

DoonJuma (`DJ`) helps worshippers find the nearest masjid and its salat times, with offline support, per-salat notifications, and a trilingual interface (English / Hindi / Urdu) that syncs with the device locale.

---

## Target Users (Personas)

- **Worshipper** — wants the nearest masjid and accurate salat times at a glance.
- **Traveler** — in an unfamiliar area, needs quick, reliable, and accessible info.
- **Masjid Editor** — privileged user who maintains masjid details and timings.
- **Salat Editor** — privileged user who updates salat times only (via admin-approved request).

---

## Journey Phases

| Phase | User Goal | Actions | Thoughts & Feelings | Pain Points | How DJ Addresses It |
|---|---|---|---|---|---|
| **1. Discovery & Onboarding** | Find a reliable masjid/salat app | Install, launch, grant location, sign in (social/Google), choose language | Trust, privacy concern, language comfort | Permission friction, account setup, language barrier | Social login, clear location handling, **3-language UI (EN/HI/UR) auto-synced with device locale** |
| **2. Dashboard (Home)** | See today's context at a glance | View location name, date, moonsighting date, next salat highlight | "Is it time yet?" anxiety | Confusion about which salat is next | Next-salat highlight, **Juma (Khutbah/Iqama) bolded on Fridays** |
| **3. Finding a Masjid** | Locate nearest masjid | Map view, list view, search/sort/filter | Urgency, unfamiliarity with area | Overwhelming map, no direction | Map + list toggle, search/filter, vicinity-based results |
| **4. Masjid Details** | Decide where to pray | View all salat times, amenities, transport, photos | Need confidence it's accessible & suitable | Missing info (parking, toilets, access) | Amenities (Parking/Toilet/Urinals), public transport column, photos |
| **5. Salat Time Awareness & Notifications** | Never miss a prayer | Check next salat, **configure per-salat notifications**, rely on offline cache | Peace of mind | Network dead zones, forgetting prayer times | **Per-salat notification settings (Fajr/Dhuhr/Asr/Maghrib/Isha, Juma)**, offline cache, adhan.js calculations |
| **6. Contributing (Privileged)** | Keep data accurate | Add/edit masjid, update salat times, request role | Responsibility, desire for accuracy | Wrong times, unauthorized edits | Role-based access, salat change history, admin approval flow |
| **7. Ongoing Use & Retention** | Trusted daily companion | Revisit, use saved/last-known location | Habit, trust | Stale data | Saved location fallback, community-maintained data |

---

## Key Touchpoints (Where DJ Shines)

- **Next-salat highlight & Juma emphasis** — removes guesswork; Friday Khutbah/Iqama shown and bolded.
- **Per-salat notification configuration** — users set reminders for each salat (Fajr, Dhuhr, Asr, Maghrib, Isha, Juma) to never miss a prayer.
- **Trilingual UI (EN/HI/UR) with locale sync** — the app automatically matches the device language, making it accessible across India's diverse users.
- **Offline-first reliability** — cached times and data work without a network.
- **Map + list dual view** — search, sort, and filter masjids in both views.
- **Amenities & transport transparency** — Parking, Toilet, Urinals, and public transport access shown upfront.
- **Role-based editing with change history** — trusted, auditable community-maintained data.

---

## Emotional Journey Curve

```
Uncertainty ──► Confidence ──► Trust ──► Habit
   │                │             │          │
   │  Onboarding    │  Dashboard  │  Reliable │  Daily use,
   │  & language    │  & finding  │  times &  │  saved
   │  choice        │  a masjid   │  offline  │  location
```

---

## Success Metrics (per Persona)

- **Worshipper** — finds the nearest masjid and next salat time in under 30 seconds.
- **Traveler** — locates an accessible masjid with amenities and transport info in an unfamiliar city.
- **Masjid Editor** — adds/updates masjid details with full change history and role-based access.
- **Salat Editor** — updates salat times quickly after admin approval, with auditable history.
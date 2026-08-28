# DoonJuma — Rough Wireframes

Text-based wireframes for the core user journey screens.

---

## 1. Onboarding / Language Selection

```
┌─────────────────────────────────────┐
│                                     │
│         🕌 DoonJuma                 │
│    Find your nearest masjid         │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  [English]                  │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  [हिन्दी]                   │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  [اردو]                     │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │     Continue with Google    │    │
│  └─────────────────────────────┘    │
│                                     │
│  Skip for now →                     │
│                                     │
└─────────────────────────────────────┘
```

**Notes:**
- Language selection first (before permissions)
- Google Sign-In as primary auth
- Skip option for viewers (see map/list only)
- Progressive permission request after this screen

---

## 2. Dashboard (Home) — Core Screen

```
┌─────────────────────────────────────┐
│ ☰  DoonJuma              🔔  👤    │
├─────────────────────────────────────┤
│                                     │
│  📍 Dehradun, Uttarakhand           │
│  📅 Thu, 27 Aug 2026                │
│  🌙 Moon: 1 Shawwal 1447            │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  ⏰ NEXT PRAYER             │    │
│  │                             │    │
│  │     ASR                      │    │
│  │   3h 12m 45s                │    │
│  │                             │    │
│  │  Fajr 04:32  Dhuhr 12:15    │    │
│  │  Asr  15:30  Maghrib 18:22  │    │
│  │  Isha  19:45                 │    │
│  │                             │    │
│  │  🕌 JUMA: Khutbah 12:30     │    │
│  │      Iqama 13:00            │    │
│  └─────────────────────────────┘    │
│                                     │
│  🕌 NEARBY MASJIDS                  │
│  ┌─────────────────────────────┐    │
│  │  Masjid A          1.2 km  │    │
│  │  Asr in 3h 12m             │    │
│  ├─────────────────────────────┤    │
│  │  Masjid B          2.1 km  │    │
│  │  Asr in 3h 12m             │    │
│  ├─────────────────────────────┤    │
│  │  Masjid C          3.4 km  │    │
│  │  Asr in 3h 12m             │    │
│  └─────────────────────────────┘    │
│                                     │
│  [View All on Map →]                │
│                                     │
├─────────────────────────────────────┤
│  🏠 Home    🔍 Explore    ⚙️ Settings│
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Next prayer countdown is the visual anchor (largest element)
- Location + date + moonsighting shown compactly
- Juma highlighted with distinct styling on Fridays
- Nearby masjids list with distance and next prayer time
- Single primary action: "View All on Map"

---

## 3. Map View (Explore)

```
┌─────────────────────────────────────┐
│ ← 🔍 Search masjids...     Filter  │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │      [MAP VIEW]             │    │
│  │                             │    │
│  │    📍 You                   │    │
│  │         🕌   🕌             │    │
│  │      🕌         🕌         │    │
│  │                             │    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─ List ─┬─ Map ─┐                │
│  │  List   │  Map  │  ← Toggle     │
│  └────────┴───────┘                │
│                                     │
│  Sort: Distance ▼                   │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  Masjid A          1.2 km  │    │
│  │  Asr in 3h 12m  🅿️ 🚿      │    │
│  ├─────────────────────────────┤    │
│  │  Masjid B          2.1 km  │    │
│  │  Asr in 3h 12m  🅿️ 🚿 🚌   │    │
│  └─────────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│  🏠 Home    🔍 Explore    ⚙️ Settings│
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Search bar at top (persistent)
- Map/List toggle as segmented control
- Filter for amenities (Parking, Toilet, Transport)
- Sort by distance (default) or prayer time
- List items show key amenities as icons

---

## 4. Masjid Detail

```
┌─────────────────────────────────────┐
│ ← Masjid A                    📤   │
├─────────────────────────────────────┤
│                                     │
│  [PHOTO CAROUSEL]                   │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │      [Masjid Photo]         │    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
│  🕌 Masjid A                        │
│  📍 123 Main St, Dehradun          │
│                                     │
│  ── Salat Times ──────────────      │
│  ┌─────────────────────────────┐    │
│  │  Fajr     04:32             │    │
│  │  Dhuhr    12:15             │    │
│  │  Asr  ▶   15:30  ← Next    │    │
│  │  Maghrib  18:22             │    │
│  │  Isha     19:45             │    │
│  │  Juma     12:30/13:00       │    │
│  └─────────────────────────────┘    │
│                                     │
│  ── Amenities ──────────────────    │
│  🅿️ Parking  🚿 Wudu  🚻 Toilets   │
│  🚌 Public Transport Access         │
│                                     │
│  ── Programs ───────────────────    │
│  Maktab, Tafseer, Hadith Lessons    │
│                                     │
│  ── Committee ──────────────────    │
│  Imam: [Name]                       │
│  Editor: [Name]                     │
│                                     │
│  [Get Directions 🗺️]               │
│  [Report Issue ⚠️]                  │
│                                     │
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Photo carousel at top (max 5 photos)
- Salat times in a clean table with "Next" indicator
- Juma times shown distinctly on Fridays
- Amenities as icons (not text) for quick scanning
- Programs listed compactly
- "Get Directions" as primary action (deep link to maps)

---

## 5. Settings

```
┌─────────────────────────────────────┐
│ ← Settings                          │
├─────────────────────────────────────┤
│                                     │
│  ── Salat Calculation ──────────    │
│  Calculation Method: Muslim World   │
│  Asr Juristic:     Hanafi          │
│  [Configure →]                      │
│                                     │
│  ── Notifications ──────────────    │
│  ☑️ Fajr      [10 min before]      │
│  ☑️ Dhuhr     [10 min before]      │
│  ☑️ Asr       [10 min before]      │
│  ☑️ Maghrib   [10 min before]      │
│  ☑️ Isha      [10 min before]      │
│  ☐ Juma                           │
│                                     │
│  ── Language ───────────────────    │
│  [English ▼]                        │
│                                     │
│  ── Account ────────────────────    │
│  Profile                            │
│  Request Editor Role                │
│  Sign Out                           │
│                                     │
│  ── About ──────────────────────    │
│  Version 1.0.0                      │
│  Privacy Policy                     │
│  Terms of Service                   │
│                                     │
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Salat calculation settings (Hanafi default for Dehradun)
- Per-salat notification toggles with timing presets
- Language override (in addition to device locale)
- Editor role request flow accessible from settings

---

## 6. Salat Editor Role Request

```
┌─────────────────────────────────────┐
│ ← Request Editor Role               │
├─────────────────────────────────────┤
│                                     │
│  Become a Salat Editor              │
│                                     │
│  Help maintain accurate prayer      │
│  times for your local masjid.       │
│                                     │
│  ── Your Details ───────────────    │
│  Name:     [________________]       │
│  Phone:    [________________]       │
│  Email:    [________________]       │
│                                     │
│  ── Masjid ────────────────────     │
│  Select: [Masjid A ▼]              │
│                                     │
│  ── Role ──────────────────────     │
│  ☑️ Salat Editor (edit times only)  │
│  ☐ Masjid Editor (full access)     │
│                                     │
│  ── Additional Info ───────────     │
│  [______________________________]   │
│  [______________________________]   │
│                                     │
│  [Submit Request →]                 │
│                                     │
│  Status: Pending ⏳                 │
│                                     │
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Clear form with required fields
- Role selection (Salat Editor vs Masjid Editor)
- Status indicator after submission
- Admin approval flow (backend)

---

## 7. Offline State

```
┌─────────────────────────────────────┐
│ ☰  DoonJuma              🔔  👤    │
├─────────────────────────────────────┤
│ ⚠️ Offline — showing cached data    │
├─────────────────────────────────────┤
│                                     │
│  📍 Dehradun, Uttarakhand           │
│  📅 Thu, 27 Aug 2026                │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  ⏰ NEXT PRAYER             │    │
│  │     ASR                      │    │
│  │   3h 12m 45s                │    │
│  │                             │    │
│  │  Last updated: 2h ago       │    │
│  └─────────────────────────────┘    │
│                                     │
│  🕌 NEARBY MASJIDS (cached)         │
│  ┌─────────────────────────────┐    │
│  │  Masjid A          1.2 km  │    │
│  │  Asr in 3h 12m             │    │
│  ├─────────────────────────────┤    │
│  │  Masjid B          2.1 km  │    │
│  │  Asr in 3h 12m             │    │
│  └─────────────────────────────┘    │
│                                     │
│  [Retry →]                          │
│                                     │
├─────────────────────────────────────┤
│  🏠 Home    🔍 Explore    ⚙️ Settings│
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Clear offline banner at top
- "Last updated" timestamp on cached data
- Retry button for manual refresh
- Map tiles cached for offline viewing

---

## 8. Notification Permission Flow

```
┌─────────────────────────────────────┐
│                                     │
│         🕌 DoonJuma                 │
│                                     │
│  Never miss a prayer!               │
│                                     │
│  Get notified before each salat     │
│  so you can prepare on time.        │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  ☑️ Fajr      10 min before │    │
│  │  ☑️ Dhuhr     10 min before │    │
│  │  ☑️ Asr       10 min before │    │
│  │  ☑️ Maghrib   10 min before │    │
│  │  ☑️ Isha      10 min before │    │
│  └─────────────────────────────┘    │
│                                     │
│  [Enable Notifications →]           │
│                                     │
│  [Maybe Later]                      │
│                                     │
└─────────────────────────────────────┘
```

**Key Design Decisions:**
- Shown after onboarding (not during)
- Clear value proposition
- Per-salat toggles visible before permission request
- "Maybe Later" option (no pressure)

# Project Rules

## Expo SDK 54
- Read the exact versioned docs at https://docs.expo.dev/versions/v54.0.0/ before writing any code.
- Do not use unversioned docs; always use the v54.0.0 URL.

## Cross-Platform (iOS / Android / Web)
- All code must work on iOS, Android, and Web.
- Use `Platform.OS` guards for platform-specific behavior.
- Never import web-only APIs (e.g. `window`, `document`, service workers) without a `Platform.OS === 'web'` check.

## Offline Support
- The app must work offline on all platforms.
- Web: service worker + CacheStorage for app shell and assets.
- Native: AsyncStorage / expo-file-system for data persistence.
- Always provide offline fallbacks for network-dependent features.

## PWA
- Use `public/manifest.json` for the PWA manifest and `app/+html.tsx` to link it (static rendering).
- Keep `public/manifest.json` and `public/service-worker.js` in sync with `app.json`.
- Service worker must use Cache-First for static assets and Network-First for API data.

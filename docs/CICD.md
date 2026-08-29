# CI/CD — GitHub Actions Pipeline

This project ships a React Native (Expo SDK 54) app for **Android**, **iOS**, and **Web (PWA)** from a single monorepo (`frontend/`). All pipelines are defined as GitHub Actions workflows in `.github/workflows/`.

## Pipeline overview

| Workflow | Trigger | What it does |
|---|---|---|
| `ci-stage.yml` | Push or PR to `stage` | Lint, unit tests, web build + typecheck. Blocks merge on any failure. |
| `deploy-android.yml` | Manual (`workflow_dispatch`) or via `release.yml` | EAS build for Android; optional Play Store submission. |
| `deploy-ios.yml` | Manual (`workflow_dispatch`) or via `release.yml` | EAS build for iOS; **skipped by default** (`skip_ios: true`). |
| `deploy-pwa.yml` | Manual (`workflow_dispatch`) or via `release.yml` | `expo export` web build → deploy to **Netlify**. |
| `release.yml` | Tag push `v*.*.*` on `master`, or manual | Orchestrates Android + iOS + PWA in **parallel** (independent, fail-fast per pipeline). |

Reusable building blocks:

- `reusable-eas-build.yml` — shared EAS build/submit logic used by Android and iOS.
- `reusable-web-build.yml` — shared `expo export` step that produces the `web-dist` artifact.

### Environment assumptions

- **Node 22** is used in all CI jobs (SDK 54 supports Node 20.19+ / 22).
- Dependencies are installed with `npm ci` (from `frontend/package-lock.json`) and cached via `actions/setup-node`.
- All workflows use concurrency groups so a given tag/branch can't run duplicate pipelines.

---

## Cutting a release (tag flow)

Releases are cut from `master`. Pushing a `v*.*.*` tag fires `release.yml`, which runs the Android, iOS, and PWA pipelines in parallel.

Use the npm scripts (run from the repo root, requires a clean working tree):

```bash
npm run release:patch   # 1.0.0 -> 1.0.1
npm run release:minor   # 1.0.0 -> 1.1.0
npm run release:major   # 1.0.0 -> 2.0.0
```

Each script runs `npm version <bump> && git push --follow-tags`, which:

1. bumps the root `package.json` version,
2. creates the annotated tag `vX.Y.Z`,
3. pushes the commit **and** the tag to `origin`.

Manual equivalent:

```bash
npm version patch
git push origin master --tags
```

> `release.yml` validates that the tag points to a commit on `master` and fails (skipping all three pipelines) otherwise. Tags must be created on `master`.

---

## Manual triggering

Each pipeline can be run independently, either from the GitHub UI or via npm scripts.

### GitHub UI

1. Go to **Actions** → select the workflow (Deploy Android / Deploy iOS / Deploy PWA / Release).
2. Click **Run workflow**.
3. Pick the branch (`master`) and set inputs:
   - **Deploy iOS**: uncheck `skip_ios` to actually build (requires Apple credentials).
   - **Deploy Android / iOS**: set `submit` to submit to the store after building (requires store credentials).

### npm scripts (requires `gh` CLI authenticated to the repo)

```bash
npm run frontend:deploy:android   # runs deploy-android.yml on master
npm run frontend:deploy:ios       # runs deploy-ios.yml with skip_ios=false
npm run frontend:deploy:pwa       # runs deploy-pwa.yml on master
npm run frontend:deploy:all       # runs release.yml on master (all three pipelines)
```

> `deploy:ios` passes `-f skip_ios=false`, overriding the default. If you don't have Apple credentials yet, leave the default (`npm run deploy:ios` will still dispatch, but the workflow skips the build — see "iOS skip flag").

### iOS skip flag

`deploy-ios.yml` declares `skip_ios` with a **default of `true`**. The workflow:

- always runs a `check-skip` job that logs whether the build will run,
- only runs the actual `build-ios` job when `skip_ios` is explicitly `false`.

Because the workflow handles both boolean (`workflow_call`) and string (`workflow_dispatch`) representations of the flag, it is safe from the orchestrator *and* the UI/CLI. This keeps iOS defined but inert until App Store credentials are configured.

---

## Adding GitHub secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Required for | Required now? |
|---|---|---|
| `EXPO_TOKEN` | EAS Android/iOS builds (create at https://expo.dev → Account → Access tokens) | ✅ Yes |
| `NETLIFY_AUTH_TOKEN` | PWA deploy (https://app.netlify.com → User settings → Applications → Personal access tokens) | ✅ Yes |
| `NETLIFY_SITE_ID` | PWA deploy (Netlify → Site settings → Site information → API ID) | ✅ Yes |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Optional Play Store auto-submission (full JSON service-account key with *"Create releases"* permission) | ⏳ No |
| `APPLE_API_KEY` | Optional App Store submission (App Store Connect API key `.p8` content) | ⏳ No |
| `APPLE_API_KEY_ID` | Optional App Store submission | ⏳ No |
| `APPLE_API_ISSUER` | Optional App Store submission | ⏳ No |

### Backend Deployment (Render)

The backend is deployed to Render using `backend/render.yaml` which defines:

- **Production service** (`jumapp-api`) — auto-deploys from `master`/`main` branch
- **Staging service** (`jumapp-api-staging`) — auto-deploys from `stage` branch

#### Render secrets (set in Render dashboard)

| Secret | Production | Staging |
|---|---|---|
| `DATABASE_URL` | Neon production connection string | Neon staging DB connection string |
| `SUPER_ADMIN_TOKEN` | Production admin token | Staging admin token |
| `CORS_ORIGINS` | `https://jumapp.netlify.app` | `https://jumapp-staging.netlify.app` |
| `REDIS_URL` | (Phase 2: Upstash production) | (Phase 2: Upstash staging) |

#### Deploy flow

1. Push to GitHub → Render auto-builds the relevant service
2. Verify `https://jumapp-api.onrender.com/health` (production) or `https://jumapp-api-staging.onrender.com/health` (staging)
3. Health checks return `{"status": "ok", "version": "..."}`

#### Cold-start mitigation (Render free tier)

Render free tier suspends after 15 minutes idle. To keep warm:
- Use [UptimeRobot](https://uptimerobot.com/) free tier → ping `/health` every 5 minutes
- Or upgrade to Render Starter ($7/mo) for always-on

### EAS project linking (one-time, local)

The Android/iOS workflows run `eas build` and need the app linked to an EAS project. Run once from `frontend/` and commit the changes:

```bash
cd frontend
npx eas-cli init        # links the project, writes extra.eas.projectId into app.json
npx eas-cli build:configure   # (optional) regenerates eas.json if needed
```

Android keystore and iOS signing credentials are managed **inside EAS** (not GitHub secrets) — EAS stores them per-project and reuses them across CI builds. They can be managed with `npx eas-cli credentials`.

---

## Stage branch protection

`ci-stage.yml` runs on push/PR to `stage`. To enforce it:

1. GitHub → **Settings → Branches → Add branch protection rule** for `stage`.
2. Enable **Require a pull request before merging**.
3. Enable **Require status checks to pass before merging** and select:
   - `Lint`
   - `Unit tests`
   - `Build web + Typecheck`
4. Optionally enable **Do not allow bypassing the above settings** and **Require branches to be up to date**.

The three status checks map to the job names in `ci-stage.yml`. Any failing check blocks the merge (each job fails fast on its first failing step).

---

## Running checks locally

All commands run from the repo root unless noted. The root scripts delegate into `frontend/`.

```bash
npm run frontend:lint          # ESLint (expo lint)
npm run typecheck     # tsc --noEmit
npm run test          # Jest unit tests
npm run frontend:build:web     # expo export --platform web (outputs frontend/dist/)
```

Directly in `frontend/`:

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run frontend:build:web
```

> **Typecheck note:** Expo generates typed-route declarations (`.expo/types/`) during `expo start` / `expo export`. If you see router-type errors in a fresh checkout, run `npm run frontend:build:web` once before `npm run typecheck` (the CI `Build web + Typecheck` job does exactly this).

## Local PWA preview

```bash
cd frontend
npx expo export --platform web
npx serve dist        # or: npx http-server dist
```

## Netlify PWA config

Deployed files come from `frontend/dist/` (expo export copies `frontend/public/` into it). Two files in `frontend/public/` tune hosting behavior:

- `_redirects` — `/* /index.html 200` (SPA fallback for deep links).
- `_headers` — no-cache for `index.html` and `service-worker.js` (fresh PWA updates), immutable cache for hashed `_expo/*` assets.

## Deploy inputs reference

| Workflow | Input | Default | Notes |
|---|---|---|---|
| Deploy Android | `profile` | `production` | EAS profile from `frontend/eas.json` |
| Deploy Android | `submit` | `false` | Play Store submission via `eas submit` |
| Deploy iOS | `skip_ios` | `true` | Set `false` to actually build iOS |
| Deploy iOS | `profile` | `production` | EAS profile |
| Deploy iOS | `submit` | `false` | App Store submission via `eas submit` |
| Deploy PWA | `deploy_message` | — | Shown in Netlify deploy log |
import fs from "fs";
import path from "path";

/**
 * Regression test for the Expo SDK 54 web dev-server error overlay bug.
 *
 * Symptom: opening the PWA in the browser showed
 *   "Cannot read properties of undefined (reading 'map')"
 * at @expo/metro-runtime error-overlay/Data/LogContext.tsx:27 (useLogs).
 *
 * Root cause: @expo/cli's metroErrorInterface.js serialized the LogBox context
 * twice (`JSON.stringify(JSON.stringify(logBoxContext))`) into the
 * `_expo-static-error` script tag. The browser parsed a plain string, so
 * `raw.logs` was undefined and `raw.logs.map(...)` crashed — hiding the real
 * underlying render error behind a broken overlay.
 *
 * Fix: patches/expo++@expo/cli+54.0.27.patch (applied via `patch-package` in
 * the postinstall script) makes the CLI serialize the context exactly once.
 *
 * The first test fails if the patch is missing (e.g. node_modules reinstalled
 * without postinstall). The second test verifies the producer/client round-trip
 * contract that LogContext relies on.
 */

const EXPOSED_CLI_FILE = path.join(
  __dirname,
  "..",
  "node_modules",
  "expo",
  "node_modules",
  "@expo",
  "cli",
  "build",
  "src",
  "start",
  "server",
  "metro",
  "metroErrorInterface.js"
);

describe("Expo static error overlay patch", () => {
  it("installed @expo/cli serializes the LogBox context exactly once", () => {
    const source = fs.readFileSync(EXPOSED_CLI_FILE, "utf8");

    // The html template must embed the already-serialized string directly,
    // never re-serialize it via JSON.stringify(serializedLogBox).
    expect(source).not.toContain("JSON.stringify(serializedLogBox)");
    expect(source).toContain('type="application/json">${serializedLogBox}');
  });

  it("round-trips a single-serialized LogBox context into a usable logs array", () => {
    const logBoxContext = {
      selectedLogIndex: 0,
      isDisabled: false,
      logs: [
        {
          level: "error",
          message: { content: "Static render failed", substitutions: [] },
          stack: [],
        },
      ],
    };

    // Producer (patched @expo/cli): serialize once, escaping "<".
    const serialized = JSON.stringify(logBoxContext).replace(/</g, "\\u003c");
    const html = `<script id="_expo-static-error" type="application/json">${serialized}</script>`;

    // Client (@expo/metro-runtime LogContext): parse & map.
    const raw = JSON.parse(
      html
        .replace(/^.*?<script id="_expo-static-error" type="application\/json">/, "")
        .replace(/<\/script>.*$/, "")
    );
    expect(Array.isArray(raw.logs)).toBe(true);
    expect(raw.logs.map((log: { level: string }) => log.level)).toEqual(["error"]);
  });
});
/* eslint-disable no-undef */
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock")
);

jest.mock("expo-localization", () => ({
  getLocales: () => [{ languageCode: "en", languageTag: "en-US", textDirection: "ltr" }],
  getCalendars: () => [{ calendar: "gregory", timeZone: "Asia/Kolkata" }],
}));

let mockUuidCounter = 1;
jest.mock("expo-crypto", () => ({
  randomUUID: () => `00000000-0000-4000-8000-${String(mockUuidCounter++).padStart(12, "0")}`,
}));

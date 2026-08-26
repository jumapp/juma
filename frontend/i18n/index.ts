import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { I18nManager, Platform } from "react-native";
import { getLocales } from "expo-localization";
import AsyncStorage from "@react-native-async-storage/async-storage";

import en from "@/locales/en.json";
import hi from "@/locales/hi.json";
import ur from "@/locales/ur.json";

export const LANGUAGE_STORAGE_KEY = "jumapp:locale";

export const supportedLanguages = [
  { code: "en", name: "English", nativeName: "English", isRTL: false },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी", isRTL: false },
  { code: "ur", name: "Urdu", nativeName: "اردو", isRTL: true },
] as const;

export type SupportedLanguageCode = (typeof supportedLanguages)[number]["code"];

const resources = {
  en: { translation: en },
  hi: { translation: hi },
  ur: { translation: ur },
};

export function getDeviceLanguage(): SupportedLanguageCode {
  try {
    const deviceLocales = getLocales();
    const primaryCode = deviceLocales[0]?.languageCode?.toLowerCase();
    if (primaryCode === "hi") return "hi";
    if (primaryCode === "ur") return "ur";
    return "en";
  } catch (e) {
    return "en";
  }
}

export function applyRTL(languageCode: string): void {
  const isRTL = languageCode === "ur";
  
  if (I18nManager.isRTL !== isRTL) {
    I18nManager.allowRTL(isRTL);
    I18nManager.forceRTL(isRTL);
  }

  if (Platform.OS === "web" && typeof document !== "undefined") {
    document.documentElement.dir = isRTL ? "rtl" : "ltr";
    document.documentElement.lang = languageCode;
  }
}

export async function initI18n(): Promise<void> {
  let initialLanguage: SupportedLanguageCode = "en";

  try {
    const savedLanguage = await AsyncStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (
      savedLanguage &&
      (savedLanguage === "en" || savedLanguage === "hi" || savedLanguage === "ur")
    ) {
      initialLanguage = savedLanguage;
    } else {
      initialLanguage = getDeviceLanguage();
    }
  } catch (e) {
    initialLanguage = getDeviceLanguage();
  }

  applyRTL(initialLanguage);

  if (!i18n.isInitialized) {
    await i18n.use(initReactI18next).init({
      compatibilityJSON: "v4",
      resources,
      lng: initialLanguage,
      fallbackLng: "en",
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    });
  } else {
    await i18n.changeLanguage(initialLanguage);
  }
}

export async function changeLanguage(code: SupportedLanguageCode): Promise<void> {
  try {
    await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, code);
    await i18n.changeLanguage(code);
    applyRTL(code);
  } catch (e) {
    console.error("Failed to change language:", e);
  }
}

// Auto-initialize i18n immediately
initI18n();

export default i18n;

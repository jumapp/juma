import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { useTranslation } from "react-i18next";
import i18n, {
  supportedLanguages,
  SupportedLanguageCode,
  changeLanguage as setI18nLanguage,
  initI18n,
} from "@/i18n";

export interface I18nContextValue {
  currentLanguage: SupportedLanguageCode;
  supportedLanguages: typeof supportedLanguages;
  isRTL: boolean;
  changeLanguage: (code: SupportedLanguageCode) => Promise<void>;
  t: ReturnType<typeof useTranslation>["t"];
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState<SupportedLanguageCode>(
    (i18n.language?.substring(0, 2) as SupportedLanguageCode) || "en"
  );
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    initI18n().then(() => {
      setCurrentLanguage((i18n.language?.substring(0, 2) as SupportedLanguageCode) || "en");
      setIsReady(true);
    });

    const handleLanguageChanged = (lng: string) => {
      setCurrentLanguage((lng.substring(0, 2) as SupportedLanguageCode) || "en");
    };

    i18n.on("languageChanged", handleLanguageChanged);
    return () => {
      i18n.off("languageChanged", handleLanguageChanged);
    };
  }, []);

  const changeLanguage = useCallback(async (code: SupportedLanguageCode) => {
    await setI18nLanguage(code);
    setCurrentLanguage(code);
  }, []);

  const isRTL = currentLanguage === "ur";

  const value: I18nContextValue = {
    currentLanguage,
    supportedLanguages,
    isRTL,
    changeLanguage,
    t,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useLanguage(): I18nContextValue {
  const context = useContext(I18nContext);
  const { t } = useTranslation();

  if (!context) {
    return {
      currentLanguage: (i18n.language?.substring(0, 2) as SupportedLanguageCode) || "en",
      supportedLanguages,
      isRTL: i18n.language?.startsWith("ur") ?? false,
      changeLanguage: setI18nLanguage,
      t,
    };
  }
  return context;
}

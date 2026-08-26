import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { useColorScheme as useDeviceColorScheme } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  lightPalette,
  darkPalette,
  spacing,
  radii,
  typography,
  shadows,
  ThemePalette,
} from "@/design/tokens";

const THEME_STORAGE_KEY = "jumapp:theme";

export type ThemePreference = "system" | "light" | "dark";

export interface ThemeContextValue {
  isDark: boolean;
  colors: ThemePalette;
  spacing: typeof spacing;
  radii: typeof radii;
  typography: typeof typography;
  shadows: typeof shadows;
  themePreference: ThemePreference;
  setThemePreference: (pref: ThemePreference) => Promise<void>;
  toggleTheme: () => Promise<void>;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const deviceColorScheme = useDeviceColorScheme();
  const [themePreference, setThemePreferenceState] = useState<ThemePreference>("system");
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    async function loadTheme() {
      try {
        const saved = await AsyncStorage.getItem(THEME_STORAGE_KEY);
        if (saved === "light" || saved === "dark" || saved === "system") {
          setThemePreferenceState(saved);
        }
      } catch (e) {
        console.warn("Failed to load theme preference from storage:", e);
      } finally {
        setIsLoaded(true);
      }
    }
    loadTheme();
  }, []);

  const setThemePreference = useCallback(async (pref: ThemePreference) => {
    setThemePreferenceState(pref);
    try {
      await AsyncStorage.setItem(THEME_STORAGE_KEY, pref);
    } catch (e) {
      console.warn("Failed to save theme preference:", e);
    }
  }, []);

  const toggleTheme = useCallback(async () => {
    const nextPref: ThemePreference =
      themePreference === "light"
        ? "dark"
        : themePreference === "dark"
        ? "system"
        : "light";
    await setThemePreference(nextPref);
  }, [themePreference, setThemePreference]);

  const isDark =
    themePreference === "dark"
      ? true
      : themePreference === "light"
      ? false
      : deviceColorScheme === "dark";

  const colors = isDark ? darkPalette : lightPalette;

  const value: ThemeContextValue = {
    isDark,
    colors,
    spacing,
    radii,
    typography,
    shadows,
    themePreference,
    setThemePreference,
    toggleTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    // Fallback if rendered outside ThemeProvider
    return {
      isDark: false,
      colors: lightPalette,
      spacing,
      radii,
      typography,
      shadows,
      themePreference: "system",
      setThemePreference: async () => {},
      toggleTheme: async () => {},
    };
  }
  return context;
}

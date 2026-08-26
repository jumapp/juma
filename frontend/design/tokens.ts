import { Platform, TextStyle, ViewStyle } from "react-native";

export const brand = {
  primary: "#0a7ea4",
  primaryDark: "#006282",
  primaryLight: "#e1f5fe",
  accent: "#10b981", // Islamic emerald green
  accentDark: "#059669",
  accentLight: "#ecfdf5",
};

export const lightPalette = {
  // Brand
  primary: brand.primary,
  onPrimary: "#ffffff",
  primaryContainer: "#e0f2fe",
  onPrimaryContainer: "#034960",

  secondary: brand.accent,
  onSecondary: "#ffffff",
  secondaryContainer: "#d1fae5",
  onSecondaryContainer: "#064e3b",

  // Background & Surface
  background: "#f8fafc",
  surface: "#ffffff",
  surfaceVariant: "#f1f5f9",
  overlay: "rgba(0, 0, 0, 0.5)",

  // Typography
  text: "#0f172a",
  textSecondary: "#475569",
  textMuted: "#94a3b8",
  textInverse: "#ffffff",

  // Borders & Dividers
  border: "#e2e8f0",
  borderLight: "#f1f5f9",
  borderFocus: brand.primary,

  // Status & Feedback
  success: "#16a34a",
  onSuccess: "#ffffff",
  successContainer: "#dcfce7",
  
  error: "#dc2626",
  onError: "#ffffff",
  errorContainer: "#fee2e2",

  warning: "#d97706",
  onWarning: "#ffffff",
  warningContainer: "#fef3c7",

  info: "#0284c7",
  onInfo: "#ffffff",
  infoContainer: "#e0f2fe",

  // Controls & States
  disabled: "#e2e8f0",
  disabledText: "#94a3b8",
  skeleton: "#e2e8f0",
  skeletonHighlight: "#f8fafc",

  // Compatibility with Expo template
  tint: brand.primary,
  icon: "#64748b",
  tabIconDefault: "#64748b",
  tabIconSelected: brand.primary,
};

export const darkPalette: typeof lightPalette = {
  primary: "#38bdf8",
  onPrimary: "#082f49",
  primaryContainer: "#075985",
  onPrimaryContainer: "#e0f2fe",

  secondary: "#34d399",
  onSecondary: "#064e3b",
  secondaryContainer: "#065f46",
  onSecondaryContainer: "#d1fae5",

  background: "#0b1120",
  surface: "#1e293b",
  surfaceVariant: "#334155",
  overlay: "rgba(0, 0, 0, 0.75)",

  text: "#f8fafc",
  textSecondary: "#cbd5e1",
  textMuted: "#64748b",
  textInverse: "#0f172a",

  border: "#334155",
  borderLight: "#1e293b",
  borderFocus: "#38bdf8",

  success: "#22c55e",
  onSuccess: "#052e16",
  successContainer: "#14532d",

  error: "#ef4444",
  onError: "#450a0a",
  errorContainer: "#7f1d1d",

  warning: "#f59e0b",
  onWarning: "#451a03",
  warningContainer: "#78350f",

  info: "#38bdf8",
  onInfo: "#082f49",
  infoContainer: "#075985",

  disabled: "#334155",
  disabledText: "#64748b",
  skeleton: "#334155",
  skeletonHighlight: "#475569",

  tint: "#38bdf8",
  icon: "#94a3b8",
  tabIconDefault: "#94a3b8",
  tabIconSelected: "#38bdf8",
};

export const spacing = {
  none: 0,
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
} as const;

export const radii = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;

export const fontFamilies = Platform.select({
  ios: {
    sans: "system-ui",
    serif: "ui-serif",
    rounded: "ui-rounded",
    mono: "ui-monospace",
  },
  default: {
    sans: "normal",
    serif: "serif",
    rounded: "normal",
    mono: "monospace",
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace",
  },
});

export const typography: Record<string, TextStyle> = {
  display: {
    fontSize: 32,
    lineHeight: 40,
    fontWeight: "700",
    fontFamily: fontFamilies?.sans,
  },
  h1: {
    fontSize: 24,
    lineHeight: 32,
    fontWeight: "700",
    fontFamily: fontFamilies?.sans,
  },
  h2: {
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "600",
    fontFamily: fontFamilies?.sans,
  },
  h3: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "600",
    fontFamily: fontFamilies?.sans,
  },
  body: {
    fontSize: 16,
    lineHeight: 22,
    fontWeight: "400",
    fontFamily: fontFamilies?.sans,
  },
  bodyBold: {
    fontSize: 16,
    lineHeight: 22,
    fontWeight: "600",
    fontFamily: fontFamilies?.sans,
  },
  bodySmall: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "400",
    fontFamily: fontFamilies?.sans,
  },
  bodySmallBold: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "600",
    fontFamily: fontFamilies?.sans,
  },
  caption: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "400",
    fontFamily: fontFamilies?.sans,
  },
  label: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "600",
    fontFamily: fontFamilies?.sans,
  },
};

export const shadows = {
  none: {
    shadowColor: "transparent",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  } as ViewStyle,
  sm: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  } as ViewStyle,
  md: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  } as ViewStyle,
  lg: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
  } as ViewStyle,
};

export type ThemePalette = typeof lightPalette;
export type SpacingKey = keyof typeof spacing;
export type RadiiKey = keyof typeof radii;
export type TypographyKey = keyof typeof typography;

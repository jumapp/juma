import { Colors } from "../constants/theme";
import {
  lightPalette,
  darkPalette,
  spacing,
  radii,
  typography,
} from "../design/tokens";

describe("Theme and Design Tokens", () => {
  it("defines light and dark color palettes with required semantic roles", () => {
    expect(lightPalette.primary).toBeDefined();
    expect(lightPalette.onPrimary).toBeDefined();
    expect(lightPalette.background).toBeDefined();
    expect(lightPalette.surface).toBeDefined();
    expect(lightPalette.text).toBeDefined();
    expect(lightPalette.border).toBeDefined();
    expect(lightPalette.success).toBeDefined();
    expect(lightPalette.error).toBeDefined();

    expect(darkPalette.primary).toBeDefined();
    expect(darkPalette.background).toBeDefined();
    expect(darkPalette.text).toBeDefined();
  });

  it("defines distinct light and dark palettes", () => {
    expect(lightPalette).not.toEqual(darkPalette);
  });

  it("exports legacy Colors object matching tokens", () => {
    expect(Colors.light.primary).toBe(lightPalette.primary);
    expect(Colors.dark.primary).toBe(darkPalette.primary);
  });

  it("provides valid spacing scale", () => {
    expect(spacing.none).toBe(0);
    expect(spacing.xs).toBe(4);
    expect(spacing.sm).toBe(8);
    expect(spacing.md).toBe(12);
    expect(spacing.lg).toBe(16);
    expect(spacing.xl).toBe(24);
  });

  it("provides valid border radii scale", () => {
    expect(radii.none).toBe(0);
    expect(radii.sm).toBe(4);
    expect(radii.md).toBe(8);
    expect(radii.full).toBe(9999);
  });

  it("provides standard typography scale with font properties", () => {
    expect(typography.display.fontSize).toBe(32);
    expect(typography.h1.fontSize).toBe(24);
    expect(typography.h2.fontSize).toBe(20);
    expect(typography.body.fontSize).toBe(16);
    expect(typography.caption.fontSize).toBe(12);
  });
});

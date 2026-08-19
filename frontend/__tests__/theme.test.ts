import { Colors } from '../constants/theme';

describe('theme constants', () => {
  it('defines light and dark color palettes', () => {
    expect(Colors.light.background).toBe('#fff');
    expect(Colors.dark.background).toBe('#151718');
  });

  it('defines distinct light and dark palettes', () => {
    expect(Colors.light).not.toEqual(Colors.dark);
  });

  it('defines tint colors for both color modes', () => {
    expect(Colors.light.tint).toBe('#0a7ea4');
    expect(Colors.dark.tint).toBe('#fff');
  });

  it('reuses the tint color for the selected tab icon', () => {
    expect(Colors.light.tabIconSelected).toBe(Colors.light.tint);
    expect(Colors.dark.tabIconSelected).toBe(Colors.dark.tint);
  });
});
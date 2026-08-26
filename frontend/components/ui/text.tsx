import React from "react";
import { Text as RNText, TextProps as RNTextProps, TextStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { TypographyKey } from "@/design/tokens";

export interface TextProps extends RNTextProps {
  variant?: TypographyKey;
  color?: "primary" | "secondary" | "muted" | "inverse" | "error" | "success" | "brand" | string;
  align?: "auto" | "left" | "right" | "center" | "justify";
  children: React.ReactNode;
}

export function Text({
  variant = "body",
  color = "primary",
  align,
  style,
  children,
  ...props
}: TextProps) {
  const { colors, typography } = useTheme();

  const resolveColor = (): string => {
    switch (color) {
      case "primary":
        return colors.text;
      case "secondary":
        return colors.textSecondary;
      case "muted":
        return colors.textMuted;
      case "inverse":
        return colors.textInverse;
      case "error":
        return colors.error;
      case "success":
        return colors.success;
      case "brand":
        return colors.primary;
      default:
        return color;
    }
  };

  const textStyle: TextStyle = {
    ...typography[variant],
    color: resolveColor(),
    textAlign: align,
  };

  return (
    <RNText style={[textStyle, style]} {...props}>
      {children}
    </RNText>
  );
}

import React from "react";
import {
  Pressable,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";

export interface CardProps {
  children: React.ReactNode;
  variant?: "elevated" | "outlined" | "filled";
  onPress?: () => void;
  style?: ViewStyle;
  padding?: "none" | "sm" | "md" | "lg";
  accessibilityLabel?: string;
}

export function Card({
  children,
  variant = "elevated",
  onPress,
  style,
  padding = "md",
  accessibilityLabel,
}: CardProps) {
  const { colors, radii, shadows, spacing } = useTheme();

  const paddingValues = {
    none: 0,
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
  }[padding];

  const getVariantStyle = (): ViewStyle => {
    switch (variant) {
      case "outlined":
        return {
          backgroundColor: colors.surface,
          borderColor: colors.border,
          borderWidth: 1,
        };
      case "filled":
        return {
          backgroundColor: colors.surfaceVariant,
          borderColor: "transparent",
          borderWidth: 0,
        };
      case "elevated":
      default:
        return {
          backgroundColor: colors.surface,
          borderColor: colors.borderLight,
          borderWidth: 1,
          ...shadows.sm,
        };
    }
  };

  const containerStyle: ViewStyle = {
    borderRadius: radii.lg,
    padding: paddingValues,
    overflow: "hidden",
    ...getVariantStyle(),
  };

  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel}
        style={({ pressed }) => [
          containerStyle,
          { opacity: pressed ? 0.92 : 1 },
          style,
        ]}
      >
        {children}
      </Pressable>
    );
  }

  return <View style={[containerStyle, style]}>{children}</View>;
}

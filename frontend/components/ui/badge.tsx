import React from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";

export interface BadgeProps {
  label: string;
  variant?: "primary" | "secondary" | "success" | "warning" | "error" | "info" | "neutral";
  size?: "sm" | "md";
  style?: ViewStyle;
}

export function Badge({
  label,
  variant = "primary",
  size = "md",
  style,
}: BadgeProps) {
  const { colors, radii } = useTheme();

  const getVariantColors = (): { bg: string; text: string } => {
    switch (variant) {
      case "secondary":
        return { bg: colors.secondaryContainer, text: colors.secondary };
      case "success":
        return { bg: colors.successContainer, text: colors.success };
      case "warning":
        return { bg: colors.warningContainer, text: colors.warning };
      case "error":
        return { bg: colors.errorContainer, text: colors.error };
      case "info":
        return { bg: colors.infoContainer, text: colors.info };
      case "neutral":
        return { bg: colors.surfaceVariant, text: colors.textSecondary };
      case "primary":
      default:
        return { bg: colors.primaryContainer, text: colors.primary };
    }
  };

  const { bg, text } = getVariantColors();

  const paddingHorizontal = size === "sm" ? 6 : 10;
  const paddingVertical = size === "sm" ? 2 : 4;

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: bg,
          borderRadius: radii.full,
          paddingHorizontal,
          paddingVertical,
        },
        style,
      ]}
    >
      <Text
        variant={size === "sm" ? "caption" : "label"}
        style={{ color: text, fontWeight: "600" }}
      >
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    alignItems: "center",
    justifyContent: "center",
  },
});

import React from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";

export interface DividerProps {
  orientation?: "horizontal" | "vertical";
  style?: ViewStyle;
}

export function Divider({
  orientation = "horizontal",
  style,
}: DividerProps) {
  const { colors, spacing } = useTheme();

  if (orientation === "vertical") {
    return (
      <View
        style={[
          styles.vertical,
          {
            backgroundColor: colors.borderLight,
            marginHorizontal: spacing.sm,
          },
          style,
        ]}
      />
    );
  }

  return (
    <View
      style={[
        styles.horizontal,
        {
          backgroundColor: colors.borderLight,
          marginVertical: spacing.sm,
        },
        style,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  horizontal: {
    height: StyleSheet.hairlineWidth,
    width: "100%",
  },
  vertical: {
    width: StyleSheet.hairlineWidth,
    height: "100%",
  },
});

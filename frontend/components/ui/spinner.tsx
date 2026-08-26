import React from "react";
import { ActivityIndicator, StyleSheet, View, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";

export interface SpinnerProps {
  size?: "small" | "large";
  color?: string;
  style?: ViewStyle;
}

export function Spinner({ size = "small", color, style }: SpinnerProps) {
  const { colors } = useTheme();

  return (
    <View style={[styles.container, style]}>
      <ActivityIndicator size={size} color={color || colors.primary} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    padding: 8,
  },
});

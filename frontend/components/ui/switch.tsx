import React from "react";
import {
  Platform,
  StyleSheet,
  Switch as RNSwitch,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";

export interface SwitchProps {
  value: boolean;
  onValueChange: (value: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Switch({
  value,
  onValueChange,
  label,
  description,
  disabled = false,
  style,
}: SwitchProps) {
  const { colors, spacing } = useTheme();

  return (
    <View style={[styles.container, style]}>
      {label || description ? (
        <View style={[styles.textContainer, { marginRight: spacing.md }]}>
          {label ? (
            <Text variant="bodyBold" color={disabled ? "muted" : "primary"}>
              {label}
            </Text>
          ) : null}
          {description ? (
            <Text variant="bodySmall" color="secondary" style={styles.description}>
              {description}
            </Text>
          ) : null}
        </View>
      ) : null}

      <RNSwitch
        value={value}
        onValueChange={onValueChange}
        disabled={disabled}
        trackColor={{ false: colors.disabled, true: colors.primaryContainer }}
        thumbColor={value ? colors.primary : Platform.OS === "android" ? colors.surface : colors.surface}
        ios_backgroundColor={colors.disabled}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 8,
    minHeight: 44,
  },
  textContainer: {
    flex: 1,
  },
  description: {
    marginTop: 2,
  },
});

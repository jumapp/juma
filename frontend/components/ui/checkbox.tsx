import React from "react";
import {
  Pressable,
  StyleSheet,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";
import { IconSymbol } from "./icon-symbol";

export interface CheckboxProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Checkbox({
  checked,
  onCheckedChange,
  label,
  description,
  disabled = false,
  style,
}: CheckboxProps) {
  const { colors, radii, spacing } = useTheme();

  return (
    <Pressable
      onPress={() => onCheckedChange(!checked)}
      disabled={disabled}
      accessibilityRole="checkbox"
      accessibilityState={{ checked, disabled }}
      style={({ pressed }) => [
        styles.container,
        { opacity: disabled ? 0.4 : pressed ? 0.8 : 1 },
        style,
      ]}
    >
      <View
        style={[
          styles.box,
          {
            borderRadius: radii.sm,
            borderColor: checked ? colors.primary : colors.border,
            backgroundColor: checked ? colors.primary : colors.surface,
            marginRight: spacing.md,
          },
        ]}
      >
        {checked ? <IconSymbol name="checkmark" size={14} color={colors.onPrimary} /> : null}
      </View>

      {label || description ? (
        <View style={styles.textContainer}>
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
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
    minHeight: 44,
  },
  box: {
    width: 22,
    height: 22,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  textContainer: {
    flex: 1,
  },
  description: {
    marginTop: 2,
  },
});

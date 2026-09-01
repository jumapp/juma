import React from "react";
import { Platform, StyleSheet, View, ViewStyle } from "react-native";
import { Text } from "@/components/ui/text";
import { useTheme } from "@/providers/theme-provider";

export interface SwitchProps {
  value?: boolean;
  checked?: boolean;
  onValueChange: (value: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  style?: ViewStyle;
}

/**
 * Platform-aware Switch component.
 * - Native (iOS/Android): uses RNSwitch
 * - Web: uses HTML checkbox input styled as toggle
 *
 * Accepts both `value` and `checked` prop names for flexibility.
 */
export function Switch({
  value,
  checked,
  onValueChange,
  label,
  description,
  disabled = false,
  style,
}: SwitchProps) {
  // Support both `value` and `checked` prop names for flexibility
  const isOn = checked ?? value ?? false;
  const { colors, spacing } = useTheme();

  // Web implementation using HTML checkbox
  if (Platform.OS === "web") {
    return (
      <View
        style={[
          styles.container,
          {
            backgroundColor: disabled ? colors.disabled : isOn ? colors.primaryContainer : colors.surfaceVariant,
            borderWidth: 1,
            borderColor: disabled ? colors.border : isOn ? colors.primary : colors.border,
            borderRadius: 16,
          },
          style,
        ]}
      >
        <input
          type="checkbox"
          checked={isOn}
          onChange={(e) => onValueChange(e.target.checked)}
          disabled={disabled}
          style={styles.webInput}
        />
        {label || description ? (
          <View style={[styles.textContainer, { marginRight: spacing.md }]}>
            {label ? (
              <View>
                <Text variant="bodyBold" color={disabled ? "muted" : "primary"}>
                  {label}
                </Text>
              </View>
            ) : null}
            {description ? (
              <Text variant="bodySmall" color="secondary" style={styles.description}>
                {description}
              </Text>
            ) : null}
          </View>
        ) : null}
      </View>
    );
  }

  // Native implementation
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

      <View
        style={[
          styles.nativeTrack,
          {
            backgroundColor: isOn ? colors.primaryContainer : colors.disabled,
            borderRadius: 16,
            width: 51,
            height: 31,
            justifyContent: "center",
            padding: 2,
          },
        ]}
      >
        <View
          style={[
            styles.nativeThumb,
            {
              width: 27,
              height: 27,
              borderRadius: 13.5,
              backgroundColor: isOn ? colors.primary : colors.surface,
            },
          ]}
        />
      </View>
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
  webInput: {
    width: 20,
    height: 20,
    marginRight: 8,
    cursor: "pointer",
  },
  nativeTrack: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  nativeThumb: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 2,
    elevation: 2,
  },
});

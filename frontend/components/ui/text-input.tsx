import React, { useState } from "react";
import {
  StyleSheet,
  TextInput as RNTextInput,
  TextInputProps as RNTextInputProps,
  TextStyle,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";

export interface TextInputProps extends RNTextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  leftAccessory?: React.ReactNode;
  rightAccessory?: React.ReactNode;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
}

export function TextInput({
  label,
  error,
  helperText,
  leftAccessory,
  rightAccessory,
  containerStyle,
  inputStyle,
  style,
  onFocus,
  onBlur,
  ...props
}: TextInputProps) {
  const { colors, radii, spacing, typography } = useTheme();
  const [isFocused, setIsFocused] = useState(false);

  const hasError = Boolean(error);

  const getBorderColor = (): string => {
    if (hasError) return colors.error;
    if (isFocused) return colors.borderFocus;
    return colors.border;
  };

  return (
    <View style={[styles.container, containerStyle]}>
      {label ? (
        <Text
          variant="label"
          color={hasError ? "error" : isFocused ? "brand" : "secondary"}
          style={styles.label}
        >
          {label}
        </Text>
      ) : null}

      <View
        style={[
          styles.inputContainer,
          {
            backgroundColor: colors.surface,
            borderColor: getBorderColor(),
            borderRadius: radii.md,
            borderWidth: isFocused || hasError ? 1.5 : 1,
            paddingHorizontal: spacing.md,
          },
        ]}
      >
        {leftAccessory ? (
          <View style={[styles.accessory, { marginRight: spacing.sm }]}>
            {leftAccessory}
          </View>
        ) : null}

        <RNTextInput
          placeholderTextColor={colors.textMuted}
          style={[
            styles.input,
            typography.body,
            {
              color: colors.text,
            },
            inputStyle,
            style,
          ]}
          onFocus={(e) => {
            setIsFocused(true);
            onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            onBlur?.(e);
          }}
          {...props}
        />

        {rightAccessory ? (
          <View style={[styles.accessory, { marginLeft: spacing.sm }]}>
            {rightAccessory}
          </View>
        ) : null}
      </View>

      {hasError ? (
        <Text variant="caption" color="error" style={styles.helper}>
          {error}
        </Text>
      ) : helperText ? (
        <Text variant="caption" color="muted" style={styles.helper}>
          {helperText}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 6,
    width: "100%",
  },
  label: {
    marginBottom: 4,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    minHeight: 48,
  },
  input: {
    flex: 1,
    paddingVertical: 10,
  },
  accessory: {
    alignItems: "center",
    justifyContent: "center",
  },
  helper: {
    marginTop: 4,
  },
});

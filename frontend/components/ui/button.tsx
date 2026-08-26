import React from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextStyle,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "danger";

export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
}

export function Button({
  title,
  onPress,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  style,
  textStyle,
  accessibilityLabel,
}: ButtonProps) {
  const { colors, radii, typography } = useTheme();

  const isDisabled = disabled || loading;

  const getContainerStyle = (pressed: boolean): ViewStyle => {
    let backgroundColor = colors.primary;
    let borderColor = "transparent";
    let borderWidth = 0;
    let opacity = pressed ? 0.8 : 1;

    if (isDisabled) {
      opacity = 0.5;
    }

    switch (variant) {
      case "primary":
        backgroundColor = colors.primary;
        break;
      case "secondary":
        backgroundColor = colors.secondary;
        break;
      case "outline":
        backgroundColor = "transparent";
        borderColor = colors.primary;
        borderWidth = 1.5;
        break;
      case "ghost":
        backgroundColor = pressed ? colors.surfaceVariant : "transparent";
        break;
      case "danger":
        backgroundColor = colors.error;
        break;
    }

    const sizePadding: Record<ButtonSize, { paddingVertical: number; paddingHorizontal: number; minHeight: number }> = {
      sm: { paddingVertical: 8, paddingHorizontal: 12, minHeight: 36 },
      md: { paddingVertical: 12, paddingHorizontal: 16, minHeight: 44 },
      lg: { paddingVertical: 14, paddingHorizontal: 20, minHeight: 52 },
    };

    return {
      backgroundColor,
      borderColor,
      borderWidth,
      borderRadius: radii.md,
      opacity,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      ...sizePadding[size],
    };
  };

  const getTextColor = (): string => {
    if (variant === "outline" || variant === "ghost") {
      return colors.primary;
    }
    if (variant === "danger") {
      return colors.onError;
    }
    if (variant === "secondary") {
      return colors.onSecondary;
    }
    return colors.onPrimary;
  };

  const getTextTypography = (): TextStyle => {
    switch (size) {
      case "sm":
        return typography.bodySmallBold;
      case "lg":
        return typography.h3;
      case "md":
      default:
        return typography.bodyBold;
    }
  };

  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || title}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      style={({ pressed }) => [getContainerStyle(pressed), style]}
    >
      {loading ? (
        <ActivityIndicator size="small" color={getTextColor()} />
      ) : (
        <View style={styles.contentRow}>
          {leftIcon ? <View style={styles.leftIcon}>{leftIcon}</View> : null}
          <Text
            style={[
              getTextTypography(),
              { color: getTextColor(), textAlign: "center" },
              textStyle,
            ]}
          >
            {title}
          </Text>
          {rightIcon ? <View style={styles.rightIcon}>{rightIcon}</View> : null}
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  contentRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  leftIcon: {
    marginRight: 8,
  },
  rightIcon: {
    marginLeft: 8,
  },
});

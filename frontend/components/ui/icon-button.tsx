import React from "react";
import { Pressable, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";

export interface IconButtonProps {
  icon: React.ReactNode;
  onPress: () => void;
  size?: "sm" | "md" | "lg";
  variant?: "standard" | "filled" | "tonal" | "outlined";
  disabled?: boolean;
  accessibilityLabel: string;
  style?: ViewStyle;
}

export function IconButton({
  icon,
  onPress,
  size = "md",
  variant = "standard",
  disabled = false,
  accessibilityLabel,
  style,
}: IconButtonProps) {
  const { colors, radii } = useTheme();

  const dimensions = {
    sm: 36,
    md: 44,
    lg: 52,
  }[size];

  const getStyle = (pressed: boolean): ViewStyle => {
    let backgroundColor = "transparent";
    let borderColor = "transparent";
    let borderWidth = 0;

    switch (variant) {
      case "filled":
        backgroundColor = colors.primary;
        break;
      case "tonal":
        backgroundColor = colors.surfaceVariant;
        break;
      case "outlined":
        borderColor = colors.border;
        borderWidth = 1;
        break;
      case "standard":
      default:
        backgroundColor = pressed ? colors.surfaceVariant : "transparent";
        break;
    }

    return {
      width: dimensions,
      height: dimensions,
      borderRadius: radii.full,
      backgroundColor,
      borderColor,
      borderWidth,
      alignItems: "center",
      justifyContent: "center",
      opacity: disabled ? 0.4 : pressed ? 0.75 : 1,
    };
  };

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ disabled }}
      style={({ pressed }) => [getStyle(pressed), style]}
    >
      {icon}
    </Pressable>
  );
}

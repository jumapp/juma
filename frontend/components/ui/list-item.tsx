import React from "react";
import {
  Pressable,
  StyleSheet,
  View,
  ViewStyle,
} from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";

export interface ListItemProps {
  title: string;
  subtitle?: string;
  left?: React.ReactNode;
  right?: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
  disabled?: boolean;
}

export function ListItem({
  title,
  subtitle,
  left,
  right,
  onPress,
  style,
  disabled = false,
}: ListItemProps) {
  const { colors, spacing } = useTheme();

  const content = (
    <View
      style={[
        styles.container,
        {
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.lg,
          borderBottomColor: colors.borderLight,
          opacity: disabled ? 0.5 : 1,
        },
        style,
      ]}
    >
      {left ? <View style={[styles.left, { marginRight: spacing.md }]}>{left}</View> : null}

      <View style={styles.textContainer}>
        <Text variant="bodyBold" color="primary" numberOfLines={1}>
          {title}
        </Text>
        {subtitle ? (
          <Text
            variant="bodySmall"
            color="secondary"
            numberOfLines={2}
            style={styles.subtitle}
          >
            {subtitle}
          </Text>
        ) : null}
      </View>

      {right ? <View style={[styles.right, { marginLeft: spacing.md }]}>{right}</View> : null}
    </View>
  );

  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        disabled={disabled}
        accessibilityRole="button"
        style={({ pressed }) => [
          { backgroundColor: pressed ? colors.surfaceVariant : "transparent" },
        ]}
      >
        {content}
      </Pressable>
    );
  }

  return content;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    borderBottomWidth: StyleSheet.hairlineWidth,
    minHeight: 56,
  },
  left: {
    alignItems: "center",
    justifyContent: "center",
  },
  textContainer: {
    flex: 1,
    justifyContent: "center",
  },
  subtitle: {
    marginTop: 2,
  },
  right: {
    alignItems: "center",
    justifyContent: "center",
  },
});

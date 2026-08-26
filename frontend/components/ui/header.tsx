import React from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import { useRouter } from "expo-router";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";
import { IconButton } from "./icon-button";
import { IconSymbol } from "./icon-symbol";

export interface HeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  style?: ViewStyle;
}

export function Header({
  title,
  subtitle,
  showBack = false,
  onBack,
  rightAction,
  style,
}: HeaderProps) {
  const router = useRouter();
  const { colors, spacing } = useTheme();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: colors.surface,
          borderBottomColor: colors.borderLight,
          paddingHorizontal: spacing.md,
          paddingVertical: spacing.sm,
        },
        style,
      ]}
    >
      <View style={styles.left}>
        {showBack ? (
          <IconButton
            icon={<IconSymbol name="chevron.left" size={24} color={colors.text} />}
            onPress={handleBack}
            accessibilityLabel="Go back"
            size="sm"
          />
        ) : null}
      </View>

      <View style={styles.center}>
        <Text variant="h3" align="center" color="primary" numberOfLines={1}>
          {title}
        </Text>
        {subtitle ? (
          <Text variant="caption" align="center" color="secondary" numberOfLines={1}>
            {subtitle}
          </Text>
        ) : null}
      </View>

      <View style={styles.right}>{rightAction}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    minHeight: 52,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  left: {
    width: 44,
    alignItems: "flex-start",
    justifyContent: "center",
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  right: {
    width: 44,
    alignItems: "flex-end",
    justifyContent: "center",
  },
});

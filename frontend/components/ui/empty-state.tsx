import React from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";
import { Button } from "./button";

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  style?: ViewStyle;
}

export function EmptyState({
  title,
  description,
  icon,
  actionLabel,
  onAction,
  style,
}: EmptyStateProps) {
  const { spacing } = useTheme();

  return (
    <View style={[styles.container, { padding: spacing.xl }, style]}>
      {icon ? <View style={[styles.iconContainer, { marginBottom: spacing.md }]}>{icon}</View> : null}
      <Text variant="h3" align="center" color="primary" style={styles.title}>
        {title}
      </Text>
      {description ? (
        <Text
          variant="bodySmall"
          align="center"
          color="secondary"
          style={[styles.description, { marginBottom: spacing.lg }]}
        >
          {description}
        </Text>
      ) : null}
      {actionLabel && onAction ? (
        <Button title={actionLabel} onPress={onAction} variant="outline" size="sm" />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
  },
  iconContainer: {
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    marginBottom: 4,
  },
  description: {
    maxWidth: 280,
  },
});

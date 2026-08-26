import React from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "./text";
import { Button } from "./button";

export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  style?: ViewStyle;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  retryLabel = "Try Again",
  style,
}: ErrorStateProps) {
  const { colors, radii, spacing } = useTheme();

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: colors.errorContainer,
          borderColor: colors.error,
          borderRadius: radii.md,
          padding: spacing.lg,
        },
        style,
      ]}
    >
      <Text variant="bodyBold" style={{ color: colors.error, marginBottom: 4 }}>
        {title}
      </Text>
      <Text
        variant="bodySmall"
        style={{ color: colors.error, marginBottom: onRetry ? spacing.md : 0 }}
      >
        {message}
      </Text>
      {onRetry ? (
        <Button
          title={retryLabel}
          onPress={onRetry}
          variant="danger"
          size="sm"
          style={{ alignSelf: "flex-start" }}
        />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderWidth: 1,
    marginVertical: 8,
    width: "100%",
  },
});

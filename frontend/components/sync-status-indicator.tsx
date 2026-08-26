import React from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import { useSync } from "@/hooks/use-sync";
import { useTheme } from "@/providers/theme-provider";
import { useTranslation } from "react-i18next";
import { Card, Text, Button, Badge } from "@/components/ui";

export function SyncStatusIndicator() {
  const { isSyncing, pendingCount, failedCount, lastSyncTime, flushOutbox } =
    useSync();
  const { colors, spacing } = useTheme();
  const { t } = useTranslation();

  const formattedTime = lastSyncTime
    ? new Date(lastSyncTime).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "Never";

  return (
    <Card variant="outlined" style={styles.card}>
      <View style={styles.row}>
        <View style={styles.infoCol}>
          <Text variant="h3" color="primary">
            {t("settings.sync_queue_status")}
          </Text>
          <Text variant="caption" color="muted">
            {t("common.last_updated")}: {formattedTime}
          </Text>
        </View>

        <View style={styles.badgeCol}>
          {isSyncing ? (
            <Badge label={t("sync.syncing")} variant="info" />
          ) : failedCount > 0 ? (
            <Badge label={`${failedCount} ${t("sync.sync_failed")}`} variant="error" />
          ) : pendingCount > 0 ? (
            <Badge label={`${pendingCount} ${t("sync.pending_changes")}`} variant="warning" />
          ) : (
            <Badge label={t("sync.synced")} variant="success" />
          )}
        </View>
      </View>

      <View style={[styles.actionRow, { marginTop: spacing.md }]}>
        <Button
          title={isSyncing ? t("sync.syncing") : t("sync.flush_now")}
          onPress={() => flushOutbox()}
          variant="outline"
          size="sm"
          disabled={isSyncing}
          leftIcon={
            isSyncing ? (
              <ActivityIndicator size="small" color={colors.primary} />
            ) : undefined
          }
        />
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginVertical: 8,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  infoCol: {
    flex: 1,
  },
  badgeCol: {
    marginLeft: 8,
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
  },
});

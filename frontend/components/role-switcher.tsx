import React, { useState } from "react";
import { StyleSheet, View } from "react-native";
import { useAuth } from "@/hooks/use-auth";
import { DEV_ROLE_OPTIONS, UserRole } from "@/services/auth/types";
import { useTheme } from "@/providers/theme-provider";
import {
  Card,
  Text,
  Chip,
  TextInput,
  Button,
  Badge,
} from "@/components/ui";

export function RoleSwitcher() {
  const { role, masjidId, switchRole } = useAuth();
  const { spacing } = useTheme();
  const [selectedRole, setSelectedRole] = useState<UserRole>(role);
  const [targetMasjidId, setTargetMasjidId] = useState(masjidId || "");
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const selectedOption = DEV_ROLE_OPTIONS.find((r) => r.role === selectedRole);

  const handleApply = async () => {
    setIsSaving(true);
    setFeedback(null);
    try {
      await switchRole(
        selectedRole,
        selectedOption?.requiresMasjidScope ? targetMasjidId || undefined : undefined
      );
      setFeedback(`Active role set to ${selectedOption?.label}`);
    } catch {
      setFeedback("Failed to update role");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card variant="outlined" style={styles.card}>
      <View style={styles.headerRow}>
        <Text variant="h3" color="primary">
          Developer Role Switcher
        </Text>
        <Badge
          label={selectedOption?.label || role}
          variant={role === "super_admin" ? "primary" : role === "viewer" ? "neutral" : "success"}
        />
      </View>

      <Text variant="bodySmall" color="secondary" style={styles.desc}>
        Select a role to test role-based access control and scoped operations.
      </Text>

      <View style={[styles.chipsRow, { marginVertical: spacing.md }]}>
        {DEV_ROLE_OPTIONS.map((opt) => (
          <Chip
            key={opt.role}
            label={opt.label}
            selected={selectedRole === opt.role}
            onPress={() => setSelectedRole(opt.role)}
            style={styles.chip}
          />
        ))}
      </View>

      <Text variant="caption" color="muted" style={styles.roleDesc}>
        {selectedOption?.description}
      </Text>

      {selectedOption?.requiresMasjidScope ? (
        <View style={styles.scopeContainer}>
          <TextInput
            label="Masjid Scope ID (UUID)"
            placeholder="00000000-0000-0000-0000-000000000001"
            value={targetMasjidId}
            onChangeText={setTargetMasjidId}
            helperText="Editor write operations require this masjid ID."
          />
        </View>
      ) : null}

      {feedback ? (
        <Text variant="caption" color="brand" style={styles.feedback}>
          {feedback}
        </Text>
      ) : null}

      <Button
        title={isSaving ? "Saving..." : "Apply Role"}
        onPress={handleApply}
        variant="primary"
        size="sm"
        disabled={isSaving}
        style={styles.applyButton}
      />
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginVertical: 12,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  desc: {
    marginTop: 4,
  },
  chipsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  chip: {
    marginBottom: 4,
  },
  roleDesc: {
    marginBottom: 8,
    fontStyle: "italic",
  },
  scopeContainer: {
    marginVertical: 6,
  },
  feedback: {
    marginVertical: 6,
    fontWeight: "600",
  },
  applyButton: {
    marginTop: 8,
    alignSelf: "flex-start",
  },
});

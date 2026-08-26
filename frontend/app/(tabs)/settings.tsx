import { RoleSwitcher } from "@/components/role-switcher";
import { SyncStatusIndicator } from "@/components/sync-status-indicator";
import { Card, Chip, Divider, Screen, Switch, Text } from "@/components/ui";
import { useLanguage } from "@/hooks/use-language";
import { useTheme } from "@/providers/theme-provider";
import React from "react";
import { useTranslation } from "react-i18next";
import { StyleSheet, View } from "react-native";

export default function SettingsScreen() {
  const { t } = useTranslation();
  const { currentLanguage, supportedLanguages, changeLanguage } = useLanguage();
  const { themePreference, setThemePreference } = useTheme();

  const handleThemeChange = async (pref: "system" | "light" | "dark") => {
    await setThemePreference(pref);
  };

  const handleLanguageChange = async (code: string) => {
    await changeLanguage(code as any);
  };

  return (
    <Screen scrollable contentContainerStyle={styles.container}>
      <Text variant="h1" color="primary">{t("settings.title")}</Text>

      <Card variant="outlined" style={styles.card}>
        <Text variant="h3" color="primary" style={styles.sectionTitle}>
          {t("settings.language_label")}
        </Text>
        <View style={styles.chipsRow}>
          {supportedLanguages.map((lang) => (
            <Chip
              key={lang.code}
              label={lang.nativeName}
              selected={currentLanguage === lang.code}
              onPress={() => handleLanguageChange(lang.code)}
            />
          ))}
        </View>
      </Card>

      <Card variant="outlined" style={styles.card}>
        <Text variant="h3" color="primary" style={styles.sectionTitle}>
          {t("settings.theme_label")}
        </Text>
        <View style={styles.switchRow}>
          <Text variant="body" color="primary">
            {t("common.system_mode")}
          </Text>
          <Switch
            value={themePreference === "system"}
            onValueChange={(v) => v && handleThemeChange("system")}
          />
        </View>
        <Divider />
        <View style={styles.switchRow}>
          <Text variant="body" color="primary">
            {t("common.light_mode")}
          </Text>
          <Switch
            value={themePreference === "light"}
            onValueChange={(v) => v && handleThemeChange("light")}
          />
        </View>
        <Divider />
        <View style={styles.switchRow}>
          <Text variant="body" color="primary">
            {t("common.dark_mode")}
          </Text>
          <Switch
            value={themePreference === "dark"}
            onValueChange={(v) => v && handleThemeChange("dark")}
          />
        </View>
      </Card>

      <RoleSwitcher />

      <SyncStatusIndicator />

      <Card variant="outlined" style={styles.card}>
        <Text variant="caption" color="muted">
          {t("settings.version")}: 1.0.0
        </Text>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  card: {
    marginVertical: 8,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  chipsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  switchRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 8,
  },
});

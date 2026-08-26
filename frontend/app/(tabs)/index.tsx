import React from "react";
import { StyleSheet, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useMasjids } from "@/hooks/queries/use-masjids";
import { useTheme } from "@/providers/theme-provider";
import { Screen, Text, Card, ListItem, Skeleton, EmptyState, Badge } from "@/components/ui";
import { config } from "@/lib/config";

export default function HomeScreen() {
  const { t } = useTranslation();
  const { spacing } = useTheme();

  // Fetch nearby masjids using default Dehradun coordinates
  const { data: masjids, isLoading, isError, error } = useMasjids({
    lat: config.defaultCoordinates.latitude,
    lon: config.defaultCoordinates.longitude,
    radius: config.defaultRadiusMeters,
  });

  if (isLoading) {
    return (
      <Screen scrollable contentContainerStyle={styles.container}>
        <Text variant="h1" color="primary" style={styles.title}>
          {t("home.title")}
        </Text>
        <Text variant="body" color="secondary" style={styles.subtitle}>
          {t("home.subtitle")}
        </Text>

        <Text variant="h3" color="primary" style={[styles.sectionTitle, { marginTop: spacing.xl }]}>
          {t("home.nearby_masjids")}
        </Text>

        <View style={styles.skeletonContainer}>
          <Skeleton height={60} style={styles.skeletonItem} />
          <Skeleton height={60} style={styles.skeletonItem} />
          <Skeleton height={60} style={styles.skeletonItem} />
        </View>
      </Screen>
    );
  }

  if (isError) {
    return (
      <Screen scrollable contentContainerStyle={styles.container}>
        <EmptyState
          title={t("errors.generic")}
          description={error?.message || t("errors.network")}
        />
      </Screen>
    );
  }

  return (
    <Screen scrollable contentContainerStyle={styles.container}>
      <Text variant="h1" color="primary" style={styles.title}>
        {t("home.title")}
      </Text>
      <Text variant="body" color="secondary" style={styles.subtitle}>
        {t("home.subtitle")}
      </Text>

      <Text variant="h3" color="primary" style={[styles.sectionTitle, { marginTop: spacing.xl }]}>
        {t("home.nearby_masjids")}
      </Text>

      {masjids && masjids.length > 0 ? (
        <Card variant="elevated" style={styles.card}>
          {masjids.map((masjid) => (
            <ListItem
              key={masjid.id}
              title={masjid.name}
              subtitle={`${masjid.city}, ${masjid.state}`}
              onPress={() => { /* TODO: navigate to masjid detail */ }}
              right={
                masjid.distance_meters !== undefined ? (
                  <Badge
                    label={`${Math.round(masjid.distance_meters)}m`}
                    variant="neutral"
                  />
                ) : null
              }
            />
          ))}
        </Card>
      ) : (
        <EmptyState
          title={t("home.no_masjids")}
          description={t("explore.no_results")}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  title: {
    marginBottom: 4,
  },
  subtitle: {
    marginBottom: 8,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  card: {
    marginTop: 8,
  },
  skeletonContainer: {
    gap: 8,
    marginTop: 8,
  },
  skeletonItem: {
    width: "100%",
  },
});

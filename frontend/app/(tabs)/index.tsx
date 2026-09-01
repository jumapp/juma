import { MapLeaflet, MapLeafletRef } from "@/components/maps/MapLeaflet";
import { Badge, Card, EmptyState, IconButton, ListItem, Screen, Skeleton, Text } from "@/components/ui";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useMasjids } from "@/hooks/queries/use-masjids";
import { useUserLocation } from "@/hooks/use-user-location";
import { config } from "@/lib/config";
import { useTheme } from "@/providers/theme-provider";
import { Masjid } from "@/services/api/masjids";
import { useRouter } from "expo-router";
import React, { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { StyleSheet, View } from "react-native";

export default function HomeScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { spacing, colors } = useTheme();
  const mapRef = useRef<MapLeafletRef>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  
  // Get user's location
  const { location: userLocation } = useUserLocation();
  
  // Fetch nearby masjids using default Dehradun coordinates
  const { data: masjids, isLoading, isError, error, refetch } = useMasjids({
    lat: userLocation?.latitude,
    lon: userLocation?.longitude,
    radius: config.defaultRadiusMeters,
  });

  // Update map markers when masjids change
  useEffect(() => {
    if (mapRef.current && masjids && viewMode === 'map') {
      mapRef.current.updateMarkers(masjids);
    }
  }, [masjids, viewMode]);

  const handleMasjidSelect = (masjid: Masjid) => {
    // TODO: Navigate to masjid detail screen
    console.log('Selected masjid:', masjid);
  };

  const handleCreateMasjid = () => {
    router.push('/create-masjid');
  };

  const toggleViewMode = () => {
    setViewMode(prev => prev === 'map' ? 'list' : 'map');
  };

  // Header component
  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerLeft}>
        <Text variant="h3" color="primary">
          {t("home.title")}
        </Text>
      </View>
      <View style={styles.headerRight}>
        <IconButton
          icon={<IconSymbol name="plus.circle.fill" size={24} color={colors.primary} />}
          onPress={handleCreateMasjid}
          accessibilityLabel={t("create_masjid.title")}
        />
        <IconButton
          icon={<IconSymbol 
            name={viewMode === 'map' ? 'list.bullet' : 'map.fill'} 
            size={24} 
            color={colors.primary} 
          />}
          onPress={toggleViewMode}
          accessibilityLabel={viewMode === 'map' ? t("home.list_view") : t("home.map_view")}
        />
      </View>
    </View>
  );

  // Loading state
  if (isLoading) {
    return (
      <Screen 
        scrollable={false}
        header={renderHeader()}
        safeAreaEdges={["top", "bottom"]}
        contentContainerStyle={styles.container}
      >
        {viewMode === 'map' ? (
          <View style={styles.mapContainer}>
            <View style={styles.mapLoading}>
              <Text color="secondary">{t("common.loading")}</Text>
            </View>
          </View>
        ) : (
          <View style={styles.listContainer}>
            <View style={styles.skeletonContainer}>
              <Skeleton height={60} style={styles.skeletonItem} />
              <Skeleton height={60} style={styles.skeletonItem} />
              <Skeleton height={60} style={styles.skeletonItem} />
            </View>
          </View>
        )}
      </Screen>
    );
  }

  // Error state
  if (isError) {
    return (
      <Screen 
        scrollable={false}
        header={renderHeader()}
        safeAreaEdges={["top", "bottom"]}
        contentContainerStyle={styles.container}
      >
        <EmptyState
          title={t("errors.generic")}
          description={error?.message || t("errors.network")}
          actionLabel={t("common.retry")}
          onAction={() => refetch()}
        />
      </Screen>
    );
  }

  return (
    <Screen 
      scrollable={false}
      header={renderHeader()}
      safeAreaEdges={["top", "bottom"]}
      contentContainerStyle={styles.container}
    >
      {viewMode === 'map' ? (
        <View style={styles.mapContainer}>
          <MapLeaflet
            ref={mapRef}
            masjids={masjids ?? []}
            userLocation={userLocation ?? undefined}
            onMarkerPress={handleMasjidSelect}
            centerOnUserLocation={true}
            showCreateButton={true}
            onCreate={handleCreateMasjid}
          />
        </View>
      ) : (
        <View style={styles.listContainer}>
          <Text variant="body" color="secondary" style={styles.subtitle}>
            {t("home.subtitle")}
          </Text>

          <Text variant="h3" color="primary" style={[styles.sectionTitle, { marginTop: spacing.md }]}>
            {t("home.nearby_masjids")}
          </Text>

          {masjids && masjids.length > 0 ? (
            <Card variant="elevated" style={styles.card}>
              {masjids.map((masjid) => (
                <ListItem
                  key={masjid.id}
                  title={masjid.name}
                  subtitle={`${masjid.city ?? ''}, ${masjid.state ?? ''}`}
                  onPress={() => handleMasjidSelect(masjid)}
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
              actionLabel={t("create_masjid.title")}
              onAction={handleCreateMasjid}
            />
          )}
        </View>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
    minHeight: 52,
    borderBottomWidth: StyleSheet.hairlineWidth,
    backgroundColor: '#ffffff',
  },
  headerLeft: {
    flex: 1,
  },
  headerRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  mapContainer: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  mapLoading: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  listContainer: {
    flex: 1,
    padding: 16,
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
  retryButton: {
    padding: 12,
    alignItems: "center",
  },
  createButton: {
    padding: 12,
    alignItems: "center",
  },
});
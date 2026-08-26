import React, { useState } from "react";
import { StyleSheet, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useMasjids } from "@/hooks/queries/use-masjids";
import { Screen, Text, TextInput, Card, ListItem, Badge, Chip, EmptyState } from "@/components/ui";

export default function ExploreScreen() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState<string | null>(null);

  // Fetch all masjids (no radius limit for explore)
  const { data: masjids, isLoading, isError, error } = useMasjids();

  const filteredMasjids = React.useMemo(() => {
    if (!masjids) return [];
    return masjids.filter((m) => {
      const matchesSearch = searchQuery === "" ||
        m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.city?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.address_line1?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCity = !selectedCity || m.city === selectedCity;
      return matchesSearch && matchesCity;
    });
  }, [masjids, searchQuery, selectedCity]);

  // Extract unique cities for filter chips
  const cities = React.useMemo(() => {
    if (!masjids) return [];
    const uniqueCities = new Set(masjids.map((m) => m.city).filter((c): c is string => !!c));
    return Array.from(uniqueCities).sort();
  }, [masjids]);

  if (isLoading) {
    return (
      <Screen scrollable contentContainerStyle={styles.container}>
        <Text variant="h1" color="primary">{t("explore.title")}</Text>
        <TextInput
          label={t("explore.search")}
          placeholder={t("explore.search")}
          value={searchQuery}
          onChangeText={setSearchQuery}
          style={styles.searchInput}
        />
        <View style={styles.chipsRow}>
          <Chip label={t("explore.filter_all")} selected={!selectedCity} onPress={() => setSelectedCity(null)} />
        </View>
        <Card variant="elevated" style={styles.card}>
          <ListItem title="Loading..." />
        </Card>
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
      <Text variant="h1" color="primary">{t("explore.title")}</Text>

      <TextInput
        label={t("explore.search")}
        placeholder={t("explore.search")}
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchInput}
      />

      {cities.length > 0 ? (
        <View style={styles.chipsRow}>
          <Chip label={t("explore.filter_all")} selected={!selectedCity} onPress={() => setSelectedCity(null)} />
          {cities.map((city) => (
            <Chip
              key={city}
              label={city}
              selected={selectedCity === city}
              onPress={() => setSelectedCity((prev) => (city === prev ? null : city))}
            />
          ))}
        </View>
      ) : null}

      {filteredMasjids.length > 0 ? (
        <Card variant="elevated" style={styles.card}>
          {filteredMasjids.map((masjid) => (
            <ListItem
              key={masjid.id}
              title={masjid.name}
              subtitle={`${masjid.city ?? ""}, ${masjid.state ?? ""}`}
              onPress={() => { /* TODO: navigate to masjid detail */ }}
              right={
                masjid.accessible_by_public_transport ? (
                  <Badge label={t("explore.accessible_transport")} variant="success" />
                ) : null
              }
            />
          ))}
        </Card>
      ) : (
        <EmptyState
          title={t("explore.no_results")}
          description={t("home.subtitle")}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  searchInput: {
    marginVertical: 8,
  },
  chipsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  card: {
    marginTop: 8,
  },
});

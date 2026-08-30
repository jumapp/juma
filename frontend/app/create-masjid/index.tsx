import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, TextInput as RNTextInput, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { useUserLocation } from '@/hooks/use-user-location';
import { createMasjid as createMasjidApi } from '@/services/api/masjids';
import { useQueryClient } from '@tanstack/react-query';
import { MapLeaflet, MapLeafletRef } from '@/components/maps/MapLeaflet';
import { useMasjids } from '@/hooks/queries/use-masjids';
import { Header } from '@/components/ui/header';
import { Button } from '@/components/ui/button';
import { Screen } from '@/components/ui/screen';
import { Card } from '@/components/ui/card';
import { Text } from '@/components/ui/text';

type Step = 'location' | 'details';

export default function CreateMasjidScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const mapRef = useRef<MapLeafletRef>(null);
  const queryClient = useQueryClient();
  
  const [step, setStep] = useState<Step>('location');
  const [selectedLocation, setSelectedLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    address_line1: '',
    address_line2: '',
    has_wudu_stations: false,
    has_urinals: false,
    has_toilets: false,
    has_womens_prayer_area: false,
    has_library: false,
    has_parking: false,
    has_street_parking: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { location: userLocation } = useUserLocation();
  const { data: masjids } = useMasjids({ radius: 50000 });

  useEffect(() => {
    if (userLocation && !selectedLocation) {
      setSelectedLocation(userLocation);
    }
  }, [userLocation]);

  const handleLocationSelect = (lat: number, lng: number) => {
    setSelectedLocation({ latitude: lat, longitude: lng });
    if (mapRef.current) {
      mapRef.current.selectLocation(lat, lng);
    }
  };

  const handleContinueToDetails = () => {
    if (selectedLocation) {
      setStep('details');
    }
  };

  const handleBackToMap = () => {
    setStep('location');
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!selectedLocation || !formData.name || !formData.city) {
      return;
    }

    setIsSubmitting(true);
    try {
      await createMasjidApi({
        name: formData.name,
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
        city: formData.city,
        state: formData.state,
        postal_code: formData.postal_code,
        country: formData.country,
        address_line1: formData.address_line1,
        address_line2: formData.address_line2,
        has_wudu_stations: formData.has_wudu_stations,
        has_urinals: formData.has_urinals,
        has_toilets: formData.has_toilets,
        has_womens_prayer_area: formData.has_womens_prayer_area,
        has_library: formData.has_library,
        has_parking: formData.has_parking,
        has_street_parking: formData.has_street_parking,
      });
      queryClient.invalidateQueries({ queryKey: ['masjids'] });
      router.back();
    } catch (error) {
      console.error('Failed to create masjid:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderLocationStep = () => (
    <View style={styles.stepContainer}>
      <View style={styles.mapWrapper}>
        <MapLeaflet
          ref={mapRef}
          masjids={masjids ?? []}
          userLocation={userLocation ?? undefined}
          onLocationSelect={handleLocationSelect}
          centerOnUserLocation={true}
          showCreateButton={false}
        />
      </View>
      
      <View style={styles.locationInfo}>
        <Text variant="body" color="secondary" style={styles.instructionText}>
          {t('create_masjid.tap_to_select')}
        </Text>
        
        {selectedLocation && (
          <View style={styles.selectedCoords}>
            <Text variant="caption" color="secondary">
              {t('create_masjid.selected_location')}:
            </Text>
            <Text variant="body" color="primary" style={styles.coordsText}>
              {selectedLocation.latitude.toFixed(5)}, {selectedLocation.longitude.toFixed(5)}
            </Text>
          </View>
        )}
        
        <Button
          title={t('create_masjid.continue')}
          onPress={handleContinueToDetails}
          disabled={!selectedLocation}
          style={styles.continueButton}
        />
      </View>
    </View>
  );

  const renderDetailsStep = () => (
    <ScrollView style={styles.stepContainer} contentContainerStyle={styles.scrollContent}>
      <View style={styles.formSection}>
        <Text variant="h3" color="primary" style={styles.sectionTitle}>
          {t('create_masjid.masjid_details')}
        </Text>
        
        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.name')} *
          </Text>
          <RNTextInput
            style={styles.input}
            value={formData.name}
            onChangeText={(text) => handleInputChange('name', text)}
            placeholder={t('create_masjid.name_placeholder')}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.city')} *
          </Text>
          <RNTextInput
            style={styles.input}
            value={formData.city}
            onChangeText={(text) => handleInputChange('city', text)}
            placeholder={t('create_masjid.city_placeholder')}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.state')}
          </Text>
          <RNTextInput
            style={styles.input}
            value={formData.state}
            onChangeText={(text) => handleInputChange('state', text)}
            placeholder={t('create_masjid.state_placeholder')}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.postal_code')}
          </Text>
          <RNTextInput
            style={styles.input}
            value={formData.postal_code}
            onChangeText={(text) => handleInputChange('postal_code', text)}
            placeholder={t('create_masjid.postal_code_placeholder')}
            placeholderTextColor="#999"
            keyboardType="numeric"
          />
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.country')}
          </Text>
          <RNTextInput
            style={styles.input}
            value={formData.country}
            onChangeText={(text) => handleInputChange('country', text)}
            placeholder={t('create_masjid.country_placeholder')}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.address')}
          </Text>
          <RNTextInput
            style={[styles.input, styles.textArea]}
            value={formData.address_line1}
            onChangeText={(text) => handleInputChange('address_line1', text)}
            placeholder={t('create_masjid.address_placeholder')}
            placeholderTextColor="#999"
            multiline
            numberOfLines={2}
          />
        </View>

        <Card variant="outlined" style={styles.amenitiesCard}>
          <Text variant="body" color="primary" style={styles.amenitiesTitle}>
            {t('create_masjid.amenities')}
          </Text>
          
          <View style={styles.amenitiesGrid}>
            <Pressable 
              style={[styles.amenityItem, formData.has_wudu_stations && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_wudu_stations', !formData.has_wudu_stations)}
            >
              <Text variant="caption" color={formData.has_wudu_stations ? 'primary' : 'secondary'}>
                {t('create_masjid.wudu_stations')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_toilets && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_toilets', !formData.has_toilets)}
            >
              <Text variant="caption" color={formData.has_toilets ? 'primary' : 'secondary'}>
                {t('create_masjid.toilets')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_parking && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_parking', !formData.has_parking)}
            >
              <Text variant="caption" color={formData.has_parking ? 'primary' : 'secondary'}>
                {t('create_masjid.parking')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_womens_prayer_area && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_womens_prayer_area', !formData.has_womens_prayer_area)}
            >
              <Text variant="caption" color={formData.has_womens_prayer_area ? 'primary' : 'secondary'}>
                {t('create_masjid.womens_area')}
              </Text>
            </Pressable>
          </View>
        </Card>
      </View>

      <View style={styles.buttonRow}>
        <Button
          title={t('common.back')}
          onPress={handleBackToMap}
          variant="outline"
          style={styles.backButton}
        />
        <Button
          title={t('create_masjid.create')}
          onPress={handleSubmit}
          loading={isSubmitting}
          disabled={!formData.name || !formData.city}
          style={styles.submitButton}
        />
      </View>
    </ScrollView>
  );

  return (
    <Screen
      header={
        <Header
          title={t('create_masjid.title')}
          showBack
          onBack={() => router.back()}
          subtitle={step === 'location' ? t('create_masjid.step_1') : t('create_masjid.step_2')}
        />
      }
    >
      {step === 'location' ? renderLocationStep() : renderDetailsStep()}
    </Screen>
  );
}

const styles = StyleSheet.create({
  stepContainer: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  mapWrapper: {
    flex: 1,
    minHeight: 250,
  },
  locationInfo: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  instructionText: {
    textAlign: 'center',
    marginBottom: 12,
  },
  selectedCoords: {
    alignItems: 'center',
    marginBottom: 16,
  },
  coordsText: {
    marginTop: 4,
  },
  continueButton: {
    marginTop: 8,
  },
  formSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 16,
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    color: '#333',
  },
  textArea: {
    minHeight: 60,
    textAlignVertical: 'top',
  },
  amenitiesCard: {
    marginTop: 8,
    padding: 12,
  },
  amenitiesTitle: {
    marginBottom: 12,
  },
  amenitiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  amenityItem: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  amenityItemSelected: {
    backgroundColor: '#e3f2fd',
    borderColor: '#2196f3',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
    marginBottom: 32,
  },
  backButton: {
    flex: 1,
  },
  submitButton: {
    flex: 1,
  },
});
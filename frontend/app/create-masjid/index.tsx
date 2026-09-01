import { MapLeaflet, MapLeafletRef } from '@/components/maps/MapLeaflet';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Header } from '@/components/ui/header';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Screen } from '@/components/ui/screen';
import { Switch } from '@/components/ui/switch';
import { Text } from '@/components/ui/text';
import { TimePicker } from '@/components/ui/time-picker';
import { useMasjids } from '@/hooks/queries/use-masjids';
import { useUserLocation } from '@/hooks/use-user-location';
import { createMasjid as createMasjidApi } from '@/services/api/masjids';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import IndianStatesCities from 'indian-states-cities-list';
import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal, Pressable, ScrollView, StyleSheet, TextInput, View } from 'react-native';

type Step = 'location' | 'details';

interface StateItem {
  label: string;
  value: string;
  name: string;
}

interface CityItem {
  label: string;
  value: string;
}

export default function CreateMasjidScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const mapRef = useRef<MapLeafletRef>(null);
  const queryClient = useQueryClient();
  const { location: userLocation } = useUserLocation();
  const { data: masjids } = useMasjids();

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
    accessible_by_public_transport: false,
    highway_masjid: false,
    on_road_masjid: false,
    accessibility_details: '',
    opens_at: '',
    closes_at: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // State/city picker visibility
  const [isStatePickerVisible, setIsStatePickerVisible] = useState(false);
  const [isCityPickerVisible, setIsCityPickerVisible] = useState(false);

  // Get states and cities from the library
  const states: StateItem[] = IndianStatesCities.STATES_OBJECT || [];
  const citiesForSelectedState: CityItem[] = formData.state
    ? (IndianStatesCities.STATE_WISE_CITIES[formData.state] || [])
    : [];

  // Load saved form data from async storage on mount
  useEffect(() => {
    const loadSavedFormData = async () => {
      try {
        const saved = await AsyncStorage.getItem('jumapp:create_masjid_draft');
        if (saved) {
          const parsed = JSON.parse(saved);
          setFormData(prev => ({ ...prev, ...parsed }));
        }
      } catch (e) {
        console.warn('Failed to load saved form data:', e);
      }
    };
    loadSavedFormData();
  }, []);

  // Save form data to async storage whenever it changes
  useEffect(() => {
    const saveFormData = async () => {
      try {
        await AsyncStorage.setItem('jumapp:create_masjid_draft', JSON.stringify(formData));
      } catch (e) {
        console.warn('Failed to save form data:', e);
      }
    };
    const timeoutId = setTimeout(saveFormData, 500);
    return () => clearTimeout(timeoutId);
  }, [formData]);

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

  const formStateLabel = (stateValue: string): string => {
    const state = states.find(s => s.value === stateValue);
    return state?.label || stateValue;
  };

  // State picker handlers
  const handleStateSelect = (state: StateItem) => {
    setFormData(prev => ({
      ...prev,
      state: state.value,
      city: '', // Reset city when state changes
    }));
    setIsStatePickerVisible(false);
  };

  // City picker handlers
  const handleCitySelect = (city: CityItem) => {
    setFormData(prev => ({
      ...prev,
      city: city.value,
    }));
    setIsCityPickerVisible(false);
  };

  

  const clearSavedDraft = async () => {
    try {
      await AsyncStorage.removeItem('jumapp:create_masjid_draft');
    } catch (e) {
      console.warn('Failed to clear saved draft:', e);
    }
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
        country: 'IN',
        address_line1: formData.address_line1,
        address_line2: formData.address_line2,
        accessible_by_public_transport: formData.accessible_by_public_transport,
        highway_masjid: formData.highway_masjid,
        on_road_masjid: formData.on_road_masjid,
        accessibility_details: formData.accessibility_details,
        opens_at: formData.opens_at || undefined,
        closes_at: formData.closes_at || undefined,
        has_wudu_stations: formData.has_wudu_stations,
        has_urinals: formData.has_urinals,
        has_toilets: formData.has_toilets,
        has_womens_prayer_area: formData.has_womens_prayer_area,
        has_library: formData.has_library,
        has_parking: formData.has_parking,
        has_street_parking: formData.has_street_parking,
      });
      await clearSavedDraft();
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
          <TextInput
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
          <Pressable
            style={[styles.input, styles.statePickerContainer]}
            onPress={() => {
              if (formData.state) {
                setIsCityPickerVisible(true);
              }
            }}
            disabled={!formData.state}
          >
            <Text
              variant="body"
              color={formData.city ? 'primary' : formData.state ? 'secondary' : 'tertiary'}
            >
              {formData.city
                ? citiesForSelectedState.find(c => c.value === formData.city)?.label || formData.city
                : formData.state
                  ? t('create_masjid.city_placeholder')
                  : t('create_masjid.select_state_first')}
            </Text>
            <IconSymbol name="chevron-down" size={16} color="secondary" />
          </Pressable>
        </View>

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.state')}
          </Text>
          <Pressable
            style={[styles.input, styles.statePickerContainer]}
            onPress={() => setIsStatePickerVisible(true)}
          >
            <Text variant="body" color={formData.state ? 'primary' : 'secondary'}>
              {formData.state ? formStateLabel(formData.state) : t('create_masjid.state_placeholder')}
            </Text>
            <IconSymbol name="chevron-down" size={16} color="secondary" />
          </Pressable>
        </View>

        <Modal visible={isStatePickerVisible} onRequestClose={() => setIsStatePickerVisible(false)}>
          <View style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text variant="h3" color="primary">
                {t('create_masjid.select_state')}
              </Text>
              <Pressable onPress={() => setIsStatePickerVisible(false)}>
                <IconSymbol name="close" size={24} color="secondary" />
              </Pressable>
            </View>
            <ScrollView style={styles.modalScroll}>
              {states.map((state) => (
                <Pressable
                  key={state.value}
                  style={[
                    styles.modalItem,
                    formData.state === state.value && styles.modalItemSelected,
                  ]}
                  onPress={() => handleStateSelect(state)}
                >
                  <Text variant="body">{state.label}</Text>
                </Pressable>
              ))}
            </ScrollView>
          </View>
        </Modal>

        {/* City Picker (shown when state is selected) */}
        {formData.state && (
          <Modal visible={isCityPickerVisible} onRequestClose={() => setIsCityPickerVisible(false)}>
            <View style={styles.modalContainer}>
              <View style={styles.modalHeader}>
                <Text variant="h3" color="primary">
                  {t('create_masjid.select_city')}
                </Text>
                <Pressable onPress={() => setIsCityPickerVisible(false)}>
                  <IconSymbol name="close" size={24} color="secondary" />
                </Pressable>
              </View>
              <ScrollView style={styles.modalScroll}>
                {citiesForSelectedState.map((city) => (
                  <Pressable
                    key={city.value}
                    style={[
                      styles.modalItem,
                      formData.city === city.value && styles.modalItemSelected,
                    ]}
                    onPress={() => handleCitySelect(city)}
                  >
                    <Text variant="body">{city.label}</Text>
                  </Pressable>
                ))}
              </ScrollView>
            </View>
          </Modal>
        )}

        <View style={styles.formGroup}>
          <Text variant="caption" color="secondary" style={styles.label}>
            {t('create_masjid.postal_code')}
          </Text>
          <TextInput
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
            {t('create_masjid.address')}
          </Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.address_line1}
            onChangeText={(text) => handleInputChange('address_line1', text)}
            placeholder={t('create_masjid.address_placeholder')}
            placeholderTextColor="#999"
            multiline
            numberOfLines={2}
          />
        </View>

        {/* Accessibility Section */}
        <View style={styles.formSection}>
          <Text variant="body" color="primary" style={styles.sectionTitle}>
            {t('create_masjid.accessibility')}
          </Text>

          <View style={styles.formGroup}>
            <Switch
              checked={formData.accessible_by_public_transport}
              onValueChange={(val) => handleInputChange('accessible_by_public_transport', val)}
              label={t('create_masjid.accessible_by_public_transport')}
            />
          </View>

          <View style={styles.formGroup}>
            <Switch
              checked={formData.highway_masjid}
              onValueChange={(val) => handleInputChange('highway_masjid', val)}
              label={t('create_masjid.highway_masjid')}
            />
          </View>

          <View style={styles.formGroup}>
            <Switch
              checked={formData.on_road_masjid}
              onValueChange={(val) => handleInputChange('on_road_masjid', val)}
              label={t('create_masjid.on_road_masjid')}
            />
          </View>

          <View style={styles.formGroup}>
            <Text variant="caption" color="secondary" style={styles.label}>
              {t('create_masjid.accessibility_details')}
            </Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={formData.accessibility_details}
              onChangeText={(text) => handleInputChange('accessibility_details', text)}
              placeholder={t('create_masjid.accessibility_details_placeholder')}
              placeholderTextColor="#999"
              multiline
              numberOfLines={2}
            />
          </View>
        </View>

        {/* Opening Hours Section */}
        <View style={styles.formSection}>
          <Text variant="body" color="primary" style={styles.sectionTitle}>
            {t('create_masjid.opening_hours')}
          </Text>

          <View style={styles.formGroup}>
            <Text variant="caption" color="secondary" style={styles.label}>
              {t('create_masjid.open_time')}
            </Text>
            <TimePicker
              value={formData.opens_at}
              onChange={(time) => handleInputChange('opens_at', time)}
              minuteInterval={5}
            />
          </View>

          <View style={styles.formGroup}>
            <Text variant="caption" color="secondary" style={styles.label}>
              {t('create_masjid.close_time')}
            </Text>
            <TimePicker
              value={formData.closes_at}
              onChange={(time) => handleInputChange('closes_at', time)}
              minuteInterval={5}
            />
          </View>
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
              <Text variant="caption" color={formData.has_wudu_stations ? 'primary' : 'text'}>
                {t('create_masjid.wudu_stations')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_toilets && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_toilets', !formData.has_toilets)}
            >
              <Text variant="caption" color={formData.has_toilets ? 'primary' : 'text'}>
                {t('create_masjid.toilets')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_parking && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_parking', !formData.has_parking)}
            >
              <Text variant="caption" color={formData.has_parking ? 'primary' : 'text'}>
                {t('create_masjid.parking')}
              </Text>
            </Pressable>
            
            <Pressable 
              style={[styles.amenityItem, formData.has_womens_prayer_area && styles.amenityItemSelected]}
              onPress={() => handleInputChange('has_womens_prayer_area', !formData.has_womens_prayer_area)}
            >
              <Text variant="caption" color={formData.has_womens_prayer_area ? 'primary' : 'text'}>
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
  statePickerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timePickerInput: {
    width: '100%',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    fontSize: 16,
    backgroundColor: '#fff',
    color: '#333',
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
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    padding: 16,
  },
  modalHeader: {
    marginBottom: 24,
    alignItems: 'center',
  },
  modalTitle: {
    marginBottom: 12,
    textAlign: 'center',
    fontSize: 18,
  },
  modalItem: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  modalItemSelected: {
    backgroundColor: '#e3f2fd',
    borderWidth: 1,
    borderColor: '#2196f3',
  },
  modalScroll: {
    maxHeight: 300,
  },
});
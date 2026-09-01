import { useState, useEffect } from 'react';
import { Platform } from 'react-native';
import * as Location from 'expo-location';

export interface UserLocation {
  latitude: number;
  longitude: number;
}

export function useUserLocation() {
  const [location, setLocation] = useState<UserLocation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        if (Platform.OS === 'web') {
          // Use web Geolocation API
          if (typeof navigator !== 'undefined' && navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              (position) => {
                setLocation({
                  latitude: position.coords.latitude,
                  longitude: position.coords.longitude,
                });
                setLoading(false);
              },
              (err) => {
                setError(err.message);
                setLoading(false);
              }
            );
          } else {
            setError('Geolocation not available');
            setLoading(false);
          }
        } else {
          // Use expo-location for iOS/Android
          const { status } = await Location.requestForegroundPermissionsAsync();
          if (status !== 'granted') {
            setError('Permission to access location was denied');
            setLoading(false);
            return;
          }

          const currentLocation = await Location.getCurrentPositionAsync({});
          setLocation({
            latitude: currentLocation.coords.latitude,
            longitude: currentLocation.coords.longitude,
          });
          setLoading(false);
        }
      } catch (err: any) {
        setError(err?.message || 'Failed to get location');
        setLoading(false);
      }
    })();
  }, []);

  return { location, error, loading };
}
import { Masjid } from '@/services/api/masjids';
import React, { forwardRef, useCallback, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { Platform, Pressable, StyleSheet, Text as RNText, View } from 'react-native';
import type { WebViewMessageEvent } from 'react-native-webview';

// Import Leaflet CSS for web platform only
if (Platform.OS === 'web') {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  require('leaflet/dist/leaflet.css');
}

// react-native-webview ships no web implementation — executing the module on
// web crashes the bundle. The type import above is erased at compile time, and
// WebView is loaded lazily below only on native platforms.
let WebView: any = null;
if (Platform.OS !== 'web') {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const WebViewModule = require('react-native-webview');
  WebView = WebViewModule.WebView;
}

export interface MapLeafletRef {
  updateMarkers: (masjids: Masjid[]) => void;
  selectLocation: (lat: number, lng: number) => void;
  centerOnLocation: (lat: number, lng: number) => void;
}

export interface MapLeafletProps {
  masjids: Masjid[];
  userLocation?: { latitude: number; longitude: number };
  onLocationSelect?: (lat: number, lng: number) => void;
  onMarkerPress?: (masjid: Masjid) => void;
  centerOnUserLocation?: boolean;
  showCreateButton?: boolean;
  onCreate?: () => void;
  initialCenter?: { latitude: number; longitude: number };
}

const DEFAULT_CENTER = { latitude: 30.3165, longitude: 78.0322 }; // Dehradun

/** @component */
const MapLeafletImpl = forwardRef<MapLeafletRef, MapLeafletProps>(
  (
    {
      masjids = [],
      userLocation,
      onLocationSelect,
      onMarkerPress,
      centerOnUserLocation = true,
      showCreateButton = false,
      onCreate,
      initialCenter = DEFAULT_CENTER,
    },
    ref,
  ) => {
  useImperativeHandle(ref, () => ({
    updateMarkers: (newMasjids: Masjid[]) => {
      if (Platform.OS === 'web') {
        window.postMessage(
          JSON.stringify({ type: 'UPDATE_MARKERS', masjids: newMasjids }),
          '*'
        );
      }
    },
    selectLocation: (lat: number, lng: number) => {
      if (Platform.OS === 'web') {
        window.postMessage(
          JSON.stringify({ type: 'SELECT_LOCATION', latitude: lat, longitude: lng }),
          '*'
        );
      }
    },
    centerOnLocation: (lat: number, lng: number) => {
      if (Platform.OS === 'web') {
        window.postMessage(
          JSON.stringify({ type: 'CENTER_ON_LOCATION', latitude: lat, longitude: lng }),
          '*'
        );
      }
    },
  }), []);

  // Web implementation
  if (Platform.OS === 'web') {
    return <WebMap
      masjids={masjids}
      userLocation={userLocation}
      onLocationSelect={onLocationSelect}
      onMarkerPress={onMarkerPress}
      centerOnUserLocation={centerOnUserLocation}
      showCreateButton={showCreateButton}
      onCreate={onCreate}
      initialCenter={initialCenter}
    />;
  }

  // Mobile implementation
  return <NativeMap
    masjids={masjids}
    userLocation={userLocation}
    onLocationSelect={onLocationSelect}
    onMarkerPress={onMarkerPress}
    centerOnUserLocation={centerOnUserLocation}
    showCreateButton={showCreateButton}
    onCreate={onCreate}
    initialCenter={initialCenter}
  />;
});

MapLeafletImpl.displayName = 'MapLeaflet';

// Web Map component
const WebMap: React.FC<MapLeafletProps> = ({
  masjids,
  userLocation,
  onLocationSelect,
  onMarkerPress,
  centerOnUserLocation = true,
  showCreateButton = false,
  onCreate,
  initialCenter = DEFAULT_CENTER,
}) => {
  const mapInstanceRef = useRef<any>(null);
  const containerRef = useRef<View>(null);
  const mapDivRef = useRef<HTMLDivElement | null>(null);
  const masjidMarkersRef = useRef<Record<string, any>>({});
  const userMarkerRef = useRef<any>(null);
  const selectionMarkerRef = useRef<any>(null);
  const [mapReady, setMapReady] = useState(false);

  // Latest-value refs so effects/listeners never close over stale props
  const userLocationRef = useRef(userLocation);
  const onLocationSelectRef = useRef(onLocationSelect);
  const onMarkerPressRef = useRef(onMarkerPress);
  const centerOnUserLocationRef = useRef(centerOnUserLocation);
  const initialCenterRef = useRef(initialCenter);

  useEffect(() => {
    userLocationRef.current = userLocation;
    onLocationSelectRef.current = onLocationSelect;
    onMarkerPressRef.current = onMarkerPress;
    centerOnUserLocationRef.current = centerOnUserLocation;
    initialCenterRef.current = initialCenter;
  }, [userLocation, onLocationSelect, onMarkerPress, centerOnUserLocation, initialCenter]);

  // Replaces all masjid markers with fresh copies for the given list.
  const syncMarkers = useCallback((masjidsArray: Masjid[]) => {
    if (typeof window === 'undefined' || Platform.OS !== 'web') return;
    const map = mapInstanceRef.current;
    if (!map) return;

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const L = require('leaflet');

    Object.values(masjidMarkersRef.current).forEach((marker: any) => {
      map.removeLayer(marker);
    });
    masjidMarkersRef.current = {};

    (masjidsArray || []).forEach((masjid) => {
      const marker = L.marker([masjid.latitude, masjid.longitude])
        .addTo(map)
        .bindPopup(
          `<div style="padding: 8px; max-width: 200px;">
            <strong style="font-size: 13px; color: #2c3e50;">${masjid.name}</strong><br>
            <span style="font-size: 11px; color: #7f8c8d;">${masjid.city || ''}${masjid.state ? ', ' + masjid.state : ''}</span>
          </div>`
        )
        .on('click', () => {
          onMarkerPressRef.current?.(masjid);
        });
      masjidMarkersRef.current[masjid.id] = marker;
    });
  }, []);

  // Places a "selection" marker at the given coordinates and zooms in.
  const selectLocation = useCallback((lat: number, lng: number) => {
    if (typeof window === 'undefined' || Platform.OS !== 'web') return;
    const map = mapInstanceRef.current;
    if (!map) return;

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const L = require('leaflet');

    if (selectionMarkerRef.current) {
      map.removeLayer(selectionMarkerRef.current);
      selectionMarkerRef.current = null;
    }

    selectionMarkerRef.current = L.marker([lat, lng], {
      icon: L.divIcon({
        className: 'custom-marker',
        html: '<div style="background-color: #3498db; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      }),
    }).addTo(map);

    map.setView([lat, lng], 16);
  }, []);

  // 1) Map initialization — runs once on mount, cleans up on unmount.
  //    Deliberately dep-free so the map is never destroyed/recreated on
  //    re-renders caused by unstable callback identities.
  useEffect(() => {
    if (typeof window === 'undefined' || Platform.OS !== 'web') return;

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const L = require('leaflet');

    const mapElement = mapDivRef.current;
    if (!mapElement) return;

    // Defensive: strip stale Leaflet init marker. StrictMode / fast-refresh
    // remount races, or a leftover node from another instance, can leave
    // this set before our cleanup runs — causes "already initialized".
    if ((mapElement as any)._leaflet_id) {
      delete (mapElement as any)._leaflet_id;
    }

    const center = centerOnUserLocationRef.current && userLocationRef.current
      ? [userLocationRef.current.latitude, userLocationRef.current.longitude]
      : [initialCenterRef.current.latitude, initialCenterRef.current.longitude];

    const map = L.map(mapElement, {
      center: center as [number, number],
      zoom: 13,
      zoomControl: true,
      attributionControl: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      dragging: true,
      keyboard: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // User location marker (position kept in sync by the centering effect)
    if (userLocationRef.current) {
      userMarkerRef.current = L.marker([
        userLocationRef.current.latitude,
        userLocationRef.current.longitude,
      ])
        .addTo(map)
        .bindPopup('Your Location');
    }

    // Handle map clicks
    if (onLocationSelectRef.current) {
      map.on('click', (e: any) => {
        onLocationSelectRef.current?.(e.latlng.lat, e.latlng.lng);
      });
    }

    mapInstanceRef.current = map;
    setMapReady(true);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
      masjidMarkersRef.current = {};
      userMarkerRef.current = null;
      selectionMarkerRef.current = null;
      setMapReady(false);
    };
  }, []);

  // 2) Sync masjid markers when the list changes (or once the map is ready)
  useEffect(() => {
    if (mapReady) {
      syncMarkers(masjids);
    }
  }, [masjids, mapReady, syncMarkers]);

  // 3) Recenter (and keep the user marker updated) when the location changes
  useEffect(() => {
    if (typeof window === 'undefined' || Platform.OS !== 'web') return;
    if (!centerOnUserLocation || !userLocation) return;

    const map = mapInstanceRef.current;
    if (!map) return;

    if (userMarkerRef.current) {
      userMarkerRef.current.setLatLng([userLocation.latitude, userLocation.longitude]);
    }
    map.setView([userLocation.latitude, userLocation.longitude], 13);
  }, [userLocation, centerOnUserLocation]);

  // 4) Imperative API bridge — handles window messages posted by the ref
  //    methods in MapLeafletImpl (updateMarkers / selectLocation / centerOnLocation)
  useEffect(() => {
    if (typeof window === 'undefined' || Platform.OS !== 'web') return;

    const handleMessage = (event: MessageEvent) => {
      if (event.source !== window || typeof event.data !== 'string') return;

      try {
        const message = JSON.parse(event.data);
        if (!message || typeof message.type !== 'string') return;

        switch (message.type) {
          case 'UPDATE_MARKERS':
            syncMarkers(message.masjids || []);
            break;
          case 'SELECT_LOCATION':
            selectLocation(message.latitude, message.longitude);
            break;
          case 'CENTER_ON_LOCATION':
            if (mapInstanceRef.current) {
              mapInstanceRef.current.setView([message.latitude, message.longitude], 15);
            }
            break;
        }
      } catch (e) {
        console.error('MapLeaflet message error:', e);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [syncMarkers, selectLocation]);

  return (
    <View style={styles.container} ref={containerRef}>
      <div ref={mapDivRef} style={{ width: '100%', height: '100%' }} />
      
      {showCreateButton && onCreate && (
        <View style={styles.fabButton} pointerEvents="box-none">
          <Pressable onPress={onCreate} style={styles.fabContent}>
            <RNText style={styles.fabText}>+</RNText>
          </Pressable>
        </View>
      )}
    </View>
  );
};

// Native Map component using react-native-webview
const NativeMap: React.FC<MapLeafletProps> = ({
  masjids,
  userLocation,
  onLocationSelect,
  onMarkerPress,
  centerOnUserLocation = true,
  showCreateButton = false,
  onCreate,
  initialCenter = DEFAULT_CENTER,
}) => {
  const webViewRef = useRef<any>(null);

  const generateMapHtml = useCallback(() => {
    const centerLat = (centerOnUserLocation && userLocation) 
      ? userLocation.latitude 
      : initialCenter.latitude;
    const centerLng = (centerOnUserLocation && userLocation)
      ? userLocation.longitude
      : initialCenter.longitude;

    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      touch-action: manipulation;
      -webkit-tap-highlight-color: transparent;
    }
    #map {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    .leaflet-container {
      background-color: #f8f9fa;
      font-size: 14px;
    }
    .leaflet-popup-content-wrapper {
      border-radius: 8px;
      padding: 8px;
    }
    .leaflet-popup-content {
      margin: 8px;
    }
    .leaflet-marker-icon,
    .leaflet-marker-shadow {
      image-rendering: optimizeSpeed;
    }
    .leaflet-control-zoom {
      display: none !important;
    }
  </style>
</head>
<body>
  <div id="web-map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    let map;
    const masjidMarkers = {};

    function initializeMap() {
      const initialLat = ${centerLat};
      const initialLng = ${centerLng};
      
      map = L.map('web-map', {
        center: [initialLat, initialLng],
        zoom: 13,
        preferCanvas: true,
        zoomControl: false,
        attributionControl: false,
        boxZoom: true,
        doubleClickZoom: true,
        dragging: true,
        keyboard: true,
        tap: true,
        tapTolerance: 12
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      updateMarkers(${JSON.stringify(masjids || [])});

      // Add user location marker if provided
      ${userLocation ? `
        L.marker([${userLocation.latitude}, ${userLocation.longitude}])
          .addTo(map)
          .bindPopup('Your Location')
          .openPopup();
        map.setView([${userLocation.latitude}, ${userLocation.longitude}], 13);
      ` : ''}

      map.on('click', function(e) {
        if (window.ReactNativeWebView) {
          window.ReactNativeWebView.postMessage(JSON.stringify({
            type: 'MAP_CLICK',
            latitude: e.latlng.lat,
            longitude: e.latlng.lng
          }));
        }
      });
    }

    function updateMarkers(masjidsArray) {
      Object.values(masjidMarkers).forEach(function(marker) {
        if (marker) {
          map.removeLayer(marker);
        }
      });
      
      masjidsArray.forEach(function(masjid) {
        const marker = L.marker([masjid.latitude, masjid.longitude])
          .addTo(map)
          .bindPopup(
            '<div style="padding: 8px; max-width: 200px; font-family: system-ui, sans-serif;">' +
            '<strong style="font-size: 13px; color: #2c3e50;">' + (masjid.name || 'Unknown') + '</strong><br>' +
            '<span style="font-size: 11px; color: #7f8c8d;">' +
            (masjid.city || '') + (masjid.state ? ', ' + masjid.state : '') +
            '</span>' +
            '</div>'
          )
          .on('click', function(e) {
            if (window.ReactNativeWebView) {
              window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'MARKER_CLICK',
                masjidId: masjid.id
              }));
            }
          });
          
        masjidMarkers[masjid.id] = marker;
      });
    }

    function selectLocation(lat, lng) {
      if (map) {
        if (map.selectionMarker) {
          map.removeLayer(map.selectionMarker);
        }
        
        map.selectionMarker = L.marker([lat, lng], {
          icon: L.divIcon({
            className: 'custom-marker',
            html: '<div style="background-color: #3498db; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
          })
        }).addTo(map);
        
        map.setView([lat, lng], 16);
      }
    }

    function centerOnLocation(lat, lng) {
      if (map) {
        map.setView([lat, lng], 15);
      }
    }

    window.addEventListener('message', function(event) {
      try {
        const message = JSON.parse(event.data);
        switch (message.type) {
          case 'UPDATE_MARKERS':
            if (map) updateMarkers(message.masjids || []);
            break;
          case 'SELECT_LOCATION':
            if (map) selectLocation(message.latitude, message.longitude);
            break;
          case 'CENTER_ON_LOCATION':
            if (map) centerOnLocation(message.latitude, message.longitude);
            break;
        }
      } catch (e) {
        console.error('Map WebView message error:', e);
      }
    });

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initializeMap);
    } else {
      initializeMap();
    }
  </script>
</body>
</html>`;
  }, [masjids, userLocation, centerOnUserLocation, initialCenter]);

  const handleWebViewMessage = (event: WebViewMessageEvent) => {
    try {
      const message = JSON.parse(event.nativeEvent.data);
      switch (message.type) {
        case 'MARKER_CLICK':
          const masjid = masjids.find((m) => m.id === message.masjidId);
          if (masjid) onMarkerPress?.(masjid);
          break;
        case 'MAP_CLICK':
          onLocationSelect?.(message.latitude, message.longitude);
          break;
      }
    } catch (e) {
      console.error('Error processing map message:', e);
    }
  };

  return (
    <View style={styles.container}>
      <WebView
        ref={webViewRef}
        source={{ html: generateMapHtml() }}
        javaScriptEnabled={true}
        domStorage={true}
        allowUniversalAccessFromFileURLs={true}
        mixedContentMode="compatibility"
        onMessage={handleWebViewMessage}
        onError={(error: unknown) => {
          console.error('WebView error:', error);
        }}
      />
      
      {showCreateButton && onCreate && (
        <View style={styles.fabButton} pointerEvents="box-none">
          <Pressable onPress={onCreate} style={styles.fabContent}>
            <RNText style={styles.fabText}>+</RNText>
          </Pressable>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  fabButton: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    zIndex: 1000,
  },
  fabContent: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#3498db',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  fabText: {
    color: '#ffffff',
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 28,
  },
});

export const MapLeaflet = MapLeafletImpl;
export default MapLeafletImpl;
import { useEffect, useState } from 'react';
import { Platform } from 'react-native';

type NetworkStatus = {
  isOnline: boolean;
  isOffline: boolean;
};

/**
 * Cross-platform hook to detect online/offline status.
 * - Web: uses navigator.onLine + online/offline events
 * - iOS/Android: uses @react-native-community/netinfo (if available) or defaults to true
 */
export function useNetworkStatus(): NetworkStatus {
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    if (Platform.OS === 'web') {
      if (typeof navigator !== 'undefined') {
        setIsOnline(navigator.onLine);
      }

      const handleOnline = () => setIsOnline(true);
      const handleOffline = () => setIsOnline(false);

      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      unsubscribe = () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    } else {
      // Native platforms: use @react-native-community/netinfo
      try {
        const NetInfo = require('@react-native-community/netinfo').default;
        if (NetInfo && typeof NetInfo.addEventListener === 'function') {
          unsubscribe = NetInfo.addEventListener((state: { isConnected: boolean; isInternetReachable: boolean | null }) => {
            setIsOnline(state.isConnected && state.isInternetReachable !== false);
          });
        }
      } catch {
        // NetInfo not available — assume online
        setIsOnline(true);
      }
    }

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []);

  return {
    isOnline,
    isOffline: !isOnline,
  };
}
import { useCallback } from 'react';
import { Platform } from 'react-native';

/**
 * Cross-platform offline data cache.
 * - Web: uses CacheStorage API (via service worker)
 * - iOS/Android: uses @react-native-async-storage/async-storage
 */
const memoryCache = new Map<string, { data: unknown; timestamp: number }>();

const CACHE_PREFIX = 'jumapp-cache:';

function isWeb(): boolean {
  return Platform.OS === 'web' && typeof caches !== 'undefined';
}

async function getWebCache(): Promise<Cache | null> {
  try {
    return await caches.open('jumapp-api-cache');
  } catch {
    return null;
  }
}

async function getAsyncStorage(): Promise<typeof import('@react-native-async-storage/async-storage').default | null> {
  if (Platform.OS === 'web') {
    return null;
  }
  try {
    const AsyncStorage = require('@react-native-async-storage/async-storage').default;
    return AsyncStorage || null;
  } catch {
    return null;
  }
}

/**
 * Cache data with a key. Works on web (CacheStorage), native (AsyncStorage), and memory.
 */
export function useOfflineCache() {
  const setCache = useCallback(async (key: string, data: unknown): Promise<void> => {
    const cacheKey = `${CACHE_PREFIX}${key}`;
    const entry = JSON.stringify({ data, timestamp: Date.now() });

    // Memory cache (fastest)
    memoryCache.set(cacheKey, { data, timestamp: Date.now() });

    // Web: CacheStorage
    if (isWeb()) {
      const cache = await getWebCache();
      if (cache) {
        const response = new Response(entry, {
          headers: { 'Content-Type': 'application/json' },
        });
        await cache.put(cacheKey, response);
      }
    }

    // Native: AsyncStorage
    const AsyncStorage = await getAsyncStorage();
    if (AsyncStorage) {
      try {
        await AsyncStorage.setItem(cacheKey, entry);
      } catch {
        // Ignore storage errors
      }
    }
  }, []);

  const getCache = useCallback(async <T>(key: string): Promise<T | null> => {
    const cacheKey = `${CACHE_PREFIX}${key}`;

    // Check memory first (fastest)
    const memoryEntry = memoryCache.get(cacheKey);
    if (memoryEntry) {
      return memoryEntry.data as T;
    }

    // Check web CacheStorage
    if (isWeb()) {
      const cache = await getWebCache();
      if (cache) {
        const cachedResponse = await cache.match(cacheKey);
        if (cachedResponse) {
          try {
            const json = await cachedResponse.json();
            if (json && json.data !== undefined) {
              memoryCache.set(cacheKey, { data: json.data, timestamp: json.timestamp ?? Date.now() });
              return json.data as T;
            }
          } catch {
            // Invalid cache entry, ignore
          }
        }
      }
    }

    // Check native AsyncStorage
    const AsyncStorage = await getAsyncStorage();
    if (AsyncStorage) {
      try {
        const stored = await AsyncStorage.getItem(cacheKey);
        if (stored) {
          const json = JSON.parse(stored);
          if (json && json.data !== undefined) {
            memoryCache.set(cacheKey, { data: json.data, timestamp: json.timestamp ?? Date.now() });
            return json.data as T;
          }
        }
      } catch {
        // Invalid cache entry, ignore
      }
    }

    return null;
  }, []);

  const clearCache = useCallback(async (key?: string): Promise<void> => {
    if (key) {
      const cacheKey = `${CACHE_PREFIX}${key}`;
      memoryCache.delete(cacheKey);
      if (isWeb()) {
        const cache = await getWebCache();
        if (cache) {
          await cache.delete(cacheKey);
        }
      }
      const AsyncStorage = await getAsyncStorage();
      if (AsyncStorage) {
        try {
          await AsyncStorage.removeItem(cacheKey);
        } catch {
          // Ignore
        }
      }
    } else {
      memoryCache.clear();
      if (isWeb()) {
        const cache = await getWebCache();
        if (cache) {
          const keys = await cache.keys();
          await Promise.all(keys.map((request) => cache.delete(request)));
        }
      }
      const AsyncStorage = await getAsyncStorage();
      if (AsyncStorage) {
        try {
          const allKeys = await AsyncStorage.getAllKeys();
          const cacheKeys = allKeys.filter((k) => k.startsWith(CACHE_PREFIX));
          if (cacheKeys.length > 0) {
            await AsyncStorage.multiRemove(cacheKeys);
          }
        } catch {
          // Ignore
        }
      }
    }
  }, []);

  return { setCache, getCache, clearCache };
}
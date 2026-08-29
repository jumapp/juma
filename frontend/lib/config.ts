/**
 * Application Configuration
 *
 * Reads configuration from EXPO_PUBLIC_* environment variables with safe defaults.
 * Selects appropriate API URL based on platform:
 * - Web: Uses EXPO_PUBLIC_API_URL (localhost for development)
 * - Mobile: Uses EXPO_PUBLIC_API_URL_MOBILE (ngrok URL for external access)
 */

import { Platform } from 'react-native';

export interface AppConfig {
  apiUrl: string;
  apiPrefix: string;
  devSuperAdminToken: string;
  defaultRadiusMeters: number;
  requestTimeoutMs: number;
  syncBatchSize: number;
  syncMaxRetries: number;
  defaultCoordinates: {
    latitude: number;
    longitude: number;
    name: string;
  };
}

export const config: AppConfig = {
  apiUrl: Platform.OS === 'web'
    ? process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000"
    : process.env.EXPO_PUBLIC_API_URL_MOBILE || "http://localhost:8000",
  apiPrefix: "/api/v1",
  devSuperAdminToken: process.env.EXPO_PUBLIC_DEV_SUPER_ADMIN_TOKEN || "dev-super-admin-token",
  defaultRadiusMeters: 2000,
  requestTimeoutMs: 10000,
  syncBatchSize: 25,
  syncMaxRetries: 5,
  defaultCoordinates: {
    latitude: 30.3165,
    longitude: 78.0322,
    name: "Dehradun",
  },
};

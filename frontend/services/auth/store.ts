import AsyncStorage from "@react-native-async-storage/async-storage";
import { Session, UserRole } from "./types";

const SESSION_STORAGE_KEY = "jumapp:session";

export const DEFAULT_DEV_SESSION: Session = {
  id: "00000000-0000-0000-0000-000000000001",
  name: "Super Admin (Dev)",
  email: "superadmin@doonjuma.org",
  role: "super_admin",
  accessLevel: "admin",
};

let currentMemorySession: Session | null = DEFAULT_DEV_SESSION;

export function getCurrentSession(): Session | null {
  return currentMemorySession;
}

export function setCurrentMemorySession(session: Session | null): void {
  currentMemorySession = session;
}

export async function loadPersistedSession(): Promise<Session> {
  try {
    const raw = await AsyncStorage.getItem(SESSION_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      currentMemorySession = parsed;
      return parsed;
    }
  } catch (e) {
    console.warn("Failed to load session from storage:", e);
  }

  currentMemorySession = DEFAULT_DEV_SESSION;
  return DEFAULT_DEV_SESSION;
}

export async function savePersistedSession(session: Session | null): Promise<void> {
  try {
    currentMemorySession = session;
    if (session) {
      await AsyncStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
    } else {
      await AsyncStorage.removeItem(SESSION_STORAGE_KEY);
    }
  } catch (e) {
    console.error("Failed to save session to storage:", e);
  }
}

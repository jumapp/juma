import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import {
  Session,
  UserRole,
  DEV_ROLE_OPTIONS,
} from "@/services/auth/types";
import {
  loadPersistedSession,
  savePersistedSession,
  DEFAULT_DEV_SESSION,
} from "@/services/auth/store";
import { can as checkPermission } from "@/services/auth/permissions";

export interface AuthContextValue {
  session: Session | null;
  role: UserRole;
  masjidId?: string;
  isSuperAdmin: boolean;
  isMasjidEditor: boolean;
  isSalatEditor: boolean;
  isViewer: boolean;
  can: (permission: string, targetMasjidId?: string) => boolean;
  switchRole: (role: UserRole, masjidId?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(DEFAULT_DEV_SESSION);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    loadPersistedSession().then((loaded) => {
      setSession(loaded);
      setIsLoaded(true);
    });
  }, []);

  const switchRole = useCallback(
    async (newRole: UserRole, targetMasjidId?: string) => {
      const option = DEV_ROLE_OPTIONS.find((r) => r.role === newRole);
      const updated: Session = {
        id: session?.id || "00000000-0000-0000-0000-000000000001",
        name: `${option?.label || newRole} (Dev)`,
        email: `${newRole}@doonjuma.org`,
        role: newRole,
        masjidId: targetMasjidId,
        accessLevel: newRole === "super_admin" ? "admin" : "editor",
      };

      setSession(updated);
      await savePersistedSession(updated);
    },
    [session]
  );

  const logout = useCallback(async () => {
    // In dev mode, logout sets role to public viewer
    await switchRole("viewer");
  }, [switchRole]);

  const can = useCallback(
    (permission: string, targetMasjidId?: string) => {
      return checkPermission(session, permission, targetMasjidId);
    },
    [session]
  );

  const role: UserRole = session?.role || "viewer";

  const value: AuthContextValue = {
    session,
    role,
    masjidId: session?.masjidId,
    isSuperAdmin: role === "super_admin",
    isMasjidEditor: role === "masjid_editor",
    isSalatEditor: role === "salat_editor",
    isViewer: role === "viewer",
    can,
    switchRole,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      session: DEFAULT_DEV_SESSION,
      role: "super_admin",
      isSuperAdmin: true,
      isMasjidEditor: false,
      isSalatEditor: false,
      isViewer: false,
      can: () => true,
      switchRole: async () => {},
      logout: async () => {},
    };
  }
  return context;
}

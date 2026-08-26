export type UserRole =
  | "super_admin"
  | "masjid_editor"
  | "salat_editor"
  | "viewer";

export interface Session {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  masjidId?: string;
  accessLevel: "admin" | "editor" | "viewer" | "general";
}

export interface DevUserRoleOption {
  role: UserRole;
  label: string;
  description: string;
  requiresMasjidScope: boolean;
}

export const DEV_ROLE_OPTIONS: DevUserRoleOption[] = [
  {
    role: "super_admin",
    label: "Super Admin",
    description: "Full read/write access to all resources and sync endpoints",
    requiresMasjidScope: false,
  },
  {
    role: "masjid_editor",
    label: "Masjid Editor",
    description: "Manage own masjid, timings, programs, people, and photos",
    requiresMasjidScope: true,
  },
  {
    role: "salat_editor",
    label: "Salat Editor",
    description: "Update salat schedules for assigned masjid",
    requiresMasjidScope: true,
  },
  {
    role: "viewer",
    label: "Viewer / Public",
    description: "Read-only access to all public masjid and timing data",
    requiresMasjidScope: false,
  },
];

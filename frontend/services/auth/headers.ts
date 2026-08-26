import { config } from "@/lib/config";
import { Session } from "./types";

export function getAuthHeaders(session: Session | null): Record<string, string> {
  if (!session) {
    // Default fallback in dev mode: super admin token
    return {
      "X-Super-Admin-Token": config.devSuperAdminToken,
    };
  }

  const { role, masjidId } = session;

  switch (role) {
    case "super_admin":
      return {
        "X-Super-Admin-Token": config.devSuperAdminToken,
      };

    case "masjid_editor":
      return {
        "X-Masjid-Editor-Token": masjidId || "unscoped-masjid",
      };

    case "salat_editor":
      return {
        "X-Salat-Editor-Token": masjidId || "unscoped-masjid",
        "X-Dev-User-Masjid-Id": masjidId || "unscoped-masjid",
      };

    case "viewer":
    default:
      return {
        "X-Viewer-Token": "viewer-token",
      };
  }
}

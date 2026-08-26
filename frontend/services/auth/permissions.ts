import { Session } from "./types";

export function can(
  session: Session | null,
  permission: string,
  targetMasjidId?: string
): boolean {
  if (!session) {
    // Unauthenticated public user behaves like Viewer
    return permission.endsWith(":read");
  }

  const { role, masjidId } = session;

  // Super Admin can do everything everywhere
  if (role === "super_admin") {
    return true;
  }

  // Read permissions are public across all roles
  if (permission.endsWith(":read")) {
    // Photos & Audit & Sync read exceptions
    if (permission === "audit:read") return false;
    if (permission === "sync:read") return false;
    return true;
  }

  // Masjid Editor scoped write permissions
  if (role === "masjid_editor") {
    if (!masjidId) return false;
    const isTargetMasjid = !targetMasjidId || targetMasjidId === masjidId;

    switch (permission) {
      case "masjid:create":
      case "masjid:update":
        return isTargetMasjid;
      case "masjid:delete":
        return false;

      case "salat:create":
      case "salat:update":
        return isTargetMasjid;
      case "salat:delete":
        return false;

      case "program:create":
      case "program:update":
      case "program:delete":
        return isTargetMasjid;

      case "person:create":
      case "person:update":
        return isTargetMasjid;
      case "person:delete":
        return false;

      case "photo:create":
      case "photo:delete":
        return isTargetMasjid;

      case "admin:approve":
        return isTargetMasjid;

      case "sync:write":
      default:
        return false;
    }
  }

  // Salat Editor can only update salat schedules for assigned masjid
  if (role === "salat_editor") {
    if (!masjidId) return false;
    const isTargetMasjid = !targetMasjidId || targetMasjidId === masjidId;

    if (permission === "salat:update") {
      return isTargetMasjid;
    }
    return false;
  }

  // Viewer has no write permissions
  return false;
}

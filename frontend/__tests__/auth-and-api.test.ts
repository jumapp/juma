import { getAuthHeaders } from "../services/auth/headers";
import { can } from "../services/auth/permissions";
import { Session } from "../services/auth/types";
import { ApiError } from "../services/api/client";

describe("Auth Headers & RBAC Permissions", () => {
  const superAdminSession: Session = {
    id: "admin-1",
    name: "Admin",
    email: "admin@test.com",
    role: "super_admin",
    accessLevel: "admin",
  };

  const masjidEditorSession: Session = {
    id: "editor-1",
    name: "Masjid Editor",
    email: "editor@test.com",
    role: "masjid_editor",
    masjidId: "masjid-001",
    accessLevel: "editor",
  };

  const salatEditorSession: Session = {
    id: "salat-1",
    name: "Salat Editor",
    email: "salat@test.com",
    role: "salat_editor",
    masjidId: "masjid-001",
    accessLevel: "editor",
  };

  const viewerSession: Session = {
    id: "viewer-1",
    name: "Viewer",
    email: "viewer@test.com",
    role: "viewer",
    accessLevel: "viewer",
  };

  describe("getAuthHeaders", () => {
    it("injects X-Super-Admin-Token for super_admin", () => {
      const headers = getAuthHeaders(superAdminSession);
      expect(headers["X-Super-Admin-Token"]).toBeDefined();
    });

    it("injects X-Masjid-Editor-Token with masjidId for masjid_editor", () => {
      const headers = getAuthHeaders(masjidEditorSession);
      expect(headers["X-Masjid-Editor-Token"]).toBe("masjid-001");
    });

    it("injects X-Salat-Editor-Token and X-Dev-User-Masjid-Id for salat_editor", () => {
      const headers = getAuthHeaders(salatEditorSession);
      expect(headers["X-Salat-Editor-Token"]).toBe("masjid-001");
      expect(headers["X-Dev-User-Masjid-Id"]).toBe("masjid-001");
    });

    it("injects X-Viewer-Token for viewer", () => {
      const headers = getAuthHeaders(viewerSession);
      expect(headers["X-Viewer-Token"]).toBeDefined();
    });
  });

  describe("can (RBAC permissions)", () => {
    it("allows super_admin everything", () => {
      expect(can(superAdminSession, "masjid:create")).toBe(true);
      expect(can(superAdminSession, "masjid:delete")).toBe(true);
      expect(can(superAdminSession, "salat:update")).toBe(true);
      expect(can(superAdminSession, "sync:write")).toBe(true);
    });

    it("allows masjid_editor to create/update own masjid only", () => {
      expect(can(masjidEditorSession, "masjid:read")).toBe(true);
      expect(can(masjidEditorSession, "masjid:update", "masjid-001")).toBe(true);
      expect(can(masjidEditorSession, "masjid:update", "different-masjid")).toBe(false);
      expect(can(masjidEditorSession, "masjid:delete")).toBe(false);
    });

    it("allows salat_editor to update salat on own masjid only", () => {
      expect(can(salatEditorSession, "salat:read")).toBe(true);
      expect(can(salatEditorSession, "salat:update", "masjid-001")).toBe(true);
      expect(can(salatEditorSession, "salat:update", "different-masjid")).toBe(false);
      expect(can(salatEditorSession, "salat:create")).toBe(false);
      expect(can(salatEditorSession, "masjid:update")).toBe(false);
    });

    it("allows viewer read permissions only", () => {
      expect(can(viewerSession, "masjid:read")).toBe(true);
      expect(can(viewerSession, "salat:read")).toBe(true);
      expect(can(viewerSession, "masjid:create")).toBe(false);
      expect(can(viewerSession, "salat:update")).toBe(false);
    });
  });

  describe("ApiError", () => {
    it("constructs with status and message", () => {
      const err = new ApiError("Not found", 404, { id: 123 });
      expect(err.message).toBe("Not found");
      expect(err.status).toBe(404);
      expect(err.details).toEqual({ id: 123 });
    });
  });
});

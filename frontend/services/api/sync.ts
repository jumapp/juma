import { apiClient } from "./client";
import { Masjid } from "./masjids";
import { SalatSchedule } from "./schedules";
import { MasjidProgram } from "./programs";
import { MasjidPerson } from "./people";
import { MasjidPhoto } from "./photos";

export interface SyncSnapshotResponse {
  snapshot: {
    masjids: Masjid[];
    salat_schedules: SalatSchedule[];
    programs: MasjidProgram[];
    people: MasjidPerson[];
    photos: MasjidPhoto[];
  };
  cursor: string;
  has_more: boolean;
}

export interface ClientMutation {
  id: string;
  entity: "masjid" | "salat_schedule" | "program" | "person";
  type: "CREATE" | "UPDATE" | "DELETE";
  payload: Record<string, any>;
}

export interface MutationResult {
  id: string;
  status: "processed" | "failed" | "duplicate";
  result?: any;
  error?: string;
}

export interface SyncMutationsResponse {
  processed: number;
  failed: number;
  duplicates?: number;
  results: MutationResult[];
}

export async function getSyncSnapshot(
  cursor?: string,
  entityTypes?: string[]
): Promise<SyncSnapshotResponse> {
  return apiClient<SyncSnapshotResponse>("/sync/", {
    params: {
      cursor,
      entity_types: entityTypes,
    },
  });
}

export async function postSyncMutations(
  mutations: ClientMutation[]
): Promise<SyncMutationsResponse> {
  return apiClient<SyncMutationsResponse>("/sync/mutations", {
    method: "POST",
    body: { mutations },
  });
}

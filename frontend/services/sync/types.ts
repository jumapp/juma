export type SyncEntityType =
  | "masjid"
  | "salat_schedule"
  | "program"
  | "person";

export type SyncMutationType = "CREATE" | "UPDATE" | "DELETE";

export type OutboxItemStatus = "queued" | "inflight" | "failed" | "confirmed";

export interface OutboxItem {
  id: string;
  entity: SyncEntityType;
  type: SyncMutationType;
  payload: Record<string, any>;
  createdAt: string;
  attempts: number;
  status: OutboxItemStatus;
  lastError?: string;
}

export interface SyncState {
  isSyncing: boolean;
  pendingCount: number;
  failedCount: number;
  lastSyncTime: string | null;
  lastError: string | null;
}

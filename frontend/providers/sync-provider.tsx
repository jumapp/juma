import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { AppState, AppStateStatus } from "react-native";
import { useNetworkStatus } from "@/hooks/use-network-status";
import {
  getOutbox,
  enqueueMutation as addMutation,
  flushOutbox as runFlush,
  clearOutbox as resetOutbox,
  removeMutation as deleteMutation,
  FlushResult,
} from "@/services/sync/outbox";
import { fetchAndApplySnapshot } from "@/services/sync/snapshot";
import { OutboxItem, SyncEntityType, SyncMutationType, SyncState } from "@/services/sync/types";

export interface SyncContextValue extends SyncState {
  outbox: OutboxItem[];
  enqueueMutation: (
    entity: SyncEntityType,
    type: SyncMutationType,
    payload: Record<string, any>
  ) => Promise<OutboxItem>;
  flushOutbox: () => Promise<FlushResult | null>;
  syncSnapshot: () => Promise<void>;
  retryFailedMutations: () => Promise<FlushResult | null>;
  clearOutbox: () => Promise<void>;
  removeMutation: (id: string) => Promise<void>;
}

const SyncContext = createContext<SyncContextValue | null>(null);

export function SyncProvider({ children }: { children: ReactNode }) {
  const { isOnline } = useNetworkStatus();
  const [outbox, setOutbox] = useState<OutboxItem[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);

  const refreshOutbox = useCallback(async () => {
    const items = await getOutbox();
    setOutbox(items);
  }, []);

  useEffect(() => {
    refreshOutbox();
  }, [refreshOutbox]);

  const flushOutbox = useCallback(async (): Promise<FlushResult | null> => {
    if (!isOnline || isSyncing) {
      return null;
    }

    setIsSyncing(true);
    setLastError(null);

    try {
      const result = await runFlush();
      await refreshOutbox();
      setLastSyncTime(new Date().toISOString());
      return result;
    } catch (e: any) {
      setLastError(e.message || "Sync failed");
      await refreshOutbox();
      return null;
    } finally {
      setIsSyncing(false);
    }
  }, [isOnline, isSyncing, refreshOutbox]);

  // Flush on reconnection
  useEffect(() => {
    if (isOnline) {
      flushOutbox();
    }
  }, [isOnline, flushOutbox]);

  // Flush on app foreground
  useEffect(() => {
    const handleAppStateChange = (nextState: AppStateStatus) => {
      if (nextState === "active" && isOnline) {
        flushOutbox();
      }
    };

    const sub = AppState.addEventListener("change", handleAppStateChange);
    return () => sub.remove();
  }, [isOnline, flushOutbox]);

  const enqueueMutation = useCallback(
    async (
      entity: SyncEntityType,
      type: SyncMutationType,
      payload: Record<string, any>
    ): Promise<OutboxItem> => {
      const item = await addMutation(entity, type, payload);
      await refreshOutbox();

      if (isOnline) {
        // Trigger background flush
        setTimeout(() => flushOutbox(), 100);
      }

      return item;
    },
    [isOnline, refreshOutbox, flushOutbox]
  );

  const syncSnapshot = useCallback(async () => {
    if (!isOnline) return;
    try {
      await fetchAndApplySnapshot();
    } catch (e: any) {
      console.warn("Snapshot sync error:", e);
    }
  }, [isOnline]);

  const retryFailedMutations = useCallback(async () => {
    return flushOutbox();
  }, [flushOutbox]);

  const clearOutboxHandler = useCallback(async () => {
    await resetOutbox();
    await refreshOutbox();
  }, [refreshOutbox]);

  const removeMutationHandler = useCallback(
    async (id: string) => {
      await deleteMutation(id);
      await refreshOutbox();
    },
    [refreshOutbox]
  );

  const pendingCount = outbox.filter(
    (item) => item.status === "queued" || item.status === "inflight"
  ).length;

  const failedCount = outbox.filter((item) => item.status === "failed").length;

  const value: SyncContextValue = {
    isSyncing,
    pendingCount,
    failedCount,
    lastSyncTime,
    lastError,
    outbox,
    enqueueMutation,
    flushOutbox,
    syncSnapshot,
    retryFailedMutations,
    clearOutbox: clearOutboxHandler,
    removeMutation: removeMutationHandler,
  };

  return <SyncContext.Provider value={value}>{children}</SyncContext.Provider>;
}

export function useSync(): SyncContextValue {
  const context = useContext(SyncContext);
  if (!context) {
    return {
      isSyncing: false,
      pendingCount: 0,
      failedCount: 0,
      lastSyncTime: null,
      lastError: null,
      outbox: [],
      enqueueMutation: async () => ({} as OutboxItem),
      flushOutbox: async () => null,
      syncSnapshot: async () => {},
      retryFailedMutations: async () => null,
      clearOutbox: async () => {},
      removeMutation: async () => {},
    };
  }
  return context;
}

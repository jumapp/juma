import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Crypto from "expo-crypto";
import { config } from "@/lib/config";
import { postSyncMutations, ClientMutation } from "@/services/api/sync";
import {
  OutboxItem,
  SyncEntityType,
  SyncMutationType,
} from "./types";

const OUTBOX_STORAGE_KEY = "jumapp:outbox";
const LAST_SYNC_STORAGE_KEY = "jumapp:last-sync";

function generateUUID(): string {
  try {
    if (typeof Crypto !== "undefined" && typeof Crypto.randomUUID === "function") {
      const id = Crypto.randomUUID();
      if (id) return id;
    }
  } catch {
    // fallback below
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export async function getOutbox(): Promise<OutboxItem[]> {
  try {
    const raw = await AsyncStorage.getItem(OUTBOX_STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.warn("Failed to load outbox:", e);
  }
  return [];
}

export async function saveOutbox(items: OutboxItem[]): Promise<void> {
  try {
    await AsyncStorage.setItem(OUTBOX_STORAGE_KEY, JSON.stringify(items));
  } catch (e) {
    console.error("Failed to save outbox:", e);
  }
}

export async function enqueueMutation(
  entity: SyncEntityType,
  type: SyncMutationType,
  payload: Record<string, any>
): Promise<OutboxItem> {
  const item: OutboxItem = {
    id: generateUUID(),
    entity,
    type,
    payload,
    createdAt: new Date().toISOString(),
    attempts: 0,
    status: "queued",
  };

  const outbox = await getOutbox();
  outbox.push(item);
  await saveOutbox(outbox);

  return item;
}

export async function removeMutation(id: string): Promise<void> {
  const outbox = await getOutbox();
  const filtered = outbox.filter((item) => item.id !== id);
  await saveOutbox(filtered);
}

export async function clearOutbox(): Promise<void> {
  await AsyncStorage.removeItem(OUTBOX_STORAGE_KEY);
}

export interface FlushResult {
  processed: number;
  failed: number;
  duplicates: number;
  remaining: number;
}

export async function flushOutbox(): Promise<FlushResult> {
  const outbox = await getOutbox();
  const pending = outbox.filter(
    (item) => item.status === "queued" || item.status === "failed"
  );

  if (pending.length === 0) {
    return {
      processed: 0,
      failed: 0,
      duplicates: 0,
      remaining: outbox.length,
    };
  }

  // Take batch of mutations up to configured syncBatchSize
  const batch = pending.slice(0, config.syncBatchSize);
  const batchIds = new Set(batch.map((b) => b.id));

  // Mark inflight
  const updatedOutbox = outbox.map((item) => {
    if (batchIds.has(item.id)) {
      return { ...item, status: "inflight" as const, attempts: item.attempts + 1 };
    }
    return item;
  });
  await saveOutbox(updatedOutbox);

  const clientMutations: ClientMutation[] = batch.map((item) => ({
    id: item.id,
    entity: item.entity,
    type: item.type,
    payload: item.payload,
  }));

  try {
    const response = await postSyncMutations(clientMutations);
    const resultMap = new Map(response.results.map((r) => [r.id, r]));

    const processedIds = new Set<string>();
    const finalOutbox: OutboxItem[] = [];

    for (const item of updatedOutbox) {
      if (batchIds.has(item.id)) {
        const res = resultMap.get(item.id);
        if (res && (res.status === "processed" || res.status === "duplicate")) {
          processedIds.add(item.id);
          // Mutation confirmed on server -> remove from outbox
          continue;
        } else if (res && res.status === "failed") {
          finalOutbox.push({
            ...item,
            status: "failed",
            lastError: res.error || "Mutation rejected by server",
          });
        } else {
          finalOutbox.push({
            ...item,
            status: "failed",
            lastError: "No response for mutation from server",
          });
        }
      } else {
        finalOutbox.push(item);
      }
    }

    await saveOutbox(finalOutbox);
    await AsyncStorage.setItem(LAST_SYNC_STORAGE_KEY, new Date().toISOString());

    return {
      processed: response.processed,
      failed: response.failed,
      duplicates: response.duplicates || 0,
      remaining: finalOutbox.length,
    };
  } catch (error: any) {
    // Network or server error -> mark failed with backoff attempt
    const failedOutbox = updatedOutbox.map((item) => {
      if (batchIds.has(item.id)) {
        return {
          ...item,
          status: "failed" as const,
          lastError: error.message || "Network error during sync",
        };
      }
      return item;
    });

    await saveOutbox(failedOutbox);

    throw error;
  }
}

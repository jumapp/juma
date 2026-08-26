import { apiClient } from "./client";

export type SalatName = "fajr" | "zuhr" | "asr" | "maghrib" | "isha" | "juma";

export interface SalatSchedule {
  id: string;
  masjid_id: string;
  salat_name: SalatName;
  adhan_time?: string;
  iqama_time?: string;
  khutbah_time?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ListSchedulesParams {
  masjid_id?: string;
  salat_name?: SalatName;
}

export interface CreateScheduleInput {
  masjid_id: string;
  salat_name: SalatName;
  adhan_time?: string;
  iqama_time?: string;
  khutbah_time?: string;
}

export async function listSchedules(
  params?: ListSchedulesParams
): Promise<SalatSchedule[]> {
  return apiClient<SalatSchedule[]>("/schedules", { params });
}

export async function getSchedule(id: string): Promise<SalatSchedule> {
  return apiClient<SalatSchedule>(`/schedules/${id}`);
}

export async function createSchedule(
  data: CreateScheduleInput
): Promise<SalatSchedule> {
  return apiClient<SalatSchedule>("/schedules/", {
    method: "POST",
    body: data,
  });
}

export async function updateSchedule(
  id: string,
  data: Partial<CreateScheduleInput>
): Promise<SalatSchedule> {
  return apiClient<SalatSchedule>(`/schedules/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteSchedule(
  id: string
): Promise<{ id: string; status: string }> {
  return apiClient<{ id: string; status: string }>(`/schedules/${id}`, {
    method: "DELETE",
  });
}

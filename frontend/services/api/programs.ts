import { apiClient } from "./client";

export type ProgramType =
  | "maktab"
  | "elder_maktab"
  | "tafseer"
  | "hadith"
  | "other_course";

export interface ProgramSchedule {
  day_of_week: number;
  start_time: string;
  end_time: string;
}

export interface MasjidProgram {
  id: string;
  masjid_id: string;
  type: ProgramType;
  name: string;
  description?: string;
  instructor_id?: string;
  max_participants?: number;
  frequency?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  schedules?: ProgramSchedule[];
}

export interface ListProgramsParams {
  masjid_id?: string;
  program_type?: ProgramType;
}

export interface CreateProgramInput {
  masjid_id: string;
  type: ProgramType;
  name: string;
  description?: string;
  instructor_id?: string;
  max_participants?: number;
  frequency?: string;
  is_active?: boolean;
  schedules?: ProgramSchedule[];
}

export async function listPrograms(
  params?: ListProgramsParams
): Promise<MasjidProgram[]> {
  return apiClient<MasjidProgram[]>("/programs", { params });
}

export async function getProgram(id: string): Promise<MasjidProgram> {
  return apiClient<MasjidProgram>(`/programs/${id}`);
}

export async function createProgram(
  data: CreateProgramInput
): Promise<MasjidProgram> {
  return apiClient<MasjidProgram>("/programs/", {
    method: "POST",
    body: data,
  });
}

export async function updateProgram(
  id: string,
  data: Partial<CreateProgramInput>
): Promise<MasjidProgram> {
  return apiClient<MasjidProgram>(`/programs/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteProgram(
  id: string
): Promise<{ id: string; status: string }> {
  return apiClient<{ id: string; status: string }>(`/programs/${id}`, {
    method: "DELETE",
  });
}

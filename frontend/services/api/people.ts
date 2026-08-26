import { apiClient } from "./client";

export type PersonRole = "imam" | "muazzin" | "committee_member" | "other";
export type AccessLevel = "admin" | "editor" | "viewer" | "general";

export interface MasjidPerson {
  id: string;
  masjid_id: string;
  full_name: string;
  role: PersonRole;
  access_level: AccessLevel;
  phone_primary?: string;
  phone_secondary?: string;
  email?: string;
  bio?: string;
  skills?: string;
  photo_url?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ListPeopleParams {
  masjid_id?: string;
  role?: PersonRole;
  access_level?: AccessLevel;
  is_active?: boolean;
}

export interface CreatePersonInput {
  masjid_id: string;
  full_name: string;
  role: PersonRole;
  access_level?: AccessLevel;
  phone_primary?: string;
  phone_secondary?: string;
  email?: string;
  bio?: string;
  skills?: string;
  photo_url?: string;
  is_active?: boolean;
}

export async function listPeople(
  params?: ListPeopleParams
): Promise<MasjidPerson[]> {
  return apiClient<MasjidPerson[]>("/people", { params });
}

export async function getPerson(id: string): Promise<MasjidPerson> {
  return apiClient<MasjidPerson>(`/people/${id}`);
}

export async function createPerson(
  data: CreatePersonInput
): Promise<MasjidPerson> {
  return apiClient<MasjidPerson>("/people/", {
    method: "POST",
    body: data,
  });
}

export async function updatePerson(
  id: string,
  data: Partial<CreatePersonInput>
): Promise<MasjidPerson> {
  return apiClient<MasjidPerson>(`/people/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deletePerson(
  id: string
): Promise<{ id: string; status: string }> {
  return apiClient<{ id: string; status: string }>(`/people/${id}`, {
    method: "DELETE",
  });
}

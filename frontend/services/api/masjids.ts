import { apiClient } from "./client";

export interface Masjid {
  id: string;
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  latitude: number;
  longitude: number;
  timezone?: string;
  map_id?: string;
  accessible_by_public_transport?: boolean;
  accessibility_details?: string;
  highway_masjid?: boolean;
  on_road_masjid?: boolean;
  opens_at?: string;
  closes_at?: string;
  is_24_hours?: boolean;
  ramadan_adjusted_hours?: boolean;
  has_wudu_stations?: boolean;
  has_urinals?: boolean;
  has_toilets?: boolean;
  has_womens_prayer_area?: boolean;
  has_library?: boolean;
  has_parking?: boolean;
  has_street_parking?: boolean;
  other_items?: string;
  meta?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  salat_schedules?: any[];
  programs?: any[];
  people?: any[];
  photos?: any[];
  distance_meters?: number;
}

export interface ListMasjidsParams {
  lat?: number;
  lon?: number;
  radius?: number;
  city?: string;
  state?: string;
  accessible_by_transport?: boolean;
}

export interface CreateMasjidInput {
  name: string;
  address_line1?: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code?: string;
  country?: string;
  latitude: number;
  longitude: number;
  timezone?: string;
  accessible_by_public_transport?: boolean;
  accessibility_details?: string;
  highway_masjid?: boolean;
  on_road_masjid?: boolean;
  opens_at?: string;
  closes_at?: string;
  is_24_hours?: boolean;
  ramadan_adjusted_hours?: boolean;
  has_wudu_stations?: boolean;
  has_urinals?: boolean;
  has_toilets?: boolean;
  has_womens_prayer_area?: boolean;
  has_library?: boolean;
  has_parking?: boolean;
  has_street_parking?: boolean;
  other_items?: string;
}

export async function listMasjids(params?: ListMasjidsParams): Promise<Masjid[]> {
  return apiClient<Masjid[]>("/masjids", { params });
}

export async function getMasjid(id: string): Promise<Masjid> {
  return apiClient<Masjid>(`/masjids/${id}`);
}

export async function createMasjid(data: CreateMasjidInput): Promise<Masjid> {
  return apiClient<Masjid>("/masjids/", {
    method: "POST",
    body: data,
  });
}

export async function updateMasjid(
  id: string,
  data: Partial<CreateMasjidInput>
): Promise<Masjid> {
  return apiClient<Masjid>(`/masjids/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function deleteMasjid(id: string): Promise<{ id: string; status: string }> {
  return apiClient<{ id: string; status: string }>(`/masjids/${id}`, {
    method: "DELETE",
  });
}

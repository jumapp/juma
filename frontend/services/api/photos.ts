import { apiClient } from "./client";

export interface MasjidPhoto {
  id: string;
  masjid_id: string;
  filename: string;
  file_path: string;
  mime_type: string;
  size: number;
  width?: number;
  height?: number;
  caption?: string;
  order_index?: number;
  is_featured?: boolean;
  moderation_status?: "pending" | "approved" | "rejected";
  created_at?: string;
  updated_at?: string;
}

export interface UploadPhotoInput {
  filename: string;
  file_path: string;
  mime_type: string;
  size: number;
  width?: number;
  height?: number;
  caption?: string;
  order_index?: number;
  is_featured?: boolean;
}

export async function createPhoto(
  masjidId: string,
  data: UploadPhotoInput
): Promise<MasjidPhoto> {
  return apiClient<MasjidPhoto>(`/photos/masjids/${masjidId}/photos`, {
    method: "POST",
    body: data,
  });
}

export async function deletePhoto(
  masjidId: string,
  photoId: string
): Promise<{ id: string; status: string }> {
  return apiClient<{ id: string; status: string }>(
    `/photos/masjids/${masjidId}/photos/${photoId}`,
    {
      method: "DELETE",
    }
  );
}

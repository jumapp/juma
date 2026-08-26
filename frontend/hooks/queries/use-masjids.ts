import { useQuery } from "@tanstack/react-query";
import {
  listMasjids,
  getMasjid,
  ListMasjidsParams,
  Masjid,
} from "@/services/api/masjids";

export const MASJIDS_QUERY_KEY = ["masjids"] as const;

export function useMasjids(params?: ListMasjidsParams) {
  return useQuery<Masjid[], Error>({
    queryKey: [...MASJIDS_QUERY_KEY, "list", params],
    queryFn: () => listMasjids(params),
  });
}

export function useMasjidDetail(id: string) {
  return useQuery<Masjid, Error>({
    queryKey: [...MASJIDS_QUERY_KEY, "detail", id],
    queryFn: () => getMasjid(id),
    enabled: Boolean(id),
  });
}

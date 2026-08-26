import { useQuery } from "@tanstack/react-query";
import {
  listPrograms,
  getProgram,
  MasjidProgram,
  ListProgramsParams,
} from "@/services/api/programs";

export const PROGRAMS_QUERY_KEY = ["programs"] as const;

export function useMasjidPrograms(params?: ListProgramsParams) {
  return useQuery<MasjidProgram[], Error>({
    queryKey: [...PROGRAMS_QUERY_KEY, "list", params],
    queryFn: () => listPrograms(params),
  });
}

export function useMasjidProgramDetail(id: string) {
  return useQuery<MasjidProgram, Error>({
    queryKey: [...PROGRAMS_QUERY_KEY, "detail", id],
    queryFn: () => getProgram(id),
    enabled: Boolean(id),
  });
}

import { useQuery } from "@tanstack/react-query";
import {
  listSchedules,
  getSchedule,
  SalatSchedule,
  ListSchedulesParams,
} from "@/services/api/schedules";

export const SCHEDULES_QUERY_KEY = ["schedules"] as const;

export function useSalatSchedules(params?: ListSchedulesParams) {
  return useQuery<SalatSchedule[], Error>({
    queryKey: [...SCHEDULES_QUERY_KEY, "list", params],
    queryFn: () => listSchedules(params),
  });
}

export function useSalatScheduleDetail(id: string) {
  return useQuery<SalatSchedule, Error>({
    queryKey: [...SCHEDULES_QUERY_KEY, "detail", id],
    queryFn: () => getSchedule(id),
    enabled: Boolean(id),
  });
}

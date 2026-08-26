import { useQuery } from "@tanstack/react-query";
import { checkHealth, checkFullHealth, FullHealthResponse } from "@/services/api/health";

export const HEALTH_QUERY_KEY = ["health"] as const;

export function useHealthCheck() {
  return useQuery({
    queryKey: [...HEALTH_QUERY_KEY, "basic"],
    queryFn: checkHealth,
    staleTime: 1000 * 30, // 30s
    retry: 1,
  });
}

export function useFullHealthCheck() {
  return useQuery<FullHealthResponse, Error>({
    queryKey: [...HEALTH_QUERY_KEY, "full"],
    queryFn: checkFullHealth,
    staleTime: 1000 * 30,
    retry: 1,
  });
}

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createMasjid as createMasjidApi } from '@/services/api/masjids';
import { Masjid } from '@/services/api/masjids';

interface UseCreateMasjidOptions {
  onSuccess?: (data: Masjid) => void;
  onError?: (error: unknown) => void;
}

export function useCreateMasjid({ onSuccess, onError }: UseCreateMasjidOptions = {}) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createMasjidApi,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['masjids'] });
      onSuccess?.(data);
    },
    onError: (error) => {
      onError?.(error);
    },
  });

  return mutation;
}
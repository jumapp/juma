import AsyncStorage from "@react-native-async-storage/async-storage";
import { getSyncSnapshot } from "@/services/api/sync";
import { queryClient } from "@/providers/query-provider";
import { MASJIDS_QUERY_KEY } from "@/hooks/queries/use-masjids";
import { SCHEDULES_QUERY_KEY } from "@/hooks/queries/use-schedules";
import { PROGRAMS_QUERY_KEY } from "@/hooks/queries/use-programs";

const SYNC_CURSOR_KEY = "jumapp:sync-cursor";

export async function fetchAndApplySnapshot(): Promise<{
  masjidsCount: number;
  schedulesCount: number;
  programsCount: number;
  cursor: string;
}> {
  const savedCursor = await AsyncStorage.getItem(SYNC_CURSOR_KEY);
  const data = await getSyncSnapshot(savedCursor || undefined);

  if (data.snapshot.masjids && data.snapshot.masjids.length > 0) {
    queryClient.setQueryData([...MASJIDS_QUERY_KEY, "list", undefined], data.snapshot.masjids);
    data.snapshot.masjids.forEach((masjid) => {
      queryClient.setQueryData([...MASJIDS_QUERY_KEY, "detail", masjid.id], masjid);
    });
  }

  if (data.snapshot.salat_schedules && data.snapshot.salat_schedules.length > 0) {
    queryClient.setQueryData(
      [...SCHEDULES_QUERY_KEY, "list", undefined],
      data.snapshot.salat_schedules
    );
  }

  if (data.snapshot.programs && data.snapshot.programs.length > 0) {
    queryClient.setQueryData(
      [...PROGRAMS_QUERY_KEY, "list", undefined],
      data.snapshot.programs
    );
  }

  if (data.cursor) {
    await AsyncStorage.setItem(SYNC_CURSOR_KEY, data.cursor);
  }

  return {
    masjidsCount: data.snapshot.masjids?.length || 0,
    schedulesCount: data.snapshot.salat_schedules?.length || 0,
    programsCount: data.snapshot.programs?.length || 0,
    cursor: data.cursor,
  };
}

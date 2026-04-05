import type { QueryClient } from "@tanstack/react-query"

import { clearAllReadCaches } from "./readCache"

/** Полный сброс клиентского состояния после импорта бэкапа (БД на сервере уже заменена). */
export async function resetAppCachesAfterBackupImport(queryClient: QueryClient): Promise<void> {
  await clearAllReadCaches()
  queryClient.clear()
}

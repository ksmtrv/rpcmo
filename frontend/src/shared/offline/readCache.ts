import { offlineDb } from "./db"

export async function saveReadCache(key: string, data: unknown): Promise<void> {
  await offlineDb.readCache.put({
    key,
    payload: JSON.stringify(data),
    updatedAt: Date.now(),
  })
}

export async function deleteReadCacheKey(key: string): Promise<void> {
  await offlineDb.readCache.delete(key)
}

export async function loadReadCache<T>(key: string): Promise<T | null> {
  const row = await offlineDb.readCache.get(key)
  if (!row) return null
  try {
    return JSON.parse(row.payload) as T
  } catch {
    return null
  }
}

export function cacheKeyTransactions(page: number, size: number) {
  return `transactions:p${page}:s${size}`
}

export const cacheKeyCategories = "categories:list"

/** После импорта бэкапа — иначе UI может показывать старые списки из IndexedDB. */
export async function clearAllReadCaches(): Promise<void> {
  await offlineDb.readCache.clear()
}

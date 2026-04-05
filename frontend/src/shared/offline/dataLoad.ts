import type { Category } from "@/shared/api/categories"
import { categoriesApi } from "@/shared/api/categories"
import type { TransactionsPage } from "@/shared/api/transactions"
import { transactionsApi } from "@/shared/api/transactions"
import { isLikelyNetworkFailure, isNavigatorOnline } from "./network"
import { pendingCategoryPatches } from "./outbox"
import { cacheKeyCategories, cacheKeyTransactions, loadReadCache, saveReadCache } from "./readCache"

async function useCacheIfOffline<T>(e: unknown, key: string): Promise<T | null> {
  if (!isNavigatorOnline() || isLikelyNetworkFailure(e)) {
    return loadReadCache<T>(key)
  }
  return null
}

export async function loadTransactionsPageMerged(page: number, size: number): Promise<TransactionsPage> {
  const key = cacheKeyTransactions(page, size)
  let base: TransactionsPage
  try {
    base = await transactionsApi.list({ page, size })
    await saveReadCache(key, base)
  } catch (e) {
    const cached = await useCacheIfOffline<TransactionsPage>(e, key)
    if (cached) base = cached
    else throw e
  }
  const patches = await pendingCategoryPatches()
  if (patches.size === 0) return base
  return {
    ...base,
    items: base.items.map((t) => {
      if (!patches.has(t.id)) return t
      return { ...t, category_id: patches.get(t.id)! }
    }),
  }
}

export async function loadCategoriesForOffline(): Promise<Category[]> {
  const key = cacheKeyCategories
  try {
    const list = await categoriesApi.list()
    await saveReadCache(key, list)
    return list
  } catch (e) {
    const cached = await useCacheIfOffline<Category[]>(e, key)
    if (cached) return cached
    throw e
  }
}

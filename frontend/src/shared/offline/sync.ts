import type { Transaction } from "@/shared/api/transactions"
import type { BulkCategorizePayload, OutboxRow, PatchTransactionPayload } from "./db"
import { notifyOutboxChanged } from "./outboxEvents"
import { listOutboxOrdered, removeOutbox } from "./outbox"

const API_BASE = "/api/v1"

export type SyncResult = {
  flushed: number
  dropped: number
  failed: number
  lastError: string | null
}

async function parseError(res: Response): Promise<string> {
  try {
    const j = (await res.json()) as { error?: { message?: string }; detail?: string }
    return j?.error?.message || j?.detail || res.statusText
  } catch {
    return res.statusText
  }
}

async function execRow(row: OutboxRow): Promise<"ok" | "drop" | "retry"> {
  if (row.op === "patch_transaction") {
    const p = row.payload as PatchTransactionPayload
    const res = await fetch(`${API_BASE}/transactions/${p.transactionId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category_id: p.categoryId }),
    })
    if (res.status === 404) return "drop"
    if (!res.ok) throw new Error(await parseError(res))
    return "ok"
  }
  if (row.op === "bulk_categorize") {
    const p = row.payload as BulkCategorizePayload
    const res = await fetch(`${API_BASE}/transactions/bulk-categorize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transaction_ids: p.transactionIds, category_id: p.categoryId }),
    })
    if (!res.ok) throw new Error(await parseError(res))
    return "ok"
  }
  return "drop"
}

/**
 * Отправляет очередь на сервер по порядку FIFO.
 * 404 на PATCH — операция снимается (сущность исчезла).
 * Остальные ошибки — операция остаётся для следующей попытки.
 */
export async function flushOutbox(): Promise<SyncResult> {
  const result: SyncResult = { flushed: 0, dropped: 0, failed: 0, lastError: null }
  const rows = await listOutboxOrdered()
  for (const row of rows) {
    try {
      const outcome = await execRow(row)
      if (outcome === "ok" || outcome === "drop") {
        await removeOutbox(row.id)
        if (outcome === "ok") result.flushed += 1
        else result.dropped += 1
      }
    } catch (e) {
      result.failed += 1
      result.lastError = e instanceof Error ? e.message : String(e)
      break
    }
  }
  notifyOutboxChanged()
  return result
}

/** Пытается PATCH на сервере; при сетевой ошибке кладёт в очередь. */
export async function patchTransactionCategoryOrQueue(
  transactionId: string,
  categoryId: string | null,
): Promise<{ ok: true; fromServer: Transaction } | { ok: true; queued: true; optimistic: Transaction }> {
  const { enqueuePatchTransaction } = await import("./outbox")
  const { isLikelyNetworkFailure } = await import("./network")

  try {
    const res = await fetch(`${API_BASE}/transactions/${transactionId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category_id: categoryId }),
    })
    if (!res.ok) {
      const msg = await parseError(res)
      if (res.status === 404) throw new Error(msg)
      throw new Error(msg)
    }
    const data = (await res.json()) as Transaction
    return { ok: true, fromServer: data }
  } catch (e) {
    if (isLikelyNetworkFailure(e)) {
      await enqueuePatchTransaction(transactionId, categoryId)
      const optimistic: Transaction = {
        id: transactionId,
        account_id: "",
        operation_date: "",
        amount: 0,
        currency: "RUB",
        direction: "out",
        description: "",
        counterparty: null,
        category_id: categoryId,
        is_manual: false,
        is_duplicate: false,
      }
      return { ok: true, queued: true, optimistic }
    }
    throw e
  }
}

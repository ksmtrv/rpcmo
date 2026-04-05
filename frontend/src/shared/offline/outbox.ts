import {
  offlineDb,
  type BulkCategorizePayload,
  type OutboxRow,
  type PatchTransactionPayload,
} from "./db"
import { notifyOutboxChanged } from "./outboxEvents"

function newId(): string {
  return crypto.randomUUID()
}

/** Последнее изменение категории по транзакции побеждает (LWW в очереди). */
export async function enqueuePatchTransaction(
  transactionId: string,
  categoryId: string | null,
): Promise<void> {
  await offlineDb.transaction("rw", offlineDb.outbox, async () => {
    const existing = await offlineDb.outbox.filter((r) => r.op === "patch_transaction").toArray()
    for (const r of existing) {
      const p = r.payload as PatchTransactionPayload
      if (p.transactionId === transactionId) {
        await offlineDb.outbox.delete(r.id)
      }
    }
    const row: OutboxRow = {
      id: newId(),
      op: "patch_transaction",
      payload: { transactionId, categoryId },
      createdAt: Date.now(),
    }
    await offlineDb.outbox.add(row)
    notifyOutboxChanged()
  })
}

export async function enqueueBulkCategorize(
  transactionIds: string[],
  categoryId: string | null,
): Promise<void> {
  const row: OutboxRow = {
    id: newId(),
    op: "bulk_categorize",
    payload: { transactionIds, categoryId } satisfies BulkCategorizePayload,
    createdAt: Date.now(),
  }
  await offlineDb.outbox.add(row)
  notifyOutboxChanged()
}

export async function listOutboxOrdered(): Promise<OutboxRow[]> {
  return offlineDb.outbox.orderBy("createdAt").toArray()
}

export async function removeOutbox(id: string): Promise<void> {
  await offlineDb.outbox.delete(id)
}

/** Активные правки категорий для слияния в UI (последняя по каждой транзакции). */
export async function pendingCategoryPatches(): Promise<Map<string, string | null>> {
  const rows = await offlineDb.outbox.filter((r) => r.op === "patch_transaction").toArray()
  const map = new Map<string, string | null>()
  for (const r of rows.sort((a, b) => a.createdAt - b.createdAt)) {
    const p = r.payload as PatchTransactionPayload
    map.set(p.transactionId, p.categoryId)
  }
  return map
}

export async function outboxPendingCount(): Promise<number> {
  return offlineDb.outbox.count()
}

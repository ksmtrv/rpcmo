import Dexie, { type Table } from "dexie"

export type PatchTransactionPayload = {
  transactionId: string
  categoryId: string | null
}

export type BulkCategorizePayload = {
  transactionIds: string[]
  categoryId: string | null
}

export type OutboxOperation = "patch_transaction" | "bulk_categorize"

export type OutboxRow = {
  id: string
  op: OutboxOperation
  payload: PatchTransactionPayload | BulkCategorizePayload
  createdAt: number
}

export type ReadCacheRow = {
  key: string
  payload: string
  updatedAt: number
}

class FincontrolOfflineDB extends Dexie {
  outbox!: Table<OutboxRow, string>
  readCache!: Table<ReadCacheRow, string>

  constructor() {
    super("fincontrol_offline")
    this.version(1).stores({
      outbox: "id, createdAt, op",
      readCache: "key, updatedAt",
    })
  }
}

export const offlineDb = new FincontrolOfflineDB()

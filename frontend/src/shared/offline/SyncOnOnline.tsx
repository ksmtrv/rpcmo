import { useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { subscribeOnlineStatus } from "./network"
import { flushOutbox } from "./sync"

/** Сбрасывает очередь IndexedDB на сервер при событии online и обновляет React Query. */
export function SyncOnOnline() {
  const qc = useQueryClient()
  useEffect(() => {
    const run = async () => {
      if (!navigator.onLine) return
      await flushOutbox()
      await qc.invalidateQueries()
    }
    const sub = subscribeOnlineStatus(() => {
      if (navigator.onLine) void run()
    })
    if (navigator.onLine) void run()
    return sub
  }, [qc])
  return null
}

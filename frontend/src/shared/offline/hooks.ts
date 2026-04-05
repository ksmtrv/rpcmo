import { useEffect, useState } from "react"
import { outboxPendingCount } from "./outbox"
import { subscribeOnlineStatus } from "./network"
import { subscribeOutboxChanged } from "./outboxEvents"

export function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(() =>
    typeof navigator !== "undefined" ? navigator.onLine : true,
  )
  useEffect(() => {
    return subscribeOnlineStatus(() => setOnline(navigator.onLine))
  }, [])
  return online
}

export function useOutboxPendingCount(): number {
  const [n, setN] = useState(0)
  useEffect(() => {
    const refresh = () => {
      void outboxPendingCount().then(setN)
    }
    refresh()
    return subscribeOutboxChanged(refresh)
  }, [])
  return n
}

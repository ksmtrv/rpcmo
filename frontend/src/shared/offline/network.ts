export function isNavigatorOnline(): boolean {
  return typeof navigator !== "undefined" ? navigator.onLine : true
}

export function subscribeOnlineStatus(cb: () => void): () => void {
  if (typeof window === "undefined") return () => {}
  window.addEventListener("online", cb)
  window.addEventListener("offline", cb)
  return () => {
    window.removeEventListener("online", cb)
    window.removeEventListener("offline", cb)
  }
}

/** Сеть недоступна или CORS/сервер недоступен — типичный сигнал для офлайн-очереди */
export function isLikelyNetworkFailure(err: unknown): boolean {
  if (!isNavigatorOnline()) return true
  if (err instanceof TypeError) {
    const m = String(err.message || "").toLowerCase()
    return m.includes("fetch") || m.includes("network") || m.includes("failed")
  }
  if (err instanceof Error) {
    const m = err.message.toLowerCase()
    if (m.includes("failed to fetch")) return true
  }
  return false
}

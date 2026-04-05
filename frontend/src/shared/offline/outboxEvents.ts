const EVENT = "fincontrol-outbox-changed"

export function notifyOutboxChanged(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(EVENT))
  }
}

export function subscribeOutboxChanged(cb: () => void): () => void {
  if (typeof window === "undefined") return () => {}
  window.addEventListener(EVENT, cb)
  return () => window.removeEventListener(EVENT, cb)
}

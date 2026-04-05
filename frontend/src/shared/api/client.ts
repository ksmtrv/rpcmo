const API_BASE = "/api/v1"

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown }

function messageFromErrorBody(body: unknown): string {
  if (!body || typeof body !== "object") return ""
  const o = body as Record<string, unknown>
  const err = o.error
  if (err && typeof err === "object" && "message" in err) {
    const m = (err as { message?: unknown }).message
    if (typeof m === "string" && m) return m
  }
  const d = o.detail
  if (typeof d === "string" && d) return d
  if (Array.isArray(d) && d.length > 0) {
    const first = d[0]
    if (first && typeof first === "object" && "msg" in first) {
      const m = (first as { msg?: unknown }).msg
      if (typeof m === "string") return m
    }
  }
  return ""
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, ...init } = options
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  }
  const fetchBody: BodyInit | null | undefined = body
    ? JSON.stringify(body as object)
    : undefined
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
    headers,
    body: fetchBody,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(messageFromErrorBody(err) || res.statusText)
  }
  if (res.status === 204) {
    return undefined as T
  }
  const raw = await res.text()
  if (!raw.trim()) {
    return undefined as T
  }
  return JSON.parse(raw) as T
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: "POST", body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: "PATCH", body }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
}

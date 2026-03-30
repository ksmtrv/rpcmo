import { api } from "./client"

export interface ImportUploadResponse {
  import_id: string
  headers: string[]
  column_map: Record<string, string>
  encoding: string
  delimiter: string
  total_rows: number
  preview: Record<string, unknown>[]
}

export interface ImportConfirmRequest {
  column_map: Record<string, string>
  account_name?: string
  date_format?: string
}

export interface ImportConfirmResponse {
  import_id: string
  status: string
  imported_rows: number
  skipped_rows: number
  duplicate_rows: number
}

export const importsApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append("file", file)
    return fetch("/api/v1/imports/upload", {
      method: "POST",
      body: form,
    }).then((r) => {
      if (!r.ok) throw new Error(r.statusText)
      return r.json() as Promise<ImportUploadResponse>
    })
  },
  confirm: (importId: string, body: ImportConfirmRequest) =>
    api.post<ImportConfirmResponse>(`/imports/${importId}/confirm`, body),
  get: (importId: string) => api.get<{ id: string; status: string; imported_rows: number }>(`/imports/${importId}`),
}

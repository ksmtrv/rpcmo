import { api } from "./client"

export async function exportBackupJson(): Promise<Record<string, unknown>> {
  return api.get<Record<string, unknown>>("/backups/export")
}

export async function exportBackupEncrypted(passphrase: string): Promise<Record<string, unknown>> {
  return api.post<Record<string, unknown>>("/backups/export", { passphrase })
}

export async function importBackupJson(
  snapshot: Record<string, unknown>,
  replace: boolean,
): Promise<{ status: string; replace?: boolean }> {
  const q = replace ? "?replace=true" : ""
  return api.post<{ status: string; replace?: boolean }>(`/backups/import${q}`, snapshot)
}

/** Импорт зашифрованного файла: сервер расшифровывает по паролю. */
export async function importEncryptedBackupJson(
  encryptedFileContent: Record<string, unknown>,
  passphrase: string,
  replace: boolean,
): Promise<{ status: string; replace?: boolean }> {
  const q = replace ? "?replace=true" : ""
  return api.post<{ status: string; replace?: boolean }>(`/backups/import${q}`, {
    passphrase,
    backup: encryptedFileContent,
  })
}

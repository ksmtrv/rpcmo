import { useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import {
  exportBackupEncrypted,
  exportBackupJson,
  importBackupJson,
  importEncryptedBackupJson,
} from "@/shared/api/backups"
import { resetAppCachesAfterBackupImport } from "@/shared/offline/resetAfterBackupImport"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { Label } from "@/shared/ui/label"

function isEncryptedEnvelope(obj: Record<string, unknown>): boolean {
  return obj.fincontrol_encrypted === true
}

export function BackupPage() {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [exportPass, setExportPass] = useState("")
  const [exportPass2, setExportPass2] = useState("")
  const [importPass, setImportPass] = useState("")

  async function onExportPlain() {
    setError(null)
    setMessage(null)
    setBusy(true)
    try {
      const data = await exportBackupJson()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
      downloadBlob(blob, `fincontrol-backup-${today()}.json`)
      setMessage("Незашифрованный JSON сохранён.")
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка экспорта")
    } finally {
      setBusy(false)
    }
  }

  async function onExportEncrypted() {
    setError(null)
    setMessage(null)
    if (exportPass.length < 8) {
      setError("Пароль для шифрования — не короче 8 символов.")
      return
    }
    if (exportPass !== exportPass2) {
      setError("Пароли не совпадают.")
      return
    }
    setBusy(true)
    try {
      const data = await exportBackupEncrypted(exportPass)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
      downloadBlob(blob, `fincontrol-backup-${today()}.encrypted.json`)
      setMessage("Зашифрованная копия сохранена. Пароль храните отдельно — без него файл не восстановить.")
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка экспорта")
    } finally {
      setBusy(false)
    }
  }

  function onImportClick() {
    const input = document.createElement("input")
    input.type = "file"
    input.accept = "application/json,.json"
    input.onchange = () => {
      const file = input.files?.[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = async () => {
        setError(null)
        setMessage(null)
        try {
          const text = String(reader.result ?? "")
          const parsed = JSON.parse(text) as Record<string, unknown>
          const encrypted = isEncryptedEnvelope(parsed)

          if (
            !window.confirm(
              "Импорт с полной заменой удалит текущие данные пользователя в базе и восстановит архив. Продолжить?",
            )
          ) {
            return
          }

          setBusy(true)
          if (encrypted) {
            const fromField = importPass.trim()
            const pass =
              fromField.length > 0 ? fromField : window.prompt("Пароль от зашифрованной резервной копии:")
            if (pass == null || pass.length === 0) {
              setError("Нужен пароль для расшифровки.")
              setBusy(false)
              return
            }
            await importEncryptedBackupJson(parsed, pass, true)
          } else {
            await importBackupJson(parsed, true)
          }
          await resetAppCachesAfterBackupImport(queryClient)
          setMessage("Импорт выполнен. Кэш приложения полностью сброшен — откройте «Категории» заново.")
        } catch (e) {
          setError(e instanceof Error ? e.message : "Ошибка импорта")
        } finally {
          setBusy(false)
        }
      }
      reader.readAsText(file)
    }
    input.click()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Резервная копия и экспорт</CardTitle>
        <p className="text-muted-foreground text-sm">
          Обычный JSON или зашифрованный (PBKDF2 + AES-256-GCM). Пароль на сервере не хранится; при импорте
          передаётся по HTTPS один раз для расшифровки на сервере.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {message ? <p className="text-sm text-green-700 dark:text-green-400">{message}</p> : null}
        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Экспорт без шифрования</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3 pt-0">
            <Button onClick={onExportPlain} disabled={busy}>
              Скачать JSON
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Экспорт с шифрованием</CardTitle>
            <p className="text-muted-foreground text-sm">Минимум 8 символов. Рекомендуемое имя: *.encrypted.json</p>
          </CardHeader>
          <CardContent className="space-y-3 pt-0 max-w-md">
            <div>
              <Label htmlFor="ex1">Пароль</Label>
              <Input
                id="ex1"
                type="password"
                autoComplete="new-password"
                value={exportPass}
                onChange={(e) => setExportPass(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="ex2">Повтор пароля</Label>
              <Input
                id="ex2"
                type="password"
                autoComplete="new-password"
                value={exportPass2}
                onChange={(e) => setExportPass2(e.target.value)}
              />
            </div>
            <Button onClick={onExportEncrypted} disabled={busy}>
              Скачать зашифрованную копию
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Импорт</CardTitle>
            <p className="text-muted-foreground text-sm">
              Для зашифрованного файла введите пароль в поле ниже (удобнее, чем диалог) или оставьте пустым —
              пароль спросим отдельно.
            </p>
          </CardHeader>
          <CardContent className="space-y-3 pt-0 max-w-md">
            <div>
              <Label htmlFor="im1">Пароль (если файл зашифрован)</Label>
              <Input
                id="im1"
                type="password"
                autoComplete="off"
                value={importPass}
                onChange={(e) => setImportPass(e.target.value)}
                placeholder="Необязательно для обычного JSON"
              />
            </div>
            <Button variant="outline" onClick={onImportClick} disabled={busy}>
              Восстановить из JSON…
            </Button>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  )
}

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

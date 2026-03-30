import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { Label } from "@/shared/ui/label"
import { importsApi, type ImportConfirmRequest, type ImportUploadResponse } from "@/shared/api/imports"

export function ImportWizard() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<ImportUploadResponse | null>(null)
  const [columnMap, setColumnMap] = useState<Record<string, string>>({})
  const [accountName, setAccountName] = useState("Основной счёт")
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const uploadMutation = useMutation({
    mutationFn: (f: File) => importsApi.upload(f),
    onSuccess: (data) => {
      setPreview(data)
      setColumnMap(data.column_map)
    },
  })

  const confirmMutation = useMutation({
    mutationFn: ({ importId, body }: { importId: string; body: ImportConfirmRequest }) =>
      importsApi.confirm(importId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] })
      navigate("/transactions")
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      setPreview(null)
      uploadMutation.mutate(f)
    }
  }

  const handleConfirm = () => {
    if (!preview) return
    confirmMutation.mutate({
      importId: preview.import_id,
      body: { column_map: columnMap, account_name: accountName },
    })
  }

  if (!preview) {
    return (
      <Card className="max-w-2xl mx-auto mt-8">
        <CardHeader>
          <CardTitle>Импорт выписки</CardTitle>
          <p className="text-muted-foreground text-sm">
            Загрузите CSV-файл банковской выписки. Система определит кодировку и разделитель.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="file">Файл CSV</Label>
              {file && <p className="text-sm text-muted-foreground mb-1">{file.name}</p>}
              <Input
                id="file"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                disabled={uploadMutation.isPending}
              />
            </div>
            {uploadMutation.isError && (
              <p className="text-destructive text-sm">{String(uploadMutation.error)}</p>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="max-w-3xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>Сопоставление колонок</CardTitle>
        <p className="text-muted-foreground text-sm">
          Проверьте соответствие колонок. Всего строк: {preview.total_rows}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label>Название счёта</Label>
          <Input
            value={accountName}
            onChange={(e) => setAccountName(e.target.value)}
            placeholder="Основной счёт"
          />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Поле</th>
                <th className="text-left py-2">Колонка CSV</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(columnMap).map(([field, col]) => (
                <tr key={field} className="border-b">
                  <td className="py-2">{field}</td>
                  <td className="py-2">
                    <select
                      value={col}
                      onChange={(e) => setColumnMap((m) => ({ ...m, [field]: e.target.value }))}
                      className="w-full rounded border px-2 py-1 bg-background"
                    >
                      {preview.headers.map((h) => (
                        <option key={h} value={h}>
                          {h}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="text-sm text-muted-foreground">
          <p>Предпросмотр (первые строки):</p>
          <pre className="mt-2 p-2 bg-muted rounded overflow-auto max-h-40 text-xs">
            {JSON.stringify(preview.preview.slice(0, 3), null, 2)}
          </pre>
        </div>
        <div className="flex gap-4">
          <Button
            onClick={handleConfirm}
            disabled={confirmMutation.isPending}
          >
            {confirmMutation.isPending ? "Импорт..." : "Подтвердить импорт"}
          </Button>
          <Button variant="outline" onClick={() => setPreview(null)}>
            Отмена
          </Button>
        </div>
        {confirmMutation.isError && (
          <p className="text-destructive text-sm">{String(confirmMutation.error)}</p>
        )}
      </CardContent>
    </Card>
  )
}

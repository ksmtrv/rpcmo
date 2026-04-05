import { useQueryClient } from "@tanstack/react-query"
import { useOnlineStatus, useOutboxPendingCount } from "@/shared/offline/hooks"
import { flushOutbox } from "@/shared/offline/sync"
import { Button } from "@/shared/ui/button"

export function OfflineBar() {
  const online = useOnlineStatus()
  const pending = useOutboxPendingCount()
  const qc = useQueryClient()

  if (online && pending === 0) return null

  return (
    <div
      className={`text-center text-sm py-2 px-4 ${online ? "bg-amber-500/15 text-amber-900 dark:text-amber-100" : "bg-destructive/15 text-destructive"}`}
      role="status"
    >
      {!online && <>Нет сети — показаны сохранённые данные. Изменения категорий ставятся в очередь.</>}
      {online && pending > 0 && (
        <span className="inline-flex flex-wrap items-center justify-center gap-3">
          <span>В очереди на сервер: {pending}</span>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="h-7"
            onClick={() => {
              void (async () => {
                await flushOutbox()
                await qc.invalidateQueries()
              })()
            }}
          >
            Отправить сейчас
          </Button>
        </span>
      )}
    </div>
  )
}

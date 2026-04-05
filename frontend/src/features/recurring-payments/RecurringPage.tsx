import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Bell, CheckCircle, RefreshCw } from "lucide-react"
import { api } from "@/shared/api/client"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { formatMoney, formatDate } from "@/shared/lib/format"

interface RecurringItem {
  id: string
  name: string
  amount: number
  currency: string
  direction: string
  next_run_date: string
  recurrence_rule: string
  is_confirmed: boolean
  is_active: boolean
}

type Tab = "all" | "reminders"

export function RecurringPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<Tab>("reminders")

  const { data, isLoading } = useQuery({
    queryKey: ["recurring"],
    queryFn: () => api.get<RecurringItem[]>("/recurring"),
  })

  const { data: reminders, isLoading: remindersLoading } = useQuery({
    queryKey: ["recurring", "reminders"],
    queryFn: () => api.get<RecurringItem[]>("/recurring/reminders?within_days=14"),
  })

  const detectMutation = useMutation({
    mutationFn: () => api.post<{ detected: number; message: string }>("/recurring/detect"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recurring"] })
      queryClient.invalidateQueries({ queryKey: ["forecast"] })
    },
  })

  const confirmMutation = useMutation({
    mutationFn: ({ id, is_confirmed }: { id: string; is_confirmed: boolean }) =>
      api.patch(`/recurring/${id}`, { is_confirmed }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recurring"] })
      queryClient.invalidateQueries({ queryKey: ["recurring", "reminders"] })
      queryClient.invalidateQueries({ queryKey: ["forecast"] })
    },
  })

  const activeItems = (data ?? []).filter((r) => r.is_active)
  const reminderItems = reminders ?? []

  return (
    <div className="space-y-6">
      {reminderItems.length > 0 && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-800 dark:text-blue-300">
              <Bell className="h-5 w-5" />
              Ближайшие платежи (14 дней)
            </CardTitle>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              Эти регулярные платежи ожидаются в ближайшие две недели.
            </p>
          </CardHeader>
          <CardContent>
            {remindersLoading ? (
              <p className="text-sm text-muted-foreground">Загрузка...</p>
            ) : (
              <div className="space-y-2">
                {reminderItems.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center justify-between py-2 px-3 rounded-lg bg-white dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800"
                  >
                    <div>
                      <span className="font-medium text-sm">{r.name}</span>
                      <span className="text-muted-foreground text-xs ml-2">
                        {formatDate(r.next_run_date)}
                        {r.is_confirmed ? " · подтверждено" : " · ожидает подтверждения"}
                      </span>
                    </div>
                    <span className={`font-medium text-sm ${r.direction === "out" ? "text-red-600" : "text-green-600"}`}>
                      {r.direction === "out" ? "−" : "+"}
                      {formatMoney(Math.abs(r.amount), r.currency)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <CardTitle>Регулярные платежи</CardTitle>
              <p className="text-muted-foreground text-sm mt-1">
                Подтверждённые операции учитываются в прогнозе на 14 дней
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => detectMutation.mutate()}
              disabled={detectMutation.isPending}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${detectMutation.isPending ? "animate-spin" : ""}`} />
              {detectMutation.isPending ? "Поиск..." : "Обнаружить"}
            </Button>
          </div>

          <div className="flex border-b mt-2">
            {(["reminders", "all"] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  tab === t
                    ? "border-primary text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                {t === "reminders" ? `Ближайшие (${reminderItems.length})` : `Все (${activeItems.length})`}
              </button>
            ))}
          </div>
        </CardHeader>

        <CardContent>
          {detectMutation.isSuccess && (
            <p className="text-sm text-muted-foreground mb-4">{detectMutation.data?.message}</p>
          )}
          {detectMutation.isError && (
            <p className="text-sm text-destructive mb-4">{String(detectMutation.error)}</p>
          )}

          {isLoading && !data ? (
            <p className="text-muted-foreground">Загрузка...</p>
          ) : (tab === "reminders" ? reminderItems : activeItems).length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              {tab === "reminders" ? (
                <p>Нет платежей в ближайшие 14 дней.</p>
              ) : (
                <>
                  <p>Нет активных регулярных платежей.</p>
                  <p className="text-sm mt-1">
                    Импортируйте CSV с повторяющимися платежами и нажмите «Обнаружить».
                  </p>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-2">
              {(tab === "reminders" ? reminderItems : activeItems).map((r) => (
                <div
                  key={r.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-3 border-b last:border-0"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium">{r.name}</span>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                          r.is_confirmed
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                        }`}
                      >
                        {r.is_confirmed ? "подтверждено" : "ожидает"}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      {formatDate(r.next_run_date)} · {r.recurrence_rule}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span
                      className={`font-medium ${
                        r.direction === "out" ? "text-red-600" : "text-green-600"
                      }`}
                    >
                      {r.direction === "out" ? "−" : "+"}
                      {formatMoney(Math.abs(r.amount), r.currency)}
                    </span>
                    {!r.is_confirmed && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-1"
                        onClick={() => confirmMutation.mutate({ id: r.id, is_confirmed: true })}
                        disabled={confirmMutation.isPending}
                      >
                        <CheckCircle className="h-3.5 w-3.5" />
                        Подтвердить
                      </Button>
                    )}
                    {r.is_confirmed && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-muted-foreground text-xs"
                        onClick={() => confirmMutation.mutate({ id: r.id, is_confirmed: false })}
                        disabled={confirmMutation.isPending}
                      >
                        Отменить
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

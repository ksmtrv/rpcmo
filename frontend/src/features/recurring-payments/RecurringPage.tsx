import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
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
  is_confirmed: boolean
}

export function RecurringPage() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ["recurring"],
    queryFn: () => api.get<RecurringItem[]>("/recurring"),
  })

  const detectMutation = useMutation({
    mutationFn: () => api.post<{ detected: number; message: string }>("/recurring/detect"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recurring"] })
      queryClient.invalidateQueries({ queryKey: ["forecast"] })
    },
  })

  if (isLoading && !data) return <div className="p-8">Загрузка...</div>

  const items = data ?? []

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Регулярные платежи</CardTitle>
            <p className="text-muted-foreground text-sm">
              Подтверждённые регулярные операции учитываются в прогнозе
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => detectMutation.mutate()}
            disabled={detectMutation.isPending}
          >
            {detectMutation.isPending ? "Поиск..." : "Обнаружить"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {detectMutation.isSuccess && (
          <p className="text-sm text-muted-foreground mb-4">{detectMutation.data?.message}</p>
        )}
        {detectMutation.isError && (
          <p className="text-sm text-destructive mb-4">{String(detectMutation.error)}</p>
        )}
        {items.length === 0 ? (
          <p className="text-muted-foreground">Нет регулярных платежей. Импортируйте CSV с повторяющимися платежами и нажмите «Обнаружить».</p>
        ) : (
          <div className="space-y-2">
            {items.map((r) => (
              <div
                key={r.id}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div>
                  <span className="font-medium">{r.name}</span>
                  <span className="text-muted-foreground text-sm ml-2">
                    {formatDate(r.next_run_date)} • {r.is_confirmed ? "подтверждено" : "ожидает"}
                  </span>
                </div>
                <span className={r.direction === "out" ? "text-red-600" : "text-green-600"}>
                  {r.direction === "out" ? "-" : "+"}
                  {formatMoney(Math.abs(r.amount), r.currency)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

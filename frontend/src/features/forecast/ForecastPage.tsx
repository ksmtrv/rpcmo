import { useQuery } from "@tanstack/react-query"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { formatMoney } from "@/shared/lib/format"
import { forecastApi } from "@/shared/api/forecast"

export function ForecastPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["forecast"],
    queryFn: () => forecastApi.get(14),
  })

  if (isLoading && !data) return <div className="p-8">Загрузка...</div>

  const items = data?.items ?? []
  const chartData = items.map((i) => ({
    date: i.date.slice(5),
    balance: i.closing_balance,
    inflow: i.inflow_amount,
    outflow: i.outflow_amount,
  }))
  const balances = chartData.map((d) => d.balance).filter((b) => b != null && !Number.isNaN(b))
  const minBal = balances.length ? Math.min(...balances) : 0
  const maxBal = balances.length ? Math.max(...balances) : 0
  const padding = Math.max((maxBal - minBal) * 0.1, 1000)
  const yDomain: [number, number] = balances.length ? [minBal - padding, maxBal + padding] : [0, 1]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Прогноз остатка на 14 дней</CardTitle>
          <p className="text-muted-foreground text-sm">
            Баланс: {data ? formatMoney(data.base_balance) : "—"} {data?.currency ?? "RUB"}
            {data?.ml_enabled && (
              <span className="ml-2 rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                ML
              </span>
            )}
          </p>
        </CardHeader>
        <CardContent>
          {data?.warnings && data.warnings.length > 0 && (
            <div className="mb-4 p-3 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400 text-sm">
              {data.warnings.map((w, i) => (
                <p key={i}>{w}</p>
              ))}
            </div>
          )}
          <div className="h-[300px] min-h-[200px] w-full">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--muted-foreground) / 0.3)" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis
                    tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                    domain={yDomain}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value: number) => formatMoney(value)}
                    labelFormatter={(label) => `Дата: ${label}`}
                    contentStyle={{ backgroundColor: "hsl(var(--background))", border: "1px solid hsl(var(--border))" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="balance"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.3}
                    strokeWidth={2}
                    baseValue={0}
                    dot={{ fill: "#3b82f6", r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
                Нет данных для графика
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Подневная разбивка</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {items.map((i) => (
              <div
                key={i.date}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div>
                  <span className="font-medium">{i.date}</span>
                  {i.explanations.length > 0 && (
                    <div className="text-xs text-muted-foreground mt-1">
                      {i.explanations.map((e, j) => (
                        <span key={j}>
                          {e.title}: {formatMoney(e.amount)}{" "}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <span>{formatMoney(i.closing_balance)}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

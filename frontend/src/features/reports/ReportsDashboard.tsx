import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { formatMoney } from "@/shared/lib/format"
import { reportsApi } from "@/shared/api/reports"
import { transactionsApi } from "@/shared/api/transactions"
import { loadCategoriesForOffline } from "@/shared/offline/dataLoad"
import { useOnlineStatus } from "@/shared/offline/hooks"

export function ReportsDashboard() {
  const queryClient = useQueryClient()
  const online = useOnlineStatus()
  const { data: cashflow } = useQuery({
    queryKey: ["reports", "cashflow"],
    queryFn: () => reportsApi.cashflow(),
  })

  const { data: categories } = useQuery({
    queryKey: ["reports", "categories"],
    queryFn: () => reportsApi.categories(),
  })

  const { data: tax } = useQuery({
    queryKey: ["reports", "tax"],
    queryFn: () => reportsApi.taxEstimate(),
  })

  const { data: catList } = useQuery({
    queryKey: ["categories"],
    queryFn: loadCategoriesForOffline,
  })

  const autoCategorizeMutation = useMutation({
    mutationFn: transactionsApi.autoCategorize,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] })
      queryClient.invalidateQueries({ queryKey: ["categories"] })
      queryClient.invalidateQueries({ queryKey: ["transactions"] })
    },
  })

  const catMap = new Map((catList ?? []).map((c) => [c.id, c.name]))
  const catChartData = categories
    ? Object.entries(categories.by_category).map(([id, v]) => ({
        name: id === "uncategorized" ? "Без категории" : (catMap.get(id) ?? id),
        расход: v.outflow,
        доход: v.inflow,
      }))
    : []

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Доходы</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold text-green-600">
              {cashflow ? formatMoney(cashflow.total_inflow) : "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Расходы</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold text-red-600">
              {cashflow ? formatMoney(cashflow.total_outflow) : "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Итого</CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-semibold ${(cashflow?.net ?? 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
              {cashflow ? formatMoney(cashflow.net) : "—"}
            </p>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>По категориям</CardTitle>
              <p className="text-muted-foreground text-sm">
                {cashflow?.date_from} — {cashflow?.date_to}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => autoCategorizeMutation.mutate()}
              disabled={autoCategorizeMutation.isPending || !online}
              title={!online ? "Нужна сеть" : undefined}
            >
              {autoCategorizeMutation.isPending ? "..." : "Авто-категоризация"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={catChartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(value: number) => formatMoney(value)} />
                <Legend />
                <Bar dataKey="расход" fill="hsl(0 70% 50%)" />
                <Bar dataKey="доход" fill="hsl(140 70% 40%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Налоговая оценка</CardTitle>
          <p className="text-muted-foreground text-sm">{tax?.disclaimer}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><span className="text-muted-foreground">Доход:</span> {tax ? formatMoney(tax.income) : "—"}</p>
            <p><span className="text-muted-foreground">Ставка:</span> {tax ? `${(tax.rate * 100).toFixed(0)}%` : "—"}</p>
            <p><span className="text-muted-foreground">Оценка налога:</span> {tax ? formatMoney(tax.estimated_tax) : "—"}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

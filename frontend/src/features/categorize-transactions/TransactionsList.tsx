import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { formatMoney, formatDate } from "@/shared/lib/format"
import { transactionsApi } from "@/shared/api/transactions"
import { categoriesApi } from "@/shared/api/categories"

export function TransactionsList() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const page = Number(searchParams.get("page") || 1)
  const [editingCategory, setEditingCategory] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ["transactions", page],
    queryFn: () => transactionsApi.list({ page, size: 50 }),
  })

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: categoriesApi.list,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, categoryId }: { id: string; categoryId: string | null }) =>
      transactionsApi.update(id, categoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] })
      setEditingCategory(null)
    },
  })

  if (isLoading && !data) return <div className="p-8">Загрузка...</div>

  const items = data?.items ?? []
  const catMap = new Map((categories ?? []).map((c) => [c.id, c]))

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Операции</CardTitle>
        <Button variant="outline" onClick={() => navigate("/import")}>
          Импорт
        </Button>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Дата</th>
                <th className="text-left py-2">Описание</th>
                <th className="text-left py-2">Контрагент</th>
                <th className="text-right py-2">Сумма</th>
                <th className="text-left py-2">Категория</th>
              </tr>
            </thead>
            <tbody>
              {items.map((t) => (
                <tr key={t.id} className="border-b hover:bg-muted/50">
                  <td className="py-2">{formatDate(t.operation_date)}</td>
                  <td className="py-2 max-w-[200px] truncate">{t.description}</td>
                  <td className="py-2">{t.counterparty || "—"}</td>
                  <td
                    className={`py-2 text-right font-medium ${
                      t.direction === "in" ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {t.direction === "in" ? "+" : "-"}
                    {formatMoney(Math.abs(t.amount))}
                  </td>
                  <td className="py-2">
                    {editingCategory === t.id ? (
                      <select
                        value={t.category_id ?? ""}
                        onChange={(e) => {
                          const v = e.target.value || null
                          updateMutation.mutate({ id: t.id, categoryId: v })
                        }}
                        className="rounded border px-2 py-1 bg-background"
                        autoFocus
                      >
                        <option value="">—</option>
                        {(categories ?? []).map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setEditingCategory(t.id)}
                        className="text-left hover:underline"
                      >
                        {t.category_id ? catMap.get(t.category_id)?.name ?? "—" : "—"}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data && data.pages > 1 && (
          <div className="mt-4 flex gap-2">
            {Array.from({ length: data.pages }, (_, i) => i + 1).map((p) => (
              <Button
                key={p}
                variant={p === page ? "default" : "outline"}
                size="sm"
                onClick={() => navigate(`/transactions?page=${p}`)}
              >
                {p}
              </Button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

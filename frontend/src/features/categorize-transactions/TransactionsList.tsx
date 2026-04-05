import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Search, X, ChevronLeft, ChevronRight, Sparkles } from "lucide-react"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { formatMoney, formatDate } from "@/shared/lib/format"
import { loadCategoriesForOffline, loadTransactionsPageMerged } from "@/shared/offline/dataLoad"
import { patchTransactionCategoryOrQueue } from "@/shared/offline/sync"
import { transactionsApi } from "@/shared/api/transactions"

export function TransactionsList() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const page = Number(searchParams.get("page") || 1)
  const [editingCategory, setEditingCategory] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [dirFilter, setDirFilter] = useState<"" | "in" | "out">("")
  const [catFilter, setCatFilter] = useState<string>("")
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ["transactions", page],
    queryFn: () => loadTransactionsPageMerged(page, 50),
  })

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: loadCategoriesForOffline,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, categoryId }: { id: string; categoryId: string | null }) =>
      patchTransactionCategoryOrQueue(id, categoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] })
      setEditingCategory(null)
    },
  })

  const autoCategorizeMutation = useMutation({
    mutationFn: transactionsApi.autoCategorize,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] })
      queryClient.invalidateQueries({ queryKey: ["rules", "suggestions"] })
    },
  })

  const catMap = new Map((categories ?? []).map((c) => [c.id, c]))

  const allItems = data?.items ?? []
  const items = allItems.filter((t) => {
    if (dirFilter && t.direction !== dirFilter) return false
    if (catFilter === "__none__" && t.category_id !== null) return false
    if (catFilter && catFilter !== "__none__" && t.category_id !== catFilter) return false
    if (search) {
      const q = search.toLowerCase()
      const inDesc = (t.description ?? "").toLowerCase().includes(q)
      const inCp = (t.counterparty ?? "").toLowerCase().includes(q)
      if (!inDesc && !inCp) return false
    }
    return true
  })

  const uncategorizedCount = allItems.filter((t) => !t.category_id).length

  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <CardTitle>Операции</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => autoCategorizeMutation.mutate()}
              disabled={autoCategorizeMutation.isPending}
              className="gap-2"
            >
              <Sparkles className="h-3.5 w-3.5" />
              {autoCategorizeMutation.isPending ? "..." : "Авто-категоризация"}
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate("/import")}>
              Импорт
            </Button>
          </div>
        </div>

        {autoCategorizeMutation.isSuccess && (
          <p className="text-sm text-green-700 dark:text-green-400">
            Категоризировано: {autoCategorizeMutation.data.updated} из {autoCategorizeMutation.data.total_uncategorized}
          </p>
        )}
        {autoCategorizeMutation.isError && (
          <p className="text-sm text-destructive">{String(autoCategorizeMutation.error)}</p>
        )}

        <div className="flex flex-wrap gap-2">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Поиск по назначению или контрагенту..."
              className="pl-8"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <select
            value={dirFilter}
            onChange={(e) => setDirFilter(e.target.value as "" | "in" | "out")}
            className="rounded border px-3 py-2 bg-background text-sm"
          >
            <option value="">Все направления</option>
            <option value="in">Доходы</option>
            <option value="out">Расходы</option>
          </select>
          <select
            value={catFilter}
            onChange={(e) => setCatFilter(e.target.value)}
            className="rounded border px-3 py-2 bg-background text-sm"
          >
            <option value="">Все категории</option>
            <option value="__none__">Без категории {uncategorizedCount > 0 ? `(${uncategorizedCount})` : ""}</option>
            {(categories ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </CardHeader>

      <CardContent>
        {isLoading && !data ? (
          <p className="text-muted-foreground py-8 text-center">Загрузка...</p>
        ) : items.length === 0 ? (
          <p className="text-muted-foreground py-8 text-center">
            {search || dirFilter || catFilter ? "Нет операций по выбранным фильтрам." : "Нет операций. Импортируйте CSV-выписку."}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="text-left py-2 pr-3 font-medium">Дата</th>
                  <th className="text-left py-2 pr-3 font-medium">Описание</th>
                  <th className="text-left py-2 pr-3 font-medium hidden md:table-cell">Контрагент</th>
                  <th className="text-right py-2 pr-3 font-medium">Сумма</th>
                  <th className="text-left py-2 font-medium">Категория</th>
                </tr>
              </thead>
              <tbody>
                {items.map((t) => (
                  <tr key={t.id} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="py-2 pr-3 whitespace-nowrap text-muted-foreground">{formatDate(t.operation_date)}</td>
                    <td className="py-2 pr-3">
                      <span className="line-clamp-1 max-w-[180px] block" title={t.description}>
                        {t.description || "—"}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-muted-foreground hidden md:table-cell">
                      {t.counterparty || "—"}
                    </td>
                    <td className="py-2 pr-3 text-right font-medium whitespace-nowrap">
                      <span className={t.direction === "in" ? "text-green-600" : "text-red-600"}>
                        {t.direction === "in" ? "+" : "−"}
                        {formatMoney(Math.abs(t.amount))}
                      </span>
                    </td>
                    <td className="py-2">
                      {editingCategory === t.id ? (
                        <div className="flex items-center gap-1">
                          <select
                            value={t.category_id ?? ""}
                            onChange={(e) => {
                              const v = e.target.value || null
                              updateMutation.mutate({ id: t.id, categoryId: v })
                            }}
                            className="rounded border px-2 py-1 bg-background text-sm"
                            autoFocus
                          >
                            <option value="">—</option>
                            {(categories ?? []).map((c) => (
                              <option key={c.id} value={c.id}>
                                {c.name}
                              </option>
                            ))}
                          </select>
                          <button
                            type="button"
                            onClick={() => setEditingCategory(null)}
                            className="text-muted-foreground hover:text-foreground"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setEditingCategory(t.id)}
                          className={`text-left hover:underline text-sm ${
                            t.category_id ? "" : "text-muted-foreground italic"
                          }`}
                        >
                          {t.category_id
                            ? catMap.get(t.category_id)?.name ?? "—"
                            : "нажмите для выбора"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data && data.pages > 1 && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Страница {page} из {data.pages} · {data.total} операций
            </p>
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => navigate(`/transactions?page=${page - 1}`)}
                className="gap-1"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              {Array.from({ length: Math.min(data.pages, 7) }, (_, i) => {
                const p = page <= 4 ? i + 1 : i + page - 3
                if (p > data.pages) return null
                return (
                  <Button
                    key={p}
                    variant={p === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => navigate(`/transactions?page=${p}`)}
                  >
                    {p}
                  </Button>
                )
              })}
              <Button
                variant="outline"
                size="sm"
                disabled={page >= data.pages}
                onClick={() => navigate(`/transactions?page=${page + 1}`)}
                className="gap-1"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

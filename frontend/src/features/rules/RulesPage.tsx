import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { CheckCircle, XCircle, Trash2, Plus, Lightbulb, ChevronDown, ChevronUp } from "lucide-react"
import { rulesApi, type Rule } from "@/shared/api/rules"
import { loadCategoriesForOffline } from "@/shared/offline/dataLoad"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { Label } from "@/shared/ui/label"

const schema = z.object({
  name: z.string().min(1, "Укажите название правила"),
  priority: z.coerce.number().int().default(0),
  category_id: z.string().min(1, "Выберите категорию"),
  direction: z.enum(["", "in", "out"]).default(""),
  keywords_any: z.string().default(""),
  counterparty_contains: z.string().default(""),
  description_contains: z.string().default(""),
})

type FormData = z.infer<typeof schema>

function conditionSummary(c: Rule["conditions_json"]): string {
  const parts: string[] = []
  if (c.keywords_any?.length) parts.push(`слова: ${c.keywords_any.join(", ")}`)
  if (c.description_contains) parts.push(`назначение: «${c.description_contains}»`)
  if (c.counterparty_contains) parts.push(`контрагент: «${c.counterparty_contains}»`)
  if (c.direction) parts.push(c.direction === "in" ? "доходы" : "расходы")
  return parts.join(" · ") || "—"
}

export function RulesPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)

  const { data: rules, isLoading: rulesLoading } = useQuery({
    queryKey: ["rules"],
    queryFn: rulesApi.list,
  })

  const { data: suggestions, isLoading: suggestionsLoading } = useQuery({
    queryKey: ["rules", "suggestions"],
    queryFn: rulesApi.listSuggestions,
  })

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: loadCategoriesForOffline,
  })

  const catMap = new Map((categories ?? []).map((c) => [c.id, c]))

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", priority: 0, category_id: "", direction: "", keywords_any: "", counterparty_contains: "", description_contains: "" },
  })

  const createMutation = useMutation({
    mutationFn: (data: FormData) => {
      const conditions: Rule["conditions_json"] = {}
      const kws = data.keywords_any.split(",").map((s) => s.trim()).filter(Boolean)
      if (kws.length) conditions.keywords_any = kws
      if (data.description_contains.trim()) conditions.description_contains = data.description_contains.trim()
      if (data.counterparty_contains.trim()) conditions.counterparty_contains = data.counterparty_contains.trim()
      if (data.direction) conditions.direction = data.direction as "in" | "out"
      return rulesApi.create({ name: data.name, priority: data.priority, category_id: data.category_id, conditions_json: conditions })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] })
      form.reset()
      setShowForm(false)
    },
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      rulesApi.update(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => rulesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  })

  const acceptMutation = useMutation({
    mutationFn: (id: string) => rulesApi.acceptSuggestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rules"] })
      queryClient.invalidateQueries({ queryKey: ["rules", "suggestions"] })
    },
  })

  const dismissMutation = useMutation({
    mutationFn: (id: string) => rulesApi.dismissSuggestion(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules", "suggestions"] }),
  })

  const pendingSuggestions = (suggestions ?? []).filter((s) => s.status === "pending")

  return (
    <div className="space-y-6">
      {pendingSuggestions.length > 0 && (
        <Card className="border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-800 dark:text-amber-300">
              <Lightbulb className="h-5 w-5" />
              Предложения правил ({pendingSuggestions.length})
            </CardTitle>
            <p className="text-sm text-amber-700 dark:text-amber-400">
              После ручной категоризации система предложила создать правила — примите нужные.
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            {suggestionsLoading ? (
              <p className="text-sm text-muted-foreground">Загрузка...</p>
            ) : (
              pendingSuggestions.map((s) => {
                const cat = catMap.get(s.suggested_category_id)
                return (
                  <div
                    key={s.id}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-white dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800"
                  >
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate">«{s.source_pattern}»</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        → <span className="font-medium">{cat?.name ?? s.suggested_category_id}</span>
                        {" · "}охват: {s.coverage_count} {pluralTx(s.coverage_count)}
                      </p>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Button
                        size="sm"
                        onClick={() => acceptMutation.mutate(s.id)}
                        disabled={acceptMutation.isPending || dismissMutation.isPending}
                        className="gap-1"
                      >
                        <CheckCircle className="h-3.5 w-3.5" />
                        Принять
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => dismissMutation.mutate(s.id)}
                        disabled={acceptMutation.isPending || dismissMutation.isPending}
                        className="gap-1"
                      >
                        <XCircle className="h-3.5 w-3.5" />
                        Отклонить
                      </Button>
                    </div>
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Правила категоризации</CardTitle>
              <p className="text-muted-foreground text-sm mt-1">
                Правила применяются при авто-категоризации: совпадение ключевых слов, назначения или контрагента.
              </p>
            </div>
            <Button onClick={() => setShowForm((v) => !v)} variant="outline" className="gap-2 shrink-0">
              {showForm ? <ChevronUp className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {showForm ? "Свернуть" : "Добавить правило"}
            </Button>
          </div>
        </CardHeader>

        {showForm && (
          <CardContent className="border-t pt-4">
            <form
              onSubmit={form.handleSubmit((data) => createMutation.mutate(data))}
              className="space-y-4 max-w-lg"
            >
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="r-name">Название правила</Label>
                  <Input id="r-name" placeholder="Например: Supermarket" {...form.register("name")} />
                  {form.formState.errors.name && (
                    <p className="text-destructive text-xs mt-1">{form.formState.errors.name.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="r-cat">Категория</Label>
                  <select
                    id="r-cat"
                    {...form.register("category_id")}
                    className="w-full rounded border px-3 py-2 bg-background text-sm"
                  >
                    <option value="">— выберите —</option>
                    {(categories ?? []).map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                  {form.formState.errors.category_id && (
                    <p className="text-destructive text-xs mt-1">{form.formState.errors.category_id.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="r-dir">Направление</Label>
                  <select
                    id="r-dir"
                    {...form.register("direction")}
                    className="w-full rounded border px-3 py-2 bg-background text-sm"
                  >
                    <option value="">Любое</option>
                    <option value="in">Доходы</option>
                    <option value="out">Расходы</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <Label htmlFor="r-kw">Ключевые слова (через запятую)</Label>
                  <Input
                    id="r-kw"
                    placeholder="магазин, market, супермаркет"
                    {...form.register("keywords_any")}
                  />
                  <p className="text-muted-foreground text-xs mt-1">
                    Подойдёт, если любое из слов встречается в назначении или контрагенте
                  </p>
                </div>
                <div>
                  <Label htmlFor="r-desc">Назначение содержит</Label>
                  <Input id="r-desc" placeholder="оплата услуг" {...form.register("description_contains")} />
                </div>
                <div>
                  <Label htmlFor="r-cp">Контрагент содержит</Label>
                  <Input id="r-cp" placeholder="ООО Ромашка" {...form.register("counterparty_contains")} />
                </div>
                <div>
                  <Label htmlFor="r-prio">Приоритет</Label>
                  <Input id="r-prio" type="number" {...form.register("priority")} />
                  <p className="text-muted-foreground text-xs mt-1">Выше — применяется раньше</p>
                </div>
              </div>

              {createMutation.isError && (
                <p className="text-destructive text-sm">{String(createMutation.error)}</p>
              )}

              <div className="flex gap-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Создание..." : "Создать правило"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => { setShowForm(false); form.reset() }}
                >
                  Отмена
                </Button>
              </div>
            </form>
          </CardContent>
        )}

        <CardContent className={showForm ? "border-t" : ""}>
          {rulesLoading ? (
            <p className="text-muted-foreground">Загрузка...</p>
          ) : !rules?.length ? (
            <div className="py-8 text-center text-muted-foreground">
              <p>Правил пока нет.</p>
              <p className="text-sm mt-1">
                Создайте первое правило или категоризируйте операции вручную — система предложит правила автоматически.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {rules.map((r) => {
                const cat = catMap.get(r.category_id)
                return (
                  <div
                    key={r.id}
                    className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg border transition-colors ${
                      r.is_active ? "bg-card" : "bg-muted/30 opacity-60"
                    }`}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{r.name}</span>
                        {!r.is_active && (
                          <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                            выключено
                          </span>
                        )}
                        <span className="text-xs text-muted-foreground">приоритет: {r.priority}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {conditionSummary(r.conditions_json)}
                        {" → "}
                        <span className="font-medium text-foreground">{cat?.name ?? r.category_id}</span>
                      </p>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleMutation.mutate({ id: r.id, is_active: !r.is_active })}
                        disabled={toggleMutation.isPending || editId === r.id}
                      >
                        {r.is_active ? "Выключить" : "Включить"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-destructive hover:text-destructive"
                        onClick={() => {
                          if (window.confirm(`Удалить правило «${r.name}»?`)) {
                            deleteMutation.mutate(r.id)
                          }
                        }}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function pluralTx(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return "операция"
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "операции"
  return "операций"
}

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { Label } from "@/shared/ui/label"
import { categoriesApi } from "@/shared/api/categories"
import { loadCategoriesForOffline } from "@/shared/offline/dataLoad"
import { useOnlineStatus } from "@/shared/offline/hooks"
import { cacheKeyCategories, deleteReadCacheKey } from "@/shared/offline/readCache"
import type { Category } from "@/shared/api/categories"

const schema = z.object({
  name: z.string().min(1),
  type: z.enum(["income", "expense", "transfer", "tax"]),
  color: z.string().optional(),
})

type FormData = z.infer<typeof schema>

export function CategoryPage() {
  const queryClient = useQueryClient()
  const online = useOnlineStatus()
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: loadCategoriesForOffline,
    staleTime: 0,
  })

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", type: "expense" },
  })

  const createMutation = useMutation({
    mutationFn: categoriesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] })
      form.reset()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: categoriesApi.delete,
    onMutate: async (removedId) => {
      setDeleteError(null)
      await queryClient.cancelQueries({ queryKey: ["categories"] })
      const prev = queryClient.getQueryData<Category[]>(["categories"])
      if (prev) {
        queryClient.setQueryData<Category[]>(
          ["categories"],
          prev.filter((c) => c.id !== removedId),
        )
      }
      await deleteReadCacheKey(cacheKeyCategories)
      return { prev }
    },
    onError: (err, _id, ctx) => {
      if (ctx?.prev) queryClient.setQueryData(["categories"], ctx.prev)
      setDeleteError(err instanceof Error ? err.message : "Не удалось удалить категорию")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] })
    },
  })

  const onSubmit = (data: FormData) => {
    createMutation.mutate(data)
  }

  if (isLoading && !categories) return <div className="p-8">Загрузка...</div>

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Новая категория</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="name">Название</Label>
              <Input id="name" {...form.register("name")} />
              {form.formState.errors.name && (
                <p className="text-destructive text-sm">{form.formState.errors.name.message}</p>
              )}
            </div>
            <div>
              <Label htmlFor="type">Тип</Label>
              <select
                id="type"
                {...form.register("type")}
                className="w-full rounded border px-3 py-2 bg-background"
              >
                <option value="income">Доход</option>
                <option value="expense">Расход</option>
                <option value="transfer">Перевод</option>
                <option value="tax">Налог</option>
              </select>
            </div>
            <Button type="submit" disabled={createMutation.isPending || !online}>
              Создать
            </Button>
            {!online && (
              <p className="text-muted-foreground text-sm">Создание категорий доступно только онлайн.</p>
            )}
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Категории</CardTitle>
        </CardHeader>
        <CardContent>
          {deleteError && (
            <p className="text-destructive text-sm mb-3" role="alert">
              {deleteError}
            </p>
          )}
          <div className="space-y-2">
            {(categories ?? []).map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between py-2 border-b last:border-0 gap-2"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {c.color && (
                    <div
                      className="w-4 h-4 rounded-full shrink-0"
                      style={{ backgroundColor: c.color }}
                    />
                  )}
                  <span className="truncate">{c.name}</span>
                  <span className="text-muted-foreground text-sm shrink-0">({c.type})</span>
                </div>
                {!c.is_system && online && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="shrink-0 text-destructive hover:text-destructive"
                    disabled={deleteMutation.isPending}
                    onClick={() => {
                      if (!window.confirm(`Удалить категорию «${c.name}»? У операций эта категория будет сброшена.`)) {
                        return
                      }
                      deleteMutation.mutate(c.id)
                    }}
                  >
                    Удалить
                  </Button>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

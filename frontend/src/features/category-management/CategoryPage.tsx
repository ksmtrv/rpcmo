import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/shared/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Input } from "@/shared/ui/input"
import { Label } from "@/shared/ui/label"
import { categoriesApi } from "@/shared/api/categories"

const schema = z.object({
  name: z.string().min(1),
  type: z.enum(["income", "expense", "transfer", "tax"]),
  color: z.string().optional(),
})

type FormData = z.infer<typeof schema>

export function CategoryPage() {
  const queryClient = useQueryClient()

  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: categoriesApi.list,
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
            <Button type="submit" disabled={createMutation.isPending}>
              Создать
            </Button>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Категории</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {(categories ?? []).map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div className="flex items-center gap-2">
                  {c.color && (
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: c.color }}
                    />
                  )}
                  <span>{c.name}</span>
                  <span className="text-muted-foreground text-sm">({c.type})</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

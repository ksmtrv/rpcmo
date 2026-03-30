import { api } from "./client"

export interface Category {
  id: string
  name: string
  type: string
  color: string | null
  is_system: boolean
}

export const categoriesApi = {
  list: () => api.get<Category[]>("/categories"),
  create: (data: { name: string; type: string; color?: string }) =>
    api.post<Category>("/categories", data),
  update: (id: string, data: { name?: string; color?: string }) =>
    api.patch<Category>(`/categories/${id}`, data),
}

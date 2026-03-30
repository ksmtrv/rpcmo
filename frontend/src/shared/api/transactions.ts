import { api } from "./client"

export interface Transaction {
  id: string
  account_id: string
  operation_date: string
  amount: number
  currency: string
  direction: string
  description: string
  counterparty: string | null
  category_id: string | null
  is_manual: boolean
  is_duplicate: boolean
}

export interface TransactionsPage {
  items: Transaction[]
  total: number
  page: number
  size: number
  pages: number
}

export const transactionsApi = {
  list: (params?: { account_id?: string; date_from?: string; date_to?: string; page?: number; size?: number }) => {
    const search = new URLSearchParams()
    if (params?.account_id) search.set("account_id", params.account_id)
    if (params?.date_from) search.set("date_from", params.date_from)
    if (params?.date_to) search.set("date_to", params.date_to)
    if (params?.page) search.set("page", String(params.page))
    if (params?.size) search.set("size", String(params.size))
    const q = search.toString()
    return api.get<TransactionsPage>(`/transactions${q ? `?${q}` : ""}`)
  },
  update: (id: string, categoryId: string | null) =>
    api.patch<Transaction>(`/transactions/${id}`, { category_id: categoryId }),
  bulkCategorize: (transactionIds: string[], categoryId: string | null) =>
    api.post<{ updated: number }>("/transactions/bulk-categorize", { transaction_ids: transactionIds, category_id: categoryId }),
  autoCategorize: () =>
    api.post<{ updated: number; total_uncategorized: number }>("/transactions/auto-categorize"),
}

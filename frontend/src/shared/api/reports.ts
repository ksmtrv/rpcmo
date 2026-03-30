import { api } from "./client"

export interface CashflowReport {
  date_from: string
  date_to: string
  total_inflow: number
  total_outflow: number
  net: number
  by_date: { date: string; net: number }[]
}

export interface CategoriesReport {
  date_from: string
  date_to: string
  by_category: Record<string, { inflow: number; outflow: number }>
}

export interface TaxEstimateReport {
  disclaimer: string
  date_from: string
  date_to: string
  income: number
  rate: number
  estimated_tax: number
}

export const reportsApi = {
  cashflow: (params?: { date_from?: string; date_to?: string }) => {
    const search = new URLSearchParams()
    if (params?.date_from) search.set("date_from", params.date_from)
    if (params?.date_to) search.set("date_to", params.date_to)
    const q = search.toString()
    return api.get<CashflowReport>(`/reports/cashflow${q ? `?${q}` : ""}`)
  },
  categories: (params?: { date_from?: string; date_to?: string }) => {
    const search = new URLSearchParams()
    if (params?.date_from) search.set("date_from", params.date_from)
    if (params?.date_to) search.set("date_to", params.date_to)
    const q = search.toString()
    return api.get<CategoriesReport>(`/reports/categories${q ? `?${q}` : ""}`)
  },
  taxEstimate: (params?: { date_from?: string; date_to?: string }) => {
    const search = new URLSearchParams()
    if (params?.date_from) search.set("date_from", params.date_from)
    if (params?.date_to) search.set("date_to", params.date_to)
    const q = search.toString()
    return api.get<TaxEstimateReport>(`/reports/tax-estimate${q ? `?${q}` : ""}`)
  },
}

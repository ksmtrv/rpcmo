import { api } from "./client"

export interface ForecastItem {
  date: string
  opening_balance: number
  inflow_amount: number
  outflow_amount: number
  closing_balance: number
  explanations: { type: string; title: string; amount: number }[]
}

export interface ForecastResponse {
  start_date: string
  end_date: string
  base_balance: number
  currency: string
  items: ForecastItem[]
  warnings: string[]
  ml_enabled?: boolean
}

export const forecastApi = {
  get: (days = 14) => api.get<ForecastResponse>(`/forecast?days=${days}`),
  recalculate: (days = 14) => api.post<ForecastResponse>(`/forecast/recalculate?days=${days}`),
}

import { api } from "./client"

export interface Rule {
  id: string
  name: string
  priority: number
  conditions_json: {
    keywords_any?: string[]
    description_contains?: string
    normalized_description_equals?: string
    counterparty_contains?: string
    direction?: "in" | "out"
  }
  category_id: string
  is_active: boolean
}

export interface RuleSuggestion {
  id: string
  source_pattern: string
  suggested_conditions_json: Record<string, unknown>
  suggested_category_id: string
  coverage_count: number
  status: string
}

export interface RuleCreate {
  name: string
  priority?: number
  conditions_json: Rule["conditions_json"]
  category_id: string
}

export interface RuleUpdate {
  name?: string
  priority?: number
  conditions_json?: Rule["conditions_json"]
  category_id?: string
  is_active?: boolean
}

export const rulesApi = {
  list: () => api.get<Rule[]>("/rules"),
  create: (body: RuleCreate) => api.post<Rule>("/rules", body),
  update: (id: string, body: RuleUpdate) => api.patch<Rule>(`/rules/${id}`, body),
  delete: (id: string) => api.delete<void>(`/rules/${id}`),

  listSuggestions: () => api.get<RuleSuggestion[]>("/rules/suggestions"),
  acceptSuggestion: (id: string) => api.post<Rule>(`/rules/suggestions/${id}/accept`),
  dismissSuggestion: (id: string) => api.post<void>(`/rules/suggestions/${id}/dismiss`),
}

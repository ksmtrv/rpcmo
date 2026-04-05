import { useQuery } from "@tanstack/react-query"
import { Routes, Route, Link, useLocation } from "react-router-dom"
import { Bell, TrendingUp, Upload, List, Tag, BarChart2, RefreshCw, Shield, BookOpen } from "lucide-react"
import { ImportWizard } from "@/features/import-transactions/ImportWizard"
import { TransactionsList } from "@/features/categorize-transactions/TransactionsList"
import { ForecastPage } from "@/features/forecast/ForecastPage"
import { ReportsDashboard } from "@/features/reports/ReportsDashboard"
import { RecurringPage } from "@/features/recurring-payments/RecurringPage"
import { BackupPage } from "@/features/backup-export/BackupPage"
import { CategoryPage } from "@/features/category-management/CategoryPage"
import { RulesPage } from "@/features/rules/RulesPage"
import { cn } from "@/shared/lib/cn"
import { OfflineBar } from "@/shared/ui/offline-bar"
import { api } from "@/shared/api/client"
import { formatMoney, formatDate } from "@/shared/lib/format"

const nav = [
  { path: "/", label: "Главная" },
  { path: "/import", label: "Импорт" },
  { path: "/transactions", label: "Операции" },
  { path: "/categories", label: "Категории" },
  { path: "/rules", label: "Правила" },
  { path: "/forecast", label: "Прогноз" },
  { path: "/reports", label: "Отчёты" },
  { path: "/recurring", label: "Регулярные" },
  { path: "/backup", label: "Резервная копия" },
]

function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation()
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center gap-6 overflow-x-auto">
          <Link to="/" className="font-bold text-primary shrink-0">
            Fincontrol
          </Link>
          <nav className="flex gap-1 min-w-0">
            {nav.map((n) => (
              <Link
                key={n.path}
                to={n.path}
                className={cn(
                  "px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap",
                  loc.pathname === n.path
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <OfflineBar />
      <main className="flex-1 container py-6">{children}</main>
    </div>
  )
}

interface RecurringReminder {
  id: string
  name: string
  amount: number
  currency: string
  direction: string
  next_run_date: string
}

interface CashflowSummary {
  total_inflow: number
  total_outflow: number
  net: number
  date_from: string
  date_to: string
}

interface RuleSuggestion {
  id: string
  coverage_count: number
  status: string
}

function HomePage() {
  const { data: reminders } = useQuery({
    queryKey: ["recurring", "reminders"],
    queryFn: () => api.get<RecurringReminder[]>("/recurring/reminders?within_days=7"),
  })

  const { data: cashflow } = useQuery({
    queryKey: ["reports", "cashflow"],
    queryFn: () => api.get<CashflowSummary>("/reports/cashflow"),
  })

  const { data: suggestions } = useQuery({
    queryKey: ["rules", "suggestions"],
    queryFn: () => api.get<RuleSuggestion[]>("/rules/suggestions"),
  })

  const pendingSuggestions = (suggestions ?? []).filter((s) => s.status === "pending")

  const quickLinks = [
    { path: "/import", icon: <Upload className="h-5 w-5" />, title: "Импорт выписки", desc: "Загрузите CSV-файл из банка" },
    { path: "/transactions", icon: <List className="h-5 w-5" />, title: "Операции", desc: "Просматривайте и категоризируйте" },
    { path: "/rules", icon: <BookOpen className="h-5 w-5" />, title: "Правила", desc: "Настройте авто-категоризацию" },
    { path: "/forecast", icon: <TrendingUp className="h-5 w-5" />, title: "Прогноз", desc: "Остаток на 14 дней вперёд" },
    { path: "/reports", icon: <BarChart2 className="h-5 w-5" />, title: "Отчёты", desc: "Кэшфлоу, категории, налоги" },
    { path: "/recurring", icon: <RefreshCw className="h-5 w-5" />, title: "Регулярные", desc: "Подписки и периодические платежи" },
    { path: "/backup", icon: <Shield className="h-5 w-5" />, title: "Резервная копия", desc: "Экспорт с шифрованием" },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Финансовый контроль</h1>
        <p className="text-muted-foreground mt-2">
          Учёт для самозанятых и ИП — импорт CSV, категоризация, прогноз и резервные копии.
        </p>
      </div>

      {(reminders?.length || 0) > 0 && (
        <div className="rounded-xl border border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900 p-4 space-y-3">
          <h2 className="font-semibold flex items-center gap-2 text-blue-800 dark:text-blue-300">
            <Bell className="h-4 w-4" />
            Платежи в ближайшие 7 дней
          </h2>
          <div className="space-y-1.5">
            {(reminders ?? []).map((r) => (
              <div key={r.id} className="flex items-center justify-between text-sm">
                <span>{r.name}</span>
                <span className="flex items-center gap-3">
                  <span className="text-muted-foreground">{formatDate(r.next_run_date)}</span>
                  <span className={r.direction === "out" ? "text-red-600 font-medium" : "text-green-600 font-medium"}>
                    {r.direction === "out" ? "−" : "+"}
                    {formatMoney(Math.abs(r.amount), r.currency)}
                  </span>
                </span>
              </div>
            ))}
          </div>
          <Link to="/recurring" className="text-xs text-blue-700 dark:text-blue-400 hover:underline">
            Посмотреть все регулярные →
          </Link>
        </div>
      )}

      {pendingSuggestions.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-900 p-4">
          <h2 className="font-semibold flex items-center gap-2 text-amber-800 dark:text-amber-300">
            <Tag className="h-4 w-4" />
            Предложений правил: {pendingSuggestions.length}
          </h2>
          <p className="text-sm text-amber-700 dark:text-amber-400 mt-1">
            Система обнаружила паттерны категоризации — примите или отклоните предложения.
          </p>
          <Link to="/rules" className="text-xs text-amber-700 dark:text-amber-400 hover:underline mt-2 inline-block">
            Перейти к правилам →
          </Link>
        </div>
      )}

      {cashflow && (
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border bg-card p-4 text-center">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Доходы</p>
            <p className="text-xl font-bold text-green-600 mt-1">{formatMoney(cashflow.total_inflow)}</p>
          </div>
          <div className="rounded-xl border bg-card p-4 text-center">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Расходы</p>
            <p className="text-xl font-bold text-red-600 mt-1">{formatMoney(cashflow.total_outflow)}</p>
          </div>
          <div className="rounded-xl border bg-card p-4 text-center">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Итого</p>
            <p className={`text-xl font-bold mt-1 ${cashflow.net >= 0 ? "text-green-600" : "text-red-600"}`}>
              {formatMoney(cashflow.net)}
            </p>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-3">Разделы</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {quickLinks.map((q) => (
            <Link
              key={q.path}
              to={q.path}
              className="flex items-start gap-3 p-4 rounded-xl border bg-card hover:bg-accent/50 hover:border-primary/30 transition-all group"
            >
              <span className="mt-0.5 text-muted-foreground group-hover:text-primary transition-colors">{q.icon}</span>
              <div>
                <p className="font-medium text-sm">{q.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{q.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/import" element={<ImportWizard />} />
        <Route path="/transactions" element={<TransactionsList />} />
        <Route path="/categories" element={<CategoryPage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/reports" element={<ReportsDashboard />} />
        <Route path="/recurring" element={<RecurringPage />} />
        <Route path="/backup" element={<BackupPage />} />
      </Routes>
    </Layout>
  )
}

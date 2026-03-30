import { Routes, Route, Link, useLocation } from "react-router-dom"
import { ImportWizard } from "@/features/import-transactions/ImportWizard"
import { TransactionsList } from "@/features/categorize-transactions/TransactionsList"
import { ForecastPage } from "@/features/forecast/ForecastPage"
import { ReportsDashboard } from "@/features/reports/ReportsDashboard"
import { RecurringPage } from "@/features/recurring-payments/RecurringPage"
import { BackupPage } from "@/features/backup-export/BackupPage"
import { CategoryPage } from "@/features/category-management/CategoryPage"
import { cn } from "@/shared/lib/cn"

const nav = [
  { path: "/", label: "Главная" },
  { path: "/import", label: "Импорт" },
  { path: "/transactions", label: "Операции" },
  { path: "/categories", label: "Категории" },
  { path: "/forecast", label: "Прогноз" },
  { path: "/reports", label: "Отчёты" },
  { path: "/recurring", label: "Регулярные" },
  { path: "/backup", label: "Резервная копия" },
]

function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation()
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <Link to="/" className="font-semibold mr-6">
            Fincontrol
          </Link>
          <nav className="flex gap-4">
            {nav.map((n) => (
              <Link
                key={n.path}
                to={n.path}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  loc.pathname === n.path ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 container py-6">{children}</main>
    </div>
  )
}

function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Финансовый контроль</h1>
        <p className="text-muted-foreground mt-2">
          Импортируйте выписку, категоризируйте операции, смотрите отчёты и прогноз на 14 дней.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          to="/import"
          className="block p-6 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
        >
          <h3 className="font-semibold">Импорт выписки</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Загрузите CSV и получите первый результат за 3–5 минут
          </p>
        </Link>
        <Link
          to="/transactions"
          className="block p-6 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
        >
          <h3 className="font-semibold">Операции</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Редактируйте категории и создавайте правила
          </p>
        </Link>
        <Link
          to="/forecast"
          className="block p-6 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
        >
          <h3 className="font-semibold">Прогноз</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Прогноз остатка на 14 дней с объяснением
          </p>
        </Link>
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
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/reports" element={<ReportsDashboard />} />
        <Route path="/recurring" element={<RecurringPage />} />
        <Route path="/backup" element={<BackupPage />} />
      </Routes>
    </Layout>
  )
}

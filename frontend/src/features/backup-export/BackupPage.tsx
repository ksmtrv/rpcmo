import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Button } from "@/shared/ui/button"

export function BackupPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Резервная копия и экспорт</CardTitle>
        <p className="text-muted-foreground text-sm">
          Экспорт данных по умолчанию шифруется. Вы можете сохранить данные и восстановить их позже.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <Card>
          <CardContent className="pt-6">
            <Button disabled>Экспорт (в разработке)</Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Button variant="outline" disabled>Импорт (в разработке)</Button>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  )
}

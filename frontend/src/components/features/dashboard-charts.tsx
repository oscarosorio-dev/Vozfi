import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { CategorySummary } from "@/lib/api"
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts"

export function DashboardCharts({ categories }: { categories: CategorySummary[] }) {
  if (!categories || categories.length === 0) return null

  const chartData = categories.map((item) => ({
    name: item.category,
    total: item.total,
    tipo: item.type === "income" ? "Ingreso" : "Gasto",
  }))

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Gastos e Ingresos por Categoría</CardTitle>
      </CardHeader>
      <CardContent className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
            <Tooltip formatter={(value) => [`$${Number(value).toLocaleString("es-ES")}`, "Monto"]} />
            <Bar dataKey="total" fill="#18181b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
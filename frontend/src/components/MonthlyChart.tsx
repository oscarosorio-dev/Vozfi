"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getMonthlySummary, type MonthlySummary } from "@/lib/api";

export default function MonthlyChart({ refreshKey }: { refreshKey?: number }) {
  const [data, setData] = useState<MonthlySummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMonthlySummary()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar el resumen mensual"));
  }, [refreshKey]);

  if (error) return <p className="text-red-600 text-sm">{error}</p>;
  if (!data) return <p className="text-gray-500 text-sm">Cargando resumen mensual...</p>;
  if (data.length === 0) return <p className="text-gray-500 text-sm">Sin datos suficientes para graficar aún.</p>;

  return (
    <div className="p-4 border rounded-lg">
      <p className="text-sm font-medium mb-2">Ingresos vs. gastos por mes</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="income" name="Ingresos" fill="#16a34a" radius={[4, 4, 0, 0]} />
          <Bar dataKey="expense" name="Gastos" fill="#dc2626" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
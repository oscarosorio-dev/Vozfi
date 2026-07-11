import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Transaction, deleteTransaction } from "@/lib/api"
import { Trash2 } from "lucide-react"

export function TransactionHistory({ transactions, onDeleted }: { transactions: Transaction[], onDeleted: () => void }) {
  const handleDelete = async (id: string) => {
    try {
      await deleteTransaction(id)
      onDeleted()
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Historial de Transacciones</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <table className="w-full text-sm text-left text-zinc-500 dark:text-zinc-400">
            <thead className="text-xs text-zinc-700 uppercase bg-zinc-50 dark:bg-zinc-800 dark:text-zinc-400">
              <tr>
                <th scope="col" className="px-6 py-3">Fecha</th>
                <th scope="col" className="px-6 py-3">Tipo</th>
                <th scope="col" className="px-6 py-3">Categoría</th>
                <th scope="col" className="px-6 py-3">Descripción</th>
                <th scope="col" className="px-6 py-3">Monto</th>
                <th scope="col" className="px-6 py-3">Acción</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center">No hay transacciones registradas.</td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr key={tx.id} className="bg-white border-b dark:bg-zinc-950 dark:border-zinc-800">
                    <td className="px-6 py-4 font-medium text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
                      {new Date(tx.occurred_at).toLocaleDateString("es-ES", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${tx.type === "income" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"}`}>
                        {tx.type === "income" ? "Ingreso" : "Gasto"}
                      </span>
                    </td>
                    <td className="px-6 py-4">{tx.category}</td>
                    <td className="px-6 py-4">{tx.description || "-"}</td>
                    <td className="px-6 py-4 font-bold">
                      ${tx.amount.toLocaleString("es-ES", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-6 py-4">
                      <Button variant="ghost" onClick={() => handleDelete(tx.id)} className="p-2 hover:text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
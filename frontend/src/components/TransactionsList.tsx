"use client";

import { useEffect, useState } from "react";
import { listTransactions, type Transaction } from "@/lib/api";

export default function TransactionsList({ refreshKey }: { refreshKey?: number }) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listTransactions()
      .then(setTransactions)
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar transacciones"));
  }, [refreshKey]);

  if (error) return <p className="text-red-600 text-sm">{error}</p>;
  if (transactions.length === 0) return <p className="text-gray-500 text-sm">Sin transacciones todavía.</p>;

  return (
    <ul className="divide-y border rounded-lg">
      {transactions.map((tx) => (
        <li key={tx.id} className="flex justify-between items-center p-3 text-sm">
          <div>
            <p className="font-medium">{tx.category}</p>
            {tx.description && <p className="text-gray-500 text-xs">{tx.description}</p>}
          </div>
          <span className={tx.type === "income" ? "text-green-600" : "text-red-600"}>
            {tx.type === "income" ? "+" : "-"}
            {tx.amount.toFixed(2)}
          </span>
        </li>
      ))}
    </ul>
  );
}
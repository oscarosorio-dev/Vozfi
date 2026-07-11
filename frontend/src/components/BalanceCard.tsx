"use client";

import { useEffect, useState } from "react";
import { getBalance, type Balance } from "@/lib/api";

export default function BalanceCard({ refreshKey }: { refreshKey?: number }) {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getBalance()
      .then(setBalance)
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar el balance"));
  }, [refreshKey]);

  if (error) return <p className="text-red-600 text-sm">{error}</p>;
  if (!balance) return <p className="text-gray-500 text-sm">Cargando balance...</p>;

  return (
    <div className="grid grid-cols-3 gap-4 p-4 border rounded-lg text-center">
      <div>
        <p className="text-xs text-gray-500">Ingresos</p>
        <p className="text-lg font-semibold text-green-600">{balance.income.toFixed(2)}</p>
      </div>
      <div>
        <p className="text-xs text-gray-500">Gastos</p>
        <p className="text-lg font-semibold text-red-600">{balance.expense.toFixed(2)}</p>
      </div>
      <div>
        <p className="text-xs text-gray-500">Balance</p>
        <p className={`text-lg font-semibold ${balance.balance >= 0 ? "text-green-600" : "text-red-600"}`}>
          {balance.balance.toFixed(2)}
        </p>
      </div>
    </div>
  );
}
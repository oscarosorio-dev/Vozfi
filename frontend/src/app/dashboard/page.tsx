"use client"

import { useEffect, useState, useCallback } from "react"
import { Header } from "@/components/layout/header"
import { FinancialSummary } from "@/components/features/financial-summary"
import { DashboardCharts } from "@/components/features/dashboard-charts"
import { VoiceAgentWidget } from "@/components/features/voice-agent-widget"
import { TransactionHistory } from "@/components/features/transaction-history"
import { getBalance, getCategorySummary, getTransactions, Balance, CategorySummary, Transaction } from "@/lib/api"

export default function Dashboard() {
  const [balance, setBalance] = useState<Balance | null>(null)
  const [categories, setCategories] = useState<CategorySummary[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = useCallback(async () => {
    try {
      const [bal, cats, txs] = await Promise.all([
        getBalance(),
        getCategorySummary(),
        getTransactions(),
      ])
      setBalance(bal)
      setCategories(cats)
      setTransactions(txs)
    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-900 border-t-transparent dark:border-zinc-50" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-8 space-y-8">
        <FinancialSummary balance={balance} />
        <div className="grid gap-8 lg:grid-cols-2">
          <VoiceAgentWidget onActionCompleted={fetchData} />
          <DashboardCharts categories={categories} />
        </div>
        <TransactionHistory transactions={transactions} onDeleted={fetchData} />
      </main>
    </div>
  )
}
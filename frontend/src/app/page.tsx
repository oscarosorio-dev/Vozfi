"use client";

import { useState } from "react";
import VoiceRecorder from "@/components/VoiceRecorder";
import BalanceCard from "@/components/BalanceCard";
import MonthlyChart from "@/components/MonthlyChart";
import TransactionsList from "@/components/TransactionsList";

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-100">
      <main className="mx-auto flex max-w-lg flex-col gap-6 px-6 py-12">
        <h1 className="text-2xl font-semibold text-center">Vozfi</h1>

        <VoiceRecorder onResult={() => setRefreshKey((k) => k + 1)} />
        <BalanceCard refreshKey={refreshKey} />
        <MonthlyChart refreshKey={refreshKey} />
        <TransactionsList refreshKey={refreshKey} />
      </main>
    </div>
  );
}
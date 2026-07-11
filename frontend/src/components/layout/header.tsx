export function Header() {
  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto w-full">
        <h1 className="text-xl font-bold tracking-tight text-zinc-950 dark:text-zinc-50">Vozfi Dashboard</h1>
        <div className="flex items-center space-x-2">
          <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
          <span className="text-xs font-semibold text-zinc-500 uppercase">Agente Activo</span>
        </div>
      </div>
    </header>
  )
}
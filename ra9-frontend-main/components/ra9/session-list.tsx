"use client"

export default function SessionList() {
  const sessions = [
    { id: "s_01", title: "Weekly summary" },
    { id: "s_02", title: "Budget planning" },
    { id: "s_03", title: "Research: LLM safety" },
  ]

  return (
    <div className="rounded-xl border border-border bg-background/60 backdrop-blur-md p-3">
      <div className="text-sm font-medium mb-2">Sessions</div>
      <ul className="space-y-1">
        {sessions.map((s) => (
          <li key={s.id}>
            <button className="w-full text-left px-2 py-1 rounded hover:bg-muted text-sm">{s.title}</button>
          </li>
        ))}
      </ul>
      <div className="mt-4 text-xs text-muted-foreground">Quick filters</div>
      <div className="mt-1 flex flex-wrap gap-2">
        <button className="px-2 py-1 rounded border border-border text-xs">With memory</button>
        <button className="px-2 py-1 rounded border border-border text-xs">Needs review</button>
      </div>
    </div>
  )
}

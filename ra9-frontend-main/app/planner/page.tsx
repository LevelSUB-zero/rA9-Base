import { PlannerCanvas } from "@/components/ra9/planner-canvas"

export default function PlannerPage() {
  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Planner</h1>
        <p className="text-sm text-muted-foreground">Create multi-step plans and connect outcomes.</p>
      </header>

      <PlannerCanvas
        nodes={[
          { id: "n1", title: "Gather Sources", confidence: 0.8 },
          { id: "n2", title: "Draft Answer", confidence: 0.7 },
          { id: "n3", title: "Verify Citations", confidence: 0.9 },
        ]}
        connections={[
          { from: "n1", to: "n2" },
          { from: "n2", to: "n3" },
        ]}
      />
    </main>
  )
}

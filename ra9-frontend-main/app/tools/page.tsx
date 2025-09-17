import { ToolRunner } from "@/components/ra9/tool-runner"

export default function ToolsPage() {
  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">Tools Console</h1>
        <p className="text-sm text-muted-foreground">Register tools, dry-run, and execute with approvals.</p>
      </header>

      <ToolRunner toolId="xman.web.fetch" inputs={{ url: "https://example.com", method: "GET" }} dryRun={true} />
    </main>
  )
}

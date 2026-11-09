/** @jsxImportSource hono/jsx */
import { readFile } from "node:fs/promises"
import { resolve } from "node:path"
import manifest from "../../registry.json"
import { CodeBlock } from "@/app/components/code-block"
import cottonUsage from "@/app/data/cotton-usage.json"
const COTTON_USAGE: Record<string, string> = cottonUsage

const ROOT = resolve(import.meta.dir, "../..")
const sources = new Map<string, Promise<string>>()
function source(path: string) {
  if (!sources.has(path)) sources.set(path, readFile(resolve(ROOT, path), "utf8"))
  return sources.get(path)!
}

export async function CottonInstallPanel({ component }: { component: string }) {
  const item = manifest.items.find((item) => item.name === component)!
  const files = item.files.filter((file) => file.path.startsWith("registry/django-cotton/"))
  return (
    <div class="space-y-5">
      <div class="space-y-2">
        <p class="text-sm font-medium">1. Install for Django-Cotton</p>
        <p class="text-xs text-muted-foreground">
          Configure Django-Cotton using the <a class="underline" href="/docs/cli#django-cotton">Django setup guide</a>.
          Templates install under templates/cotton/ with all their component parts.
        </p>
        {await CodeBlock({ code: `npx shadcn-htmx add ${component} --flavour cotton`, lang: "bash" })}
      </div>
      <div class="space-y-2">
        <p class="text-sm font-medium">2. Use it</p>
        {await CodeBlock({ code: COTTON_USAGE[component]!, lang: "html" })}
      </div>
      {await Promise.all(files.map(async (file) => (
        <details class="rounded-lg border bg-muted/20">
          <summary class="cursor-pointer px-4 py-2.5 text-sm font-medium">{file.target}</summary>
          <div class="border-t bg-background p-4">
            {await CodeBlock({ code: await source(file.path), lang: file.path.endsWith(".py") ? "python" : "html", filename: file.target })}
          </div>
        </details>
      )))}
    </div>
  )
}

import { test, expect } from "@playwright/test"

test("Cotton selection exposes install files and persists between docs pages", async ({ page }) => {
  await page.goto("/docs/card")
  await page.locator("[data-framework-select]").selectOption("cotton")
  const panel = page.locator('.lang-panel[data-lang="cotton"]').first()
  await expect(panel).toBeVisible()
  await expect(panel).toContainText("shadcn-htmx add card --flavour cotton")
  await expect(panel).toContainText("<c-card.header>")
  await expect(panel).toContainText("templates/cotton/card/header.html")
  await expect(page.locator('.lang-panel[data-lang="jinja"]').first()).toBeHidden()

  await page.goto("/docs/rating")
  await expect(page.locator("[data-framework-select]")).toHaveValue("cotton")
  await expect(page.locator('.lang-panel[data-lang="cotton"]').first()).toBeVisible()
  await expect(page.locator('.lang-panel[data-lang="cotton"]').first()).toContainText("shadcn_htmx.py")
  await page.locator('a[href="/docs/cli#django-cotton"]').first().click()
  await expect(page.locator("#django-cotton")).toBeVisible()

  await page.locator("[data-framework-select]").selectOption("jsx")
  await page.goto("/docs/card")
  await expect(page.locator('.lang-panel[data-lang="jsx"]').first()).toBeVisible()
  await expect(page.locator('.lang-panel[data-lang="cotton"]').first()).toBeHidden()
})

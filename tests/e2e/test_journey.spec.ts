import { test, expect } from "@playwright/test";

// E2E stub — roda com `npx playwright test` quando web estiver em preview
// Cobre jornada feliz: upload → flow → drawer → patterns (sem IA)

test("journey happy path", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Cascudo — Mapa Mental")).toBeVisible();
  // Upload dropzone existe
  await expect(page.getByText("Arraste o ZIP")).toBeVisible();
  // Flow demo renderiza
  await page.goto("/flow");
  await expect(page.getByText("Fluxo — demo")).toBeVisible();
  // Patterns page
  await page.goto("/patterns");
  await expect(page.getByText("Padrões do Corpus")).toBeVisible();
});

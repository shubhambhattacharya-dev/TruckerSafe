import { expect, test } from "@playwright/test";

test("plans a route and exposes the dashboard workflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Plan Your Truck Route" })).toBeVisible();
  await page.getByRole("button", { name: /Find Safe Routes/ }).click();
  await expect(page.getByText(/DEMO DATA/)).toBeVisible();
  await expect(page.locator(".route-card").first()).toBeVisible();
  await page.getByRole("button", { name: "Rain" }).click();
  await expect(page.locator("#map-holder").getByText("Rain (in/hr)")).toBeVisible();
  await page.getByRole("button", { name: /Save Trip/ }).click();
  await expect(page.getByRole("button", { name: "Saved ✓" })).toBeVisible();
});

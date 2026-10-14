// One POST /api/route-plans, typed DTOs. The recorded fixture is only used
// when VITE_DEMO_MODE=true, so API and validation failures remain visible
// during normal development and production use.

import demoFixture from "./demoFixture.json";
import type { RoutePlanRequest, RoutePlanResponse } from "../types";

const API_BASE: string = import.meta.env.VITE_API_BASE ?? "";
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";
// 60s: Render free tier cold-starts can take 30s+ and a full corridor plan
// runs ~20-25s of provider calls. Override with VITE_REQUEST_TIMEOUT_MS.
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS ?? 60_000);

type DemoFixture = RoutePlanResponse & { request: RoutePlanRequest };

export interface RoutePlanResult {
  plan: RoutePlanResponse;
  request: RoutePlanRequest;
  source: "api" | "fixture";
}

export async function fetchRoutePlan(
  request: RoutePlanRequest,
): Promise<RoutePlanResult> {
  if (DEMO_MODE) {
    const fixture = demoFixture as unknown as DemoFixture;
    return {
      plan: { ...fixture, demo_data: true },
      request,
      source: "fixture",
    };
  }

  try {
    const res = await fetch(`${API_BASE}/api/route-plans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => null) as { message?: string; error?: string } | null;
      throw new Error(body?.message ?? body?.error ?? `The API responded with ${res.status}.`);
    }
    const plan = (await res.json()) as RoutePlanResponse;
    return { plan, request, source: "api" };
  } catch (error) {
    if (!DEMO_MODE) {
      if (error instanceof Error && error.name === "TimeoutError") {
        throw new Error("The route-planning service took too long. Please try again.");
      }
      throw error;
    }
    const fixture = demoFixture as unknown as DemoFixture;
    // Demo mode is deliberate and visibly labelled in the UI.
    return {
      plan: { ...fixture, demo_data: true },
      request,
      source: "fixture",
    };
  }
}

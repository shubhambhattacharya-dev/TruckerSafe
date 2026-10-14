import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RiskBar from "../components/RiskBar";

describe("RiskBar", () => {
  it("renders each risk band with rounded shares that total 100%", () => {
    render(<RiskBar distanceMi={100} risk={{ severe_mi: 10, no_travel_mi: 0, high_mi: 20, moderate_mi: 30, low_mi: 40, avg_score: 2.5 }} />);
    expect(screen.getByRole("img", { name: "Miles per risk band" })).toBeInTheDocument();
    expect(screen.getByText("10 mi (10%)")).toBeInTheDocument();
    expect(screen.getByText("40 mi (40%)")).toBeInTheDocument();
    expect(screen.getByText("No Travel")).toBeInTheDocument();
  });
});

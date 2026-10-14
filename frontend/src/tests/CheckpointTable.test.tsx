import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CheckpointTable from "../components/CheckpointTable";
import type { Checkpoint } from "../types";

const checkpoints: Checkpoint[] = Array.from({ length: 9 }, (_, index) => ({
  idx: index + 1, lat: 41 + index, lon: -87 - index, distance_mi: index * 25,
  eta: "2026-10-15T08:00:00Z", location_name: `Stop ${index + 1}`,
  wind_mph: 12, rain_in_hr: 0, snow_in_hr: 0, risk_band: "LOW",
}));

describe("CheckpointTable", () => {
  it("paginates and expands a checkpoint's weather details", () => {
    render(<CheckpointTable checkpoints={checkpoints} intervalMi={25} allExpanded={false} />);
    expect(screen.getByText("Showing 1–8 of 9 checkpoints (every 25 miles)")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Stop 1"));
    expect(screen.getByText(/Weather matched to this checkpoint's/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "›" }));
    expect(screen.getByText("Stop 9")).toBeInTheDocument();
  });
});

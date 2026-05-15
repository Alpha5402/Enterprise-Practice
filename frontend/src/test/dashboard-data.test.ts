import { describe, expect, it } from "vitest";
import { getReportIdFromPath } from "@/App";

describe("dashboard smoke test", () => {
  it("keeps test runner wired", () => {
    expect(true).toBe(true);
  });

  it("parses report detail routes", () => {
    expect(getReportIdFromPath("/reports/abc-123")).toBe("abc-123");
    expect(getReportIdFromPath("/")).toBeNull();
  });
});

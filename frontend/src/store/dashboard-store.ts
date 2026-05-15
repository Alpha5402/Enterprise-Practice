import { create } from "zustand";

interface DashboardState {
  selectedIndustry: string | null;
  setSelectedIndustry: (industry: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  selectedIndustry: null,
  setSelectedIndustry: (industry) => set({ selectedIndustry: industry }),
}));


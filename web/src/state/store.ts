import { create } from "zustand";
import { MAX_HISTORY_DEPTH } from "../constants";
import { popTermHistory, pushTermHistory } from "../lib/history";

interface AppState {
  history: string[];
  push: (slug: string | null | undefined) => void;
  pop: () => string | null;
  clear: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  history: [],
  push: (slug) =>
    set((state) => ({
      history: pushTermHistory(state.history, slug, MAX_HISTORY_DEPTH),
    })),
  pop: () => {
    const { slug, remaining } = popTermHistory(get().history);
    set({ history: remaining });
    return slug;
  },
  clear: () => set({ history: [] }),
}));

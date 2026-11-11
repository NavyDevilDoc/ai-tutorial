import { useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAppStore } from "../state/store";

const TERM_PATH_RE = /^\/term\/(.+)$/;

/**
 * Centralizes term-page navigation + history management.
 *
 * `goToTerm` pushes the current term (if any) onto the history stack so
 * `goBack` can drain it one hop at a time back to Home. `goBack` never
 * pushes, which is what makes a multi-level back traversal possible.
 */
export function useTermNav(): {
  goToTerm: (slug: string) => void;
  goBack: () => void;
  goHome: () => void;
} {
  const navigate = useNavigate();
  const location = useLocation();
  const push = useAppStore((s) => s.push);
  const pop = useAppStore((s) => s.pop);
  const clear = useAppStore((s) => s.clear);

  const goToTerm = useCallback(
    (slug: string) => {
      const match = location.pathname.match(TERM_PATH_RE);
      if (match && match[1] !== slug) push(match[1]!);
      navigate(`/term/${slug}`);
    },
    [push, navigate, location.pathname],
  );

  const goBack = useCallback(() => {
    const slug = pop();
    if (slug) navigate(`/term/${slug}`);
    else navigate("/");
  }, [pop, navigate]);

  const goHome = useCallback(() => {
    clear();
    navigate("/");
  }, [clear, navigate]);

  return { goToTerm, goBack, goHome };
}

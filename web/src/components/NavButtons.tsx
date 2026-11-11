import { useTermNav } from "../lib/useTermNav";
import type { Term } from "../models";
import { useAppStore } from "../state/store";
import { Button } from "./ui/button";

export function NavButtons({
  bySlug,
}: {
  bySlug: ReadonlyMap<string, Term>;
}) {
  const { goBack, goHome } = useTermNav();
  const history = useAppStore((s) => s.history);

  const prevSlug = history[history.length - 1] ?? null;
  const prevTerm = prevSlug ? bySlug.get(prevSlug) : null;

  return (
    <div className="flex items-center gap-2">
      <Button variant="ghost" size="sm" onClick={goHome}>
        Home
      </Button>
      {prevTerm && (
        <Button variant="ghost" size="sm" onClick={goBack}>
          ← Back to {prevTerm.term}
        </Button>
      )}
    </div>
  );
}

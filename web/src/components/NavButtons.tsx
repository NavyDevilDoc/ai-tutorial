import { useNavigate } from "react-router-dom";
import { useAppStore } from "../state/store";
import type { Term } from "../models";
import { Button } from "./ui/button";

export function NavButtons({
  bySlug,
}: {
  bySlug: ReadonlyMap<string, Term>;
}) {
  const navigate = useNavigate();
  const history = useAppStore((s) => s.history);
  const pop = useAppStore((s) => s.pop);
  const clear = useAppStore((s) => s.clear);

  const prevSlug = history[history.length - 1] ?? null;
  const prevTerm = prevSlug ? bySlug.get(prevSlug) : null;

  function handleHome() {
    clear();
    navigate("/");
  }

  function handleBack() {
    const slug = pop();
    if (slug) navigate(`/term/${slug}`);
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="ghost" size="sm" onClick={handleHome}>
        Home
      </Button>
      {prevTerm && (
        <Button variant="ghost" size="sm" onClick={handleBack}>
          ← Back to {prevTerm.term}
        </Button>
      )}
    </div>
  );
}

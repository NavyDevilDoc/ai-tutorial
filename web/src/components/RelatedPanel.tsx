import { Link } from "react-router-dom";
import type { Term } from "../models";

const MAX_RELATED = 6;

export function RelatedPanel({
  term,
  bySlug,
}: {
  term: Term;
  bySlug: ReadonlyMap<string, Term>;
}) {
  const related = term.related_terms
    .map((slug) => bySlug.get(slug))
    .filter((t): t is Term => Boolean(t))
    .slice(0, MAX_RELATED);

  if (related.length === 0) return null;

  return (
    <section className="space-y-3">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Related Terms
      </h2>
      <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {related.map((r) => (
          <li key={r.slug}>
            <Link
              to={`/term/${r.slug}`}
              className="block rounded-md border p-3 transition-colors hover:border-primary hover:bg-accent"
            >
              <p className="text-sm font-medium">{r.term}</p>
              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                {r.definition}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

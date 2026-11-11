import { Link, useParams } from "react-router-dom";
import { NavButtons } from "../components/NavButtons";
import { RelatedPanel } from "../components/RelatedPanel";
import { TermCard } from "../components/TermCard";
import { TermGraph } from "../components/TermGraph";
import { Button } from "../components/ui/button";
import { TERM_NOT_FOUND_MSG } from "../constants";
import { loadAllTerms } from "../data";

export function TermRoute() {
  const { slug } = useParams<{ slug: string }>();
  const loaded = loadAllTerms();
  const term = slug ? loaded.bySlug.get(slug) : undefined;

  if (!term) {
    return (
      <section className="mx-auto max-w-3xl space-y-4 py-8">
        <p className="text-sm text-muted-foreground">{TERM_NOT_FOUND_MSG}</p>
        <Button asChild variant="outline" size="sm">
          <Link to="/">Back to home</Link>
        </Button>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl space-y-6 py-4">
      <NavButtons bySlug={loaded.bySlug} />
      <TermCard term={term} />
      <RelatedPanel term={term} bySlug={loaded.bySlug} />
      <TermGraph term={term} bySlug={loaded.bySlug} />
    </section>
  );
}

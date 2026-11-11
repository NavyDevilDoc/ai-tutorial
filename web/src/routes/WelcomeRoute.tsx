import { useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { SuggestionForm } from "../components/SuggestionForm";
import { Button } from "../components/ui/button";
import {
  APP_SUBTITLE,
  QUICK_START_SLUGS,
  WELCOME_HEADING,
  WELCOME_SUBTEXT,
} from "../constants";
import { loadAllTerms } from "../data";

export function WelcomeRoute() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const loaded = loadAllTerms();

  const legacyTerm = searchParams.get("term");
  useEffect(() => {
    if (legacyTerm && loaded.bySlug.has(legacyTerm)) {
      navigate(`/term/${legacyTerm}`, { replace: true });
    }
  }, [legacyTerm, loaded, navigate]);

  return (
    <section className="mx-auto max-w-2xl space-y-8 py-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">
          {WELCOME_HEADING}
        </h1>
        <p className="text-muted-foreground">{WELCOME_SUBTEXT}</p>
        <p className="text-xs text-muted-foreground">{APP_SUBTITLE}</p>
      </div>

      <div>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Quick starts
        </h2>
        <div className="flex flex-wrap gap-2">
          {QUICK_START_SLUGS.filter((s) => loaded.bySlug.has(s)).map((slug) => {
            const term = loaded.bySlug.get(slug)!;
            return (
              <Button key={slug} asChild variant="secondary" size="sm">
                <Link to={`/term/${slug}`}>{term.term}</Link>
              </Button>
            );
          })}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        {loaded.bySlug.size} terms across {loaded.byCategory.size} categories.
      </p>

      <SuggestionForm />
    </section>
  );
}

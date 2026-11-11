import {
  ANALOGY_PREFIX,
  CATEGORY_DISPLAY_NAMES,
  SENTENCE_PREFIX,
} from "../constants";
import { cn } from "../lib/utils";
import type { Term } from "../models";

const DIFFICULTY_BADGE_CLASSES = {
  beginner: "bg-green-600 text-white",
  intermediate: "bg-amber-500 text-white",
  advanced: "bg-red-600 text-white",
} as const;

export function TermCard({ term }: { term: Term }) {
  const categoryName =
    CATEGORY_DISPLAY_NAMES[term.category] ?? term.category;

  return (
    <article className="space-y-5">
      <header className="space-y-2">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-semibold tracking-tight">{term.term}</h1>
          <span
            className={cn(
              "rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
              DIFFICULTY_BADGE_CLASSES[term.difficulty],
            )}
          >
            {term.difficulty}
          </span>
        </div>
        <p className="text-xs uppercase tracking-wide text-muted-foreground">
          {categoryName}
        </p>
      </header>

      <p className="text-base leading-relaxed">{term.definition}</p>

      <Callout tone="info" title={ANALOGY_PREFIX} body={term.analogy} />
      <Callout
        tone="success"
        title={SENTENCE_PREFIX}
        body={term.use_in_a_sentence}
      />

      <section className="space-y-1">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Business Context
        </h2>
        <p className="text-sm text-foreground/90">{term.business_context}</p>
      </section>

      {term.tags.length > 0 && (
        <section className="flex flex-wrap gap-1.5 pt-2">
          {term.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-secondary px-2 py-0.5 text-xs text-secondary-foreground"
            >
              {tag}
            </span>
          ))}
        </section>
      )}
    </article>
  );
}

function Callout({
  tone,
  title,
  body,
}: {
  tone: "info" | "success";
  title: string;
  body: string;
}) {
  const bg = tone === "info" ? "bg-info" : "bg-success";
  const fg = tone === "info" ? "text-info-foreground" : "text-success-foreground";
  return (
    <aside className={cn("rounded-md p-4", bg, fg)}>
      <p className="text-sm font-semibold">{title}</p>
      <p className="mt-1 text-sm leading-relaxed">{body}</p>
    </aside>
  );
}

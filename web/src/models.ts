import { z } from "zod";

export const DIFFICULTIES = ["beginner", "intermediate", "advanced"] as const;
export type Difficulty = (typeof DIFFICULTIES)[number];

const SLUG_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

export const TermSchema = z.object({
  term: z.string().min(1),
  slug: z
    .string()
    .regex(SLUG_RE, "Slug must be lowercase and hyphen-separated"),
  category: z.string().min(1),
  difficulty: z.enum(DIFFICULTIES),
  definition: z.string().min(1),
  analogy: z.string().min(1),
  use_in_a_sentence: z.string().min(1),
  business_context: z.string().min(1),
  related_terms: z.array(z.string()),
  tags: z.array(z.string()),
});

export type Term = z.infer<typeof TermSchema>;

export const TermListSchema = z.array(TermSchema);

export function validateRelatedTerms(
  term: Term,
  allSlugs: ReadonlySet<string>,
): void {
  for (const slug of term.related_terms) {
    if (!allSlugs.has(slug)) {
      throw new Error(
        `Term '${term.slug}' references unknown related term '${slug}'`,
      );
    }
  }
}

export const MAX_TERM_NAME_LENGTH = 100;
export const MAX_SHORT_TEXT_LENGTH = 1000;
export const MAX_PROSE_LENGTH = 2000;

const CATEGORY_KEY_RE = /^[a-z][a-z_]*$/;
const optionalProse = () =>
  z
    .string()
    .trim()
    .max(MAX_PROSE_LENGTH)
    .optional()
    .transform((v) => (v && v.length > 0 ? v : undefined));

export const SuggestionSchema = z.object({
  termName: z.string().trim().min(1).max(MAX_TERM_NAME_LENGTH),
  category: z
    .string()
    .trim()
    .min(1)
    .max(64)
    .regex(CATEGORY_KEY_RE, "Category must be a snake_case key"),
  difficulty: z.enum(DIFFICULTIES),
  context: z
    .string()
    .trim()
    .max(MAX_SHORT_TEXT_LENGTH)
    .optional()
    .transform((v) => (v && v.length > 0 ? v : undefined)),
  definition: optionalProse(),
  analogy: optionalProse(),
  use_in_a_sentence: optionalProse(),
  business_context: optionalProse(),
});

export type SuggestionInput = z.input<typeof SuggestionSchema>;
export type SuggestionData = z.output<typeof SuggestionSchema>;

import {
  MAX_PROSE_LENGTH,
  MAX_SHORT_TEXT_LENGTH,
  MAX_TERM_NAME_LENGTH,
} from "../models";

export { MAX_PROSE_LENGTH, MAX_SHORT_TEXT_LENGTH, MAX_TERM_NAME_LENGTH };

export function sanitizeText(raw: string, maxLength: number = 500): string {
  let text = raw.trim();
  text = text.replaceAll("\x00", "");
  text = text.replace(/[\x01-\x09\x0b-\x0c\x0e-\x1f]/g, " ");
  return text.slice(0, maxLength);
}

export function sanitizeTermName(raw: string): string {
  let text = sanitizeText(raw, MAX_TERM_NAME_LENGTH);
  text = text.replace(/[^a-zA-Z0-9\s\-().'/]/g, "");
  text = text.trim();
  if (text.length === 0) {
    throw new Error("Term name is empty after sanitization");
  }
  return text;
}

export function sanitizeContext(raw: string): string {
  return sanitizeText(raw, MAX_SHORT_TEXT_LENGTH);
}

export function sanitizeProse(raw: string): string {
  return sanitizeText(raw, MAX_PROSE_LENGTH);
}

export interface IssuePayload {
  termName: string;
  category: string;
  difficulty: string;
  context?: string;
  definition?: string;
  analogy?: string;
  use_in_a_sentence?: string;
  business_context?: string;
}

const PROSE_FIELD_LABELS: Record<
  Exclude<keyof IssuePayload, "termName" | "category" | "difficulty">,
  string
> = {
  context: "Additional Context",
  definition: "Definition",
  analogy: "Analogy",
  use_in_a_sentence: "Use in a Sentence",
  business_context: "Business Context",
};

export function buildIssueBody(payload: IssuePayload): string {
  const jsonRecord: Record<string, string> = {
    term_name: payload.termName,
    category: payload.category,
    difficulty: payload.difficulty,
  };
  for (const key of [
    "context",
    "definition",
    "analogy",
    "use_in_a_sentence",
    "business_context",
  ] as const) {
    const value = payload[key];
    if (value && value.length > 0) jsonRecord[key] = value;
  }
  const jsonBlock = JSON.stringify(jsonRecord, null, 2);

  const headerTable =
    `| Field | Value |\n` +
    `|---|---|\n` +
    `| Term | ${payload.termName} |\n` +
    `| Category | ${payload.category} |\n` +
    `| Difficulty | ${payload.difficulty} |\n`;

  const proseSections: string[] = [];
  for (const key of Object.keys(PROSE_FIELD_LABELS) as Array<
    keyof typeof PROSE_FIELD_LABELS
  >) {
    const value = payload[key];
    if (value && value.length > 0) {
      proseSections.push(`### ${PROSE_FIELD_LABELS[key]}\n\n${value}`);
    }
  }
  const proseBlock =
    proseSections.length > 0
      ? proseSections.join("\n\n")
      : "### Additional Context\n\nNone provided.";

  return (
    `## Suggested Term\n\n` +
    headerTable +
    `\n` +
    proseBlock +
    `\n\n### Structured Data\n\n` +
    `\`\`\`json\n${jsonBlock}\n\`\`\``
  );
}

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import {
  CATEGORY_DISPLAY_NAMES,
  SUGGEST_ERROR_MSG,
  SUGGEST_RATE_LIMIT_MSG,
  SUGGEST_SUCCESS_MSG,
  SUGGEST_TERM_HEADING,
  SUGGEST_TERM_SUBTEXT,
} from "../constants";
import { loadAllTerms } from "../data";
import { DIFFICULTIES, SuggestionSchema, type SuggestionInput } from "../models";
import { Button } from "./ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { Input } from "./ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Textarea } from "./ui/textarea";

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; issueUrl?: string }
  | { kind: "error"; message: string };

const DEFAULT_VALUES: SuggestionInput = {
  termName: "",
  category: "",
  difficulty: "beginner",
  context: "",
  definition: "",
  analogy: "",
  use_in_a_sentence: "",
  business_context: "",
};

export function SuggestionForm() {
  const loaded = loadAllTerms();
  const categoryKeys = [...loaded.byCategory.keys()].sort();

  const form = useForm<SuggestionInput>({
    resolver: zodResolver(SuggestionSchema),
    defaultValues: DEFAULT_VALUES,
    mode: "onBlur",
  });

  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const submitting = status.kind === "submitting";

  async function onSubmit(values: SuggestionInput) {
    setStatus({ kind: "submitting" });
    try {
      const res = await fetch("/api/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (res.status === 429) {
        setStatus({ kind: "error", message: SUGGEST_RATE_LIMIT_MSG });
        return;
      }
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as {
          error?: string;
        };
        setStatus({
          kind: "error",
          message: data.error ?? SUGGEST_ERROR_MSG,
        });
        return;
      }
      const data = (await res.json()) as { issueUrl?: string };
      setStatus({ kind: "success", issueUrl: data.issueUrl });
      form.reset(DEFAULT_VALUES);
    } catch {
      setStatus({ kind: "error", message: SUGGEST_ERROR_MSG });
    }
  }

  return (
    <section className="space-y-3 rounded-md border bg-muted/30 p-4">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {SUGGEST_TERM_HEADING}
        </h2>
        <p className="text-xs text-muted-foreground">{SUGGEST_TERM_SUBTEXT}</p>
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-4"
          noValidate
        >
          <FormField
            control={form.control}
            name="termName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Term</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g. Fine-tuning"
                    maxLength={100}
                    disabled={submitting}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={submitting}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {categoryKeys.map((key) => (
                        <SelectItem key={key} value={key}>
                          {CATEGORY_DISPLAY_NAMES[key] ?? key}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="difficulty"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Difficulty</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={submitting}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a difficulty" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {DIFFICULTIES.map((d) => (
                        <SelectItem key={d} value={d}>
                          <span className="capitalize">{d}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="space-y-4 rounded-md border bg-background/40 p-3">
            <p className="text-xs text-muted-foreground">
              The four fields below are optional. Fill in what you know — we'll
              generate the rest with Claude during review.
            </p>

            <FormField
              control={form.control}
              name="definition"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Definition</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={3}
                      placeholder="Plain-language explanation."
                      maxLength={2000}
                      disabled={submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="analogy"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Analogy</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={3}
                      placeholder="A non-technical comparison."
                      maxLength={2000}
                      disabled={submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="use_in_a_sentence"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Use in a sentence</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={2}
                      placeholder="A realistic business scenario."
                      maxLength={2000}
                      disabled={submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="business_context"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Business context</FormLabel>
                  <FormControl>
                    <Textarea
                      rows={2}
                      placeholder="Where this comes up in practice."
                      maxLength={2000}
                      disabled={submitting}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="context"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Note to maintainer (optional)</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Where did you hear it? Anything we should know?"
                    maxLength={1000}
                    disabled={submitting}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Context for the maintainer during review — not published.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" disabled={submitting}>
            {submitting ? "Submitting…" : "Submit suggestion"}
          </Button>

          {status.kind === "success" && (
            <p
              role="status"
              className="rounded-md bg-success p-3 text-sm text-success-foreground"
            >
              {SUGGEST_SUCCESS_MSG}
              {status.issueUrl && (
                <>
                  {" "}
                  <a
                    className="underline"
                    href={status.issueUrl}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View issue
                  </a>
                </>
              )}
            </p>
          )}
          {status.kind === "error" && (
            <p
              role="alert"
              className="rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive"
            >
              {status.message}
            </p>
          )}
        </form>
      </Form>
    </section>
  );
}

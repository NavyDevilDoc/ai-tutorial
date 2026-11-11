import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { TermCard } from "../components/TermCard";
import { SAMPLE_TERMS } from "./fixtures";

const ALPHA = SAMPLE_TERMS[0]!;

describe("TermCard", () => {
  test("renders all core text fields", () => {
    render(<TermCard term={ALPHA} />);
    expect(screen.getByRole("heading", { name: ALPHA.term })).toBeInTheDocument();
    expect(screen.getByText(ALPHA.definition)).toBeInTheDocument();
    expect(screen.getByText(ALPHA.analogy)).toBeInTheDocument();
    expect(screen.getByText(ALPHA.use_in_a_sentence)).toBeInTheDocument();
    expect(screen.getByText(ALPHA.business_context)).toBeInTheDocument();
  });

  test("renders every tag as a chip", () => {
    render(<TermCard term={ALPHA} />);
    for (const tag of ALPHA.tags) {
      expect(screen.getByText(tag)).toBeInTheDocument();
    }
  });

  test("shows the difficulty badge", () => {
    render(<TermCard term={ALPHA} />);
    expect(screen.getByText(ALPHA.difficulty)).toBeInTheDocument();
  });
});

import { readdirSync, readFileSync } from "node:fs";
import { join, dirname, basename, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { loadFromRawCategories } from "../src/data/loader";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, "..", "src", "data");

function readRawCategories(): Record<string, unknown> {
  const entries = readdirSync(DATA_DIR)
    .filter((f) => f.endsWith(".json") && !f.startsWith("_"))
    .sort();

  const out: Record<string, unknown> = {};
  for (const file of entries) {
    const key = basename(file, extname(file));
    const text = readFileSync(join(DATA_DIR, file), "utf-8");
    out[key] = JSON.parse(text);
  }
  return out;
}

try {
  const loaded = loadFromRawCategories(readRawCategories());
  const total = loaded.bySlug.size;
  const categories = loaded.byCategory.size;
  console.log(
    `validate-data: OK — ${total} terms across ${categories} categories.`,
  );
} catch (err) {
  const message = err instanceof Error ? err.message : String(err);
  console.error(`validate-data: FAIL — ${message}`);
  process.exit(1);
}

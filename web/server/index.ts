import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createSuggestRouter } from "./suggest";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DIST_DIR = join(__dirname, "..", "dist");
const PORT = Number(process.env.PORT ?? 3000);

const app = new Hono();

app.route("/api", createSuggestRouter());

app.get("/healthz", (c) => c.text("ok"));

app.use(
  "/*",
  serveStatic({
    root: DIST_DIR,
    rewriteRequestPath: (path) => (path === "/" ? "/index.html" : path),
  }),
);

app.notFound(async (c) => {
  try {
    const html = await readFile(join(DIST_DIR, "index.html"), "utf-8");
    return c.html(html);
  } catch {
    return c.text("Not found", 404);
  }
});

serve({ fetch: app.fetch, port: PORT }, (info) => {
  console.log(`Server listening on http://localhost:${info.port}`);
});

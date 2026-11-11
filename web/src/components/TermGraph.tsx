import { useMemo, useState } from "react";
import {
  Background,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useNavigate } from "react-router-dom";
import { DIFFICULTY_COLORS } from "../constants";
import type { Term } from "../models";
import { Button } from "./ui/button";

const CENTER = { x: 0, y: 0 };
const RADIUS = 220;

export function TermGraph({
  term,
  bySlug,
}: {
  term: Term;
  bySlug: ReadonlyMap<string, Term>;
}) {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const related = useMemo(
    () =>
      term.related_terms
        .map((slug) => bySlug.get(slug))
        .filter((t): t is Term => Boolean(t)),
    [term, bySlug],
  );

  const { nodes, edges } = useMemo(() => {
    const centerNode: Node = {
      id: term.slug,
      position: CENTER,
      data: { label: term.term },
      style: nodeStyle(term, true),
      draggable: false,
    };
    const relatedNodes: Node[] = related.map((r, i) => {
      const angle = (i / related.length) * 2 * Math.PI;
      return {
        id: r.slug,
        position: {
          x: CENTER.x + RADIUS * Math.cos(angle),
          y: CENTER.y + RADIUS * Math.sin(angle),
        },
        data: { label: r.term },
        style: nodeStyle(r, false),
        draggable: false,
      };
    });
    const relatedEdges: Edge[] = related.map((r) => ({
      id: `${term.slug}->${r.slug}`,
      source: term.slug,
      target: r.slug,
      style: { stroke: "hsl(var(--muted-foreground))" },
    }));
    return { nodes: [centerNode, ...relatedNodes], edges: relatedEdges };
  }, [term, related]);

  if (related.length === 0) return null;

  return (
    <section className="space-y-2">
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => setOpen((v) => !v)}
      >
        {open ? "Hide" : "Show"} relationship graph ({related.length})
      </Button>
      {open && (
        <div
          className="h-80 w-full rounded-md border bg-background"
          aria-label={`Relationship graph for ${term.term}`}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable
            proOptions={{ hideAttribution: true }}
            onNodeClick={(_, node) => {
              if (node.id !== term.slug) navigate(`/term/${node.id}`);
            }}
          >
            <Background />
          </ReactFlow>
        </div>
      )}
    </section>
  );
}

function nodeStyle(t: Term, isCenter: boolean): React.CSSProperties {
  const bg = DIFFICULTY_COLORS[t.difficulty];
  return {
    background: bg,
    color: "white",
    border: isCenter ? "3px solid white" : "1px solid rgba(255,255,255,0.4)",
    borderRadius: 10,
    padding: "6px 10px",
    fontSize: isCenter ? 13 : 11,
    fontWeight: isCenter ? 600 : 500,
    width: "auto",
    cursor: isCenter ? "default" : "pointer",
  };
}

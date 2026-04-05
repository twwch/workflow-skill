# Coze Workflow Generation Skill - Design Spec

## Overview

A Claude Code skill (`/coze-workflow`) that generates Coze Studio-compatible workflow JSON files from natural language descriptions. Users describe what they want, the skill produces a JSON file that can be directly imported into Coze Studio.

## Core Decisions

| Dimension | Decision |
|-----------|----------|
| Trigger | `/coze-workflow` as standalone skill |
| Output format | JSON only (Coze native format) |
| Node info | Layered: summary table in SKILL.md + full schema in references |
| Generation strategy | Template match first, schema assembly fallback |
| Interaction | Smart: generate directly if clear, ask questions if ambiguous (max 3 rounds) |
| Source repo | `coze-dev/coze-studio` cloned to `source/coze-studio/` |

## Project Structure

```
coze-workflow/                       # skill directory (parallel to dify-workflow/)
├── SKILL.md                         # main skill file
├── references/
│   ├── nodes/                       # one .md per node type
│   ├── templates/                   # common workflow templates (.json)
│   ├── dsl-format.md                # Coze canvas JSON format spec
│   └── edge-and-layout.md           # edge connections and layout rules
└── examples/                        # example workflows (.json)
```

Source code: `source/coze-studio/` (already git-ignored via `source/` in .gitignore)

## Data Extraction Sources

From Coze Studio source code:

1. **Frontend node registries**: `packages/workflow/playground/src/nodes-registries/` — each node type has `node-registry.ts`, `constants.ts`, `form.tsx`, `data-transformer.tsx`
2. **Backend node implementations**: `backend/domain/workflow/internal/nodes/` — Go implementations
3. **Canvas entity**: `backend/domain/workflow/entity/vo/canvas.go` — canvas/graph structure
4. **Import/export logic**: search for export/import workflow handlers
5. **Wiki docs**: referenced for node type catalog

## SKILL.md Structure

Identical to Dify skill structure:
1. Frontmatter (name: coze-workflow, description, triggers)
2. Smart Interaction Logic
3. Node Router Table (all Coze node types)
4. Generation Flow (parse → select → template match → assemble → output JSON)
5. DSL Structure Quick Reference (Coze canvas JSON format)
6. Output Rules (filename: `<name>.coze.json`, node key format, position rules)
7. Template Matching
8. Few-Shot Example
9. Format (JSON only)

## Node Reference File Format

Same as Dify — each `references/nodes/<node>.md`:
- Purpose, Core Fields table, Full Schema, Variable Reference Rules, Example JSON snippet
- Target: 200-400 lines per file

## Template Strategy

Initial templates (adapted to Coze's node types):
1. **chatbot.json** — Basic conversation flow
2. **rag.json** — Knowledge retrieval + LLM
3. **agent.json** — Tool-calling workflow
4. **translation.json** — Multi-step LLM chain

## Output Conventions

- Filename: `<kebab-case-description>.coze.json`
- JSON format matching Coze Studio's import schema
- Node keys use Coze's key format
- Positions follow Coze's DAG layout conventions

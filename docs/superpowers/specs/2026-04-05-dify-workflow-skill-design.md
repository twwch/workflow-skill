# Dify Workflow Generation Skill - Design Spec

## Overview

A Claude Code skill (`/dify-workflow`) that generates Dify-compatible workflow DSL files from natural language descriptions. Users describe what they want, the skill produces a YAML (or JSON) file that can be directly imported into Dify.

## Core Decisions

| Dimension | Decision |
|-----------|----------|
| Trigger | `/dify-workflow` as standalone skill |
| Output format | YAML (default), JSON (when user specifies) |
| Node info | Layered: summary table in SKILL.md + full schema in references |
| Generation strategy | Template match first, schema assembly fallback |
| Interaction | Smart: generate directly if clear, ask questions if ambiguous (max 3 rounds) |
| Extensibility | Same directory pattern reusable for Coze and future platforms |

## Project Structure

```
workflow-skill/
├── source/                          # git ignored - third-party source code
│   └── dify/                        # Dify repo clone
├── dify-workflow/                   # skill directory
│   ├── SKILL.md                     # main skill file
│   ├── references/
│   │   ├── nodes/                   # one .md per node type
│   │   │   ├── llm.md
│   │   │   ├── knowledge-retrieval.md
│   │   │   ├── code.md
│   │   │   ├── http-request.md
│   │   │   ├── if-else.md
│   │   │   ├── variable-aggregator.md
│   │   │   ├── iteration.md
│   │   │   ├── template-transform.md
│   │   │   ├── question-classifier.md
│   │   │   ├── parameter-extractor.md
│   │   │   ├── tool.md
│   │   │   ├── start.md
│   │   │   ├── end.md
│   │   │   └── answer.md
│   │   ├── templates/               # common workflow templates
│   │   │   ├── chatbot.yml
│   │   │   ├── rag.yml
│   │   │   ├── agent.yml
│   │   │   └── translation.yml
│   │   ├── dsl-format.md            # Dify DSL format spec (YAML + JSON)
│   │   └── edge-and-layout.md       # edge connections and layout rules
│   └── examples/                    # example workflows for few-shot
│       ├── simple-chatbot.yml
│       └── rag-with-rerank.yml
├── .gitignore                       # source/ ignored
└── docs/superpowers/specs/          # design documents
```

## SKILL.md Structure

### 1. Frontmatter

- `name`: `dify-workflow`
- `description`: Generate Dify workflow DSL files from natural language descriptions. Produces importable YAML/JSON workflow definitions.
- Trigger words: "generate dify workflow", "dify workflow", "create dify flow", "dify 工作流", "生成 dify 流程"

### 2. Smart Interaction Logic

```
User input received
  → Is the description clear? (has explicit input/output and processing logic)
    → YES: proceed to generation
    → NO: ask clarifying questions (max 3 rounds)
      - What is the input/output?
      - What processing steps are needed?
      - Any specific models or tools to use?
```

### 3. Node Router Table (Summary)

A compact table in SKILL.md, one line per node:

| Node | Type Key | Purpose | Key Params | Schema Path |
|------|----------|---------|------------|-------------|
| Start | `start` | Entry point, defines input variables | input variables | `references/nodes/start.md` |
| End | `end` | Terminal node, defines output | output variables | `references/nodes/end.md` |
| Answer | `answer` | Streaming text response | answer content | `references/nodes/answer.md` |
| LLM | `llm` | Call language model | model, prompt, context | `references/nodes/llm.md` |
| Knowledge Retrieval | `knowledge-retrieval` | Query knowledge base | dataset_ids, query | `references/nodes/knowledge-retrieval.md` |
| Code | `code` | Execute Python/JS code | code, language, variables | `references/nodes/code.md` |
| HTTP Request | `http-request` | Call external API | method, url, headers, body | `references/nodes/http-request.md` |
| If/Else | `if-else` | Conditional branching | conditions, comparators | `references/nodes/if-else.md` |
| Variable Aggregator | `variable-aggregator` | Merge variables from branches | variable list | `references/nodes/variable-aggregator.md` |
| Iteration | `iteration` | Loop over list items | iterator variable, steps | `references/nodes/iteration.md` |
| Template Transform | `template-transform` | Jinja2 template rendering | template, variables | `references/nodes/template-transform.md` |
| Question Classifier | `question-classifier` | Route by question intent | model, classes | `references/nodes/question-classifier.md` |
| Parameter Extractor | `parameter-extractor` | Extract structured params from text | model, parameters | `references/nodes/parameter-extractor.md` |
| Tool | `tool` | Invoke built-in/custom tool | provider, tool name, params | `references/nodes/tool.md` |

### 4. Generation Flow

```
1. Parse user requirement
2. Select node combination based on router table
3. Check template match:
   a. Match found → load template, customize nodes/params/prompts
   b. No match → assemble from individual node schemas
4. Generate edges (connections between nodes)
5. Calculate layout coordinates (left-to-right, branch expansion)
6. Produce output:
   - Default: YAML file written to current directory
   - If user requests JSON: JSON file
   - Filename: <descriptive-name>.dify.yml or .dify.json
7. Present summary of generated workflow to user
```

### 5. DSL Generation Rules

Reference `references/dsl-format.md` for:
- App metadata fields (app name, mode, description, icon)
- `workflow` block structure: `graph` (nodes + edges) + `features`
- Node definition format: id, type, data, position
- Edge format: id, source, target, sourceHandle, targetHandle
- Variable reference syntax: `{{#node_id.output_key#}}`
- System variable syntax: `{{#sys.query#}}`, `{{#sys.files#}}`

### 6. Output Conventions

- Filename: `<kebab-case-description>.dify.yml` (or `.dify.json`)
- Every workflow must include: app metadata, start node, at least one processing node, end/answer node
- All node IDs use UUID v4 format
- Position coordinates auto-calculated: start at (0, 0), 250px horizontal gap, 150px vertical gap for branches

## Node Reference File Format

Each `references/nodes/<node>.md` follows this structure:

```markdown
# <Node Name> (<type_key>)

## Purpose
One-line description of what this node does.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ... | ... | ... | ... |

## Full Schema
Complete field definitions extracted from Dify source code, including:
- All optional fields with defaults
- Enum values for constrained fields
- Nested object structures

## Variable Reference Rules
- Input variable format
- Available system variables
- Output variable names

## Example Snippet
Minimal working YAML snippet for this node.
```

Target: 200-400 lines per file to keep context usage reasonable on lazy load.

## Template Strategy

### Source
- Extract from Dify source code test fixtures
- Adapt from Dify community templates
- Each template is a complete, importable YAML

### Initial Templates (4)
1. **chatbot.yml** — Basic conversation: Start → LLM → Answer
2. **rag.yml** — Knowledge retrieval QA: Start → Knowledge Retrieval → LLM (with context) → Answer
3. **agent.yml** — Tool-calling agent: Start → LLM (with tools) → Tool → LLM → Answer
4. **translation.yml** — Translation chain: Start → LLM (detect language) → LLM (translate) → Answer

### Template Customization Points
Each template includes YAML comments marking customizable sections:
- Model selection
- Prompt content
- Knowledge base IDs
- Tool configurations
- Variable names

## Edge and Layout Rules

Documented in `references/edge-and-layout.md`:
- Edge format: `{id, source, sourceHandle, target, targetHandle, type}`
- sourceHandle/targetHandle naming conventions from Dify source
- Auto-layout algorithm: topological sort → assign x/y coordinates
- Branch handling: if-else creates parallel vertical tracks

## Data Extraction Plan

From Dify source code (`source/dify/`), extract:
1. Node type definitions from `api/core/workflow/nodes/` — each node's entity class defines the schema
2. DSL serialization format from `api/core/app/apps/` — how workflows are exported/imported
3. Edge/graph structure from `api/core/workflow/graph/` — connection validation rules
4. Test fixtures from `api/tests/` — real workflow examples
5. Community templates if available in the repo

## Future Extensibility

When adding Coze support, create a parallel structure:
```
coze-workflow/
├── SKILL.md
├── references/
│   ├── nodes/
│   ├── templates/
│   └── dsl-format.md
└── examples/
```

The pattern is identical — only the node definitions, DSL format, and templates change per platform.
